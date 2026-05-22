import os
import subprocess

# Atur path sesuai dengan struktur folder proyekmu
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
AUDIO_DIR = os.path.join(BASE_DIR, "data", "corpus", "audio")
FIXED_DIR = os.path.join(BASE_DIR, "data", "corpus", "audio_fixed")

# Buat folder output jika belum ada
os.makedirs(FIXED_DIR, exist_ok=True)

# Ambil SEMUA file .wav di folder corpus/audio
all_audio_files = [f for f in os.listdir(AUDIO_DIR) if f.endswith(".wav")]

print(f"Memulai standardisasi format untuk keseluruhan {len(all_audio_files)} file audio...")
print("Proses ini akan memastikan seluruh dataset seragam 100% untuk Whisper.\n")

for filename in all_audio_files:
    input_path = os.path.join(AUDIO_DIR, filename)
    output_path = os.path.join(FIXED_DIR, filename)
    
    # Perintah FFmpeg untuk menyeragamkan format
    cmd = [
        "ffmpeg",
        "-y",                 # Timpa file output jika sudah ada
        "-i", input_path,     # Input file
        "-ar", "16000",       # Sample rate 16kHz
        "-ac", "1",           # Mono channel
        "-c:a", "pcm_s16le",  # Codec 16-bit PCM
        output_path
    ]

    try:
        # Jalankan command FFmpeg
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        print(f"  [OK] Siap digunakan: {filename}")
    except subprocess.CalledProcessError:
        print(f"  [ERROR] FFmpeg gagal memproses file ini: {filename}")

print("\nSelesai! Sekarang folder 'audio_fixed' berisi SELURUH dataset dengan format yang sudah sempurna.")