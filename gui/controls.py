"""
gui/controls.py
----------------
A horizontal toolbar panel (CTkFrame) containing all playback, navigation,
and zoom controls. Styled to resemble professional Linux document viewers
(Evince / Okular). No emoji — uses plain text labels and Unicode symbols
only where they are conventional (< > for prev/next).
"""

import customtkinter as ctk


# ── Colour tokens ─────────────────────────────────────────────────────────────
_BTN_ACCENT   = ("#1a6fa8", "#1a6fa8")   # blue  — primary action (Play)
_BTN_NEUTRAL  = ("gray30", "gray30")     # dark  — secondary actions
_BTN_STOP     = ("#7a1515", "#7a1515")   # dark red — destructive
_BTN_GHOST    = "transparent"
_BORDER       = ("gray45", "gray45")

# Fonts are created inside ControlPanel.__init__ (CTkFont requires a live Tk root)


def _sep(master):
    """Thin vertical separator for use inside a horizontal toolbar."""
    return ctk.CTkFrame(master, width=1, height=28,
                        fg_color=("gray40", "gray35"))


class ControlPanel(ctk.CTkFrame):
    """
    Horizontal toolbar panel.  Laid out as:
      [Open] | [Prev] [Page/Total] [Next] | [−] [100%] [+] | [Play] [Pause] [Stop]
    Speed slider + status live in a thin row below the toolbar.
    """

    def __init__(self, master, callbacks, **kwargs):
        super().__init__(master, fg_color=("gray18", "gray18"),
                         corner_radius=0, **kwargs)
        self.cb = callbacks

        # Fonts must be created after the Tk root window exists
        self._fn  = ctk.CTkFont(family="Sans", size=12)
        self._fb  = ctk.CTkFont(family="Sans", size=12, weight="bold")
        self._fl  = ctk.CTkFont(family="Sans", size=11)
        self._fs  = ctk.CTkFont(family="Sans", size=11, slant="italic")

        self._build_toolbar()
        self._build_statusbar()
        self.set_state("no_document")

    # ── Build ─────────────────────────────────────────────────────────────────

    def _build_toolbar(self):
        tb = ctk.CTkFrame(self, fg_color="transparent")
        tb.pack(side="top", fill="x", padx=12, pady=(8, 4))

        # ── File ──────────────────────────────────────────────────────────────
        self.btn_open = ctk.CTkButton(
            tb, text="Open File", width=88, height=30,
            font=self._fb,
            fg_color=_BTN_NEUTRAL, hover_color=("gray40", "gray40"),
            command=self.cb.get("on_open"),
        )
        self.btn_open.pack(side="left", padx=(0, 8))

        _sep(tb).pack(side="left", padx=8)

        # ── Navigation ────────────────────────────────────────────────────────
        self.btn_prev = ctk.CTkButton(
            tb, text="<", width=30, height=30,
            font=self._fb,
            fg_color=_BTN_GHOST, hover_color=("gray35", "gray35"),
            border_width=1, border_color=_BORDER,
            command=self.cb.get("on_prev"),
        )
        self.btn_prev.pack(side="left", padx=(0, 2))

        nav_center = ctk.CTkFrame(tb, fg_color="transparent")
        nav_center.pack(side="left", padx=4)

        self.ent_page = ctk.CTkEntry(
            nav_center, width=40, height=30,
            justify="center", font=self._fl,
        )
        self.ent_page.pack(side="left")
        self.ent_page.bind(
            "<Return>",
            lambda e: self.cb.get("on_jump")(self.ent_page.get()),
        )

        self.lbl_total = ctk.CTkLabel(
            nav_center, text=" / 0", font=self._fl,
            text_color=("gray65", "gray65"),
        )
        self.lbl_total.pack(side="left")

        self.btn_next = ctk.CTkButton(
            tb, text=">", width=30, height=30,
            font=self._fb,
            fg_color=_BTN_GHOST, hover_color=("gray35", "gray35"),
            border_width=1, border_color=_BORDER,
            command=self.cb.get("on_next"),
        )
        self.btn_next.pack(side="left", padx=(2, 0))

        _sep(tb).pack(side="left", padx=8)

        # ── Zoom ──────────────────────────────────────────────────────────────
        self.btn_zoom_out = ctk.CTkButton(
            tb, text="-", width=30, height=30,
            font=self._fb,
            fg_color=_BTN_GHOST, hover_color=("gray35", "gray35"),
            border_width=1, border_color=_BORDER,
            command=self.cb.get("on_zoom_out"),
        )
        self.btn_zoom_out.pack(side="left", padx=(0, 2))

        self.btn_zoom_reset = ctk.CTkButton(
            tb, text="100%", width=48, height=30,
            font=self._fl,
            fg_color=_BTN_GHOST, hover_color=("gray35", "gray35"),
            border_width=1, border_color=_BORDER,
            command=self.cb.get("on_zoom_reset"),
        )
        self.btn_zoom_reset.pack(side="left", padx=2)

        self.btn_zoom_in = ctk.CTkButton(
            tb, text="+", width=30, height=30,
            font=self._fb,
            fg_color=_BTN_GHOST, hover_color=("gray35", "gray35"),
            border_width=1, border_color=_BORDER,
            command=self.cb.get("on_zoom_in"),
        )
        self.btn_zoom_in.pack(side="left", padx=(2, 0))

        _sep(tb).pack(side="left", padx=8)

        # ── Playback ──────────────────────────────────────────────────────────
        self.btn_play = ctk.CTkButton(
            tb, text="Play", width=60, height=30,
            font=self._fb,
            fg_color=_BTN_ACCENT, hover_color=("#13527e", "#13527e"),
            command=self.cb.get("on_play"),
        )
        self.btn_play.pack(side="left", padx=(0, 4))

        self.btn_pause = ctk.CTkButton(
            tb, text="Pause", width=60, height=30,
            font=self._fn,
            fg_color=_BTN_NEUTRAL, hover_color=("gray40", "gray40"),
            command=self.cb.get("on_pause"),
        )
        self.btn_pause.pack(side="left", padx=4)

        self.btn_stop = ctk.CTkButton(
            tb, text="Stop", width=60, height=30,
            font=self._fn,
            fg_color=_BTN_STOP, hover_color=("#5a1010", "#5a1010"),
            command=self.cb.get("on_stop"),
        )
        self.btn_stop.pack(side="left", padx=(4, 0))

    def _build_statusbar(self):
        """Thin second row: speed slider on the left, status text on the right."""
        sb = ctk.CTkFrame(self, fg_color=("gray16", "gray16"), corner_radius=0)
        sb.pack(side="top", fill="x")

        # Speed
        speed_row = ctk.CTkFrame(sb, fg_color="transparent")
        speed_row.pack(side="left", padx=12, pady=(3, 5))

        ctk.CTkLabel(
            speed_row, text="Speed:", font=self._fl,
            text_color=("gray65", "gray65"),
        ).pack(side="left", padx=(0, 6))

        self.scale_speed = ctk.CTkSlider(
            speed_row, from_=0.5, to=2.0,
            number_of_steps=15, width=140, height=14,
            command=self._on_slider_move,
        )
        self.scale_speed.set(1.0)
        self.scale_speed.pack(side="left")
        self.scale_speed.bind(
            "<ButtonRelease-1>",
            lambda e: self.cb.get("on_speed_change")(float(self.scale_speed.get())),
        )

        self.lbl_speed_val = ctk.CTkLabel(
            speed_row, text="1.0x", width=36, font=self._fl,
            text_color=("gray65", "gray65"),
        )
        self.lbl_speed_val.pack(side="left", padx=(6, 0))

        # Status text — pinned to right
        self.lbl_status = ctk.CTkLabel(
            sb, text="No document open.",
            font=self._fs,
            text_color=("gray55", "gray55"),
            anchor="e",
        )
        self.lbl_status.pack(side="right", padx=14)

    # ── Public helpers ────────────────────────────────────────────────────────

    def _on_slider_move(self, val):
        self.lbl_speed_val.configure(text=f"{float(val):.1f}x")

    def update_page_label(self, current_1_based, total):
        self.ent_page.delete(0, "end")
        self.ent_page.insert(0, str(current_1_based))
        self.lbl_total.configure(text=f" / {total}")

    def update_zoom_label(self, zoom_factor: float):
        self.btn_zoom_reset.configure(text=f"{int(zoom_factor * 100)}%")

    def update_status(self, text: str):
        self.lbl_status.configure(text=text)

    def set_state(self, state: str):
        """
        Enable/disable controls based on application state.
        States: 'no_document' | 'stopped' | 'playing' | 'paused'
        """
        _all_nav   = [self.btn_prev, self.btn_next, self.ent_page]
        _all_zoom  = [self.btn_zoom_in, self.btn_zoom_out, self.btn_zoom_reset]
        _all_play  = [self.btn_play, self.btn_pause, self.btn_stop]

        def _en(widgets):
            for w in widgets:
                w.configure(state="normal")

        def _dis(widgets):
            for w in widgets:
                w.configure(state="disabled")

        if state == "no_document":
            _dis(_all_nav + _all_zoom + _all_play + [self.scale_speed])

        elif state == "stopped":
            _en(_all_nav + _all_zoom + [self.btn_play, self.scale_speed])
            _dis([self.btn_pause, self.btn_stop])
            self.btn_pause.configure(text="Pause")

        elif state == "playing":
            _dis([self.btn_play] + _all_nav + [self.ent_page])
            _en([self.btn_pause, self.btn_stop])
            self.btn_pause.configure(text="Pause")

        elif state == "paused":
            _dis([self.btn_play])
            _en([self.btn_pause, self.btn_stop])
            self.btn_pause.configure(text="Resume")
