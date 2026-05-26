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
./models/download-ggml-model.sh <nama-model>
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
│       └── whisper.cpp/                # Hasil clone whisper.cpp
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
- Model whisper yang dipakai pada percobaan ini adalah `ggml-base` **dengan** initial prompt dan flag `-id`.
- Speaker yang dipakai pada percobaan ini adalah `wibowo` dari coqui TTS.
- Percobaan dilakukan tanpa menggunakan GPU.

## 📊 Hasil Evaluasi Pipeline

### Summary Keseluruhan

| Metrik            | Nilai       |
| ----------------- | ----------- |
| Total File Audio  | 561         |
| Rata-rata WER     | 0.2604      |
| Rata-rata CER     | 0.0903      |
| Rata-rata Latency | 75.72 detik |

### Summary Per Utterance

| Utterance | Naskah                                                                  | WER    | CER    | STT (s) | LLM (s)  | TTS (s) | Total (s) |
| --------- | ----------------------------------------------------------------------- | ------ | ------ | ------- | -------- | ------- | --------- |
| audio1    | Aku mau book flight ke Jeddah minggu depan, bisa bantu schedule?        | 0.0545 | 0.0185 | 1.6473  | 45.2836  | 17.6740 | 64.6052   |
| audio2    | Aku butuh travel umrah simple tapi include Madinah visit                | 0.2081 | 0.0841 | 1.6005  | 60.9860  | 17.1656 | 79.7525   |
| audio3    | Can you help aku arrange transport dari Jeddah ke Madinah tomorrow      | 0.0711 | 0.0355 | 1.6242  | 45.5986  | 17.4556 | 64.6793   |
| audio4    | Explain step by step cara apply visa Saudi dengan benar                 | 0.2018 | 0.0575 | 1.5842  | 44.9230  | 18.4025 | 64.9096   |
| audio5    | Ya akhi, uridu book flight ila Jeddah al-usbu'al qadim...               | 0.6344 | 0.2064 | 2.0983  | 69.7495  | 17.6762 | 89.5240   |
| audio6    | Uridu arrange transport min Jeddah ila Madinah ghadan                   | 0.6273 | 0.1633 | 1.6990  | 51.8584  | 17.0964 | 70.6546   |
| audio7    | Book flight ke Jeddah lalu lanjut ke Madinah, schedule terbaik kapan    | 0.0331 | 0.0158 | 1.6792  | 140.2009 | 17.4991 | 159.3792  |
| audio8    | Arid schedule trip min jeddah ila makkah bukra sabah                    | 0.8519 | 0.6122 | 1.8425  | 47.0408  | 19.3425 | 68.2283   |
| audio9    | Mumkin book transport min makkah ila madinah untuk besok                | 0.6825 | 0.4974 | 1.6621  | 43.1271  | 20.2214 | 65.0114   |
| audio10   | Apa perbedaan umrah dan hajj secara detail dalam Islam                  | 0.3450 | 0.2193 | 1.7637  | 49.2947  | 19.0045 | 70.0637   |
| audio11   | Kenapa fasting di ramadan itu wajib bagi muslim                         | 0.1812 | 0.0394 | 1.7748  | 37.2987  | 17.8612 | 56.9365   |
| audio12   | Bagaimana proses visa Saudi untuk umrah dari Indonesia sekarang         | 0.1161 | 0.0274 | 1.5173  | 60.8382  | 17.1330 | 79.4875   |
| audio13   | Jelaskan step by step cara booking flight ke Jeddah secara online       | 0.1186 | 0.0214 | 1.6580  | 41.9057  | 17.9996 | 61.5637   |
| audio14   | How to prepare dokumen umrah dari Indonesia dengan benar                | 0.1600 | 0.0550 | 1.5012  | 56.3172  | 17.4524 | 75.2694   |
| audio15   | Tolong buat checklist persiapan umrah termasuk barang wajib dibawa      | 0.2824 | 0.0423 | 1.6583  | 40.9208  | 17.8940 | 60.4731   |
| audio16   | Guide aku cara pilih hotel di Makkah dekat Haram dengan budget terbatas | 0.2188 | 0.0880 | 1.4312  | 49.1912  | 17.8925 | 68.5169   |
| audio17   | Menurut kamu belajar bahasa Arab itu susah gak untuk pemula             | 0.1750 | 0.0487 | 1.5450  | 46.3165  | 17.4854 | 65.3463   |
| audio18   | I feel overwhelmed dengan persiapan umrah, ada tips sederhana?          | 0.1481 | 0.0574 | 1.7328  | 45.5856  | 16.9300 | 64.2500   |
| audio19   | Ahyanan saya bingung mulai dari mana untuk umrah                        | 0.2321 | 0.0357 | 1.3414  | 52.2814  | 20.6200 | 74.2421   |
| audio20   | Translate ke English: aku mau pergi ke Makkah minggu depan              | 0.2750 | 0.2061 | 1.5237  | 54.1725  | 18.2487 | 73.9463   |

## 🔊 Contoh Output Audio

| Mode      | Link                                                                                            |
| --------- | ----------------------------------------------------------------------------------------------- |
| Normalize | [Dengarkan](https://drive.google.com/file/d/1AQC9e2swmO-nz69rr6Q1Xlwf2PbUg2Mo/view?usp=sharing) |
| Preserve  | [Dengarkan](https://drive.google.com/file/d/1xs7oR8Kdlvb64cAZouN5FOLCzj5wvzJi/view?usp=sharing) |

## 👨‍💻 Dibuat Untuk

Proyek UAS mata kuliah _Praktikum Pemrosesan Bahasa Alami_ — Semester Genap 2025/2026.
