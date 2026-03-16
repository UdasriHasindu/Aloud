"""
gui/pdf_viewer.py
------------------
A custom Tkinter Canvas widget that handles rendering and displaying PDF pages.
"""

import tkinter as tk
from PIL import ImageTk, Image
from core.pdf_reader import PDFReader

class PDFViewer(tk.Canvas):
    def __init__(self, master, **kwargs):
        super().__init__(master, bg="darkgray", **kwargs)
        self.image = None       # Keep reference to avoid garbage collection
        self.photo = None       # Tkinter PhotoImage reference
        self.bind("<Configure>", self._on_resize)  # Redraw when window resizes
        
        self.current_reader = None
        self.current_page = 0

    def display_page(self, reader: PDFReader, page_index: int):
        """Render and display the given page from the PDF reader."""
        self.current_reader = reader
        self.current_page = page_index
        
        if not reader or page_index < 0 or page_index >= reader.page_count:
            self.delete("all")
            self.image = None
            self.photo = None
            return

        # 1. Ask PyMuPDF to render the page to a PNG byte stream
        png_bytes = reader.get_page_image(page_index)
        
        # 2. Load bytes into Pillow Image
        import io
        img = Image.open(io.BytesIO(png_bytes))
        self.original_image = img
        
        # 3. Draw immediately sized to current canvas dimensions
        self._redraw()

    def _on_resize(self, event):
        """Triggered automatically when the canvas width/height changes."""
        if hasattr(self, 'original_image') and self.original_image:
            self._redraw()

    def _redraw(self):
        """Scale the PIL image to fit the current canvas size and draw it."""
        if not hasattr(self, 'original_image') or not self.original_image:
            return

        # Current canvas dimensions
        cw = self.winfo_width()
        ch = self.winfo_height()
        
        if cw <= 1 or ch <= 1:
            return # Canvas not fully initialized yet

        # Original image dimensions
        img_w, img_h = self.original_image.size

        # Calculate scaling factor to fit *within* the canvas (maintain aspect ratio)
        scale_w = cw / img_w
        scale_h = ch / img_h
        scale = min(scale_w, scale_h) * 0.95  # 95% to leave a small margin

        new_width = max(1, int(img_w * scale))
        new_height = max(1, int(img_h * scale))

        # Scale down 
        # (LANCZOS is high quality downsampling, good for text)
        resized_img = self.original_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # Convert to Tkinter PhotoImage (must keep a reference to self.photo!)
        self.photo = ImageTk.PhotoImage(resized_img)

        # Clear old image and draw new one centered
        self.delete("all")
        self.create_image(cw // 2, ch // 2, anchor=tk.CENTER, image=self.photo)
