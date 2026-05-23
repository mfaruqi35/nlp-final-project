from app.tts import transcribe_text_to_speech
import os

text = "I can help you check the schedule, akhi. Please let me know your timing departure city, agar saya bisa cari opsi flight terbaik for next week, insyaAllah."
output = transcribe_text_to_speech(text)
print(f"Output: {output}")
os.startfile(output)