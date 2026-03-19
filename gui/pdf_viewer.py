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
        super().__init__(master, bg="#2b2b2b", **kwargs)
        self.image = None       # Keep reference to avoid garbage collection
        self.photo = None       # Tkinter PhotoImage reference
        self.bind("<Configure>", self._on_resize)  # Redraw when window resizes
        
        # Panning bindings
        self.bind("<ButtonPress-1>", self._on_drag_start)
        self.bind("<B1-Motion>", self._on_drag_motion)
        self.bind("<ButtonRelease-1>", self._on_drag_stop)
        
        self.zoom_factor = 1.0
        
        self.current_reader = None
        self.current_page = 0

    def _on_drag_start(self, event):
        self.config(cursor="fleur")
        self.scan_mark(event.x, event.y)

    def _on_drag_motion(self, event):
        self.scan_dragto(event.x, event.y, gain=1)

    def _on_drag_stop(self, event):
        self.config(cursor="")

    def zoom_in(self):
        self.zoom_factor = min(5.0, self.zoom_factor + 0.2)
        self._redraw()

    def zoom_out(self):
        self.zoom_factor = max(0.2, self.zoom_factor - 0.2)
        self._redraw()
        
    def zoom_reset(self):
        self.zoom_factor = 1.0
        self._redraw()

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

        # Calculate base scaling factor to fit within the canvas identically
        scale_w = cw / img_w
        scale_h = ch / img_h
        base_scale = min(scale_w, scale_h) * 0.95  # 95% to leave a small margin
        
        # Apply the explicit user zoom on top of the auto-fit scale
        final_scale = base_scale * self.zoom_factor

        new_width = max(1, int(img_w * final_scale))
        new_height = max(1, int(img_h * final_scale))

        # Scale down / up
        resized_img = self.original_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # Convert to Tkinter PhotoImage
        self.photo = ImageTk.PhotoImage(resized_img)

        self.delete("all")
        
        # If the image is smaller than the canvas, center it perfectly.
        # If it's larger, anchor it to the center of its own scroll region to allow panning.
        cx = max(cw, new_width) // 2
        cy = max(ch, new_height) // 2
        
        self.create_image(cx, cy, anchor=tk.CENTER, image=self.photo)
        self.configure(scrollregion=(0, 0, max(cw, new_width), max(ch, new_height)))
