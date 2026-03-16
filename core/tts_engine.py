"""
core/tts_engine.py
-------------------
Text-to-Speech engine powered by Piper TTS — a neural, offline TTS engine
that produces human-quality speech using ONNX voice models.

How Piper works
---------------
  1. Load a voice model (.onnx file) + its config (.onnx.json)
  2. Call voice.synthesize(text) → yields chunks of raw PCM audio bytes
  3. Play those bytes through the sound card using `sounddevice`

Why Piper over espeak-ng?
--------------------------
  - espeak-ng uses rule-based synthesis → robotic, mechanical sound
  - Piper uses a trained neural network → natural, human-sounding speech
  - Both are 100% offline and free

Learning note: Generators and streaming audio
----------------------------------------------
`voice.synthesize()` is a Python *generator* — it yields small chunks of
audio as they are computed instead of waiting for the full synthesis to
finish. This means audio starts playing faster (lower latency).

`sounddevice.RawOutputStream` writes raw PCM bytes directly to the audio
hardware, bypassing the need for any intermediate WAV/MP3 file.
"""

import io
import threading
import wave
from typing import Callable, Optional
import sounddevice as sd
from piper.voice import PiperVoice
from piper.config import SynthesisConfig

from utils.config import (
    PIPER_MODEL_PATH,
    PIPER_MODEL_CONFIG,
    TTS_RATE_SCALE,
    TTS_VOLUME,
)


class TTSEngine:
    """
    Piper-based TTS engine with play / pause / stop / speed control.
    Drop-in replacement for the old pyttsx3 engine.
    """

    def __init__(self):
        # Load the voice model once at startup (takes ~1 second)
        print(f"  Loading Piper voice model: {PIPER_MODEL_PATH}")
        self._voice = PiperVoice.load(PIPER_MODEL_PATH, config_path=PIPER_MODEL_CONFIG)

        # Threading state
        self._thread: threading.Thread | None = None
        self._stop_event  = threading.Event()
        self._pause_event = threading.Event()   # set → paused

        # Public state flags  (read by the GUI to update button labels)
        self.is_speaking = False
        self.is_paused   = False

        # Speed: 1.0 = normal, 0.5 = half speed, 2.0 = double speed
        # Piper controls speed via `length_scale` (higher = slower)
        self.speed = TTS_RATE_SCALE   # default from config

        # Volume: 0.0 – 1.0
        self.volume = TTS_VOLUME

        # Optional callback — called when speaking naturally finishes
        self.on_done: Optional[Callable[[], None]] = None

    # ── Public API ────────────────────────────────────────────────────────────

    def speak(self, text: str):
        """
        Speak *text* asynchronously in a background thread.
        Any current speech is stopped before starting.
        """
        self.stop()                     # cancel anything already playing

        self._stop_event.clear()
        self._pause_event.clear()
        self.is_speaking = True
        self.is_paused   = False

        self._thread = threading.Thread(
            target=self._speak_worker,
            args=(text,),
            daemon=True,
        )
        self._thread.start()

    def pause(self):
        """Pause playback after the current audio chunk finishes."""
        if self.is_speaking and not self.is_paused:
            self._pause_event.set()
            self.is_paused = True

    def resume(self):
        """Resume a paused session."""
        if self.is_paused:
            self._pause_event.clear()
            self.is_paused = False

    def list_voices(self) -> list[str]:
        """
        Return a list of available voice model names.
        Currently returns just the loaded voice name.
        (Multi-voice support can be added later.)
        """
        return ["en_US-lessac-medium"]

    def stop(self):
        """Immediately stop all playback."""
        if self._thread and self._thread.is_alive():
            self._stop_event.set()
            self._pause_event.clear()   # unblock any pause-wait loops
            self._thread.join(timeout=3)
        self.is_speaking = False
        self.is_paused   = False

    # ── Internal worker ───────────────────────────────────────────────────────

    def _speak_worker(self, text: str):
        """
        Runs in a background thread.

        Strategy:
        1. Split text into manageable sentence-sized chunks
        2. For each chunk: synthesize PCM bytes → stream to sounddevice
        3. Between chunks: check if stop/pause was requested
        """
        sentences = self._split_sentences(text)

        try:
            for sentence in sentences:
                # ── Check stop before each sentence ──
                if self._stop_event.is_set():
                    break

                # ── Wait while paused ──
                while self._pause_event.is_set():
                    if self._stop_event.is_set():
                        break
                    threading.Event().wait(0.1)

                if self._stop_event.is_set():
                    break

                # ── Synthesize this sentence ──
                import numpy as np
                
                syn_config = SynthesisConfig(
                    length_scale=1.0 / self.speed,   # higher = slower
                    volume=self.volume,
                )
                
                # Collect all audio chunks from Piper into a single array
                audio_arrays = []
                for audio_chunk in self._voice.synthesize(sentence, syn_config):
                    audio_arrays.append(audio_chunk.audio_int16_array)
                
                if not audio_arrays:
                    continue  # Empty synthesis, skip
                
                # Concatenate all chunks into one audio array
                audio_data = np.concatenate(audio_arrays)

                if self._stop_event.is_set():
                    break

                # ── Play the audio via sounddevice ──
                # Piper outputs 16-bit signed integers at 22050 Hz
                sample_rate = 22050
                
                # Non-blocking play with a stop check
                sd.play(audio_data, samplerate=sample_rate)
                # Wait until playback completes or stop is requested
                while sd.get_stream().active:
                    if self._stop_event.is_set():
                        sd.stop()
                        break
                    threading.Event().wait(0.05)

        finally:
            self.is_speaking = False
            self.is_paused   = False
            # Notify GUI that reading finished naturally
            if self.on_done and not self._stop_event.is_set():
                self.on_done()

    # ── Helpers ───────────────────────────────────────────────────────────────

    @staticmethod
    def _split_sentences(text: str) -> list[str]:
        """
        Split text into sentence-sized chunks for interruptible playback.
        We split on sentence-ending punctuation followed by whitespace.
        """
        import re
        parts = re.split(r'(?<=[.!?])\s+', text)
        return [p.strip() for p in parts if len(p.strip()) > 2]
