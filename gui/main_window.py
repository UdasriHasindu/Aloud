"""
gui/main_window.py
-------------------
The main CustomTkinter application window.
"""

import threading
import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk

from core.pdf_reader import PDFReader
from core.ocr_engine import OCREngine
from core.tts_engine import TTSEngine
from gui.pdf_viewer import PDFViewer
from gui.controls import ControlPanel
from utils.config import APP_NAME, APP_VERSION

# Set global appearance mode and theme
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class MainWindow:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title(f"{APP_NAME} v{APP_VERSION}")
        self.root.geometry("1100x800")
        self.root.minsize(900, 600)
        
        # Make the layout expand
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(0, weight=1)
        
        # Keyboard shortcuts
        self.root.bind("<Left>", lambda e: self.on_prev_page())
        self.root.bind("<Right>", lambda e: self.on_next_page())
        self.root.bind("<space>", lambda e: self.on_play_pause_toggle())
        self.root.bind("<Control-o>", lambda e: self.on_open_file())
        self.root.bind("<Control-q>", lambda e: self.on_closing())
        
        # Safe shutdown
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Core Engines
        print("Initializing engines...")
        self.tts = TTSEngine()
        self.tts.on_done = self._on_tts_finished
        
        self.ocr = OCREngine()
        self.pdf_reader = None
        self.current_page = 0
        self.current_pdf_path = ""

        self._build_ui()
        self._update_ui_state()
        print("Ready!")

    def _build_ui(self):
        # ── Left Sidebar (Controls & Info) ──
        # We moved the controls to a sidebar for a more modern app feel
        self.sidebar = ctk.CTkFrame(self.root, width=320, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(2, weight=1) # Spacer to push playback controls down

        self.logo_label = ctk.CTkLabel(
            self.sidebar, text=f"{APP_NAME} Reader", 
            font=ctk.CTkFont(size=24, weight="bold")
        )
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        self.btn_open = ctk.CTkButton(
            self.sidebar, text="📂 Open PDF", 
            command=self.on_open_file, 
            height=40, font=ctk.CTkFont(size=14, weight="bold")
        )
        self.btn_open.grid(row=1, column=0, padx=20, pady=10)

        # ── Control Panel Integration ──
        callbacks = {
            'on_play': self.on_play,
            'on_pause': self.on_pause,
            'on_stop': self.on_stop,
            'on_prev': self.on_prev_page,
            'on_next': self.on_next_page,
            'on_jump': self.on_jump_page,
            'on_speed_change': self.on_speed_change,
            'on_zoom_in': self.on_zoom_in,
            'on_zoom_out': self.on_zoom_out,
            'on_zoom_reset': self.on_zoom_reset,
        }
        
        self.controls = ControlPanel(self.sidebar, callbacks)
        self.controls.grid(row=3, column=0, padx=20, pady=20, sticky="ew")

        # ── Right Main Area (PDF Viewer) ──
        # We use a CTkFrame as a wrapper, containing the old tk.Canvas viewer
        # because CustomTkinter doesn't have a native image canvas.
        self.main_frame = ctk.CTkFrame(self.root, corner_radius=10)
        self.main_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        self.main_frame.pack_propagate(False) # Keep fixed size
        
        # The PDFViewer (tk.Canvas) lives inside the main frame
        self.viewer = PDFViewer(self.main_frame, highlightthickness=0)
        self.viewer.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)


    # ── UI State Management ───────────────────────────────────────────────────
    
    def _update_ui_state(self):
        if not self.pdf_reader:
            self.controls.set_state("no_document")
            self.root.title(f"{APP_NAME} v{APP_VERSION}")
            return

        filename = self.current_pdf_path.split('/')[-1]
        self.root.title(f"{APP_NAME} - {filename}")
        
        if self.tts.is_speaking and not self.tts.is_paused:
            self.controls.set_state("playing")
            self.controls.update_status(f"Reading page {self.current_page + 1}...")
        elif self.tts.is_paused:
            self.controls.set_state("paused")
            self.controls.update_status("Paused.")
        else:
            self.controls.set_state("stopped")
            self.controls.update_status("Ready to read.")

        self.controls.update_page_label(self.current_page + 1, self.pdf_reader.page_count)

    def _render_current_page(self):
        if self.pdf_reader:
            self.viewer.display_page(self.pdf_reader, self.current_page)
            self._update_ui_state()

    # ── File Handling ─────────────────────────────────────────────────────────

    def on_open_file(self):
        filepath = filedialog.askopenfilename(
            title="Open PDF",
            filetypes=[("PDF Files", "*.pdf")]
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

    # ── Playback Callbacks ────────────────────────────────────────────────────

    def on_play(self):
        if not self.pdf_reader: return
        
        self.controls.update_status("Reading layout...")
        self.root.update()

        text = self.pdf_reader.get_page_text(self.current_page, ocr_engine=self.ocr)

        if not text:
            messagebox.showinfo("Empty Page", "No text found on this page.")
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

    def _on_tts_finished(self):
        """Called from the TTS background thread when a page finishes reading naturally."""
        self.root.after(0, self._auto_advance_page)

    def _auto_advance_page(self):
        """Advance to the next page and keep reading, or stop if at the last page."""
        if not self.pdf_reader:
            return
        if self.current_page < self.pdf_reader.page_count - 1:
            self.current_page += 1
            self._render_current_page()
            self.on_play()     # continue reading on the new page
        else:
            self.controls.update_status("Finished reading document.")
            self._update_ui_state()

    # ── Navigation & Settings Callbacks ───────────────────────────────────────

    def on_play_pause_toggle(self):
        """Space bar: if stopped start playing; if playing pause; if paused resume."""
        if not self.pdf_reader:
            return
        if self.tts.is_speaking:
            self.on_pause()
        else:
            self.on_play()

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
            target_index = int(page_num_str) - 1
            target_index = max(0, min(target_index, self.pdf_reader.page_count - 1))
            
            if target_index != self.current_page:
                self.on_stop()
                self.current_page = target_index
                self._render_current_page()
        except ValueError:
            pass

    def on_zoom_in(self):
        self.viewer.zoom_in()

    def on_zoom_out(self):
        self.viewer.zoom_out()

    def on_zoom_reset(self):
        self.viewer.zoom_reset()

    def on_speed_change(self, scale_value: float):
        self.tts.speed = scale_value

    def on_closing(self):
        self.tts.stop()
        if self.pdf_reader:
            self.pdf_reader.close()
        self.root.destroy()

    def run(self):
        self.root.mainloop()
