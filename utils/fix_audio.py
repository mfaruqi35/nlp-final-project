import os
import subprocess

"""
Program untuk memperbaiki format audio 
yang tidak sesuai dengan whisper
"""

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
AUDIO_DIR = os.path.join(BASE_DIR, "data", "corpus", "audio")
FIXED_DIR = os.path.join(BASE_DIR, "data", "corpus", "audio_fixed")

os.makedirs(FIXED_DIR, exist_ok=True)
all_audio_files = [f for f in os.listdir(AUDIO_DIR) if f.endswith(".wav")]

print(f"Standardize {len(all_audio_files)} audio files...")

for filename in all_audio_files:
    input_path = os.path.join(AUDIO_DIR, filename)
    output_path = os.path.join(FIXED_DIR, filename)
    
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
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        print(f"  [OK] Ready to use: {filename}")
    except subprocess.CalledProcessError:
        print(f"  [ERROR] FFmpeg fail to process: {filename}")

print("\nAudio fixing done, all new audio stored in 'audio_fixed' folder")