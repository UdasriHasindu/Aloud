"""
gui/downloader.py
------------------
A small UI to download the ONNX voice model on the first run.
"""

import os
import urllib.request
import threading
import tkinter as tk
import customtkinter as ctk

from utils.config import (
    PIPER_MODEL_PATH,
    PIPER_MODEL_CONFIG,
    PIPER_MODEL_URL,
    PIPER_CONFIG_URL,
    APP_NAME
)


class ModelDownloader(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title(f"{APP_NAME} - First Run Setup")
        self.geometry("450x200")
        self.resizable(False, False)
        
        # Center the window
        self.update_idletasks()
        w = self.winfo_width()
        h = self.winfo_height()
        ws = self.winfo_screenwidth()
        hs = self.winfo_screenheight()
        x = (ws / 2) - (w / 2)
        y = (hs / 2) - (h / 2)
        self.geometry(f"+{int(x)}+{int(y)}")

        self._build_ui()
        self.success = False

    def _build_ui(self):
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        self.lbl_title = ctk.CTkLabel(
            main_frame, text="Downloading Voice Model",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.lbl_title.pack(anchor="w", pady=(0, 10))

        self.lbl_info = ctk.CTkLabel(
            main_frame, 
            text="Aloud needs to download a high-quality neural voice\nbefore its first use (~60MB). This only happens once.",
            justify="left"
        )
        self.lbl_info.pack(anchor="w", pady=(0, 20))

        self.progress = ctk.CTkProgressBar(main_frame, mode="determinate")
        self.progress.pack(fill="x")
        self.progress.set(0)

        self.lbl_status = ctk.CTkLabel(
            main_frame, text="Starting download...",
            text_color="gray"
        )
        self.lbl_status.pack(anchor="w", pady=(5, 0))

    def start_download(self):
        # Run download in background thread so UI doesn't freeze
        threading.Thread(target=self._download_worker, daemon=True).start()

    def _report_hook(self, count, block_size, total_size):
        if total_size > 0:
            percent = (count * block_size) / total_size
            percent = min(1.0, max(0.0, percent))
            
            # Update UI on main thread
            self.after(0, self._update_progress, percent, total_size)

    def _update_progress(self, percent, total_size):
        self.progress.set(percent)
        mb_total = total_size / (1024 * 1024)
        mb_current = (percent * total_size) / (1024 * 1024)
        self.lbl_status.configure(text=f"Downloading: {mb_current:.1f} MB / {mb_total:.1f} MB")

    def _download_worker(self):
        try:
            os.makedirs(os.path.dirname(PIPER_MODEL_PATH), exist_ok=True)
            
            self.after(0, self.lbl_status.configure, {"text": "Downloading ONNX model..."})
            urllib.request.urlretrieve(PIPER_MODEL_URL, PIPER_MODEL_PATH, reporthook=self._report_hook)
            
            self.after(0, self.progress.set, 0)
            self.after(0, self.lbl_status.configure, {"text": "Downloading config JSON..."})
            urllib.request.urlretrieve(PIPER_CONFIG_URL, PIPER_MODEL_CONFIG)
            
            self.success = True
            self.after(0, self.destroy)
            
        except Exception as e:
            self.after(0, self._show_error, str(e))

    def _show_error(self, err_msg):
        self.lbl_status.configure(text=f"Error: {err_msg}", text_color="#d64949")
        # Provide a close button now
        btn_close = ctk.CTkButton(self, text="Close", command=self.destroy)
        btn_close.pack(pady=10)

def ensure_model_exists() -> bool:
    """
    Checks if model exists. If not, shows the downloader dialog.
    Returns True if models are available, False if the user cancelled/failed.
    """
    if os.path.exists(PIPER_MODEL_PATH) and os.path.exists(PIPER_MODEL_CONFIG):
        return True
        
    # We need to download
    dl = ModelDownloader()
    # Schedule download to start immediately after mainloop begins 
    dl.after(100, dl.start_download)
    dl.mainloop()
    return dl.success
