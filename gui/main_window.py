"""
gui/main_window.py
-------------------
The main Tkinter application window.
Responsible for layout, file dialogs, and coordinating the PDFReader and TTSEngine.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading

from core.pdf_reader import PDFReader
from core.ocr_engine import OCREngine
from core.tts_engine import TTSEngine
from gui.pdf_viewer import PDFViewer
from gui.controls import ControlPanel
from utils.config import APP_NAME, APP_VERSION

class MainWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title(f"{APP_NAME} v{APP_VERSION}")
        self.root.geometry("1000x800")
        self.root.minsize(800, 600)
        
        # Safe shutdown
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Core Engines
        print("Initializing engines...")
        self.tts = TTSEngine()
        self.tts.on_done = self._on_tts_finished # Callback from background thread
        
        self.ocr = OCREngine()
        self.pdf_reader = None
        self.current_page = 0
        self.current_pdf_path = ""

        self._build_ui()
        self._update_ui_state()
        print("Ready!")

    def _build_ui(self):
        # Apply a simple modern theme
        style = ttk.Style()
        style.theme_use('clam')

        # Menu bar
        menubar = tk.Menu(self.root)
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="Open PDF...", command=self.on_open_file)
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=self.on_closing)
        menubar.add_cascade(label="File", menu=filemenu)
        self.root.config(menu=menubar)

        # Main PanedWindow (splittable view)
        paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Left pane: PDF Viewer (takes up most space)
        left_frame = ttk.Frame(paned, borderwidth=1, relief="sunken")
        self.viewer = PDFViewer(left_frame)
        self.viewer.pack(fill=tk.BOTH, expand=True)
        paned.add(left_frame, weight=3) # 3:1 ratio

        # Right pane: Controls
        right_frame = ttk.Frame(paned, width=300)
        
        # Package callbacks for the ControlPanel
        callbacks = {
            'on_play': self.on_play,
            'on_pause': self.on_pause,
            'on_stop': self.on_stop,
            'on_prev': self.on_prev_page,
            'on_next': self.on_next_page,
            'on_jump': self.on_jump_page,
            'on_speed_change': self.on_speed_change,
        }
        
        self.controls = ControlPanel(right_frame, callbacks)
        self.controls.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        paned.add(right_frame, weight=1)

    # ── UI State Management ───────────────────────────────────────────────────
    
    def _update_ui_state(self):
        """Sync the GUI buttons based on what the engine is doing."""
        if not self.pdf_reader:
            self.controls.set_state("no_document")
            self.root.title(f"{APP_NAME} v{APP_VERSION}")
            return

        self.root.title(f"{APP_NAME} - {self.current_pdf_path.split('/')[-1]}")
        
        if self.tts.is_speaking and not self.tts.is_paused:
            self.controls.set_state("playing")
            self.controls.update_status(f"Reading page {self.current_page + 1}...")
        elif self.tts.is_paused:
            self.controls.set_state("paused")
            self.controls.update_status("Paused.")
        else:
            self.controls.set_state("stopped")
            self.controls.update_status("Ready.")

        # Always update page label
        self.controls.update_page_label(self.current_page + 1, self.pdf_reader.page_count)

    def _render_current_page(self):
        """Ask the viewer to draw the current page."""
        if self.pdf_reader:
            self.viewer.display_page(self.pdf_reader, self.current_page)
            self._update_ui_state()

    # ── Menu Actions ──────────────────────────────────────────────────────────

    def on_open_file(self):
        filepath = filedialog.askopenfilename(
            title="Open PDF",
            filetypes=[("PDF Files", "*.pdf")]
        )
        if not filepath:
            return

        # Stop anything playing currently
        self.on_stop()
        
        # Close old PDF
        if self.pdf_reader:
            self.pdf_reader.close()

        try:
            self.pdf_reader = PDFReader(filepath)
            self.current_pdf_path = filepath
            self.current_page = 0
            self._render_current_page()
            self.controls.update_status(f"Loaded {self.pdf_reader.page_count} pages.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open PDF:\n{e}")
            self.pdf_reader = None
            self._update_ui_state()

    # ── Playback Callbacks ────────────────────────────────────────────────────

    def on_play(self):
        """Extract text for the current page and trigger the TTS background thread."""
        if not self.pdf_reader: return
        
        self.controls.update_status("Extracting text...")
        self.root.update() # Force UI refresh

        text = ""
        # 1. Decide if we need full-page OCR (scanned PDF)
        if self.pdf_reader.needs_ocr(self.current_page):
            self.controls.update_status("Running OCR on scanned page...")
            self.root.update()
            png_bytes = self.pdf_reader.get_page_image(self.current_page)
            text = self.ocr.extract_text_from_bytes(png_bytes)
        else:
            # Pass the OCR engine so it can read embedded images inside normal text pages
            text = self.pdf_reader.get_page_text(self.current_page, ocr_engine=self.ocr)

        # 2. Check if page is empty
        if not text:
            messagebox.showinfo("Empty Page", "No text found on this page.")
            self.controls.update_status("Ready.")
            return

        # 3. Start speaking!
        self.tts.speak(text)
        self._update_ui_state()

    def on_pause(self):
        if self.tts.is_paused:
            self.tts.resume()
        else:
            self.tts.pause()
        self._update_ui_state()

    def on_stop(self):
        self.tts.stop()
        self._update_ui_state()

    def _on_tts_finished(self):
        """
        Called BY THE BACKGROUND THREAD when speaking naturally finishes.
        We cannot safely update Tkinter UI directly from a background thread,
        so we use `after(0)` to schedule the update back on the main thread.
        """
        self.root.after(0, self._update_ui_state)

    # ── Navigation & Settings Callbacks ───────────────────────────────────────

    def on_prev_page(self):
        if self.pdf_reader and self.current_page > 0:
            self.on_stop()
            self.current_page -= 1
            self._render_current_page()

    def on_next_page(self):
        if self.pdf_reader and self.current_page < self.pdf_reader.page_count - 1:
            self.on_stop()
            self.current_page += 1
            self._render_current_page()

    def on_jump_page(self, page_num_str: str):
        """Called when user types a page number and hits Enter/Go."""
        if not self.pdf_reader:
            return
            
        try:
            # Convert user's 1-based string to our 0-based index
            target_page_1_based = int(page_num_str)
            target_index = target_page_1_based - 1
            
            # Clamp to valid range
            target_index = max(0, min(target_index, self.pdf_reader.page_count - 1))
            
            if target_index != self.current_page:
                self.on_stop()
                self.current_page = target_index
                self._render_current_page()
        except ValueError:
            pass # Ignore invalid inputs like letters

    def on_speed_change(self, scale_value: float):
        """Slider value changed. Update TTS engine."""
        # scale_value comes in as 0.5 (fastest) to 2.0 (slowest in terms of Piper's length_scale)
        # We just pass it through directly
        self.tts.speed = scale_value

    def on_closing(self):
        """Safe shutdown."""
        self.tts.stop()
        if self.pdf_reader:
            self.pdf_reader.close()
        self.root.destroy()

    def run(self):
        self.root.mainloop()
