import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.tts import transcribe_text_to_speech
import os

"""
Py file for debugging
"""

text = "tung tung tung tung tung tung tung tung sahur, anomali mengerikan yang hanya keluar pada sahur. konon katanya kalau ada orang yang dipanggil sahur 3 kali, dan tidak nyaut, maka makhluk ini datang ke rumah kalian. iih seremnyaaa, tung tung ini biasanya bersuara layaknya pukulan kentungan seperti ini, tung tung tung tung tung"
print(f"[TEXT] {text}")
output = transcribe_text_to_speech(text)
if "[ERROR]" not in output:
    print(f"Play audio in: {output}")
    os.startfile(output)
else:
    print("Audio failed to create.")
os.startfile(output)