"""
core/ocr_engine.py
-------------------
OCR (Optical Character Recognition) fallback for scanned PDF pages.

How it works
------------
When a PDF page has no embedded text (it is just an image), we:
  1. Get the raw PNG bytes of the page from PDFReader
  2. Open them with Pillow into an in-memory Image object
  3. Hand that image to Tesseract via pytesseract
  4. Get back a plain-text string

Learning note
-------------
Tesseract is a C++ program. `pytesseract` is just a thin Python wrapper
that writes a temp file and calls the `tesseract` command-line binary.
Make sure `tesseract` is installed: `sudo apt install tesseract-ocr`
"""

import io
from PIL import Image          # Pillow — image loading/manipulation
import pytesseract             # Python wrapper around the Tesseract binary


class OCREngine:
    """Extracts text from page images using Tesseract OCR."""

    def __init__(self, language: str = "eng"):
        """
        Args:
            language: Tesseract language code.
                      'eng' = English (default).
                      You can install more language packs with:
                      `sudo apt install tesseract-ocr-<lang>`
                      e.g. tesseract-ocr-fra for French.
        """
        self.language = language

    # ── Public API ────────────────────────────────────────────────────────────

    def extract_text_from_bytes(self, png_bytes: bytes) -> str:
        """
        Run OCR on raw PNG bytes (as returned by PDFReader.get_page_image).

        Args:
            png_bytes: A page rendered to PNG bytes.

        Returns:
            Extracted text string. Empty string if nothing was recognised.
        """
        # Wrap the raw bytes in a file-like object so Pillow can read it
        image = Image.open(io.BytesIO(png_bytes))
        # Ask Tesseract to read the image
        text = pytesseract.image_to_string(image, lang=self.language)
        return text.strip()

    def extract_text_from_file(self, image_path: str) -> str:
        """
        Run OCR on an image file saved to disk.

        Args:
            image_path: Path to a PNG/JPG image file.

        Returns:
            Extracted text string.
        """
        image = Image.open(image_path)
        text = pytesseract.image_to_string(image, lang=self.language)
        return text.strip()
