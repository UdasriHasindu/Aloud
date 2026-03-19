"""
gui/main_window.py
-------------------
Main application window for Aloud PDF Reader.

Layout
------
  ┌──────────────────────────────────────────────────────┐
  │  Toolbar  (ControlPanel — horizontal, top)           │
  │  Speed + Status bar                                  │
  ├──────────────────────────────────────────────────────┤
  │                                                      │
  │  PDF Canvas  (PDFViewer — fills remaining space)     │
  │                                                      │
  └──────────────────────────────────────────────────────┘
"""

import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk

from core.pdf_reader import PDFReader
from core.ocr_engine import OCREngine
from core.tts_engine import TTSEngine
from gui.pdf_viewer import PDFViewer
from gui.controls import ControlPanel
from utils.config import APP_NAME, APP_VERSION

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class MainWindow:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title(f"{APP_NAME} {APP_VERSION}")
        self.root.geometry("1200x820")
        self.root.minsize(900, 600)

        # Root grid: row 0 = toolbar, row 1 = canvas
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        # ── Keyboard shortcuts ──────────────────────────────────────────────
        self.root.bind("<Left>",      lambda e: self.on_prev_page())
        self.root.bind("<Right>",     lambda e: self.on_next_page())
        self.root.bind("<space>",     lambda e: self.on_play_pause_toggle())
        self.root.bind("<Escape>",    lambda e: self.on_stop())
        self.root.bind("<Control-o>", lambda e: self.on_open_file())
        self.root.bind("<Control-q>", lambda e: self.on_closing())
        
        self.root.bind("<Control-plus>",  lambda e: self.on_zoom_in())
        self.root.bind("<Control-equal>", lambda e: self.on_zoom_in())
        self.root.bind("<Control-minus>", lambda e: self.on_zoom_out())

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        # ── Engines ─────────────────────────────────────────────────────────
        print("Initializing engines…")
        self.tts = TTSEngine()
        self.tts.on_done = self._on_tts_finished
        self.ocr = OCREngine()

        self.pdf_reader: PDFReader | None = None
        self.current_page = 0
        self.current_pdf_path = ""

        self._build_ui()
        self._update_ui_state()
        print("Ready.")

    # ── UI construction ────────────────────────────────────────────────────

    def _build_ui(self):
        # Pass the open-file callback into ControlPanel via the callbacks dict
        callbacks = {
            "on_open":         self.on_open_file,
            "on_play":         self.on_play,
            "on_pause":        self.on_pause,
            "on_stop":         self.on_stop,
            "on_prev":         self.on_prev_page,
            "on_next":         self.on_next_page,
            "on_jump":         self.on_jump_page,
            "on_speed_change": self.on_speed_change,
            "on_zoom_in":      self.on_zoom_in,
            "on_zoom_out":     self.on_zoom_out,
            "on_zoom_reset":   self.on_zoom_reset,
        }

        # Toolbar row (row 0)
        self.controls = ControlPanel(self.root, callbacks)
        self.controls.grid(row=0, column=0, sticky="ew")

        # PDF canvas row (row 1) — fills all remaining vertical space
        viewer_frame = ctk.CTkFrame(self.root, corner_radius=0,
                                    fg_color=("#2b2b2b", "#2b2b2b"))
        viewer_frame.grid(row=1, column=0, sticky="nsew")
        viewer_frame.grid_rowconfigure(0, weight=1)
        viewer_frame.grid_columnconfigure(0, weight=1)

        self.viewer = PDFViewer(viewer_frame, highlightthickness=0)
        self.viewer.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)

    # ── UI state ───────────────────────────────────────────────────────────

    def _update_ui_state(self):
        if not self.pdf_reader:
            self.controls.set_state("no_document")
            self.root.title(f"{APP_NAME} {APP_VERSION}")
            self.controls.update_status("No document open.")
            return

        filename = self.current_pdf_path.rsplit("/", 1)[-1]
        self.root.title(f"{filename}  —  {APP_NAME}")

        if self.tts.is_speaking and not self.tts.is_paused:
            self.controls.set_state("playing")
            self.controls.update_status(
                f"Reading page {self.current_page + 1} of "
                f"{self.pdf_reader.page_count}…"
            )
        elif self.tts.is_paused:
            self.controls.set_state("paused")
            self.controls.update_status("Paused.")
        else:
            self.controls.set_state("stopped")
            self.controls.update_status("Ready.")

        self.controls.update_page_label(
            self.current_page + 1, self.pdf_reader.page_count
        )

    def _render_current_page(self):
        if self.pdf_reader:
            self.viewer.display_page(self.pdf_reader, self.current_page)
            self._update_ui_state()

    # ── File handling ──────────────────────────────────────────────────────

    def on_open_file(self):
        filepath = filedialog.askopenfilename(
            title="Open PDF",
            filetypes=[("PDF Files", "*.pdf")],
        )
        if not filepath:
            return

        self.on_stop()
        if self.pdf_reader:
            self.pdf_reader.close()

        try:
            self.pdf_reader = PDFReader(filepath)
            self.current_pdf_path = filepath
            self.current_page = 0
            self._render_current_page()
            self.controls.update_status("Document loaded.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open PDF:\n{e}")
            self.pdf_reader = None
            self._update_ui_state()

    # ── Playback ───────────────────────────────────────────────────────────

    def on_play(self):
        if not self.pdf_reader:
            return

        self.controls.update_status("Preparing…")
        self.root.update()

        text = self.pdf_reader.get_page_text(self.current_page, ocr_engine=self.ocr)
        if not text.strip():
            messagebox.showinfo(
                "Empty Page",
                f"No readable text found on page {self.current_page + 1}.",
            )
            self.controls.update_status("Ready.")
            return

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

    def on_play_pause_toggle(self):
        """Space bar handler: play if idle, pause/resume if active."""
        if not self.pdf_reader:
            return
        if self.tts.is_speaking:
            self.on_pause()
        else:
            self.on_play()

    def _on_tts_finished(self):
        """Called from TTS thread when a page finishes naturally."""
        self.root.after(0, self._auto_advance_page)

    def _auto_advance_page(self):
        """Advance to next page and keep reading, or finish gracefully."""
        if not self.pdf_reader:
            return
        if self.current_page < self.pdf_reader.page_count - 1:
            self.current_page += 1
            self._render_current_page()
            self.on_play()
        else:
            self.controls.update_status("End of document.")
            self._update_ui_state()

    # ── Navigation ─────────────────────────────────────────────────────────

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
        if not self.pdf_reader:
            return
        try:
            target = int(page_num_str) - 1
            target = max(0, min(target, self.pdf_reader.page_count - 1))
            if target != self.current_page:
                self.on_stop()
                self.current_page = target
                self._render_current_page()
        except ValueError:
            pass

    # ── Zoom ───────────────────────────────────────────────────────────────

    def on_zoom_in(self):
        self.viewer.zoom_in()
        self.controls.update_zoom_label(self.viewer.zoom_factor)

    def on_zoom_out(self):
        self.viewer.zoom_out()
        self.controls.update_zoom_label(self.viewer.zoom_factor)

    def on_zoom_reset(self):
        self.viewer.zoom_reset()
        self.controls.update_zoom_label(self.viewer.zoom_factor)

    # ── Settings ───────────────────────────────────────────────────────────

    def on_speed_change(self, scale_value: float):
        self.tts.speed = scale_value

    # ── Lifecycle ──────────────────────────────────────────────────────────

    def on_closing(self):
        self.tts.stop()
        if self.pdf_reader:
            self.pdf_reader.close()
        self.root.destroy()

    def run(self):
        self.root.mainloop()
