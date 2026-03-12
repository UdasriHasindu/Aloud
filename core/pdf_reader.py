"""
core/pdf_reader.py
-------------------
Handles everything related to opening and reading a PDF file.

Key idea
--------
PyMuPDF (imported as `fitz`) can open a PDF and give us:
  1. The raw text embedded in each page  → fast, accurate for digital PDFs
  2. A rendered image of each page       → used by ocr_engine.py for scanned PDFs

Learning note
-------------
We wrap PyMuPDF in our own class so the rest of the app never needs to know
*how* the PDF is read — it just asks for text or images. This is called the
"Facade" design pattern and makes swapping the library easy later.
"""

import fitz  # PyMuPDF
from utils.config import OCR_FALLBACK_THRESHOLD, OCR_DPI


class PDFReader:
    """Opens a PDF and provides page-level text and image access."""

    def __init__(self, filepath: str):
        """
        Open the PDF at *filepath*.

        Args:
            filepath: Absolute or relative path to the .pdf file.

        Raises:
            FileNotFoundError: If the file doesn't exist.
            fitz.FileDataError: If the file is not a valid PDF.
        """
        self.filepath = filepath
        self._doc = fitz.open(filepath)          # opens the PDF in memory
        self.page_count = len(self._doc)         # total number of pages

    # ── Public API ────────────────────────────────────────────────────────────

    def get_page_text(self, page_index: int) -> str:
        """
        Extract the text layer from a single page.

        Args:
            page_index: 0-based page number.

        Returns:
            Extracted text string. Empty string if the page has no text layer.
        """
        page = self._doc[page_index]
        text = page.get_text("text")        # "text" = plain text mode
        return text.strip()

    def get_page_image(self, page_index: int) -> bytes:
        """
        Render a page as a PNG image (used for OCR on scanned pages).

        Args:
            page_index: 0-based page number.

        Returns:
            Raw PNG bytes that Pillow / pytesseract can open directly.
        """
        page = self._doc[page_index]
        # mat = zoom matrix; OCR_DPI / 72 scales the default 72-dpi rendering
        zoom = OCR_DPI / 72
        mat = fitz.Matrix(zoom, zoom)
        pixmap = page.get_pixmap(matrix=mat, colorspace=fitz.csRGB)
        return pixmap.tobytes("png")        # returns raw PNG bytes

    def needs_ocr(self, page_index: int) -> bool:
        """
        Decide whether a page should be OCR'd instead of using the text layer.

        A page "needs OCR" when it has very little embedded text — which
        typically means it is a scanned image or a page full of diagrams.

        Args:
            page_index: 0-based page number.

        Returns:
            True if OCR is recommended for this page.
        """
        text = self.get_page_text(page_index)
        return len(text) < OCR_FALLBACK_THRESHOLD

    def get_all_text(self) -> str:
        """
        Extract text from ALL pages joined with page separators.

        Useful for short documents where you want everything at once.

        Returns:
            Full document text as a single string.
        """
        parts = []
        for i in range(self.page_count):
            parts.append(f"--- Page {i + 1} ---\n{self.get_page_text(i)}")
        return "\n\n".join(parts)

    def close(self):
        """Release the file handle. Always call this when done."""
        self._doc.close()

    # ── Context Manager support  (allows: `with PDFReader(path) as r:`) ──────
    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()
