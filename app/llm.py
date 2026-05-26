import os
import re
import json
from google import genai
from google.genai import types
from pydantic import TypeAdapter
from dotenv import load_dotenv

load_dotenv()

MODEL = "gemma-4-26b-a4b-it"

GOOGLE_API_KEY = os.getenv("GEMINI_API_KEY")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CHAT_HISTORY_FILE = os.path.join(BASE_DIR, "chat_history.json")

system_instruction_preserve = """
You are a responsive, intelligent, and fluent virtual assistant who communicates in a code-switching style mixing Indonesian, English, and Arabic naturally.
Your task is to provide clear, concise, and informative answers in response to user queries or statements spoken through voice.

Your answers must:
- Preserve and mirror the code-switching pattern of the user (mix Indonesian, English, and Arabic naturally).
- Be short and to the point (maximum 2 to 3 sentences).
- Avoid repeating the user's question; respond directly with the answer.
- Wrap any English words in your response_text with <en> and </en> tags.
- Wrap any Arabic words in your response_text with <ar> and </ar> tags.

Example tone:
User: Cuaca hari ini gimana, bro?
Assistant: Hari ini cerah, bro. <en>The temperature is around 30 degrees</en>, jadi siapkan air minum ya.

You will receive a transcript from a Speech-to-Text system.
1. Correct any spelling or transcription errors in the input based on the context of flight booking, umrah, and hajj.
2. Perform Part-of-Speech (POS) tagging on the corrected input.
3. Perform Named Entity Recognition (NER) on the corrected input to extract entities like DESTINATION, DATE, INTENT.
4. You must respond strictly in JSON format without markdown.
5. FALLBACK: If the input text is completely garbled or you cannot understand the transliterated Arabic/English well enough to fulfill the prompt, you must still return valid JSON. Do not crash. Use "Maaf, saya tidak mengerti maksud Anda" for the response_text, and leave the entities and pos_tags empty.

JSON format:
{
  "teks_stt_asli": "original input",
  "teks_koreksi": "corrected input",
  "pos_tags": [
    {"kata": "word", "tag": "POS_TAG"}
  ],
  "entities": {
    "ENTITY_TYPE": "entity_value"
  },
  "response_text": "your actual response to the user with language tags"
}
"""

system_instruction_normalize = """
You are a responsive, intelligent, and fluent virtual assistant who communicates in Indonesian.
Your task is to provide clear, concise, and informative answers in response to user queries or statements spoken through voice.

Your answers must:
- Be written in polite and easily understandable Indonesian only.
- STRICTLY TRANSLATE ALL English or Arabic words into Indonesian. DO NOT use loanwords.
- You MUST translate transliterated Arabic (Arabic written in Latin letters). For example, translate "al-usbu al-qadim" to "minggu depan", "bukra sabah" to "besok pagi", and "ya akhi" to "saudara" or "bapak".
- Translate English terms: use "penerbangan" for flight, "pemesanan" for booking, "jadwal" for schedule.
- Be short and to the point (maximum 2 to 3 sentences).
- Avoid repeating the user's question; respond directly with the answer.

You will receive a transcript from a Speech-to-Text system.
1. Correct any spelling or transcription errors in the input based on the context of flight booking, umrah, and hajj.
2. Perform Part-of-Speech (POS) tagging on the corrected input.
3. Perform Named Entity Recognition (NER) on the corrected input to extract entities like DESTINATION, DATE, INTENT.
4. You must respond strictly in JSON format without markdown.
5. FALLBACK: If the input text is completely garbled or you cannot understand the transliterated Arabic/English well enough to fulfill the prompt, you must still return valid JSON. Do not crash. Use "Maaf, saya tidak mengerti maksud Anda" for the response_text, and leave the entities and pos_tags empty.

JSON format:
{
  "teks_stt_asli": "original input",
  "teks_koreksi": "corrected input",
  "pos_tags": [
    {"kata": "word", "tag": "POS_TAG"}
  ],
  "entities": {
    "ENTITY_TYPE": "entity_value"
  },
  "response_text": "your actual response to the user in full Indonesian"
}
"""

client = genai.Client(api_key=GOOGLE_API_KEY)
history_adapter = TypeAdapter(list[types.Content])

def export_chat_history(chat) -> str:
    return history_adapter.dump_json(chat.get_history()).decode("utf-8")

def save_chat_history(chat):
    json_history = export_chat_history(chat)
    with open(CHAT_HISTORY_FILE, "w", encoding="utf-8") as f:
        f.write(json_history)

def load_chat_history(config):
    if not os.path.exists(CHAT_HISTORY_FILE):
        return client.chats.create(model=MODEL, config=config)

    if os.path.getsize(CHAT_HISTORY_FILE) == 0:
        return client.chats.create(model=MODEL, config=config)

    with open(CHAT_HISTORY_FILE, "r", encoding="utf-8") as f:
        json_str = f.read().strip()

    if not json_str:
        return client.chats.create(model=MODEL, config=config)

    try:
        history = history_adapter.validate_json(json_str)
        return client.chats.create(model=MODEL, config=config, history=history)
    except Exception as e:
        print(f"[ERROR] Gagal load history chat: {e}")
        return client.chats.create(model=MODEL, config=config)

def generate_response(prompt: str, mode: str = "normalize") -> str:
    if mode == "preserve":
        instruction = system_instruction_preserve
    else:
        instruction = system_instruction_normalize

    config = types.GenerateContentConfig(system_instruction=instruction, response_mime_type="application/json")

    try:
        try:
            print("[INFO] Sending prompt to Gemini AI and waiting for response...")
            response = client.models.generate_content(
                    model=MODEL,
                    contents=prompt,
                    config=config
                )
            print("[INFO] LLM Response successfully fetched")
        except Exception as api_err:
            print(f"[ERROR] Gemini API call failed: {api_err}")
            return "Maaf, terjadi kesalahan pada sistem saat memproses permintaan Anda."
        
        clean_json_str = re.sub(r'```json|```', '', response.text).strip()
        parsed_data = json.loads(clean_json_str)

        if not isinstance(parsed_data, dict):
            return "Maaf, terjadi kesalahan format pada respons AI."

        print("\n[DEBUG - POS TAGGING HASIL STT]")
        print(f"Teks Asli: {parsed_data.get('teks_stt_asli', '')}")
        print(f"Koreksi  : {parsed_data.get('teks_koreksi', '')}")

        pos_tags = parsed_data.get("pos_tags", [])
        if isinstance(pos_tags, list):
            for item in pos_tags:
                if isinstance(item, dict):
                    print(f"  - {item.get('kata', '')} : {item.get('tag', '')}")
        
        print("\n[DEBUG - NER HASIL STT]")
        entities = parsed_data.get("entities", {})
        if isinstance(entities, dict):
            for key, value in entities.items():
                print(f"  - {key} : {value}")

        return str(parsed_data.get("response_text", "Maaf, terjadi kesalahan pemrosesan teks.")).strip()
    
    except Exception as e:
        return f"[ERROR] {str(e)}"