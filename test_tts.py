from app.tts import transcribe_text_to_speech
import os


text = "cari first taxi 6 bulan KSA"
output = transcribe_text_to_speech(text)
print(f"Output: {output}")
os.startfile(output)