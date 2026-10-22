"""
================================================================================
                    JARVIS DIGITAL SIGNAL PROCESSOR & AUDIO ENHANCER
================================================================================
Acoustic signal processing engine featuring:
  - Butterworth Bandpass speech filter (80Hz - 7500Hz)
  - Spectral subtraction noise gate
  - Dynamic Range Compression (DRC)
  - Automatic Gain Control (AGC) with peak limiter
================================================================================
"""

import numpy as np
from typing import Tuple, Optional

try:
    from scipy.signal import butter, lfilter
    _SCIPY_AVAILABLE = True
except ImportError:
    _SCIPY_AVAILABLE = False

from jarvis.core.logger import get_logger


class AudioEnhancer:
    """Enhances speech signals to improve STT transcription accuracy."""

    def __init__(self, sample_rate: int = 16000) -> None:
        self.logger = get_logger()
        self.sample_rate = sample_rate

    def apply_bandpass_filter(
        self,
        audio_float: np.ndarray,
        lowcut: float = 80.0,
        highcut: float = 7500.0,
        order: int = 4
    ) -> np.ndarray:
        """
        Butterworth bandpass filter: eliminates low-frequency desk rumbles
        and high-frequency electronic hiss, preserving vocal clarity.
        """
        if not _SCIPY_AVAILABLE or audio_float is None or len(audio_float) == 0:
            return audio_float

        try:
            nyq = 0.5 * self.sample_rate
            low = max(lowcut / nyq, 0.001)
            high = min(highcut / nyq, 0.999)
            b, a = butter(order, [low, high], btype='band')
            filtered = lfilter(b, a, audio_float)
            return filtered.astype(np.float32)
        except Exception as e:
            self.logger.debug(f"Bandpass filter error: {e}", "DSP")
            return audio_float

    def apply_spectral_noise_gate(
        self,
        audio_float: np.ndarray,
        threshold_db: float = -40.0
    ) -> np.ndarray:
        """
        Spectral energy gate: attenuates audio frames below noise threshold.
        """
        if audio_float is None or len(audio_float) == 0:
            return audio_float

        try:
            # Frame-by-frame energy gating
            frame_len = 512
            output = audio_float.copy()

            num_frames = len(audio_float) // frame_len
            thresh_linear = 10.0 ** (threshold_db / 20.0)

            for i in range(num_frames):
                start = i * frame_len
                end = start + frame_len
                chunk = audio_float[start:end]
                rms = np.sqrt(np.mean(chunk**2) + 1e-12)

                if rms < thresh_linear:
                    # Suppress noise chunk with gentle decay
                    output[start:end] *= 0.15

            return output
        except Exception:
            return audio_float

    def apply_dynamic_range_compression(
        self,
        audio_float: np.ndarray,
        threshold: float = 0.3,
        ratio: float = 4.0
    ) -> np.ndarray:
        """
        DRC compressor: tames sudden loud shouts while boosting quiet whispers.
        """
        if audio_float is None or len(audio_float) == 0:
            return audio_float

        try:
            magnitudes = np.abs(audio_float)
            signs = np.sign(audio_float)

            compressed = np.where(
                magnitudes > threshold,
                threshold + (magnitudes - threshold) / ratio,
                magnitudes
            )
            return (compressed * signs).astype(np.float32)
        except Exception:
            return audio_float

    def apply_automatic_gain_control(
        self,
        audio_float: np.ndarray,
        target_peak: float = 0.92
    ) -> np.ndarray:
        """
        Normalize audio peak amplitude to target ceiling without clipping.
        """
        if audio_float is None or len(audio_float) == 0:
            return audio_float

        peak = np.max(np.abs(audio_float))
        if peak > 1e-6:
            gain = target_peak / peak
            # Bound maximum digital boost to +18 dB (approx 8x)
            gain = min(gain, 8.0)
            boosted = audio_float * gain
            return np.clip(boosted, -1.0, 1.0).astype(np.float32)
        return audio_float

    def process_speech_pipeline(self, raw_audio: np.ndarray) -> np.ndarray:
        """
        Complete processing chain: Bandpass -> Gate -> DRC -> AGC.
        """
        step1 = self.apply_bandpass_filter(raw_audio)
        step2 = self.apply_spectral_noise_gate(step1)
        step3 = self.apply_dynamic_range_compression(step2)
        final_signal = self.apply_automatic_gain_control(step3)
        return final_signal


def get_audio_enhancer() -> AudioEnhancer:
    return AudioEnhancer()
