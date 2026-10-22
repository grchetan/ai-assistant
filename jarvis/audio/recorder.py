"""
================================================================================
                    JARVIS LOW-LATENCY AUDIO RECORDER
================================================================================
Real-time streaming microphone capture engine using SoundDevice / PyAudio with
dynamic noise floor calibration, Voice Activity Detection (VAD), and live RMS
telemetry feeding the Arc Reactor UI HUD.
================================================================================
"""

import time
import math
import threading
import numpy as np
from typing import Optional, Callable, Tuple, List

try:
    import sounddevice as sd
    _SD_AVAILABLE = True
except ImportError:
    _SD_AVAILABLE = False

try:
    import speech_recognition as sr
    _SR_AVAILABLE = True
except ImportError:
    _SR_AVAILABLE = False

from jarvis.core.config import get_config
from jarvis.core.events import get_event_bus, EventType, Priority
from jarvis.core.state import get_state_manager
from jarvis.core.logger import get_logger


class AudioRecorder:
    """High-performance audio capturer with real-time signal metering."""

    def __init__(self) -> None:
        self.config = get_config()
        self.bus = get_event_bus()
        self.state = get_state_manager()
        self.logger = get_logger()

        self.sample_rate: int = self.config.get("audio", "sample_rate", 16000)
        self.channels: int = self.config.get("audio", "channels", 1)
        self.chunk_size: int = self.config.get("audio", "chunk_size", 1024)

        self._stream: Optional[sd.InputStream] = None
        self._is_recording = False
        self._frames: List[np.ndarray] = []
        self._lock = threading.Lock()

        # Calibration & VAD metrics
        self._ambient_rms = 50.0
        self._energy_threshold = self.config.get("audio", "energy_threshold", 300)
        self._is_calibrated = False

        # Live RMS listener
        self._rms_listeners: List[Callable[[float, bool], None]] = []

    def calibrate_ambient_noise(self, duration: float = 1.0) -> float:
        """Measure ambient silence to establish dynamic speech thresholds."""
        self.logger.info("Calibrating microphone ambient noise floor...", "AUDIO")
        if not _SD_AVAILABLE:
            self._is_calibrated = True
            return self._energy_threshold

        try:
            samples = int(self.sample_rate * duration)
            recording = sd.rec(
                samples,
                samplerate=self.sample_rate,
                channels=self.channels,
                dtype="float32",
                blocking=True
            )
            rms = float(np.sqrt(np.mean(np.square(recording))) * 32767.0)
            self._ambient_rms = max(rms, 15.0)
            self._energy_threshold = max(self._ambient_rms * 2.8, 250.0)
            self._is_calibrated = True
            self.logger.success(
                f"Mic calibrated. Ambient: {self._ambient_rms:.1f} RMS | Gate: {self._energy_threshold:.1f}",
                "AUDIO"
            )
            return self._energy_threshold
        except Exception as e:
            self.logger.warning(f"Calibration failed, using default threshold: {e}", "AUDIO")
            self._is_calibrated = True
            return self._energy_threshold

    def start_monitoring_stream(self) -> None:
        """Start a background stream to continuously feed RMS to the HUD canvas."""
        if not _SD_AVAILABLE or self._stream is not None:
            return

        def _audio_callback(indata, frames, time_info, status):
            if status:
                pass
            # Calculate instantaneous RMS
            mono = indata[:, 0] if indata.ndim > 1 else indata
            rms = float(np.sqrt(np.mean(np.square(mono))) * 32767.0)
            is_speech = rms > self._energy_threshold

            self.state.update_rms(rms, is_speech)
            for listener in self._rms_listeners:
                try:
                    listener(rms, is_speech)
                except Exception:
                    pass

        try:
            self._stream = sd.InputStream(
                samplerate=self.sample_rate,
                channels=self.channels,
                blocksize=self.chunk_size,
                dtype="float32",
                callback=_audio_callback
            )
            self._stream.start()
        except Exception as e:
            self.logger.warning(f"Could not open live monitoring stream: {e}", "AUDIO")

    def stop_monitoring_stream(self) -> None:
        if self._stream is not None:
            try:
                self._stream.stop()
                self._stream.close()
            except Exception:
                pass
            self._stream = None

    def add_rms_listener(self, callback: Callable[[float, bool], None]) -> None:
        if callback not in self._rms_listeners:
            self._rms_listeners.append(callback)

    def record_seconds(self, duration: float) -> Tuple[np.ndarray, int]:
        """Synchronously record audio for an exact duration (useful for voice enroll)."""
        if not _SD_AVAILABLE:
            raise RuntimeError("SoundDevice is not available.")

        samples = int(self.sample_rate * duration)
        recording = sd.rec(
            samples,
            samplerate=self.sample_rate,
            channels=self.channels,
            dtype="float32",
            blocking=True
        )
        # Flatten to 1D array
        return recording.flatten(), self.sample_rate

    def record_until_silence(
        self,
        max_duration: float = 12.0,
        silence_timeout: float = 1.2
    ) -> Optional[np.ndarray]:
        """VAD-driven recorder: records until user stops speaking."""
        if not _SD_AVAILABLE:
            return None

        chunk = 1024
        collected_chunks: List[np.ndarray] = []
        speech_started = False
        silence_frames = 0
        silence_limit = int((self.sample_rate / chunk) * silence_timeout)
        max_frames = int((self.sample_rate / chunk) * max_duration)
        frame_count = 0

        try:
            with sd.InputStream(samplerate=self.sample_rate, channels=1, dtype="float32", blocksize=chunk) as stream:
                while frame_count < max_frames:
                    data, _ = stream.read(chunk)
                    data_flat = data.flatten()
                    collected_chunks.append(data_flat)
                    frame_count += 1

                    rms = float(np.sqrt(np.mean(np.square(data_flat))) * 32767.0)
                    is_speech = rms > self._energy_threshold
                    self.state.update_rms(rms, is_speech)

                    if is_speech:
                        speech_started = True
                        silence_frames = 0
                    elif speech_started:
                        silence_frames += 1
                        if silence_frames >= silence_limit:
                            break

                if not speech_started or len(collected_chunks) == 0:
                    return None

                return np.concatenate(collected_chunks)
        except Exception as e:
            self.logger.error(f"Error recording audio: {e}", "AUDIO")
            return None


def get_audio_recorder() -> AudioRecorder:
    return AudioRecorder()
