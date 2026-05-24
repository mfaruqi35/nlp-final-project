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

custom_css = """
@import url('https://fonts.googleapis.com/css2?family=Amiri:wght@400;700&family=Plus+Jakarta+Sans:wght@300;400;500;600&display=swap');

* {
    box-sizing: border-box;
}

body, .gradio-container {
    background: #f0f7f2 !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    min-height: 100vh;
}

.gradio-container,
.gradio-container > .main,
.gradio-container > .main > .wrap,
.gradio-container .contain,
div.gradio-container {
    max-width: 100% !important;
    width: 100% !important;
    margin: 0 !important;
    padding: 0 !important;
}

/* Header section */
#header-section {
    background: linear-gradient(135deg, #1a5c38 0%, #2e7d50 50%, #1a5c38 100%);
    padding: 48px 40px 40px;
    text-align: center;
    position: relative;
    overflow: hidden;
    border-bottom: 4px solid #c8a951;
    width: 100%;
}

#header-section::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0; bottom: 0;
    background-image: 
        radial-gradient(circle at 20% 50%, rgba(200, 169, 81, 0.12) 0%, transparent 50%),
        radial-gradient(circle at 80% 20%, rgba(255,255,255,0.06) 0%, transparent 40%);
    pointer-events: none;
}

#header-section .ornament {
    font-size: 13px;
    color: #c8a951;
    letter-spacing: 4px;
    text-transform: uppercase;
    font-weight: 500;
    margin-bottom: 10px;
    font-family: 'Plus Jakarta Sans', sans-serif;
}

#header-section h1 {
    font-family: 'Amiri', serif !important;
    font-size: 42px !important;
    font-weight: 700 !important;
    color: #ffffff !important;
    margin: 0 0 8px !important;
    letter-spacing: 1px;
    line-height: 1.2;
}

#header-section .subtitle {
    font-family: 'Amiri', serif;
    font-size: 20px;
    color: #c8a951;
    margin-bottom: 12px;
    letter-spacing: 2px;
}

#header-section p {
    color: rgba(255,255,255,0.75) !important;
    font-size: 14px !important;
    font-weight: 300 !important;
    margin: 0 !important;
    letter-spacing: 0.3px;
}

/* Main card */
#main-card {
    background: #ffffff;
    margin: 0;
    padding: 40px 48px;
    border-left: 1px solid #d4e8da;
    border-right: 1px solid #d4e8da;
    width: 100%;
}

/* Section labels */
.section-label {
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: #2e7d50;
    margin-bottom: 10px;
    display: flex;
    align-items: center;
    gap: 8px;
}

.section-label::after {
    content: '';
    flex: 1;
    height: 1px;
    background: linear-gradient(to right, #d4e8da, transparent);
}

/* Audio components */
.audio-block {
    background: #f8fcf9;
    border: 1.5px solid #c8e6d0;
    border-radius: 12px;
    overflow: hidden;
    transition: border-color 0.2s;
}

.audio-block:hover {
    border-color: #2e7d50;
}

select.mic-select,
.audio-block select,
[data-testid="microphone-waveform"] ~ div select,
.controls select {
    color: #1a3d2b !important;
    background: #ffffff !important;
    border: 1.5px solid #2e7d50 !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;

    height: 44px !important;
    line-height: 44px !important;
    padding: 0 14px !important;

    display: flex !important;
    align-items: center !important;

    overflow: visible !important;
    vertical-align: middle !important;

    appearance: none;
    -webkit-appearance: none;
    -moz-appearance: none;
}


/* Audio label fix - override dark background on label */
.audio-block label,
.audio-block .label-wrap,
.audio-block .label-wrap span,
.audio-block span.svelte-1b6s6xi,
[class*="audio"] .label-wrap span {
    background: #f8fcf9 !important;
    color: #1a3d2b !important;
}

/* Override Gradio default dark label pill */
.audio-block .label-wrap {
    background: #e6f4ec !important;
    border-bottom: 1px solid #c8e6d0 !important;
    padding: 6px 12px !important;
}

.audio-block .label-wrap * {
    color: #1a3d2b !important;
    fill: #2e7d50 !important;
}

/* Dropdown */
select, .gr-dropdown select {
    background: #f8fcf9 !important;
    border: 1.5px solid #c8e6d0 !important;
    border-radius: 10px !important;
    color: #1a3d2b !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-size: 14px !important;
    padding: 10px 14px !important;
    transition: border-color 0.2s !important;
}

select:focus {
    border-color: #2e7d50 !important;
    outline: none !important;
    box-shadow: 0 0 0 3px rgba(46, 125, 80, 0.1) !important;
}

/* Submit button */
#submit-btn {
    background: linear-gradient(135deg, #2e7d50, #1a5c38) !important;
    border: none !important;
    border-radius: 10px !important;
    color: #ffffff !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-size: 14px !important;
    font-weight: 600 !important;
    letter-spacing: 1px !important;
    padding: 13px 28px !important;
    cursor: pointer !important;
    transition: all 0.2s !important;
    box-shadow: 0 4px 14px rgba(26, 92, 56, 0.3) !important;
    text-transform: uppercase !important;
    width: 100% !important;
    margin-top: 6px !important;
}

#submit-btn:hover {
    background: linear-gradient(135deg, #1a5c38, #134a2d) !important;
    box-shadow: 0 6px 20px rgba(26, 92, 56, 0.4) !important;
    transform: translateY(-1px) !important;
}

#submit-btn:active {
    transform: translateY(0) !important;
}

/* Labels */
label, .gr-label {
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    color: #2d5a3d !important;
    margin-bottom: 6px !important;
}

/* Divider */
.divider {
    height: 1px;
    background: linear-gradient(to right, transparent, #c8e6d0, transparent);
    margin: 28px 0;
}

/* Response section */
#response-area {
    background: linear-gradient(180deg, #f0f9f3 0%, #ffffff 100%);
    border: 1.5px solid #c8e6d0;
    border-radius: 12px;
    padding: 20px;
    position: relative;
}

#response-area::before {
    content: 'JAWABAN ASISTEN';
    position: absolute;
    top: -10px;
    left: 16px;
    background: #ffffff;
    padding: 0 8px;
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 2px;
    color: #2e7d50;
    font-family: 'Plus Jakarta Sans', sans-serif;
}

/* Footer */
#footer-section {
    background: #1a3d2b;
    padding: 20px 40px;
    text-align: center;
    border-top: 3px solid #c8a951;
    width: 100%;
}

#footer-section p {
    color: rgba(255,255,255,0.45) !important;
    font-size: 12px !important;
    margin: 0 !important;
    letter-spacing: 0.5px;
}

/* Gradio internals cleanup */
.gr-panel, .gr-box {
    border: none !important;
    background: transparent !important;
    box-shadow: none !important;
}

footer { display: none !important; }

.gap { gap: 16px !important; }
"""

