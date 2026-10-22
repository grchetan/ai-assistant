"""
================================================================================
                    JARVIS SCREEN VIDEO RECORDER
================================================================================
Captures dynamic desktop screen video sequences using PIL ImageGrab and OpenCV
VideoWriter for bug reproduction, demonstrations, and active session capture.
================================================================================
"""

import time
import threading
import numpy as np
from typing import Optional, Tuple
from pathlib import Path

try:
    import cv2
    _CV2_AVAILABLE = True
except ImportError:
    _CV2_AVAILABLE = False

try:
    from PIL import ImageGrab
    _PIL_AVAILABLE = True
except ImportError:
    _PIL_AVAILABLE = False

from jarvis.core.logger import get_logger

RECORDINGS_DIR = Path(__file__).resolve().parent.parent.parent / "jarvis" / "data" / "recordings"
RECORDINGS_DIR.mkdir(parents=True, exist_ok=True)


class ScreenRecorder:
    """Records desktop video into MP4 format."""

    def __init__(self) -> None:
        self.logger = get_logger()
        self._is_recording = False
        self._thread: Optional[threading.Thread] = None
        self._output_file: Optional[Path] = None

    def start_recording(self, duration_seconds: int = 10, fps: int = 15) -> Tuple[bool, str, Optional[Path]]:
        """Capture screen video for fixed duration."""
        if not _CV2_AVAILABLE or not _PIL_AVAILABLE:
            return False, "OpenCV and PIL are required for screen recording.", None

        if self._is_recording:
            return False, "Recording is already active.", None

        filename = f"recording_{int(time.time())}.avi"
        self._output_file = RECORDINGS_DIR / filename
        self._is_recording = True

        def _record_worker():
            self.logger.info(f"Screen video recording started ({duration_seconds}s)...", "RECORDER")
            screen = ImageGrab.grab()
            width, height = screen.size
            fourcc = cv2.VideoWriter_fourcc(*'XVID')
            out = cv2.VideoWriter(str(self._output_file), fourcc, fps, (width, height))

            start_t = time.time()
            frame_delay = 1.0 / fps

            while self._is_recording and (time.time() - start_t) < duration_seconds:
                t0 = time.time()
                img = ImageGrab.grab()
                frame = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
                out.write(frame)
                dt = time.time() - t0
                if dt < frame_delay:
                    time.sleep(frame_delay - dt)

            out.release()
            self._is_recording = False
            self.logger.success(f"Video saved to: {self._output_file.name}", "RECORDER")

        self._thread = threading.Thread(target=_record_worker, daemon=True)
        self._thread.start()

        return True, f"Screen recording started for {duration_seconds} seconds.", self._output_file

    def stop_recording(self) -> None:
        self._is_recording = False
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=2.0)


def get_screen_recorder() -> ScreenRecorder:
    return ScreenRecorder()
