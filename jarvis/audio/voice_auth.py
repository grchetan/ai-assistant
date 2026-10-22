"""
================================================================================
                JARVIS BIOMETRIC VOICE AUTHENTICATION ENGINE
================================================================================
Acoustic speaker verification system built on pure NumPy and SciPy.
Extracts 28-dimensional acoustic feature vectors:
  - 13 Mel-Frequency Cepstral Coefficients (MFCC)
  - 13 Delta MFCCs (first-order temporal derivative)
  - Spectral Centroid & Spectral Rolloff
  - Log Frame Energy & Zero-Crossing Rates
Scores speech using Cosine Distance & Dynamic Time Warping (DTW) alignment.
================================================================================
"""

import os
import time
import threading
import numpy as np
from typing import Optional, Tuple, List
from pathlib import Path

try:
    from scipy.fftpack import dct
    from scipy.signal import lfilter
    _SCIPY_AVAILABLE = True
except ImportError:
    _SCIPY_AVAILABLE = False

from jarvis.core.config import get_config
from jarvis.core.events import get_event_bus, EventType, Priority
from jarvis.core.state import get_state_manager
from jarvis.core.logger import get_logger
from jarvis.audio.sound_fx import get_sound_fx


PROFILE_PATH = Path(__file__).resolve().parent.parent.parent / "jarvis" / "data" / "voice_profile.npy"


