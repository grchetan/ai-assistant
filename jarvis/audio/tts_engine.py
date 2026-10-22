"""
================================================================================
                    JARVIS DUAL-ENGINE NEURAL TTS PIPELINE
================================================================================
Next-generation Text-To-Speech architecture combining:
  1. Microsoft Edge-TTS Neural Voices (Ultra-realistic, natural human intonation)
  2. Windows SAPI5 / PyTTSx3 (Instant zero-latency offline fallback)
Features non-blocking queued playback, instant interruption, and sentence pipelining.
================================================================================
"""

import os
import sys
import time
import queue
import asyncio
import threading
import tempfile
from typing import Optional, Callable
from pathlib import Path

try:
    import edge_tts
    _EDGE_TTS_AVAILABLE = True
except ImportError:
    _EDGE_TTS_AVAILABLE = False

try:
    import pygame
    _PYGAME_AVAILABLE = True
except ImportError:
    _PYGAME_AVAILABLE = False

try:
    import pyttsx3
    _PYTTSX3_AVAILABLE = True
except ImportError:
    _PYTTSX3_AVAILABLE = False

from jarvis.core.config import get_config
from jarvis.core.events import get_event_bus, EventType, Priority
from jarvis.core.state import get_state_manager, AssistantMode
from jarvis.core.logger import get_logger


