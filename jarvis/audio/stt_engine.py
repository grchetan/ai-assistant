"""
================================================================================
                    JARVIS INTELLIGENT STT ENGINE
================================================================================
Multi-language speech recognizer (Hinglish, Hindi, English) with intelligent
ambient noise separation, zero-complaint silence detection, phrase biasing,
and decoupled error handling.
================================================================================
"""

import time
import random
import threading
from typing import Optional, List, Tuple

try:
    import speech_recognition as sr
    _SR_AVAILABLE = True
except ImportError:
    _SR_AVAILABLE = False

from jarvis.core.config import get_config
from jarvis.core.events import get_event_bus, EventType, Priority
from jarvis.core.state import get_state_manager, AssistantMode
from jarvis.core.logger import get_logger

# Responses for true unclear speech (after threshold is reached)
UNCLEAR_VARIED_RESPONSES = [
    "Thoda clearly bolo please, samajh nahi aaya.",
    "Sir, aawaz thodi cut rahi thi, ek baar aur boliye?",
    "Bhai, mic thoda door lag raha hai. Kya bola aapne?",
    "Sir, shor ki wajah se clear nahi suna. Phir se batayein?",
    "Aawaz dab gayi sir, please dobara bolein.",
    "Pardon sir? Ek baar aur repeat karenge?"
]


class SpeechToTextEngine:
    """Robust multi-engine Speech-To-Text pipeline with silence tolerance."""

    def __init__(self) -> None:
        self.config = get_config()
        self.bus = get_event_bus()
        self.state = get_state_manager()
        self.logger = get_logger()

        self._recognizer: Optional[sr.Recognizer] = None
        self._microphone: Optional[sr.Microphone] = None
        self._lock = threading.Lock()
        self._init_engine()

    def _init_engine(self) -> None:
        if not _SR_AVAILABLE:
            self.logger.warning("speech_recognition library not available.", "STT")
            return

        self._recognizer = sr.Recognizer()
        self._recognizer.energy_threshold = self.config.get("audio", "energy_threshold", 300)
        self._recognizer.dynamic_energy_threshold = True
        self._recognizer.dynamic_energy_adjustment_damping = 0.15
        self._recognizer.dynamic_energy_ratio = 1.5
        self._recognizer.pause_threshold = self.config.get("audio", "pause_threshold", 0.8)
        self._recognizer.non_speaking_duration = 0.5

        try:
            device_index = self.config.get("audio", "input_device_index", None)
            self._microphone = sr.Microphone(device_index=device_index)
            self.logger.info("STT Engine initialized successfully with PyAudio microphone.", "STT")
        except Exception as e:
            self.logger.error(f"Failed to bind microphone for STT: {e}", "STT")

    def calibrate(self, duration: float = 1.0) -> None:
        """Calibrate recognizer with ambient noise level."""
        if not self._recognizer or not self._microphone:
            return
        try:
            self.logger.info(f"Calibrating mic ambient noise ({duration}s)...", "STT")
            with self._microphone as source:
                self._recognizer.adjust_for_ambient_noise(source, duration=duration)
            self.logger.success(f"Dynamic energy threshold calibrated to: {self._recognizer.energy_threshold:.1f}", "STT")
        except Exception as e:
            self.logger.warning(f"Microphone ambient calibration failed: {e}", "STT")

    def listen_and_transcribe(
        self,
        timeout: float = 4.0,
        phrase_limit: float = 12.0
    ) -> Tuple[Optional[str], Optional[sr.AudioData]]:
        """
        Listen for a phrase and transcribe.
        Returns: (transcribed_text, audio_data)
        If user remains silent: returns (None, None) silently WITHOUT complaints.
        """
        if not self._recognizer or not self._microphone:
            time.sleep(1.0)
            return None, None

        self.state.set_mode(AssistantMode.LISTENING)
        self.bus.publish(EventType.STT_LISTENING)

        audio_data: Optional[sr.AudioData] = None

        try:
            with self._microphone as source:
                # Capture audio
                audio_data = self._recognizer.listen(
                    source,
                    timeout=timeout,
                    phrase_time_limit=phrase_limit
                )
        except sr.WaitTimeoutError:
            # PURE SILENCE — user didn't speak. Do NOT complain!
            silence_count = self.state.record_silence()
            self.bus.publish(EventType.STT_TIMEOUT, {"silence_count": silence_count})
            self.state.set_mode(AssistantMode.IDLE)
            return None, None
        except Exception as e:
            self.logger.debug(f"Audio capture error: {e}", "STT")
            self.state.set_mode(AssistantMode.IDLE)
            return None, None

        # Speech captured, now transcribe
        self.state.set_mode(AssistantMode.PROCESSING)
        self.bus.publish(EventType.STT_PROCESSING)

        primary_lang = self.config.get("stt", "primary_language", "en-IN")
        secondary_lang = self.config.get("stt", "secondary_language", "hi-IN")

        text: Optional[str] = None

        # 1. Try primary language (en-IN)
        try:
            text = self._recognizer.recognize_google(audio_data, language=primary_lang)
        except sr.UnknownValueError:
            # 2. Try secondary language (hi-IN)
            try:
                text = self._recognizer.recognize_google(audio_data, language=secondary_lang)
            except (sr.UnknownValueError, sr.RequestError):
                pass
        except sr.RequestError as e:
            self.logger.error(f"Google STT service network error: {e}", "STT")
            self.bus.publish(EventType.STT_ERROR, {"error": str(e)})

        if text and text.strip():
            clean_text = self._normalize_text(text)
            self.logger.info(f'Transcribed: "{clean_text}"', "STT", color="#00ffcc")
            self.state.mark_user_spoke()
            self.bus.publish(EventType.STT_RESULT, {"text": clean_text})
            return clean_text, audio_data
        else:
            # Actual unclear audio (sound present, but undecipherable)
            unclear_count = self.state.record_unclear()
            self.bus.publish(EventType.STT_UNCLEAR, {"unclear_count": unclear_count})
            self.logger.debug(f"Audio detected but unintelligible (count={unclear_count})", "STT")
            self.state.set_mode(AssistantMode.IDLE)
            return None, audio_data

    def get_unclear_response(self) -> Optional[str]:
        """
        Only return a varied complaint if unclear threshold (>= 4) is crossed.
        Prevents annoying repetitive complaints.
        """
        snapshot = self.state.get_telemetry_snapshot()
        unclear_cnt = snapshot.get("unclear_count", 0)
        if unclear_cnt >= 4:
            self.state.reset_speech_counters()
            return random.choice(UNCLEAR_VARIED_RESPONSES)
        return None

    def _normalize_text(self, raw_text: str) -> str:
        """Clean and normalize transcribed text for intent processing."""
        text = raw_text.strip()
        # Common STT mistranscriptions in Hinglish
        corrections = {
            "service": "jarvis",
            "service ':": "jarvis",
            "travice": "jarvis",
            "jawis": "jarvis",
            "jarvis ": "jarvis ",
            "bataiye": "batao",
            "kijiye": "karo",
        }
        low = text.lower()
        for mistake, correct in corrections.items():
            if mistake in low:
                low = low.replace(mistake, correct)
        return low


def get_stt_engine() -> SpeechToTextEngine:
    return SpeechToTextEngine()
