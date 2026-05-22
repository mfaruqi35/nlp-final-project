import os
import uuid
import tempfile
import subprocess
import re

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
COQUI_DIR = os.path.join(BASE_DIR, "coqui_tts")

COQUI_MODEL_PATH = os.path.join(COQUI_DIR, "checkpoint_1260000-inference.pth")
COQUI_CONFIG_PATH = os.path.join(COQUI_DIR, "config.json")
COQUI_SPEAKERS_PATH = os.path.join(COQUI_DIR, "speakers.pth")
COQUI_SPEAKER = "wibowo"

def _normalize_tts_text(text: str) -> str:
    """
    Membersihkan markdown dari LLM dan menyesuaikan ejaan (Spoken Form)
    agar lebih natural saat diucapkan oleh model.
    """
    spoken_text = text.lower()

    # 1. Bersihkan simbol Markdown/noise dari LLM (*, _, ~, dll)
    spoken_text = re.sub(r'[\*\_\~]', '', spoken_text)
    
    # 2. Aturan Fonetik Konsonan Mati (Devoicing)
    spoken_text = re.sub(r'd\b', 't', spoken_text)
    spoken_text = re.sub(r'b\b', 'p', spoken_text)

    # # 3. Kamus Pengecualian (Lexicon) untuk kata spesifik
    # lexicon = {
    #     "jadwal": "jatwal",
    #     "jeddah": "jedah",
    # }
    # for word, replacement in lexicon.items():
    #     spoken_text = re.sub(rf'\b{word}\b', replacement, spoken_text)

    return spoken_text

def _grapheme_to_phoneme(text: str) -> str:
    """
    Mengonversi huruf alfabet biasa menjadi simbol fonetik (IPA).
    """
    text = text.lower()
    
    mapping = {
        'v': 'f',
        'ng': 'ŋ',
        'ny': 'ɲ',
        'sy': 'ʃ',
        'kh': 'x',
        'c': 'tʃ',
        'j': 'dʒ',
        'y': 'j',  
        'g': 'ɡ'
    }
    
    for grapheme, phoneme in mapping.items():
        text = text.replace(grapheme, phoneme)
        
    return text

def _normalize_tts_text(text: str) -> str:
    
    return text

def transcribe_text_to_speech(text: str) -> str:
    """
    Fungsi untuk mengonversi teks menjadi suara menggunakan TTS engine yang ditentukan.
    Args:
        text (str): Teks yang akan diubah menjadi suara.
    Returns:
        str: Path ke file audio hasil konversi.
    """

# Alur Pipeline TTS:
    # 1. Teks Mentah -> 2. Teks Normal (Spoken Form) -> 3. Teks IPA -> 4. Audio
    normalized_text = _normalize_tts_text(text)
    phonemic_text = _grapheme_to_phoneme(normalized_text)
    path = _tts_with_coqui(phonemic_text)

# === ENGINE 1: Coqui TTS ===
def _tts_with_coqui(text: str) -> str:
    tmp_dir = tempfile.gettempdir()
    output_path = os.path.join(tmp_dir, f"tts_{uuid.uuid4()}.wav")

    cmd = [
        "tts",
        "--text", text,
        "--model_path", COQUI_MODEL_PATH,
        "--config_path", COQUI_CONFIG_PATH,
        "--speaker_idx", COQUI_SPEAKER,
        "--speakers_file_path", COQUI_SPEAKERS_PATH,
        "--out_path", output_path
    ]
    
    try:
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] TTS subprocess failed: {e}")
        return "[ERROR] Failed to synthesize speech"

    return output_path
