"""
utils/config.py
----------------
Central configuration for the Aloud app.
Change values here to tune behaviour without touching any other file.
"""

import os

# ── Project root (absolute path, works regardless of where you run from) ──────
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ── Piper TTS Settings ────────────────────────────────────────────────────────
# Path to the downloaded Piper voice model files
# Voice: en_US-lessac-medium  (female, US English, neural quality)
PIPER_MODEL_PATH   = os.path.join(_PROJECT_ROOT, "models", "en_US-lessac-medium.onnx")
PIPER_MODEL_CONFIG = os.path.join(_PROJECT_ROOT, "models", "en_US-lessac-medium.onnx.json")

# Speed scale: 1.0 = normal speed, 0.75 = slightly slower, 1.5 = faster
# Tip: 0.9 sounds the most natural for document reading
TTS_RATE_SCALE = 0.9

# Volume: 0.0 (silent) → 1.0 (full)
TTS_VOLUME = 1.0

# ── PDF / OCR Settings ────────────────────────────────────────────────────────
# Pages with fewer embedded characters than this are sent to OCR
OCR_FALLBACK_THRESHOLD = 30

# DPI for rendering a page to image for OCR (200–300 is a good range)
OCR_DPI = 200

# ── App Meta ──────────────────────────────────────────────────────────────────
APP_NAME    = "Aloud"
APP_VERSION = "0.1.0"