class TextToSpeechEngine:
    """Threaded high-fidelity TTS synthesizer with queue management."""

    _instance: Optional["TextToSpeechEngine"] = None
    _lock = threading.RLock()

    def __new__(cls) -> "TextToSpeechEngine":
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(TextToSpeechEngine, cls).__new__(cls)
                cls._instance._init_system()
            return cls._instance

    def _init_system(self) -> None:
        self.config = get_config()
        self.bus = get_event_bus()
        self.state = get_state_manager()
        self.logger = get_logger()

        self._speech_queue: queue.Queue = queue.Queue(maxsize=20)
        self._is_speaking = False
        self._interrupt_flag = threading.Event()
        self._worker_running = True

        # PyTTSx3 fallback engine
        self._pyttsx3_engine: Optional[pyttsx3.Engine] = None
        self._init_pyttsx3()

        # Temporary audio cache dir
        self._temp_dir = Path(tempfile.gettempdir()) / "jarvis_tts_cache"
        self._temp_dir.mkdir(parents=True, exist_ok=True)

        # Start playback worker thread
        self._worker_thread = threading.Thread(
            target=self._speech_worker,
            name="JarvisTTSWorker",
            daemon=True
        )
        self._worker_thread.start()

    def _init_pyttsx3(self) -> None:
        if not _PYTTSX3_AVAILABLE:
            return
        try:
            self._pyttsx3_engine = pyttsx3.init()
            rate = self.config.get("tts", "pyttsx3_rate", 185)
            volume = self.config.get("tts", "pyttsx3_volume", 1.0)
            self._pyttsx3_engine.setProperty("rate", rate)
            self._pyttsx3_engine.setProperty("volume", volume)
        except Exception as e:
            self.logger.warning(f"Could not initialize pyttsx3: {e}", "TTS")

    def _speech_worker(self) -> None:
        """Background thread dequeuing and rendering speech requests."""
        while self._worker_running:
            try:
                item = self._speech_queue.get(timeout=0.1)
                if item is None:
                    break
                text, voice, callback = item
                self._render_and_play(text, voice, callback)
                self._speech_queue.task_done()
            except queue.Empty:
                continue
            except Exception as e:
                self.logger.error(f"Error in TTS worker: {e}", "TTS")

    def speak(
        self,
        text: str,
        voice: Optional[str] = None,
        block: bool = False,
        callback: Optional[Callable[[], None]] = None
    ) -> None:
        """Enqueue speech request."""
        clean_text = text.strip()
        if not clean_text:
            return

        if block:
            self._render_and_play(clean_text, voice, callback)
        else:
            try:
                self._speech_queue.put((clean_text, voice, callback), timeout=1.0)
            except queue.Full:
                self.logger.warning("TTS queue full; dropping item.", "TTS")

    def stop(self) -> None:
        """Interrupt and clear currently queued audio."""
        self._interrupt_flag.set()
        # Empty queue
        while not self._speech_queue.empty():
            try:
                self._speech_queue.get_nowait()
                self._speech_queue.task_done()
            except queue.Empty:
                break

        if _PYGAME_AVAILABLE and pygame.mixer.get_init():
            try:
                pygame.mixer.music.stop()
            except Exception:
                pass

        if self._pyttsx3_engine:
            try:
                self._pyttsx3_engine.stop()
            except Exception:
                pass

        self.state.set_mode(AssistantMode.IDLE)
        self.bus.publish(EventType.TTS_INTERRUPT)
        self.logger.info("Speech playback interrupted.", "TTS")

    def _render_and_play(
        self,
        text: str,
        custom_voice: Optional[str] = None,
        callback: Optional[Callable[[], None]] = None
    ) -> None:
        self._interrupt_flag.clear()
        self._is_speaking = True
        self.state.set_mode(AssistantMode.SPEAKING)
        self.bus.publish(EventType.TTS_START, {"text": text})

        preferred_engine = self.config.get("tts", "engine", "edge_tts")
        voice = custom_voice or self.config.get("tts", "edge_voice", "hi-IN-MadhurNeural")

        played_successfully = False

        # Attempt 1: Edge-TTS
        if preferred_engine == "edge_tts" and _EDGE_TTS_AVAILABLE and _PYGAME_AVAILABLE:
            played_successfully = self._speak_with_edge_tts(text, voice)

        # Attempt 2: PyTTSx3 Fallback
        if not played_successfully and self._pyttsx3_engine:
            played_successfully = self._speak_with_pyttsx3(text)

        self._is_speaking = False
        self.state.mark_assistant_spoke()
        self.state.set_mode(AssistantMode.IDLE)
        self.bus.publish(EventType.TTS_FINISH, {"text": text})

        if callback and callable(callback):
            try:
                callback()
            except Exception as e:
                self.logger.warning(f"Error in TTS callback: {e}", "TTS")

    def _speak_with_edge_tts(self, text: str, voice: str) -> bool:
        """Generate audio using Edge-TTS and stream via Pygame Mixer."""
        cache_file = self._temp_dir / f"tts_{int(time.time()*1000)}.mp3"
        try:
            rate = self.config.get("tts", "rate", "+0%")
            pitch = self.config.get("tts", "pitch", "+0Hz")
            volume = self.config.get("tts", "volume", "+0%")

            async def _generate():
                communicate = edge_tts.Communicate(text, voice, rate=rate, pitch=pitch, volume=volume)
                await communicate.save(str(cache_file))

            # Run event loop for Edge-TTS
            asyncio.run(_generate())

            if not cache_file.exists() or cache_file.stat().st_size == 0:
                return False

            # Play using pygame
            if not pygame.mixer.get_init():
                pygame.mixer.init()

            pygame.mixer.music.load(str(cache_file))
            pygame.mixer.music.play()

            while pygame.mixer.music.get_busy():
                if self._interrupt_flag.is_set():
                    pygame.mixer.music.stop()
                    break
                time.sleep(0.05)

            # Cleanup
            try:
                pygame.mixer.music.unload()
                if cache_file.exists():
                    cache_file.unlink(missing_ok=True)
            except Exception:
                pass

            return True

        except Exception as e:
            self.logger.warning(f"Edge-TTS failed ({e}); falling back to SAPI5.", "TTS")
            if cache_file.exists():
                try:
                    cache_file.unlink(missing_ok=True)
                except Exception:
                    pass
            return False

    def _speak_with_pyttsx3(self, text: str) -> bool:
        """Offline fallback speech via SAPI5."""
        try:
            if self._pyttsx3_engine:
                self._pyttsx3_engine.say(text)
                self._pyttsx3_engine.runAndWait()
                return True
        except Exception as e:
            self.logger.error(f"PyTTSx3 synthesis error: {e}", "TTS")
        return False

    def is_busy(self) -> bool:
        return self._is_speaking or not self._speech_queue.empty()

    def shutdown(self) -> None:
        self._worker_running = False
        self.stop()
        if self._worker_thread.is_alive():
            self._worker_thread.join(timeout=1.0)


def get_tts_engine() -> TextToSpeechEngine:
    return TextToSpeechEngine()
