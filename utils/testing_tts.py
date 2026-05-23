import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.tts import transcribe_text_to_speech
import os

"""
Py file for debugging
"""

text = "upacara mencari cari carikan percikan secercah ceria canda cinta"
print(f"[TEXT] {text}")
output = transcribe_text_to_speech(text)
print(f"Output: {output}")
os.startfile(output)