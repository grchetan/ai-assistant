"""
================================================================================
                    JARVIS PROCEDURAL SCI-FI SOUNDBOARD
================================================================================
Comprehensive high-tech acoustic feedback generator creating authentic Marvel
Iron Man & Sci-Fi cinematic sound effects directly in-memory using pure NumPy math.
Zero external audio asset files required!
================================================================================
"""

import math
import numpy as np
from typing import Optional

try:
    import pygame
    _PYGAME_AVAILABLE = True
except ImportError:
    _PYGAME_AVAILABLE = False

from jarvis.core.logger import get_logger


class SciFiSoundboard:
    """Generates and plays cinematic Sci-Fi sound effects."""

    _instance: Optional["SciFiSoundboard"] = None

    def __new__(cls) -> "SciFiSoundboard":
        if cls._instance is None:
            cls._instance = super(SciFiSoundboard, cls).__new__(cls)
            cls._instance._init_soundboard()
        return cls._instance

    def _init_soundboard(self) -> None:
        self.logger = get_logger()
        self.sample_rate = 44100
        self.enabled = True

        if _PYGAME_AVAILABLE:
            try:
                if not pygame.mixer.get_init():
                    pygame.mixer.init(frequency=self.sample_rate, size=-16, channels=2, buffer=512)
            except Exception as e:
                self.logger.warning(f"Pygame mixer init error: {e}", "SFX")
                self.enabled = False
        else:
            self.enabled = False

    def _play(self, samples: np.ndarray, volume: float = 0.4) -> None:
        if not self.enabled or not _PYGAME_AVAILABLE:
            return
        try:
            samples = np.clip(samples, -1.0, 1.0)
            pcm16 = (samples * 32767).astype(np.int16)
            stereo = np.column_stack((pcm16, pcm16))
            sound = pygame.sndarray.make_sound(stereo)
            sound.set_volume(volume)
            sound.play()
        except Exception as e:
            self.logger.debug(f"Audio playback error: {e}", "SFX")

    def play_repulsor_blast(self) -> None:
        """Iron Man hand repulsor beam blast: high-energy rise, explosion, and dissipate."""
        duration = 0.45
        t = np.linspace(0, duration, int(self.sample_rate * duration), endpoint=False)

        # Rising high-pitch charge then exponential bass pop
        charge = np.sin(2 * np.pi * np.geomspace(400, 3200, len(t)) * t) * (t / duration)
        boom = np.sin(2 * np.pi * 90 * t) * np.exp(-12.0 * t)
        noise = np.random.normal(0, 0.4, len(t)) * np.exp(-8.0 * t)

        wave = 0.4 * charge + 0.5 * boom + 0.3 * noise
        self._play(wave, volume=0.45)

    def play_sonar_ping(self) -> None:
        """Deep submarine / radar echo pulse."""
        duration = 1.2
        t = np.linspace(0, duration, int(self.sample_rate * duration), endpoint=False)
        ping = np.sin(2 * np.pi * 1800 * t) * np.exp(-4.5 * t)
        sub = np.sin(2 * np.pi * 900 * t) * np.exp(-3.0 * t) * 0.3
        wave = ping + sub
        self._play(wave, volume=0.3)

    def play_warp_jump(self) -> None:
        """Hyperspace warp drive engagement whoosh."""
        duration = 0.75
        t = np.linspace(0, duration, int(self.sample_rate * duration), endpoint=False)

        # Downward pitch dive with resonance
        freqs = np.geomspace(2400, 80, len(t))
        phase = 2 * np.pi * np.cumsum(freqs) / self.sample_rate
        sweep = np.sin(phase)

        env = np.sin(np.pi * (t / duration)) ** 1.5
        wave = sweep * env
        self._play(wave, volume=0.4)

    def play_hydraulic_airlock(self) -> None:
        """Pneumatic airlock release whoosh."""
        duration = 0.6
        t = np.linspace(0, duration, int(self.sample_rate * duration), endpoint=False)

        noise = np.random.normal(0, 0.5, len(t))
        env = (1.0 - t / duration) ** 2.0
        tone = 0.3 * np.sin(2 * np.pi * 220 * t) * env
        wave = (noise * env) + tone
        self._play(wave, volume=0.35)

    def play_breach_siren(self) -> None:
        """Two-tone emergency tactical alarm siren."""
        duration = 0.8
        t = np.linspace(0, duration, int(self.sample_rate * duration), endpoint=False)

        # Alternating frequency modulation
        mod = np.sin(2 * np.pi * 3.5 * t)
        freq = 880 + 320 * mod
        phase = 2 * np.pi * np.cumsum(freq) / self.sample_rate
        wave = 0.5 * np.sin(phase)
        self._play(wave, volume=0.4)


def get_soundboard() -> SciFiSoundboard:
    return SciFiSoundboard()
