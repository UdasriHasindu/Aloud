"""
main.py
--------
Phase 1 CLI entry point for Aloud.

Run this to test the core engine without any GUI:
    python3 main.py /path/to/your/file.pdf [page_number]

Examples:
    python3 main.py ~/Desktop/sample.pdf        # reads page 1
    python3 main.py ~/Desktop/sample.pdf 3      # reads page 3

What it does:
    1. Opens the PDF
    2. Extracts text (or uses OCR if the page is scanned)
    3. Prints the text to the terminal
    4. Speaks it aloud using the TTS engine
"""

import sys
from core.pdf_reader import PDFReader
from core.ocr_engine import OCREngine
from core.tts_engine import TTSEngine
from utils.config import APP_NAME, APP_VERSION


def main():
    # ── Argument parsing ──────────────────────────────────────────────────────
    if len(sys.argv) < 2:
        print(f"{APP_NAME} v{APP_VERSION} — PDF Reader")
        print("\nUsage:  python3 main.py <path-to-pdf> [page-number]")
        print("        page-number is 1-based (default: 1)")
        sys.exit(1)

    pdf_path = sys.argv[1]
    # sys.argv[2] is the page number (1-based), default to page 1
    page_num = int(sys.argv[2]) if len(sys.argv) >= 3 else 1
    page_index = page_num - 1      # convert to 0-based index

    # ── Open PDF ──────────────────────────────────────────────────────────────
    print(f"\n📄  Opening: {pdf_path}")
    try:
        reader = PDFReader(pdf_path)
    except FileNotFoundError:
        print(f"❌  File not found: {pdf_path}")
        sys.exit(1)

    print(f"    Pages in document: {reader.page_count}")

    if page_index >= reader.page_count or page_index < 0:
        print(f"❌  Page {page_num} doesn't exist. Document has {reader.page_count} page(s).")
        sys.exit(1)

    # ── Extract text ──────────────────────────────────────────────────────────
    print(f"\n📖  Reading page {page_num}...")

    if reader.needs_ocr(page_index):
        # Scanned / image-based page — use OCR
        print("    (Page has no text layer — using OCR...)")
        ocr = OCREngine()
        png_bytes = reader.get_page_image(page_index)
        text = ocr.extract_text_from_bytes(png_bytes)
    else:
        # Digital text PDF — fast extraction
        text = reader.get_page_text(page_index)

    reader.close()

    if not text:
        print("⚠️   No text could be extracted from this page.")
        sys.exit(0)

    # ── Print to terminal ─────────────────────────────────────────────────────
    print("\n" + "─" * 60)
    print(text)
    print("─" * 60)

    # ── Speak aloud ───────────────────────────────────────────────────────────
    print("\n🔊  Speaking... (press Ctrl+C to stop)\n")

    tts = TTSEngine()
    print(f"    Available voices: {tts.list_voices()}")

    # Block the main thread until speaking is done
    # (In the real GUI app the GUI event loop handles this instead)
    done_event = __import__("threading").Event()
    tts.on_done = done_event.set

    tts.speak(text)
    done_event.wait()   # wait here until TTS thread signals it's finished

    print("\n✅  Done!")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⛔  Interrupted by user.")
        sys.exit(0)
