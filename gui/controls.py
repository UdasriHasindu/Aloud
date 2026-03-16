"""
gui/controls.py
----------------
A Tkinter Frame containing the playback buttons, page navigation, and speed slider.
Delegates event handling back to the main window via callbacks.
"""

import tkinter as tk
from tkinter import ttk

class ControlPanel(ttk.Frame):
    def __init__(self, master, callbacks, **kwargs):
        """
        callbacks is a dict of functions provided by the main window:
            on_play, on_pause, on_stop, on_prev, on_next, on_speed_change
        """
        super().__init__(master, padding="10", **kwargs)
        self.cb = callbacks
        self._build_ui()
        self.set_state("no_document") # Initial state

    def _build_ui(self):
        # ── Navigation Row ──
        nav_frame = ttk.Frame(self)
        nav_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.btn_prev = ttk.Button(nav_frame, text="◀ Prev", command=self.cb.get('on_prev'), width=8)
        self.btn_prev.pack(side=tk.LEFT)
        
        # Center section: "Page [Entry] / Total"
        center_frame = ttk.Frame(nav_frame)
        center_frame.pack(side=tk.LEFT, expand=True)
        
        ttk.Label(center_frame, text="Page ").pack(side=tk.LEFT)
        
        self.ent_page = ttk.Entry(center_frame, width=4, justify="center")
        self.ent_page.pack(side=tk.LEFT)
        self.ent_page.bind("<Return>", lambda e: self.cb.get('on_jump')(self.ent_page.get()))
        
        self.lbl_total = ttk.Label(center_frame, text=" / 0")
        self.lbl_total.pack(side=tk.LEFT)

        self.btn_next = ttk.Button(nav_frame, text="Next ▶", command=self.cb.get('on_next'), width=8)
        self.btn_next.pack(side=tk.RIGHT)

        # ── Separator ──
        ttk.Separator(self, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)

        # ── Playback Controls Row ──
        play_frame = ttk.Frame(self)
        play_frame.pack(fill=tk.X, pady=10)

        # We keep references so we can change text/state later
        self.btn_play = ttk.Button(play_frame, text="▶ Play", command=self.cb.get('on_play'), width=10)
        self.btn_play.pack(side=tk.LEFT, padx=5, expand=True)

        self.btn_pause = ttk.Button(play_frame, text="⏸ Pause", command=self.cb.get('on_pause'), width=10)
        self.btn_pause.pack(side=tk.LEFT, padx=5, expand=True)

        self.btn_stop = ttk.Button(play_frame, text="⏹ Stop", command=self.cb.get('on_stop'), width=10)
        self.btn_stop.pack(side=tk.LEFT, padx=5, expand=True)

        # ── Speed Slider Row ──
        speed_frame = ttk.Frame(self)
        speed_frame.pack(fill=tk.X, pady=20)
        
        ttk.Label(speed_frame, text="Reading Speed (Scale):").pack(side=tk.LEFT)
        
        self.lbl_speed_val = ttk.Label(speed_frame, text="1.0x")
        self.lbl_speed_val.pack(side=tk.RIGHT)

        # Piper speed is inverted: higher scale = slower speech
        # Let's make the slider intuitive for the user: 
        # Left (0.5) = slower, Right (2.0) = faster
        self.scale_speed = ttk.Scale(
            speed_frame, 
            from_=0.5, to_=2.0, 
            orient=tk.HORIZONTAL, 
            command=self._on_slider_move
        )
        self.scale_speed.set(1.0)  # Default
        self.scale_speed.pack(fill=tk.X, pady=5)
        
        self.scale_speed.bind("<ButtonRelease-1>", lambda e: self.cb.get('on_speed_change')(self._get_intuitive_speed()))

        # ── Status Row ──
        self.lbl_status = ttk.Label(self, text="Ready.", foreground="gray")
        self.lbl_status.pack(side=tk.BOTTOM, fill=tk.X, pady=(20, 0))

    def _on_slider_move(self, val):
        """Update the label text instantly while dragging."""
        speed = float(val)
        self.lbl_speed_val.config(text=f"{speed:.1f}x")

    def _get_intuitive_speed(self) -> float:
        """Return the slider value. The TTS engine will invert this if needed."""
        return float(self.scale_speed.get())

    def update_page_label(self, current_1_based, total):
        self.ent_page.delete(0, tk.END)
        self.ent_page.insert(0, str(current_1_based))
        self.lbl_total.config(text=f" / {total}")

    def update_status(self, text):
        self.lbl_status.config(text=text)

    def set_state(self, state: str):
        """
        Manages enabling/disabling buttons based on current app state.
        States: 'no_document', 'stopped', 'playing', 'paused'
        """
        if state == "no_document":
            self.btn_prev.state(['disabled'])
            self.btn_next.state(['disabled'])
            self.btn_play.state(['disabled'])
            self.btn_pause.state(['disabled'])
            self.btn_stop.state(['disabled'])
            self.scale_speed.state(['disabled'])
            
        elif state == "stopped":
            self.btn_prev.state(['!disabled'])
            self.btn_next.state(['!disabled'])
            self.btn_play.state(['!disabled'])
            self.btn_pause.state(['disabled'])
            self.btn_stop.state(['disabled'])
            self.scale_speed.state(['!disabled'])
            self.btn_play.config(text="▶ Play")
            
        elif state == "playing":
            # Can't change pages or play again while already playing
            self.btn_prev.state(['disabled'])
            self.btn_next.state(['disabled'])
            self.btn_play.state(['disabled'])
            self.btn_pause.state(['!disabled'])
            self.btn_stop.state(['!disabled'])
            
        elif state == "paused":
            self.btn_play.state(['disabled'])
            self.btn_pause.state(['!disabled'])
            self.btn_pause.config(text="▶ Resume") # Turn pause button into resume
            self.btn_stop.state(['!disabled'])

        if state != "paused":
             self.btn_pause.config(text="⏸ Pause")
