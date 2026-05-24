import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.tts import transcribe_text_to_speech
import os

"""
Py file for debugging
"""

text = " First, open a travel website or airline app and input your departure city, Jeddah as your destination, and your travel dates. Then, choose your flight, fill in the passenger details, and complete the payment online, insyaAllah."
print(f"[TEXT] {text}")
output = transcribe_text_to_speech(text)
print(f"Output: {output}")
os.startfile(output)