with gr.Blocks(css=custom_css) as demo:
    with gr.Column(elem_id="header-section"):
        gr.HTML("""
            <div class="ornament">&#9670; Asisten Digital Ibadah &#9670;</div>
            <h1>Tanya Haji & Umrah</h1>
            <div class="subtitle">بِسْمِ اللهِ الرَّحْمٰنِ الرَّحِيْمِ</div>
            <p>Ajukan pertanyaan seputar ibadah haji dan umrah melalui suara, dapatkan jawaban langsung dari asisten AI.</p>
        """)

    with gr.Column(elem_id="main-card"):
        gr.HTML('<div class="section-label">Rekam Pertanyaan Anda</div>')
        audio_input = gr.Audio(
            sources=["microphone"],
            type="filepath",
            format="wav",
            label="Ketuk untuk merekam",
            elem_classes=["audio-block"]
        )

        gr.HTML('<div style="height:20px"></div>')

        mode_input = gr.Dropdown(
            choices=["normalize", "preserve"],
            value="normalize",
            label="Mode Respons"
        )

        submit_btn = gr.Button("Kirim Pertanyaan", elem_id="submit-btn")

        gr.HTML('<div class="divider"></div>')

        gr.HTML('<div class="section-label">Jawaban Asisten</div>')
        with gr.Column(elem_id="response-area"):
            audio_output = gr.Audio(
                type="filepath",
                label="",
                elem_classes=["audio-block"]
            )

    with gr.Column(elem_id="footer-section"):
        gr.HTML('<p>Semua jawaban bersifat informatif. Konsultasikan keputusan ibadah Anda kepada ulama atau pembimbing resmi.</p>')

    submit_btn.click(
        fn=voice_chat,
        inputs=[audio_input, mode_input], 
        outputs=audio_output
    )

demo.launch()