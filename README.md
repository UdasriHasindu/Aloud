# Aloud 🔊

A Debian/Linux desktop application that reads PDF files aloud using Text-to-Speech.

---

## Features (Planned)
- 📄 Open any PDF (digital or scanned)
- 🔊 Read pages aloud using espeak-ng TTS
- 🖼️ OCR fallback for scanned / image-based PDFs (Tesseract)
- 🎛️ GUI with Play / Pause / Stop / Speed controls
- 📑 Page-by-page navigation

---

## Project Structure

```
Aloud/
├── main.py          # Entry point
├── requirements.txt
├── core/
│   ├── pdf_reader.py    # PDF text extraction (PyMuPDF)
│   ├── ocr_engine.py    # OCR fallback (Tesseract)
│   └── tts_engine.py    # Text-to-Speech (pyttsx3 + espeak-ng)
├── gui/             # Tkinter GUI (Phase 2)
└── utils/
    └── config.py    # App settings
```

---

## Installation

### 1. System Dependencies
```bash
sudo apt install python3 python3-pip espeak-ng tesseract-ocr python3-tk
```

### 2. Python Packages
```bash
pip install -r requirements.txt
```

---

## Phase 1 — CLI Test

```bash
# Read page 1 of any PDF aloud:
python3 main.py /path/to/yourfile.pdf

# Read a specific page:
python3 main.py /path/to/yourfile.pdf 3
```

---

## Tech Stack

| Component | Library |
|-----------|---------|
| PDF parsing | PyMuPDF (`fitz`) |
| OCR | Tesseract + pytesseract |
| TTS | pyttsx3 + espeak-ng |
| GUI (Phase 2) | Tkinter |
| Language | Python 3.10+ |
