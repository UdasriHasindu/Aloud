"""
core/tts_engine.py
-------------------
Text-to-Speech engine: converts text strings into spoken audio.

Key design decisions
--------------------
1. We wrap `pyttsx3` in our own class so the GUI layer is decoupled from
   the TTS library. If we ever swap pyttsx3 for Coqui TTS the GUI won't
   change at all.

2. TTS runs in a BACKGROUND THREAD. Speaking a long page of text can take
   minutes. If we ran it on the main (GUI) thread the window would freeze.
   Threading keeps the UI responsive while audio plays.

3. We use threading.Event objects as simple on/off flags to implement
   pause/resume without needing complex synchronisation code.

Learning note: Threading basics
--------------------------------
`threading.Thread(target=fn)` creates a new execution path.
`.start()` launches it.
`threading.Event` is like a boolean flag that threads can wait on:
  - event.set()   →  "signal is ON"
  - event.clear() →  "signal is OFF"
  - event.wait()  →  "block here until signal turns ON"
"""

import threading
import pyttsx3
from utils.config import TTS_RATE, TTS_VOLUME, TTS_VOICE_INDEX


class TTSEngine:
    """Wraps pyttsx3 to provide threaded, controllable text-to-speech."""

    def __init__(self):
        # Initialise the underlying pyttsx3 engine.
        # On Linux this automatically uses the espeak-ng backend.
        self._engine = pyttsx3.init()
        self._apply_defaults()

        # Threading state
        self._thread: threading.Thread | None = None
        self._stop_event = threading.Event()   # set() = stop speaking
        self._pause_event = threading.Event()  # set() = paused
        self._pause_event.clear()              # not paused initially

        # Current state flags (read by the GUI to update button labels)
        self.is_speaking = False
        self.is_paused = False

        # Callback hooks — set these from the GUI if you want to be notified
        # when speaking finishes.  e.g. engine.on_done = my_function
        self.on_done: callable | None = None

    # ── Configuration ─────────────────────────────────────────────────────────

    def _apply_defaults(self):
        """Apply settings from config.py to the pyttsx3 engine."""
        self._engine.setProperty("rate", TTS_RATE)
        self._engine.setProperty("volume", TTS_VOLUME)
        voices = self._engine.getProperty("voices")
        if voices and TTS_VOICE_INDEX < len(voices):
            self._engine.setProperty("voice", voices[TTS_VOICE_INDEX].id)

    @property
    def rate(self) -> int:
        """Current speech rate in words-per-minute."""
        return self._engine.getProperty("rate")

    @rate.setter
    def rate(self, value: int):
        """Set speech rate. Typical range: 80–300 wpm."""
        self._engine.setProperty("rate", value)

    @property
    def volume(self) -> float:
        """Current volume (0.0 – 1.0)."""
        return self._engine.getProperty("volume")

    @volume.setter
    def volume(self, value: float):
        self._engine.setProperty("volume", max(0.0, min(1.0, value)))

    def list_voices(self) -> list[str]:
        """Return the names of all available TTS voices on this system."""
        voices = self._engine.getProperty("voices")
        return [v.name for v in voices] if voices else []

    def set_voice_by_index(self, index: int):
        """Switch to a different voice by its index in list_voices()."""
        voices = self._engine.getProperty("voices")
        if voices and 0 <= index < len(voices):
            self._engine.setProperty("voice", voices[index].id)

    # ── Core speak / control ──────────────────────────────────────────────────

    def speak(self, text: str):
        """
        Speak *text* in a background thread.

        If something is already being spoken it is stopped first.

        Args:
            text: The string to speak.
        """
        # Stop any current speech before starting new
        self.stop()

        self._stop_event.clear()
        self._pause_event.clear()
        self.is_speaking = True
        self.is_paused = False

        self._thread = threading.Thread(
            target=self._speak_worker,
            args=(text,),
            daemon=True,    # daemon threads die automatically when the app exits
        )
        self._thread.start()

    def _speak_worker(self, text: str):
        """
        Internal worker that runs in a background thread.

        We split the text into sentences so we can check for stop/pause
        signals between each sentence — pyttsx3 doesn't support mid-sentence
        interruption natively.
        """
        sentences = self._split_into_sentences(text)

        for sentence in sentences:
            # Check stop flag before each sentence
            if self._stop_event.is_set():
                break

            # If paused, wait here until resumed or stopped
            while self._pause_event.is_set():
                if self._stop_event.is_set():
                    break
                threading.Event().wait(0.1)   # sleep 100ms then check again

            if self._stop_event.is_set():
                break

            # Speak one sentence synchronously (blocks until done)
            self._engine.say(sentence)
            self._engine.runAndWait()

        self.is_speaking = False
        self.is_paused = False

        # Notify the GUI that reading finished (if callback set)
        if self.on_done and not self._stop_event.is_set():
            self.on_done()

    def pause(self):
        """Pause speech after the current sentence finishes."""
        if self.is_speaking and not self.is_paused:
            self._pause_event.set()
            self.is_paused = True

    def resume(self):
        """Resume a paused reading session."""
        if self.is_paused:
            self._pause_event.clear()
            self.is_paused = False

    def stop(self):
        """Immediately stop speaking and clear the queue."""
        if self._thread and self._thread.is_alive():
            self._stop_event.set()
            self._pause_event.clear()   # unblock any waiting-on-pause loops
            self._engine.stop()         # interrupt current utterance
            self._thread.join(timeout=2)
        self.is_speaking = False
        self.is_paused = False

    # ── Helpers ───────────────────────────────────────────────────────────────

    @staticmethod
    def _split_into_sentences(text: str) -> list[str]:
        """
        Simple sentence splitter.

        Splits on '. ', '! ', '? ' so we can pause between sentences.
        Good enough for most PDF content.
        """
        import re
        # Split on sentence-ending punctuation followed by a space or newline
        parts = re.split(r'(?<=[.!?])\s+', text)
        # Filter empty strings and very short fragments
        return [p.strip() for p in parts if len(p.strip()) > 2]
