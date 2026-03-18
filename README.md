# Aloud 🔊

> A modern Linux desktop application that reads PDF files aloud using neural Text-to-Speech synthesis with beautiful, intuitive controls.

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](#license)
[![Version](https://img.shields.io/badge/Version-0.1.0-orange.svg)](#)

## 🎯 Overview

**Aloud** is a feature-rich PDF reader for Debian/Ubuntu Linux that brings your documents to life through high-quality, natural-sounding speech synthesis. Whether you're reading research papers, e-books, or scanned documents, Aloud makes it easy to listen while you work, drive, or relax.

Perfect for:

- 📚 Studying and learning on the go
- ♿ Accessibility needs
- 📖 Enjoying e-books and documents hands-free
- 📄 Digitizing and reading scanned documents

## ✨ Features

### Core Capabilities

- **🔊 Neural Text-to-Speech** — Piper TTS with ONNX models for natural, human-like speech
- **📄 Universal PDF Support** — Read any PDF, whether digital or scanned
- **🖼️ Smart OCR Fallback** — Automatic Tesseract OCR for image-based PDFs
- **🎛️ Full Playback Control** — Play, pause, stop with intuitive buttons
- **⚡ Variable Speed Reading** — Adjust reading speed from 0.5x to 2.0x (normal: 0.9x)
- **📑 Page Navigation** — Jump to any page or use prev/next controls
- **🔍 Zoom Controls** — Zoom in/out PDF viewer for better readability
- **🌙 Modern Dark UI** — Beautiful CustomTkinter interface with keyboard shortcuts
- **⌨️ Keyboard Shortcuts** — Left/Right arrow keys for page navigation

### Technical Highlights

- **100% Offline** — No cloud dependencies, all processing local
- **Privacy-First** — No data sent to external services
- **Efficient** — Minimal resource usage with streaming audio
- **Cross-Page Reading** — Seamlessly read across multiple pages
- **Live Status Updates** — See current page and reading status in real-time

## 📋 Requirements

### System Dependencies

**Debian/Ubuntu:**

```bash
sudo apt-get install \
  python3 \
  python3-tk \
  python3-pip \
  tesseract-ocr \
  espeak-ng
```

**Optional:** For additional OCR languages:

```bash
sudo apt-get install tesseract-ocr-[language-code]
# Examples: tesseract-ocr-fra (French), tesseract-ocr-deu (German)
```

### Python Version

- **Requires:** Python 3.10 or higher
- **Recommended:** Python 3.11+

## 🚀 Installation

### Option 1: From Debian Package (Easiest)

```bash
sudo dpkg -i aloud_0.1.0-1_all.deb
sudo apt-get install -f  # Install missing dependencies if needed
aloud
```

### Option 2: From Source

**1. Clone the repository:**

```bash
git clone https://github.com/yourusername/aloud.git
cd aloud
```

**2. Create and activate a virtual environment:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

**3. Install Python dependencies:**

```bash
pip install -r requirements.txt
```

**4. Run the application:**

```bash
python3 main.py
```

## 💻 Usage

### Starting Aloud

```bash
# If installed via package
aloud

# If running from source
python3 main.py
```

### Basic Workflow

1. **Open a PDF** — Click the folder icon or drag & drop a PDF file
2. **Play** — Click the ▶ Play button to start reading
3. **Control** — Use Pause (⏸) and Stop (⏹) buttons as needed
4. **Navigate** — Use ◀ Previous and Next ▶ buttons to jump between pages
5. **Adjust Speed** — Drag the speed slider for faster or slower reading
6. **Zoom** — Use zoom buttons to adjust PDF display size

### Keyboard Shortcuts

| Key           | Action        |
| ------------- | ------------- |
| `Left Arrow`  | Previous page |
| `Right Arrow` | Next page     |
| `Space`       | Play/Pause    |
| `Ctrl+O`      | Open PDF      |
| `Ctrl+Q`      | Quit          |

## 🏗️ Project Architecture

### Directory Structure

```
aloud/
├── main.py                 # Application entry point
├── requirements.txt        # Python dependencies
├── setup.py               # Package configuration
├── aloud_app_theme.png    # Application icon
├── README.md              # This file
│
├── core/                  # Core processing engines
│   ├── __init__.py
│   ├── pdf_reader.py      # PDF extraction (PyMuPDF)
│   ├── ocr_engine.py      # OCR support (Tesseract)
│   └── tts_engine.py      # Text-to-Speech (Piper)
│
├── gui/                   # User interface
│   ├── __init__.py
│   ├── main_window.py     # Main application window
│   ├── controls.py        # Playback controls panel
│   └── pdf_viewer.py      # PDF display component
│
├── utils/                 # Utilities
│   ├── __init__.py
│   └── config.py          # Configuration & settings
│
├── models/                # TTS Voice models
│   ├── en_US-lessac-medium.onnx        # Neural voice model
│   └── en_US-lessac-medium.onnx.json   # Model configuration
│
├── sample/                # Sample PDFs for testing
│   ├── sample.pdf
│   ├── workout.pdf
│   └── Lecture 1 - Hashing.pdf
│
└── debian/                # Debian packaging
    ├── control
    ├── rules
    ├── changelog
    ├── copyright
    ├── aloud.desktop
    └── aloud.install
```

### Component Breakdown

**`core/pdf_reader.py` — PDF Processing**

- Extracts text from digital PDFs using PyMuPDF
- Renders pages to images for OCR processing
- Maintains reading order (top-to-bottom)
- Handles both text and embedded images

**`core/ocr_engine.py` — Optical Character Recognition**

- Tesseract-based text extraction
- Handles scanned PDFs and image-based documents
- Supports multiple languages
- Provides fallback for text-poor pages

**`core/tts_engine.py` — Text-to-Speech Engine**

- Piper TTS neural synthesis for natural speech
- Multi-threaded async playback
- Play/Pause/Stop controls
- Configurable speed (0.5x - 2.0x)
- Real-time audio streaming

**`gui/main_window.py` — Main Application**

- CustomTkinter dark-themed interface
- Manages core engine initialization
- Handles file opening and page navigation
- Coordinates UI updates

**`gui/controls.py` — Control Panel**

- Playback buttons (Play, Pause, Stop)
- Page navigation and jump controls
- Speed slider with real-time feedback
- Zoom controls for PDF viewer
- Dynamic button enable/disable logic

**`gui/pdf_viewer.py` — PDF Display**

- Tkinter Canvas-based renderer
- Image scaling and zoom support
- Responsive layout management

**`utils/config.py` — Configuration**

- Centralized settings management
- TTS parameters (speed, volume, model path)
- OCR thresholds
- Application metadata

## ⚙️ Configuration

Edit `utils/config.py` to customize:

```python
# TTS Settings
TTS_RATE_SCALE = 0.9        # Default reading speed (0.5 - 2.0)
TTS_VOLUME = 1.0             # Volume level (0.0 - 1.0)

# PDF/OCR Settings
OCR_FALLBACK_THRESHOLD = 30  # Min chars to trigger OCR
OCR_DPI = 200                # PDF rendering quality (200-300)

# Application
APP_NAME = "Aloud"
APP_VERSION = "0.1.0"
```

## 📦 Dependencies

### Core Libraries

| Package         | Version | Purpose                     |
| --------------- | ------- | --------------------------- |
| `PyMuPDF`       | ≥1.23.0 | PDF text & image extraction |
| `pytesseract`   | ≥0.3.10 | OCR engine interface        |
| `piper-tts`     | ≥1.2.0  | Neural text-to-speech       |
| `sounddevice`   | ≥0.4.6  | Audio output                |
| `customtkinter` | ≥5.2.0  | Modern UI framework         |
| `Pillow`        | ≥10.0.0 | Image processing            |

See `requirements.txt` for complete dependency list with pinned versions.

## 🎮 Development

### Setting Up Dev Environment

```bash
# Clone and setup
git clone https://github.com/yourusername/aloud.git
cd aloud
python3 -m venv .venv
source .venv/bin/activate

# Install development dependencies
pip install -r requirements.txt
pip install pytest pytest-cov flake8 black

# Run tests
pytest tests/

# Format code
black core/ gui/ utils/ main.py

# Lint
flake8 core/ gui/ utils/ main.py
```

### Building the Debian Package

```bash
# Install build tools
sudo apt-get install build-essential debhelper python3-all dh-python

# Build package
dpkg-buildpackage -us -uc -b

# Output: ../aloud_0.1.0-1_all.deb
```

## 🐛 Troubleshooting

### "ModuleNotFoundError: No module named 'customtkinter'"

```bash
pip install --upgrade customtkinter
```

### OCR not working

Ensure Tesseract is installed:

```bash
sudo apt-get install tesseract-ocr
# Verify installation
tesseract --version
```

### Audio not playing

Check sound device configuration:

```bash
python3 -c "import sounddevice; print(sounddevice.default_device)"
```

### Slow performance on large PDFs

- Reduce `OCR_DPI` in config (e.g., 150 instead of 200)
- Close other applications consuming system resources
- Check available RAM with `free -h`

## 📝 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

```
MIT License

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
```

## 🤝 Contributing

We welcome contributions! To contribute:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** changes (`git commit -m 'Add amazing feature'`)
4. **Push** to branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

### Development Guidelines

- Follow PEP 8 style guide
- Write descriptive commit messages
- Add docstrings to all functions and classes
- Test thoroughly before submitting PRs
- Update documentation for new features



**Made with ❤️ for Linux users who love accessibility and efficiency.**
