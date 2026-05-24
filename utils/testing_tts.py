import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.tts import transcribe_text_to_speech
import os

"""
Py file for debugging
"""

text = "best"
print(f"[TEXT] {text}")
output = transcribe_text_to_speech(text)
# Pastikan output bukan error sebelum diputar
if "[ERROR]" not in output:
    print(f"Berhasil! Memutar audio di: {output}")
    os.startfile(output)
else:
    print("Pembuatan audio gagal, file tidak diputar.")
print(f"Output: {output}")
os.startfile(output)