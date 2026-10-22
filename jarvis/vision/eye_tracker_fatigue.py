"""
================================================================================
                    JARVIS EYE FATIGUE & BLINK MONITOR
================================================================================
User wellness and ergonomics monitor using webcam facial analysis. Tracks eye
blink rates, prolonged screen gaze duration without blinking, and enforces the
clinical 20-20-20 visual rest rule with proactive spoken notifications.
================================================================================
"""

import os
import time
import threading
import numpy as np
from typing import Optional, Tuple, Dict, Any, Callable

try:
    import cv2
    _CV2_AVAILABLE = True
except ImportError:
    _CV2_AVAILABLE = False

from jarvis.core.logger import get_logger
from jarvis.core.events import get_event_bus, EventType, Priority


class EyeFatigueMonitor:
    """Monitors blink velocity and continuous gaze duration."""

    _instance: Optional["EyeFatigueMonitor"] = None
    _lock = threading.RLock()

    def __new__(cls) -> "EyeFatigueMonitor":
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(EyeFatigueMonitor, cls).__new__(cls)
                cls._instance._init_monitor()
            return cls._instance

    def _init_monitor(self) -> None:
        self.logger = get_logger()
        self.bus = get_event_bus()

        self._eye_cascade: Optional[cv2.CascadeClassifier] = None
        self._face_cascade: Optional[cv2.CascadeClassifier] = None
        self._is_running = False
        self._thread: Optional[threading.Thread] = None

        self._blink_counter = 0
        self._last_blink_time = time.time()
        self._session_start_time = time.time()
        self._continuous_screen_time_seconds = 0.0
        self._fatigue_alert_callback: Optional[Callable[[str], None]] = None

        self._load_cascades()

    def _load_cascades(self) -> None:
        if not _CV2_AVAILABLE:
            return
        try:
            face_p = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
            eye_p = cv2.data.haarcascades + "haarcascade_eye.xml"
            if os.path.exists(face_p):
                self._face_cascade = cv2.CascadeClassifier(face_p)
            if os.path.exists(eye_p):
                self._eye_cascade = cv2.CascadeClassifier(eye_p)
        except Exception as e:
            self.logger.warning(f"Error loading eye cascades: {e}", "ERGONOMICS")

    def set_alert_callback(self, callback: Callable[[str], None]) -> None:
        self._fatigue_alert_callback = callback

    def start_monitoring(self, camera_index: int = 0) -> bool:
        if self._is_running or not _CV2_AVAILABLE or self._eye_cascade is None:
            return False

        self._is_running = True
        self._session_start_time = time.time()
        self._thread = threading.Thread(
            target=self._worker_loop,
            args=(camera_index,),
            name="JarvisEyeMonitorThread",
            daemon=True
        )
        self._thread.start()
        self.logger.info("Eye fatigue and blink rate monitor activated.", "ERGONOMICS")
        return True

    def stop_monitoring(self) -> None:
        self._is_running = False
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=1.0)

    def _worker_loop(self, camera_index: int) -> None:
        cap = cv2.VideoCapture(camera_index)
        if not cap.isOpened():
            self._is_running = False
            return

        eyes_previously_detected = True
        no_blink_warning_triggered = False

        try:
            while self._is_running:
                ret, frame = cap.read()
                if not ret:
                    time.sleep(0.1)
                    continue

                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                faces = self._face_cascade.detectMultiScale(gray, 1.2, 5, minSize=(100, 100))

                now = time.time()

                if len(faces) > 0:
                    x, y, w, h = faces[0]
                    # Eye region is typically in the upper half of the face
                    face_roi_gray = gray[y:y + int(h * 0.6), x:x + w]
                    eyes = self._eye_cascade.detectMultiScale(face_roi_gray, 1.15, 4, minSize=(25, 25))

                    eyes_currently_open = len(eyes) >= 1

                    # Transition from open -> closed -> open indicates a completed blink
                    if eyes_previously_detected and not eyes_currently_open:
                        # Eyes momentarily closed
                        pass
                    elif not eyes_previously_detected and eyes_currently_open:
                        # Eyes reopened
                        self._blink_counter += 1
                        self._last_blink_time = now
                        no_blink_warning_triggered = False

                    eyes_previously_detected = eyes_currently_open

                    # Check for dry-eye stare (no blink for > 15 seconds)
                    if (now - self._last_blink_time) > 15.0 and not no_blink_warning_triggered:
                        no_blink_warning_triggered = True
                        msg = "Sir, kaafi der se palkein nahi jhapkayi hain. Aankhon ko dry hone se bachane ke liye blink kijiye."
                        self.logger.warning(msg, "ERGONOMICS")
                        if self._fatigue_alert_callback:
                            self._fatigue_alert_callback(msg)

                    # 20-20-20 Rule: Continuous screen time exceeding 20 minutes (1200 seconds)
                    continuous_secs = now - self._session_start_time
                    if continuous_secs > 1200.0:
                        rule_msg = "Sir, 20 minute ho gaye hain screen dekhte huye. 20-20-20 rule follow kijiye — 20 feet door dekhein 20 seconds ke liye!"
                        self.logger.info(rule_msg, "ERGONOMICS")
                        if self._fatigue_alert_callback:
                            self._fatigue_alert_callback(rule_msg)
                        self._session_start_time = now # Reset interval

                time.sleep(0.1) # 10 FPS is sufficient for blink tracking
        finally:
            cap.release()

    def get_session_stats(self) -> Dict[str, Any]:
        """Return total blinks and continuous minutes elapsed."""
        now = time.time()
        elapsed_min = round((now - self._session_start_time) / 60.0, 1)
        blinks_per_min = round(self._blink_counter / max(elapsed_min, 0.1), 1)

        return {
            "total_blinks": self._blink_counter,
            "session_minutes": elapsed_min,
            "blinks_per_minute": blinks_per_min,
            "seconds_since_last_blink": round(now - self._last_blink_time, 1)
        }


def get_eye_fatigue_monitor() -> EyeFatigueMonitor:
    return EyeFatigueMonitor()
