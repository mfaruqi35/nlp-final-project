from app.tts import transcribe_text_to_speech
import os

text = "upacara mencari cari carikan percikan secercah ceria canda cinta"
print(f"[TEXT] {text}")
output = transcribe_text_to_speech(text)
print(f"Output: {output}")
os.startfile(output)