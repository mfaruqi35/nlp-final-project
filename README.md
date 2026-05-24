# Voice Chatbot UAS – STT, Gemini LLM, TTS Integration

Proyek UAS ini merupakan aplikasi chatbot berbasis suara yang memungkinkan pengguna berbicara langsung melalui antarmuka web. Sistem akan mengenali suara pengguna, mengubahnya menjadi teks (Speech-to-Text), memprosesnya menggunakan model bahasa besar (Gemini API), lalu mengubah hasil jawabannya kembali menjadi suara (Text-to-Speech).

## 📌 Fitur Utama

- 🎙️ Speech-to-Text (STT) menggunakan `whisper.cpp` dari OpenAI.
- 🧠 LLM Integration menggunakan Google Gemini API untuk menghasilkan respons dalam Bahasa Indonesia.
- 🔊 Text-to-Speech (TTS) menggunakan model Coqui TTS (Indonesian TTS).
- 🧪 Antarmuka pengguna interaktif berbasis `Gradio` untuk pengujian langsung dari browser.

## ⚙️ Persiapan

### 1. Clone Repository

```bash
git clone https://github.com/mfaruqi35/voice_chatbot_project.git
cd voice_chatbot_project
```

### 2. Buat Virtual Environment

```bash
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
```

### 3. Setup Whisper.cpp

Clone dan build whisper.cpp, lalu download model:

```bash
mkdir whisper
cd whisper
git clone https://github.com/ggerganov/whisper.cpp
cd whisper.cpp
cmake -B build
cmake --build build --config Release
```

Download model whisper:

```bash
cd whisper/whisper.cpp
./models/download-ggml-model.sh large-v3-turbo
```

### 4. Setup Coqui TTS

