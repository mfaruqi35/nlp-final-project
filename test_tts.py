from app.tts import transcribe_text_to_speech
import os


text = "B2B P3K KPK PPP PSSI UP3AI C2C"
output = transcribe_text_to_speech(text)
print(f"Output: {output}")
os.startfile(output)