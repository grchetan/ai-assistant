"""
================================================================================
                    JARVIS PROCEDURAL SOUND FX SYNTHESIZER
================================================================================
Generates high-tech Sci-Fi interface chimes, boot tones, and confirmation
bleeps entirely in-memory using pure NumPy waveform math & Pygame Mixer.
Zero external audio files required!
================================================================================
"""

import math
import threading
import numpy as np
from typing import Optional

try:
    import pygame
    _PYGAME_AVAILABLE = True
except ImportError:
    _PYGAME_AVAILABLE = False


class SoundFXManager:
    """Synthesizes and plays sci-fi audio cues for interface feedback."""
    
    _instance: Optional["SoundFXManager"] = None
    _lock = threading.RLock()

    def __new__(cls) -> "SoundFXManager":
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(SoundFXManager, cls).__new__(cls)
                cls._instance._init_mixer()
            return cls._instance

    def _init_mixer(self) -> None:
        self._enabled = True
        self._sample_rate = 44100
        if _PYGAME_AVAILABLE:
            try:
                if not pygame.mixer.get_init():
                    pygame.mixer.init(frequency=self._sample_rate, size=-16, channels=2, buffer=512)
            except Exception as e:
                print(f"[SoundFX] Failed to initialize pygame.mixer: {e}")
                self._enabled = False
        else:
            self._enabled = False

    def _play_wave(self, samples: np.ndarray) -> None:
        """Convert float numpy wave (-1.0 to 1.0) into stereo 16-bit sound and play."""
        if not self._enabled or not _PYGAME_AVAILABLE:
            return
        
        try:
            # Scale to 16-bit signed PCM
            samples = np.clip(samples, -1.0, 1.0)
            pcm16 = (samples * 32767).astype(np.int16)
            
            # Make stereo
            stereo = np.column_stack((pcm16, pcm16))
            sound = pygame.sndarray.make_sound(stereo)
            sound.set_volume(0.35)
            sound.play()
        except Exception as e:
            print(f"[SoundFX] Playback error: {e}")

    def play_boot(self) -> None:
        """Sci-Fi Arc Reactor spin-up chirp: rising frequency sweep + chime."""
        if not self._enabled:
            return
        
        duration = 0.55
        sr = self._sample_rate
        t = np.linspace(0, duration, int(sr * duration), endpoint=False)
        
        # Exponential frequency sweep from 220Hz to 1200Hz
        freq = np.geomspace(220, 1200, len(t))
        phase = 2 * np.pi * np.cumsum(freq) / sr
        sweep = 0.6 * np.sin(phase)
        
        # Envelope: smooth fade-in and sustained harmonic ping at the end
        env = np.sin(np.pi * (t / duration) ** 0.6)
        
        # Add high shimmer harmonic
        shimmer = 0.25 * np.sin(2 * np.pi * 1760 * t) * (t / duration)
        
        wave = (sweep + shimmer) * env
        self._play_wave(wave)

    def play_listening(self) -> None:
        """Gentle ascending dual-tone ping indicating mic is listening."""
        if not self._enabled:
            return
        
        duration = 0.22
        sr = self._sample_rate
        t = np.linspace(0, duration, int(sr * duration), endpoint=False)
        
        half = len(t) // 2
        f1, f2 = 587.33, 880.00  # D5 -> A5
        
        wave = np.zeros_like(t)
        wave[:half] = 0.5 * np.sin(2 * np.pi * f1 * t[:half]) * np.sin(np.pi * np.linspace(0, 1, half))
        wave[half:] = 0.5 * np.sin(2 * np.pi * f2 * t[half:]) * np.sin(np.pi * np.linspace(0, 1, len(t) - half))
        
        self._play_wave(wave)

    def play_success(self) -> None:
        """Pleasant confirmation chime (major chord triad)."""
        if not self._enabled:
            return
        
        duration = 0.35
        sr = self._sample_rate
        t = np.linspace(0, duration, int(sr * duration), endpoint=False)
        
        c6, e6, g6 = 1046.50, 1318.51, 1567.98
        wave = (
            0.35 * np.sin(2 * np.pi * c6 * t) +
            0.30 * np.sin(2 * np.pi * e6 * t) +
            0.25 * np.sin(2 * np.pi * g6 * t)
        )
        # Exponential decay envelope
        decay = np.exp(-7.0 * t)
        wave = wave * decay
        self._play_wave(wave)

    def play_auth_granted(self) -> None:
        """Futuristic high-tech access granted sequence."""
        if not self._enabled:
            return
        
        duration = 0.45
        sr = self._sample_rate
        t = np.linspace(0, duration, int(sr * duration), endpoint=False)
        
        notes = [784.0, 1046.5, 1567.98] # G5, C6, G6
        segment = len(t) // 3
        wave = np.zeros_like(t)
        
        for i, n in enumerate(notes):
            idx_start = i * segment
            idx_end = (i + 1) * segment if i < 2 else len(t)
            sub_t = t[idx_start:idx_end] - t[idx_start]
            sub_len = len(sub_t)
            env = np.sin(np.pi * np.linspace(0, 1, sub_len))
            wave[idx_start:idx_end] = 0.45 * np.sin(2 * np.pi * n * sub_t) * env
            
        self._play_wave(wave)

    def play_auth_denied(self) -> None:
        """Low-pitch double buzz error sound."""
        if not self._enabled:
            return
        
        duration = 0.3
        sr = self._sample_rate
        t = np.linspace(0, duration, int(sr * duration), endpoint=False)
        
        wave = 0.6 * np.sign(np.sin(2 * np.pi * 140 * t)) * np.sin(np.pi * 15 * t)
        decay = np.exp(-4.0 * t)
        wave = wave * decay
        self._play_wave(wave)

    def play_alert(self) -> None:
        """Attention radar pulse."""
        if not self._enabled:
            return
        
        duration = 0.28
        sr = self._sample_rate
        t = np.linspace(0, duration, int(sr * duration), endpoint=False)
        f = 950 + 200 * np.sin(2 * np.pi * 8 * t)
        phase = 2 * np.pi * np.cumsum(f) / sr
        wave = 0.4 * np.sin(phase) * (1 - t / duration)
        self._play_wave(wave)


def get_sound_fx() -> SoundFXManager:
    return SoundFXManager()
