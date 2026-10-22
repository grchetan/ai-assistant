"""
================================================================================
                    JARVIS DSP VOICE CHANGER & ACOUSTIC MORPHER
================================================================================
Real-time vocal transformation engine built with pure NumPy & SciPy:
  - Robotic Ring Modulator (Vocoder Effect)
  - Iron Man Mark VII Helmet Acoustic Resonance Simulator
  - Tactical Radio Walkie-Talkie Filter with Squelch Noise
  - Dynamic Pitch Transposer
================================================================================
"""

import math
import numpy as np
from typing import Optional

try:
    from scipy.signal import resample, butter, lfilter
    _SCIPY_AVAILABLE = True
except ImportError:
    _SCIPY_AVAILABLE = False

from jarvis.core.logger import get_logger


class VoiceChanger:
    """Acoustic transformer for voice synthesis and microphone streams."""

    def __init__(self, sample_rate: int = 24000) -> None:
        self.logger = get_logger()
        self.sample_rate = sample_rate

    def apply_robotic_vocoder(
        self,
        audio: np.ndarray,
        carrier_freq: float = 65.0,
        depth: float = 0.85
    ) -> np.ndarray:
        """
        Ring modulation with low-frequency square/sine carrier wave
        giving a mechanical, robotic tone.
        """
        if audio is None or len(audio) == 0:
            return audio

        t = np.linspace(0, len(audio) / self.sample_rate, len(audio), endpoint=False)
        carrier = (1.0 - depth) + depth * np.cos(2 * np.pi * carrier_freq * t)
        modulated = audio * carrier
        return np.clip(modulated, -1.0, 1.0).astype(np.float32)

    def apply_iron_man_helmet_effect(
        self,
        audio: np.ndarray,
        resonance_delay_ms: float = 18.0,
        decay: float = 0.55
    ) -> np.ndarray:
        """
        Comb filter and metallic reflection simulating speaking from inside
        the armored Titanium Gold helmet of Iron Man.
        """
        if audio is None or len(audio) == 0:
            return audio

        delay_samples = int((resonance_delay_ms / 1000.0) * self.sample_rate)
        if delay_samples <= 0 or delay_samples >= len(audio):
            return audio

        output = audio.copy()
        # Feedforward comb filter
        for i in range(delay_samples, len(audio)):
            output[i] = audio[i] + decay * audio[i - delay_samples]

        # Slight treble boost for metallic clarity
        if _SCIPY_AVAILABLE:
            try:
                b, a = butter(2, 2800 / (0.5 * self.sample_rate), btype='high')
                treble = lfilter(b, a, output)
                output = output * 0.7 + treble * 0.4
            except Exception:
                pass

        return np.clip(output, -1.0, 1.0).astype(np.float32)

    def apply_tactical_radio(self, audio: np.ndarray) -> np.ndarray:
        """
        Bandpass filter (300Hz - 3400Hz) with subtle static and saturation
        to simulate military tactical radio communication.
        """
        if audio is None or len(audio) == 0:
            return audio

        if _SCIPY_AVAILABLE:
            try:
                nyq = 0.5 * self.sample_rate
                b, a = butter(3, [300.0 / nyq, 3400.0 / nyq], btype='band')
                bandpassed = lfilter(b, a, audio)
            except Exception:
                bandpassed = audio
        else:
            bandpassed = audio

        # Soft-clipping saturation (cubic harmonic distortion)
        saturated = np.tanh(bandpassed * 2.2)

        # Subtle white noise squelch
        noise = np.random.normal(0, 0.008, len(audio)).astype(np.float32)
        radio_out = saturated * 0.85 + noise

        return np.clip(radio_out, -1.0, 1.0).astype(np.float32)

    def shift_pitch(self, audio: np.ndarray, semitones: float = -2.0) -> np.ndarray:
        """
        Resampling pitch shifter. Negative semitones for deeper voice,
        positive for higher pitched synthetic voice.
        """
        if not _SCIPY_AVAILABLE or audio is None or len(audio) == 0:
            return audio

        try:
            factor = 2.0 ** (semitones / 12.0)
            target_len = int(len(audio) / factor)
            # Resample length then stretch back
            resampled = resample(audio, target_len)
            stretched = resample(resampled, len(audio))
            return np.clip(stretched, -1.0, 1.0).astype(np.float32)
        except Exception:
            return audio


def get_voice_changer() -> VoiceChanger:
    return VoiceChanger()
