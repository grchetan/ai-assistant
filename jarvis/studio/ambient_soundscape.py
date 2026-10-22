"""
================================================================================
                    JARVIS PROCEDURAL AMBIENT SOUNDSCAPES
================================================================================
Continuous background ambient audio generator designed for deep study, focus,
and relaxation. Generates pure mathematical soundscapes:
  - Cyberpunk Rain & Distant Thunder
  - Cosmic Alpha-Wave Binaural Drone (432Hz tuned, 10Hz beat)
  - Deep Brown Noise Acoustic Isolator
================================================================================
"""

import time
import math
import threading
import numpy as np
from typing import Optional

try:
    import pygame
    _PYGAME_AVAILABLE = True
except ImportError:
    _PYGAME_AVAILABLE = False

from jarvis.core.logger import get_logger


class AmbientSoundscape:
    """Streams continuous background white/pink noise and focus soundscapes."""

    _instance: Optional["AmbientSoundscape"] = None
    _lock = threading.RLock()

    def __new__(cls) -> "AmbientSoundscape":
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(AmbientSoundscape, cls).__new__(cls)
                cls._instance._init_soundscape()
            return cls._instance

    def _init_soundscape(self) -> None:
        self.logger = get_logger()
        self.sample_rate = 22050
        self._is_playing = False
        self._thread: Optional[threading.Thread] = None
        self._active_mode = "NONE"
        self._volume = 0.25

    def start_rain_soundscape(self) -> None:
        """Procedural rain shower: filtered noise with random droplet transients."""
        self.stop()
        self._active_mode = "RAIN"
        self._is_playing = True
        self._thread = threading.Thread(target=self._stream_rain, daemon=True)
        self._thread.start()
        self.logger.info("Ambient Cyberpunk Rain Soundscape started.", "STUDIO")

    def start_binaural_drone(self, base_freq: float = 216.0, beat_freq: float = 10.0) -> None:
        """
        Alpha-wave binaural beat (10Hz difference between left and right ears)
        for deep cognitive focus and stress reduction.
        """
        self.stop()
        self._active_mode = "BINAURAL"
        self._is_playing = True
        self._thread = threading.Thread(
            target=self._stream_binaural,
            args=(base_freq, beat_freq),
            daemon=True
        )
        self._thread.start()
        self.logger.info(f"Alpha-wave Binaural Focus Drone ({beat_freq}Hz beat) active.", "STUDIO")

    def start_brown_noise(self) -> None:
        """Integrated Brownian noise (1/f^2) for acoustic isolation and focus."""
        self.stop()
        self._active_mode = "BROWN_NOISE"
        self._is_playing = True
        self._thread = threading.Thread(target=self._stream_brown_noise, daemon=True)
        self._thread.start()
        self.logger.info("Brown Noise Acoustic Isolator active.", "STUDIO")

    def stop(self) -> None:
        """Halt ambient sound generation."""
        self._is_playing = False
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=1.0)
        self._active_mode = "NONE"

    def _play_buffer(self, buffer_stereo: np.ndarray) -> None:
        if not _PYGAME_AVAILABLE or not pygame.mixer.get_init():
            return
        try:
            pcm = (np.clip(buffer_stereo, -1.0, 1.0) * 32767).astype(np.int16)
            sound = pygame.sndarray.make_sound(pcm)
            sound.set_volume(self._volume)
            sound.play()
        except Exception:
            pass

    def _stream_rain(self) -> None:
        chunk_sec = 2.0
        n_samples = int(self.sample_rate * chunk_sec)

        while self._is_playing:
            # Pinkish noise via moving average of white noise
            white = np.random.normal(0, 0.3, n_samples)
            pink = np.convolve(white, np.ones(5)/5, mode='same')

            # Add occasional gentle droplet transients
            droplets = np.zeros(n_samples)
            drop_positions = np.random.randint(0, n_samples, size=15)
            for pos in drop_positions:
                decay_len = min(600, n_samples - pos)
                t_drop = np.linspace(0, 0.03, decay_len)
                f_drop = np.random.uniform(900, 2200)
                droplets[pos:pos+decay_len] += 0.2 * np.sin(2 * np.pi * f_drop * t_drop) * np.exp(-150 * t_drop)

            rain_mono = (pink * 0.7 + droplets).astype(np.float32)
            stereo = np.column_stack((rain_mono, rain_mono))
            self._play_buffer(stereo)
            time.sleep(chunk_sec * 0.95)

    def _stream_binaural(self, base_freq: float, beat_freq: float) -> None:
        chunk_sec = 3.0
        n_samples = int(self.sample_rate * chunk_sec)
        t = np.linspace(0, chunk_sec, n_samples, endpoint=False)

        left_freq = base_freq
        right_freq = base_freq + beat_freq

        while self._is_playing:
            left_wave = 0.25 * np.sin(2 * np.pi * left_freq * t)
            right_wave = 0.25 * np.sin(2 * np.pi * right_freq * t)
            stereo = np.column_stack((left_wave, right_wave)).astype(np.float32)

            self._play_buffer(stereo)
            time.sleep(chunk_sec * 0.95)

    def _stream_brown_noise(self) -> None:
        chunk_sec = 2.0
        n_samples = int(self.sample_rate * chunk_sec)

        while self._is_playing:
            white = np.random.normal(0, 0.2, n_samples)
            brown = np.cumsum(white)
            # Remove DC offset and normalize
            brown = (brown - np.mean(brown)) / (np.max(np.abs(brown)) + 1e-9)
            brown *= 0.4
            stereo = np.column_stack((brown, brown)).astype(np.float32)

            self._play_buffer(stereo)
            time.sleep(chunk_sec * 0.95)


def get_ambient_soundscape() -> AmbientSoundscape:
    return AmbientSoundscape()
