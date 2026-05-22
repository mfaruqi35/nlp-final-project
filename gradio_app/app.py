import os
import tempfile
import uuid 
import requests
import gradio as gr

def voice_chat(audio_path, mode):
    if audio_path is None:
        return None
    
    with open(audio_path, "rb") as f:
        files = {"file": ("voice.wav", f, "audio/wav")}
        data = {"mode": mode}
        response = requests.post("http://localhost:8000/voice-chat", files=files, data=data, timeout=180)

    if response.status_code == 200:
        unique_filename = f"tts_output_{uuid.uuid4()}.wav"
        output_audio_path = os.path.join(tempfile.gettempdir(), unique_filename)
        
        with open(output_audio_path, "wb") as f:
            f.write(response.content)
        return output_audio_path
    else:
        print(f"Error dari backend: {response.status_code} - {response.text}")
        return None

with gr.Blocks() as demo:
    gr.Markdown("# Voice Chatbot")
    gr.Markdown("Berbicara langsung ke mikrofon dan dapatkan jawaban suara dari asisten AI.")

    with gr.Row():
        with gr.Column():
            audio_input = gr.Audio(sources=["microphone"], type="filepath", format="wav", label="Rekam Pertanyaan Anda")
            mode_input = gr.Dropdown(
                choices=["normalize", "preserve"],
                value="normalize",
                label="Mode Respons"
            ) 
            submit_btn = gr.Button("Submit")
            audio_output = gr.Audio(type="filepath", label="Balasan dari Asisten")

        submit_btn.click(
            fn=voice_chat,
            inputs=[audio_input, mode_input], 
            outputs=audio_output
        )

demo.launch()