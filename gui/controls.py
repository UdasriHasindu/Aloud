"""
gui/controls.py
----------------
A CustomTkinter Frame containing the playback buttons, page navigation, 
and speed slider. Delegates event handling back to the main window via callbacks.
"""

import customtkinter as ctk

class ControlPanel(ctk.CTkFrame):
    def __init__(self, master, callbacks, **kwargs):
        """
        callbacks is a dict of functions provided by the main window:
            on_play, on_pause, on_stop, on_prev, on_next, on_jump, on_speed_change
        """
        # fg_color="transparent" lets it blend into the sidebar
        super().__init__(master, fg_color="transparent", **kwargs)
        self.cb = callbacks
        self._build_ui()
        self.set_state("no_document")

    def _build_ui(self):
        # ── Navigation Row ──
        nav_frame = ctk.CTkFrame(self, fg_color="transparent")
        nav_frame.pack(fill="x", pady=(0, 20))
        
        self.btn_prev = ctk.CTkButton(
            nav_frame, text="◀", width=40, font=ctk.CTkFont(weight="bold"),
            command=self.cb.get('on_prev')
        )
        self.btn_prev.pack(side="left")
        
        # Center section: "Page [Entry] / Total"
        center_frame = ctk.CTkFrame(nav_frame, fg_color="transparent")
        center_frame.pack(side="left", expand=True)
        
        ctk.CTkLabel(center_frame, text="Page ").pack(side="left")
        
        self.ent_page = ctk.CTkEntry(center_frame, width=40, justify="center")
        self.ent_page.pack(side="left")
        self.ent_page.bind("<Return>", lambda e: self.cb.get('on_jump')(self.ent_page.get()))
        
        self.lbl_total = ctk.CTkLabel(center_frame, text=" / 0")
        self.lbl_total.pack(side="left")

        self.btn_next = ctk.CTkButton(
            nav_frame, text="▶", width=40, font=ctk.CTkFont(weight="bold"),
            command=self.cb.get('on_next')
        )
        self.btn_next.pack(side="right")

        # ── Zoom Row ──
        zoom_frame = ctk.CTkFrame(self, fg_color="transparent")
        zoom_frame.pack(fill="x", pady=(0, 15))
        
        ctk.CTkLabel(zoom_frame, text="Zoom:", font=ctk.CTkFont(weight="bold")).pack(side="left", padx=(0, 10))
        
        self.btn_zoom_out = ctk.CTkButton(zoom_frame, text="-", width=35, command=self.cb.get('on_zoom_out'))
        self.btn_zoom_out.pack(side="left", padx=2)
        
        self.btn_zoom_reset = ctk.CTkButton(zoom_frame, text="100%", width=45, command=self.cb.get('on_zoom_reset'), fg_color="transparent", border_width=1)
        self.btn_zoom_reset.pack(side="left", padx=2)

        self.btn_zoom_in = ctk.CTkButton(zoom_frame, text="+", width=35, command=self.cb.get('on_zoom_in'))
        self.btn_zoom_in.pack(side="left", padx=2)

        # ── Playback Controls Row ──
        play_frame = ctk.CTkFrame(self, fg_color="transparent")
        play_frame.pack(fill="x", pady=10)

        # Primary play button gets a different color to stand out
        self.btn_play = ctk.CTkButton(
            play_frame, text="▶ Play", 
            command=self.cb.get('on_play'), 
            fg_color="#1f6aa5", hover_color="#144870"
        )
        self.btn_play.pack(side="top", fill="x", pady=5)

        sub_play_frame = ctk.CTkFrame(play_frame, fg_color="transparent")
        sub_play_frame.pack(fill="x")

        self.btn_pause = ctk.CTkButton(
            sub_play_frame, text="⏸ Pause", 
            command=self.cb.get('on_pause'), 
            fg_color="#4a4a4a", hover_color="#333333"
        )
        self.btn_pause.pack(side="left", padx=(0, 5), expand=True, fill="x")

        self.btn_stop = ctk.CTkButton(
            sub_play_frame, text="⏹ Stop", 
            command=self.cb.get('on_stop'), 
            fg_color="#8b0000", hover_color="#5c0000"
        )
        self.btn_stop.pack(side="left", padx=(5, 0), expand=True, fill="x")

        # ── Speed Slider Row ──
        speed_frame = ctk.CTkFrame(self, fg_color="transparent")
        speed_frame.pack(fill="x", pady=30)
        
        lbl_frame = ctk.CTkFrame(speed_frame, fg_color="transparent")
        lbl_frame.pack(fill="x")
        ctk.CTkLabel(lbl_frame, text="Reading Speed", font=ctk.CTkFont(weight="bold")).pack(side="left")
        self.lbl_speed_val = ctk.CTkLabel(lbl_frame, text="1.0x")
        self.lbl_speed_val.pack(side="right")

        self.scale_speed = ctk.CTkSlider(
            speed_frame, 
            from_=0.5, to=2.0, 
            number_of_steps=15,
            command=self._on_slider_move
        )
        self.scale_speed.set(1.0)
        self.scale_speed.pack(fill="x", pady=(10, 0))
        
        self.scale_speed.bind("<ButtonRelease-1>", lambda e: self.cb.get('on_speed_change')(self._get_intuitive_speed()))

        # ── Status Row ──
        self.lbl_status = ctk.CTkLabel(
            self, text="Ready.", 
            text_color="gray", 
            font=ctk.CTkFont(slant="italic")
        )
        self.lbl_status.pack(side="bottom", fill="x", pady=(30, 0))

    def _on_slider_move(self, val):
        speed = float(val)
        self.lbl_speed_val.configure(text=f"{speed:.1f}x")

    def _get_intuitive_speed(self) -> float:
        return float(self.scale_speed.get())

    def update_page_label(self, current_1_based, total):
        self.ent_page.delete(0, "end")
        self.ent_page.insert(0, str(current_1_based))
        self.lbl_total.configure(text=f" / {total}")

    def update_status(self, text):
        self.lbl_status.configure(text=text)

    def set_state(self, state: str):
        """
        Manages enabling/disabling buttons based on current app state.
        States: 'no_document', 'stopped', 'playing', 'paused'
        """
        if state == "no_document":
            self.btn_prev.configure(state="disabled")
            self.btn_next.configure(state="disabled")
            self.btn_play.configure(state="disabled")
            self.btn_pause.configure(state="disabled")
            self.btn_stop.configure(state="disabled")
            self.scale_speed.configure(state="disabled")
            self.ent_page.configure(state="disabled")
            self.btn_zoom_in.configure(state="disabled")
            self.btn_zoom_out.configure(state="disabled")
            self.btn_zoom_reset.configure(state="disabled")
            
        elif state == "stopped":
            self.btn_prev.configure(state="normal")
            self.btn_next.configure(state="normal")
            self.btn_play.configure(state="normal")
            self.btn_pause.configure(state="disabled")
            self.btn_stop.configure(state="disabled")
            self.scale_speed.configure(state="normal")
            self.ent_page.configure(state="normal")
            self.btn_zoom_in.configure(state="normal")
            self.btn_zoom_out.configure(state="normal")
            self.btn_zoom_reset.configure(state="normal")
            self.btn_play.configure(text="▶ Play")
            
        elif state == "playing":
            self.btn_prev.configure(state="disabled")
            self.btn_next.configure(state="disabled")
            self.btn_play.configure(state="disabled")
            self.btn_pause.configure(state="normal")
            self.btn_stop.configure(state="normal")
            self.ent_page.configure(state="disabled")
            
        elif state == "paused":
            self.btn_play.configure(state="disabled")
            self.btn_pause.configure(state="normal")
            self.btn_pause.configure(text="▶ Resume")
            self.btn_stop.configure(state="normal")
            self.ent_page.configure(state="disabled")

        if state != "paused":
             self.btn_pause.configure(text="⏸ Pause")
