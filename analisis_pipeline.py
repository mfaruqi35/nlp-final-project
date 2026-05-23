import os
import json
import time
from datetime import datetime
from jiwer import wer, cer
import gc
import re
import shutil

from app.stt import transcribe_speech_to_text
from app.llm import generate_response
from app.tts import transcribe_text_to_speech


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
AUDIO_DIR = os.path.join(BASE_DIR, "data", "corpus", "audio_fixed")
REFERENCE_FILE = os.path.join(BASE_DIR, "data", "corpus", "transcripts", "reference.json")
RESULTS_DIR = os.path.join(BASE_DIR, "data", "results")

AUDIO_OUT_DIR = os.path.join(RESULTS_DIR, "audio_output")
CHECKPOINT_FILE = os.path.join(RESULTS_DIR, "checkpoint.json")
os.makedirs(RESULTS_DIR, exist_ok=True)
os.makedirs(AUDIO_OUT_DIR, exist_ok=True)

# Preprocessing hasil transkrip whisper
def clean_text(text):
    text = text.lower()
    text = re.sub(r'[^\w\s]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()

    return text

# Checkpoint agar progres tidak ulang dari awal saat program dihentikan tengah jalan
def load_checkpoint():
    if os.path.exists(CHECKPOINT_FILE):
        with open(CHECKPOINT_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_checkpoint(results):
    with open(CHECKPOINT_FILE, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)    

def load_reference():
    with open(REFERENCE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

# Mengambil id ujaran
def get_utterance_id(filename):
    filename = filename.lower()
    parts = os.path.splitext(filename)[0].split("_")
    if len(parts) >= 2:
        raw_id = parts[1]
        # normalize: audio01 -> audio1
        if raw_id.startswith("audio"):
            number = raw_id.replace("audio", "").lstrip("0") or "0"
            return f"audio{number}"
    return None

def run_pipeline(audio_path, mode):
    with open(audio_path, "rb") as f:
        file_bytes = f.read()

    # STT
    t0 = time.time()
    transcript = transcribe_speech_to_text(file_bytes, ".wav")
    stt_latency = time.time() - t0

    # LLM
    t1 = time.time()
    time.sleep(15)
    response_text = generate_response(transcript, mode)
    llm_latency = time.time() - t1

    if "[ERROR]" in response_text or "500" in response_text:
        print(" [INFO] LLM error detected, skipping TTS syntehsis")
        raise Exception("LLM_500_ERROR")

    else:
        t2 = time.time()
        audio_output = transcribe_text_to_speech(response_text)
        tts_latency = time.time() - t2

    total_latency = time.time() - t0

    return {
        "transcript": transcript.strip(),
        "response": response_text,
        "audio_output": audio_output,
        "stt_latency": round(stt_latency, 2),
        "llm_latency": round(llm_latency, 2),
        "tts_latency": round(tts_latency, 2),
        "total_latency": round(total_latency, 2)
    }

def summarize_by_utterance(results):
    utterance_data = {}

    for r in results:
        if "error" in r and "transcript" not in r:
            continue
        uid = r.get("utterance_id")
        if not uid:
            continue
        if uid not in utterance_data:
            utterance_data[uid] = {"wer": [], "cer": [], "stt_latency": [], "llm_latency": [], "tts_latency": [], "total_latency": []}

        if r.get("wer") is not None:
            utterance_data[uid]["wer"].append(r["wer"])
        if r.get("cer") is not None:
            utterance_data[uid]["cer"].append(r["cer"])
        for key in ["stt_latency", "llm_latency", "tts_latency", "total_latency"]:
            if r.get(key) is not None:
                utterance_data[uid][key].append(r[key])

    print("\nSUMMARY PER UTTERANCE")
    print("=" * 60)
    for uid in sorted(utterance_data.keys(), key=lambda x: int(x.replace("audio", ""))):
        data = utterance_data[uid]
        avg = lambda lst: round(sum(lst) / len(lst), 4) if lst else None
        print(f"\n  {uid}:")
        print(f"    Avg WER        : {avg(data['wer'])}")
        print(f"    Avg CER        : {avg(data['cer'])}")
        print(f"    Avg STT latency: {avg(data['stt_latency'])}s")
        print(f"    Avg LLM latency: {avg(data['llm_latency'])}s")
        print(f"    Avg TTS latency: {avg(data['tts_latency'])}s")
        print(f"    Avg Total      : {avg(data['total_latency'])}s")

    return utterance_data

def main():
    reference = load_reference()
    audio_files = sorted([
        f for f in os.listdir(AUDIO_DIR) if f.endswith(".wav")
    ])

    results = load_checkpoint()
    processed = set((r["filename"], r["mode"]) for r in results if "error" not in r or r.get("transcript"))
    wer_scores = []
    cer_scores = []

    print(f"Total audio files: {len(audio_files)}")
    print("=" * 60)

    for filename in audio_files:
        audio_path = os.path.join(AUDIO_DIR, filename)
        utterance_id = get_utterance_id(filename)
        ref_text = reference.get(utterance_id, None)

        print(f"\nProcessing: {filename}")
        print(f"Utterance ID: {utterance_id}")
        print(f"Reference: {ref_text}")

        for mode in ["normalize", "preserve"]:
            if(filename, mode) in processed:
                print(f" Mode: {mode} - skipped (already preprocessed)")
                continue
            print(f"\n  Mode: {mode}")
            success = False
            while not success:
                try:
                    result = run_pipeline(audio_path, mode)

                    transcript = result["transcript"]
                    print(f"  Transcript: {transcript}")
                    print(f"  Response: {result['response']}")
                    print(f"  STT latency: {result['stt_latency']}s")
                    print(f"  LLM latency: {result['llm_latency']}s")
                    print(f"  TTS latency: {result['tts_latency']}s")
                    print(f"  Total latency: {result['total_latency']}s")

                    temp_audio_path = result["audio_output"]
                    if os.path.exists(temp_audio_path):
                        # Buat nama file rapi, misal: 2362_audio01_normalize.wav
                        new_audio_name = f"{os.path.splitext(filename)[0]}_{mode}.wav"
                        permanent_audio_path = os.path.join(AUDIO_OUT_DIR, new_audio_name)
                        
                        # Copy dari folder Temp ke folder data/results/audio_output
                        shutil.copy(temp_audio_path, permanent_audio_path)
                        
                        # Timpa path lama dengan path baru agar JSON mencatat path permanen
                        result["audio_output"] = permanent_audio_path
                        print(f"  Audio saved to: {permanent_audio_path}")

                    if ref_text:
                        clean_ref = clean_text(ref_text)
                        clean_trans = clean_text(result["transcript"])

                        print(f"    DEBUG - Clean Ref: {clean_ref}")
                        print(f"    DEBUG - Clean Trans: {clean_trans}")

                        word_error = wer(clean_ref, clean_trans)
                        char_error = cer(clean_ref, clean_trans)
                        
                        print(f"  WER: {round(word_error, 4)}")
                        print(f"  CER: {round(char_error, 4)}")
                        wer_scores.append(word_error)
                        cer_scores.append(char_error)
                    else:
                        word_error = None
                        char_error = None
                        print(f"  WER/CER: no reference found for {utterance_id}")

                    results.append({
                        "filename": filename,
                        "utterance_id": utterance_id,
                        "mode": mode,
                        "reference": ref_text,
                        "transcript": transcript,
                        "response": result["response"],
                        "audio_output": result["audio_output"],
                        "wer": round(word_error, 4) if word_error is not None else None,
                        "cer": round(char_error, 4) if char_error is not None else None,
                        "stt_latency": result["stt_latency"],
                        "llm_latency": result["llm_latency"],
                        "tts_latency": result["tts_latency"],
                        "total_latency": result["total_latency"]
                    })
                    save_checkpoint(results)
                    success = True

                except Exception as e:
                    if str(e) == "LLM_500_ERROR":
                        print(f"  [!] Terdeteksi Error 500, menunggu 30 detik...")
                        time.sleep(30)
                    else:
                        print(f"  [ERROR] {e}")
                        results.append({"filename": filename, "mode": mode, "error": str(e)})
                        save_checkpoint(results)
                        success = True

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    if wer_scores:
        avg_wer = round(sum(wer_scores) / len(wer_scores), 4)
        avg_cer = round(sum(cer_scores) / len(cer_scores), 4)
        print(f"Average WER: {avg_wer}")
        print(f"Average CER: {avg_cer}")

    latencies = [r["total_latency"] for r in results if "total_latency" in r]
    if latencies:
        avg_latency = round(sum(latencies) / len(latencies), 2)
        print(f"Average total latency: {avg_latency}s")

    utterance_summary = summarize_by_utterance(results)

    # Simpan hasil
    output_file = os.path.join(RESULTS_DIR, f"pipeline_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump({
            "summary": {
                "total_files": len(audio_files),
                "average_wer": avg_wer if wer_scores else None,
                "average_cer": avg_cer if wer_scores else None,
                "average_latency": avg_latency if latencies else None
            },
                "summary_per_utterance": {
                    uid: {k: round(sum(v)/len(v), 4) if v else None for k, v in data.items()}
                    for uid, data in utterance_summary.items()
                },
            "results": results
        }, f, ensure_ascii=False, indent=2)

    print(f"\nResults saved to: {output_file}")

if __name__ == "__main__":
    main()