Download file berikut dari [Wikidepia Indonesian-TTS v1.2](https://github.com/Wikidepia/indonesian-tts/releases/tag/v1.2) dan letakkan di `app/coqui_tts/`:

- `checkpoint_1260000-inference.pth`
- `config.json`
- `speakers.pth`

### 5. Setup API Key

Buat file `.env` di root project:

## 🗂️ Struktur Proyek

```
voice_chatbot_project/
│
├── app/
│   ├── main.py                         # Endpoint utama FastAPI
│   ├── llm.py                          # Integrasi Gemini API
│   ├── stt.py                          # Transkripsi suara (whisper.cpp)
│   ├── tts.py                          # TTS dengan Coqui
│   └── whisper/
        └── whisper.cpp/                # Hasil clone whisper.cpp
│   └── coqui_utils/                    # Model dan config Coqui TTS
│
├── gradio_app/
│   └── app.py                          # Frontend dengan Gradio
│
├── data/
│   ├── corpus/
│   │    └── transcripts/
│   │        ├── english_words.json     # Daftar pengucapan kata bahasa inggris
│   │        └── reference.json         # Naskah audio untuk menghitung WER dan CER
│   │
│   └── results/
│       └── pipeline_result_*.json      # Hasil perhitungan WER, CER dan latency untuk semua audio
│
├── utils/
│   ├── fix_audio.py                    # File python untuk memperbaiki format audio yang invalid
│   └── testing_tts.py                  # File debugging output audio TTS
│
├── analisis_pipeline.py                # Pipeline perhitungan WER, CER dan latency
│
├── .env                                # Menyimpan Gemini API Key
├── requirements.txt                    # Daftar dependensi Python
```

## 📚 Catatan

- Semua file audio sudah diconvert ke format `.wav`.
- Model whisper yang dipakai pada percobaan ini adalah `ggml-base` tanpa initial prompt.
- Speaker yang dipakai pada percobaan ini adalah `wibowo` dari coqui_tts.
- Percobaan dilakukan tanpa menggunakan GPU.

## 📊 Hasil Evaluasi Pipeline

### Summary Keseluruhan

| Metrik            | Nilai       |
| ----------------- | ----------- |
| Total File Audio  | 561         |
| Rata-rata WER     | 0.8774      |
| Rata-rata CER     | 0.4667      |
| Rata-rata Latency | 57.01 detik |

### Summary Per Utterance

| Utterance | Naskah                                                                  | WER    | CER    | STT (s) | LLM (s) | TTS (s) | Total (s) |
| --------- | ----------------------------------------------------------------------- | ------ | ------ | ------- | ------- | ------- | --------- |
| audio1    | Aku mau book flight ke Jeddah minggu depan, bisa bantu schedule?        | 1.0826 | 0.5918 | 8.59    | 27.57   | 17.09   | 53.25     |
| audio2    | Aku butuh travel umrah simple tapi include Madinah visit                | 0.9849 | 0.5420 | 7.17    | 30.52   | 17.30   | 54.98     |
| audio3    | Can you help aku arrange transport dari Jeddah ke Madinah tomorrow      | 0.4347 | 0.1964 | 6.50    | 29.03   | 17.23   | 52.76     |
| audio4    | Explain step by step cara apply visa Saudi dengan benar                 | 0.4691 | 0.1889 | 7.00    | 31.00   | 17.17   | 55.17     |
| audio5    | Ya akhi, uridu book flight ila Jeddah al-usbu'al qadim...               | 1.0384 | 0.5175 | 10.21   | 32.13   | 16.87   | 59.43     |
| audio6    | Uridu arrange transport min Jeddah ila Madinah ghadan                   | 0.8125 | 0.2602 | 6.92    | 29.90   | 17.17   | 53.99     |
| audio7    | Book flight ke Jeddah lalu lanjut ke Madinah, schedule terbaik kapan    | 0.6150 | 0.3100 | 26.93   | 31.66   | 18.35   | 76.95     |
| audio8    | Arid schedule trip min jeddah ila makkah bukra sabah                    | 1.0972 | 0.7812 | 6.00    | 28.89   | 19.65   | 54.54     |
| audio9    | Mumkin book transport min makkah ila madinah untuk besok                | 1.1975 | 0.8175 | 5.94    | 30.68   | 18.86   | 55.48     |
| audio10   | Apa perbedaan umrah dan hajj secara detail dalam Islam                  | 1.2778 | 0.8093 | 5.37    | 35.13   | 18.81   | 59.31     |
| audio11   | Kenapa fasting di ramadan itu wajib bagi muslim                         | 1.0750 | 0.6266 | 6.41    | 36.96   | 18.03   | 61.40     |
| audio12   | Bagaimana proses visa Saudi untuk umrah dari Indonesia sekarang         | 1.0688 | 0.6723 | 7.76    | 28.97   | 17.62   | 54.36     |
| audio13   | Jelaskan step by step cara booking flight ke Jeddah secara online       | 0.7438 | 0.5035 | 6.21    | 32.45   | 18.22   | 56.88     |
| audio14   | How to prepare dokumen umrah dari Indonesia dengan benar                | 0.6111 | 0.3850 | 6.64    | 38.57   | 17.37   | 62.58     |
| audio15   | Tolong buat checklist persiapan umrah termasuk barang wajib dibawa      | 1.3426 | 0.6547 | 9.91    | 26.26   | 16.96   | 53.14     |
| audio16   | Guide aku cara pilih hotel di Makkah dekat Haram dengan budget terbatas | 0.9375 | 0.5669 | 5.32    | 33.09   | 20.85   | 59.27     |
| audio17   | Menurut kamu belajar bahasa Arab itu susah gak untuk pemula             | 1.1565 | 0.7653 | 7.35    | 27.15   | 17.28   | 51.78     |
| audio18   | I feel overwhelmed dengan persiapan umrah, ada tips sederhana?          | 1.1358 | 0.6288 | 8.59    | 26.96   | 16.54   | 52.10     |
| audio19   | Ahyanan saya bingung mulai dari mana untuk umrah                        | 1.1250 | 0.5521 | 5.09    | 30.70   | 17.99   | 53.77     |
| audio20   | Translate ke English: aku mau pergi ke Makkah minggu depan              | 0.9000 | 0.4589 | 5.42    | 56.55   | 17.58   | 79.55     |

## 🔊 Contoh Output Audio

| Mode      | Link                                                                                            |
| --------- | ----------------------------------------------------------------------------------------------- |
| Normalize | [Dengarkan](https://drive.google.com/file/d/1Iu6R-zZ_ZSZOCsk6-1xVT6o4G7aC6QOV/view?usp=sharing) |
| Preserve  | [Dengarkan](https://drive.google.com/file/d/1jFWTyK7yWLlyqH1kXzN7Hl-tyZ8rhbCJ/view?usp=sharing) |

## 👨‍💻 Dibuat Untuk

Proyek UAS mata kuliah _Praktikum Pemrosesan Bahasa Alami_ — Semester Genap 2025/2026.
