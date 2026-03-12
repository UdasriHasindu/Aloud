"""
utils/config.py
----------------
Central configuration for the Aloud app.
All default settings live here. You can change these values to tune
the app's behaviour without touching any other file.
"""

# ── TTS Settings ──────────────────────────────────────────────────────────────
# Words per minute. Human speech is ~130–150 wpm; raise for faster reading.
TTS_RATE = 130

# Volume: 0.0 (silent)  →  1.0 (full)
TTS_VOLUME = 1.0

# Voice index to pick from the voices available on this system.
# 0 = first available voice (usually the default espeak-ng voice).
TTS_VOICE_INDEX = 0

# ── PDF / OCR Settings ────────────────────────────────────────────────────────
# Minimum characters extracted from a page before we consider it "text-based".
# Pages with fewer characters are treated as scanned images and sent to OCR.
OCR_FALLBACK_THRESHOLD = 20

# DPI used when rendering a PDF page to an image for OCR.
# Higher = more accurate OCR but slower. 200–300 is a good range.
OCR_DPI = 200

# ── App Meta ──────────────────────────────────────────────────────────────────
APP_NAME = "Aloud"
APP_VERSION = "0.1.0"