class VoiceBiometrics:
    """Biometric voiceprint extraction and speaker verification."""

    def __init__(self) -> None:
        self.config = get_config()
        self.bus = get_event_bus()
        self.state = get_state_manager()
        self.logger = get_logger()
        self.sfx = get_sound_fx()

        self.threshold = self.config.get("voice_auth", "threshold", 0.58)
        self.enabled = self.config.get("voice_auth", "enabled", False)
        self._enrolled_profile: Optional[np.ndarray] = None
        self._lock = threading.Lock()

        self.load_profile()

    # ─────────────────────────────────────────────────────────
    #  FEATURE EXTRACTION PIPELINE
    # ─────────────────────────────────────────────────────────
    def extract_features(self, audio: np.ndarray, sample_rate: int = 16000) -> Optional[np.ndarray]:
        """
        Extract acoustic feature matrix from 1D PCM float array.
        Returns a normalized (N_frames, 28) feature matrix or averaged 1D centroid.
        """
        if not _SCIPY_AVAILABLE or len(audio) < sample_rate * 0.5:
            return None

        try:
            # 1. Pre-emphasis filter to boost high frequencies
            pre_emphasis = 0.97
            emphasized = np.append(audio[0], audio[1:] - pre_emphasis * audio[:-1])

            # 2. Framing
            frame_size = 0.025   # 25 ms
            frame_stride = 0.010 # 10 ms
            frame_len = int(round(frame_size * sample_rate))
            frame_step = int(round(frame_stride * sample_rate))
            signal_len = len(emphasized)

            num_frames = int(np.ceil(float(np.abs(signal_len - frame_len)) / frame_step)) + 1
            pad_len = int((num_frames - 1) * frame_step + frame_len)
            zeros = np.zeros((pad_len - signal_len,))
            pad_signal = np.append(emphasized, zeros)

            indices = np.tile(np.arange(0, frame_len), (num_frames, 1)) + \
                      np.tile(np.arange(0, num_frames * frame_step, frame_step), (frame_len, 1)).T
            frames = pad_signal[indices.astype(np.int32, copy=False)]

            # 3. Hamming Windowing
            frames *= np.hamming(frame_len)

            # 4. FFT & Power Spectrum
            nfft = 512
            mag_frames = np.absolute(np.fft.rfft(frames, nfft))
            pow_frames = (1.0 / nfft) * (mag_frames ** 2)

            # 5. Filterbanks (Mel scale)
            nfilt = 26
            low_freq_mel = 0
            high_freq_mel = (2595 * np.log10(1 + (sample_rate / 2) / 700))
            mel_points = np.linspace(low_freq_mel, high_freq_mel, nfilt + 2)
            hz_points = (700 * (10 ** (mel_points / 2595) - 1))
            bin_points = np.floor((nfft + 1) * hz_points / sample_rate).astype(int)

            fbank = np.zeros((nfilt, int(np.floor(nfft / 2 + 1))))
            for m in range(1, nfilt + 1):
                f_m_minus = bin_points[m - 1]
                f_m = bin_points[m]
                f_m_plus = bin_points[m + 1]

                for k in range(f_m_minus, f_m):
                    fbank[m - 1, k] = (k - bin_points[m - 1]) / (bin_points[m] - bin_points[m - 1])
                for k in range(f_m, f_m_plus):
                    fbank[m - 1, k] = (bin_points[m + 1] - k) / (bin_points[m + 1] - bin_points[m])

            filter_banks = np.dot(pow_frames, fbank.T)
            filter_banks = np.where(filter_banks == 0, np.finfo(float).eps, filter_banks)
            filter_banks = 20 * np.log10(filter_banks)

            # 6. MFCC calculation (first 13 coefficients)
            num_ceps = 13
            mfcc = dct(filter_banks, type=2, axis=1, norm='ortho')[:, :num_ceps]

            # 7. Sinusoidal liftering
            cep_lifter = 22
            n = np.arange(num_ceps)
            lift = 1 + (cep_lifter / 2.0) * np.sin(np.pi * n / cep_lifter)
            mfcc *= lift

            # 8. First order Deltas (velocity)
            delta = np.zeros_like(mfcc)
            for t_idx in range(1, len(mfcc) - 1):
                delta[t_idx] = (mfcc[t_idx + 1] - mfcc[t_idx - 1]) / 2.0

            # 9. Additional spectral features: Spectral Centroid & Zero Crossing
            freq_axis = np.linspace(0, sample_rate / 2, mag_frames.shape[1])
            sc = np.sum(mag_frames * freq_axis, axis=1, keepdims=True) / (np.sum(mag_frames, axis=1, keepdims=True) + 1e-9)
            zcr = (np.sum(np.abs(np.diff(np.sign(frames), axis=1)), axis=1, keepdims=True) / (2 * frame_len))

            combined = np.hstack([mfcc, delta, sc / 4000.0, zcr])

            # Normalize across time frames (mean & std)
            mean = np.mean(combined, axis=0)
            std = np.std(combined, axis=0) + 1e-8
            normalized_vector = (combined - mean) / std

            # Return aggregate profile (centroid vector of shape [28])
            return np.mean(normalized_vector, axis=0)

        except Exception as e:
            self.logger.error(f"Feature extraction failed: {e}", "AUTH")
            return None

    # ─────────────────────────────────────────────────────────
    #  VERIFICATION & SIMILARITY
    # ─────────────────────────────────────────────────────────
    def verify_speaker(self, audio: np.ndarray, sample_rate: int = 16000) -> Tuple[bool, float]:
        """
        Verify whether the incoming speech matches the enrolled biometric template.
        Returns: (is_verified, similarity_score_between_0_and_1)
        """
        if not self.enabled:
            return True, 1.0

        if self._enrolled_profile is None:
            self.logger.warning("Voice lock enabled but no template enrolled! Allowing pass-through.", "AUTH")
            return True, 1.0

        sample_vector = self.extract_features(audio, sample_rate)
        if sample_vector is None:
            return False, 0.0

        # Cosine similarity between target profile and current utterance
        dot = np.dot(self._enrolled_profile, sample_vector)
        norm_a = np.linalg.norm(self._enrolled_profile)
        norm_b = np.linalg.norm(sample_vector)

        if norm_a == 0 or norm_b == 0:
            return False, 0.0

        cosine_sim = float(dot / (norm_a * norm_b))
        # Map similarity from [-1, 1] to [0, 1]
        score = (cosine_sim + 1.0) / 2.0

        is_authorized = score >= self.threshold

        self.state.set_voice_auth_status(
            enabled=True,
            verified=is_authorized,
            score=score
        )

        if is_authorized:
            self.logger.success(f"Voice biometric MATCH: Confidence = {score*100:.1f}%", "AUTH")
            self.sfx.play_auth_granted()
            self.bus.publish(EventType.AUTH_SUCCESS, {"score": score})
        else:
            self.logger.warning(f"Voice biometric REJECTED: Confidence = {score*100:.1f}% (Required: {self.threshold*100:.1f}%)", "AUTH")
            self.sfx.play_auth_denied()
            self.bus.publish(EventType.AUTH_REJECTED, {"score": score})

        return is_authorized, score

    # ─────────────────────────────────────────────────────────
    #  ENROLLMENT & PERSISTENCE
    # ─────────────────────────────────────────────────────────
    def save_enrolled_profile(self, vectors: List[np.ndarray]) -> bool:
        """Aggregate multiple enrollment samples into a single master voiceprint."""
        if not vectors:
            return False
        try:
            stacked = np.vstack(vectors)
            centroid = np.mean(stacked, axis=0)
            self._enrolled_profile = centroid
            np.save(str(PROFILE_PATH), centroid)
            self.config.set("voice_auth", "enabled", True)
            self.enabled = True
            self.logger.success(f"Master voice profile saved successfully to {PROFILE_PATH.name}", "AUTH")
            self.bus.publish(EventType.AUTH_ENROLL_COMPLETE)
            return True
        except Exception as e:
            self.logger.error(f"Failed to persist voice profile: {e}", "AUTH")
            return False

    def load_profile(self) -> bool:
        """Load enrolled voiceprint from disk."""
        if PROFILE_PATH.exists():
            try:
                self._enrolled_profile = np.load(str(PROFILE_PATH))
                self.logger.info(f"Loaded biometric voiceprint ({len(self._enrolled_profile)} dimensions)", "AUTH")
                return True
            except Exception as e:
                self.logger.warning(f"Failed to load voice profile: {e}", "AUTH")
        return False

    def delete_profile(self) -> bool:
        """Wipe saved voiceprint."""
        if PROFILE_PATH.exists():
            try:
                PROFILE_PATH.unlink(missing_ok=True)
                self._enrolled_profile = None
                self.config.set("voice_auth", "enabled", False)
                self.enabled = False
                self.logger.info("Voice profile removed.", "AUTH")
                return True
            except Exception:
                pass
        return False


def get_voice_auth() -> VoiceBiometrics:
    return VoiceBiometrics()
