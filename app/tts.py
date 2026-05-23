import os
import uuid
import tempfile
import subprocess
import re
import json

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
COQUI_DIR = os.path.join(BASE_DIR, "coqui_tts")

COQUI_MODEL_PATH = os.path.join(COQUI_DIR, "checkpoint_1260000-inference.pth")
COQUI_CONFIG_PATH = os.path.join(COQUI_DIR, "config.json")
COQUI_SPEAKERS_PATH = os.path.join(COQUI_DIR, "speakers.pth")
COQUI_SPEAKER = "wibowo"

ENGLISH_WORDS_PATH = os.path.join(BASE_DIR, "..", "data", "corpus", "transcripts", "english_words.json")

with open(ENGLISH_WORDS_PATH, "r", encoding="utf-8") as f:
    ENGLISH_WORDS = json.load(f)

def _expand_numbers(text: str) -> str:
    """
    Mengonversi angka ke teks Indonesia.
    """
    ones = ['', 'satu', 'dua', 'tiga', 'empat', 'lima', 'enam', 'tujuh', 'delapan', 'sembilan',
            'sepuluh', 'sebelas', 'dua belas', 'tiga belas', 'empat belas', 'lima belas',
            'enam belas', 'tujuh belas', 'delapan belas', 'sembilan belas']
    tens = ['', '', 'dua puluh', 'tiga puluh', 'empat puluh', 'lima puluh',
            'enam puluh', 'tujuh puluh', 'delapan puluh', 'sembilan puluh']

    def convert(n):
        if n < 20:
            return ones[n]
        elif n < 100:
            return tens[n // 10] + ((' ' + ones[n % 10]) if n % 10 else '')
        elif n < 1000:
            prefix = 'seratus' if n // 100 == 1 else ones[n // 100] + ' ratus'
            rest = convert(n % 100)
            return prefix + ((' ' + rest) if rest else '')
        elif n < 1000000:
            prefix = 'seribu' if n // 1000 == 1 else ones[n // 1000] + ' ribu'
            rest = convert(n % 1000)
            return prefix + ((' ' + rest) if rest else '')
        else:
            return str(n)

    def replace_number(match):
        num_str = match.group(0).replace(',', '').replace('.', '')
        try:
            return convert(int(num_str))
        except:
            return match.group(0)

    return re.sub(r'\b\d[\d,\.]*\b', replace_number, text)

def _expand_acronym(text: str) -> str:
    """
    Mengubah singkatan kapital menjadi huruf yang dieja satu per satu.
    Contoh: KSA -> ke es a, PBB -> pe be be
    """
    vowel_map = {
        'a': 'a', 'b': 'be', 'c': 'ce', 'd': 'de', 'e': 'e',
        'f': 'ef', 'g': 'ge', 'h': 'ha', 'i': 'i', 'j': 'je',
        'k': 'ka', 'l': 'el', 'm': 'em', 'n': 'en', 'o': 'o',
        'p': 'pe', 'q': 'ki', 'r': 'er', 's': 'es', 't': 'te',
        'u': 'u', 'v': 'fe', 'w': 'we', 'x': 'eks', 'y': 'ye',
        'z': 'zet', '0': 'nol', '1': 'satu', '2': 'dua', '3': 'tiga', '4': 'empat',
        '5': 'lima', '6': 'enam', '7': 'tujuh', '8': 'delapan', '9': 'sembilan'
    }

    def expand(match):
        word = match.group(0)
        if not any(c.isupper() for c in word):
            return word
        return ' '.join(vowel_map.get(c.lower(), c) for c in word)

    # hanya match kata yang semua hurufnya kapital, minimal 2 huruf
    return re.sub(r'\b[A-Z0-9]{2,}\b', expand, text)

def _normalize_tts_text(text: str) -> str:
    """
    Membersihkan markdown dari LLM dan menyesuaikan ejaan (Spoken Form)
    agar lebih natural saat diucapkan oleh model.
    """
    spoken_text = _expand_acronym(text)
    spoken_text = _expand_numbers(spoken_text)
    spoken_text = spoken_text.lower()

    # 1. Bersihkan simbol Markdown/noise dari LLM (*, _, ~, dll)
    spoken_text = re.sub(r'[\*\_\~\"\']', '', spoken_text)
    
    # 2. Aturan Fonetik Konsonan Mati (Devoicing)
    spoken_text = re.sub(r'd\b', 't', spoken_text)
    spoken_text = re.sub(r'b\b', 'p', spoken_text)

    for word, replacement in ENGLISH_WORDS.items():
        spoken_text = re.sub(rf'\b{word}\b', replacement, spoken_text)

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
    print(f"[DEBUG - normalized] {normalized_text}")
    phonemic_text = _grapheme_to_phoneme(normalized_text)
    print(f"[DEBUG - phonemic] {phonemic_text}")
    path = _tts_with_coqui(phonemic_text)

    return path

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
