from app.tts import transcribe_text_to_speech
import os

text = "main game gaming gamer games riot games"
output = transcribe_text_to_speech(text)
print(f"Output: {output}")
os.startfile(output)