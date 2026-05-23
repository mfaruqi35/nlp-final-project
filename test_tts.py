from app.tts import transcribe_text_to_speech
import os

text = 'klik tombol "cari" lalu pilih'
output = transcribe_text_to_speech(text)
print(f"Output: {output}")
os.startfile(output)