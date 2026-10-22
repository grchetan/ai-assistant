"""
================================================================================
                    JARVIS OPTICAL GESTURE CONTROLLER
================================================================================
Computer vision hand gesture recognition system operating over webcam streams.
Uses YCrCb skin segmentation, morphological noise filtration, convex hull
topology, and convexity defect analysis to classify real-time hand gestures
(Open Palm, Closed Fist, Peace Sign, Thumbs Up) into desktop actions.
================================================================================
"""

import time
import math
import threading
import numpy as np
from typing import Optional, Tuple, Dict, Any, Callable
from enum import Enum

try:
    import cv2
    _CV2_AVAILABLE = True
except ImportError:
    _CV2_AVAILABLE = False

from jarvis.core.logger import get_logger
from jarvis.core.events import get_event_bus, EventType, Priority


class HandGesture(Enum):
    NONE        = "NONE"
    PALM_OPEN   = "PALM_OPEN"     # 4 or 5 extended fingers -> Play/Pause
    FIST_CLOSED = "FIST_CLOSED"   # 0 fingers -> Mute
    PEACE_SIGN  = "PEACE_SIGN"    # 2 fingers -> Screenshot
    THUMBS_UP   = "THUMBS_UP"     # 1 thumb upward -> Volume Up
    POINTING    = "POINTING"      # 1 finger -> Select


class GestureController:
    """Classifies user hand shapes and maps them to assistant commands."""

    def __init__(self, camera_index: int = 0) -> None:
        self.logger = get_logger()
        self.bus = get_event_bus()
        self.camera_index = camera_index
        self._is_active = False
        self._worker_thread: Optional[threading.Thread] = None
        self._gesture_callbacks: Dict[HandGesture, Callable[[], None]] = {}
        self._last_trigger_time = 0.0
        self._cooldown_seconds = 2.0 # Prevent continuous rapid triggering

    def register_action(self, gesture: HandGesture, action: Callable[[], None]) -> None:
        """Assign a callable trigger to a recognized physical hand gesture."""
        self._gesture_callbacks[gesture] = action
        self.logger.info(f"Registered gesture mapping: {gesture.value} -> {action.__name__}", "GESTURE")

    def start_monitoring(self) -> bool:
        """Launch background camera polling thread."""
        if not _CV2_AVAILABLE:
            self.logger.warning("OpenCV not available. Gesture controller cannot start.", "GESTURE")
            return False

        if self._is_active:
            return True

        self._is_active = True
        self._worker_thread = threading.Thread(
            target=self._processing_loop,
            name="JarvisGestureWorker",
            daemon=True
        )
        self._worker_thread.start()
        self.logger.success("Optical gesture monitoring active.", "GESTURE")
        return True

    def stop_monitoring(self) -> None:
        self._is_active = False
        if self._worker_thread and self._worker_thread.is_alive():
            self._worker_thread.join(timeout=1.0)
        self.logger.info("Optical gesture controller stopped.", "GESTURE")

    def _processing_loop(self) -> None:
        cap = cv2.VideoCapture(self.camera_index)
        if not cap.isOpened():
            self.logger.error("Could not initialize video capture stream for gestures.", "GESTURE")
            self._is_active = False
            return

        # Lower capture resolution for minimum CPU footprint
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 480)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 360)

        consecutive_gesture = HandGesture.NONE
        stable_count = 0

        try:
            while self._is_active:
                ret, frame = cap.read()
                if not ret:
                    time.sleep(0.05)
                    continue

                # Mirror frame for natural human interaction
                frame = cv2.flip(frame, 1)

                gesture = self.detect_gesture_from_frame(frame)

                if gesture != HandGesture.NONE:
                    if gesture == consecutive_gesture:
                        stable_count += 1
                    else:
                        consecutive_gesture = gesture
                        stable_count = 1

                    # Require 3 consecutive consistent frames to prevent false flickers
                    if stable_count >= 3:
                        now = time.time()
                        if (now - self._last_trigger_time) > self._cooldown_seconds:
                            self._trigger_gesture_action(gesture)
                            self._last_trigger_time = now
                            stable_count = 0
                else:
                    consecutive_gesture = HandGesture.NONE
                    stable_count = 0

                time.sleep(0.04) # ~25 FPS
        finally:
            cap.release()

    def detect_gesture_from_frame(self, frame_bgr: np.ndarray) -> HandGesture:
        """
        Segment skin mask and analyze contour geometric properties.
        """
        if frame_bgr is None or frame_bgr.size == 0:
            return HandGesture.NONE

        try:
            # 1. Convert to YCrCb color space (robust against ambient illumination shifts)
            ycrcb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2YCrCb)

            # Human skin color boundaries in YCrCb space
            lower_skin = np.array([0, 133, 77], dtype=np.uint8)
            upper_skin = np.array([255, 173, 127], dtype=np.uint8)
            mask = cv2.inRange(ycrcb, lower_skin, upper_skin)

            # 2. Morphological closing to fill holes inside the palm
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
            mask = cv2.dilate(mask, kernel, iterations=2)
            mask = cv2.GaussianBlur(mask, (5, 5), 100)

            # 3. Locate external contours
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            if not contours:
                return HandGesture.NONE

            # Find the largest skin region
            hand_contour = max(contours, key=cv2.contourArea)
            area = cv2.contourArea(hand_contour)

            # Reject small noise regions
            if area < 5000:
                return HandGesture.NONE

            # 4. Convex Hull & Convexity Defects Analysis
            hull = cv2.convexHull(hand_contour, returnPoints=False)
            if len(hull) < 4:
                return HandGesture.NONE

            defects = cv2.convexityDefects(hand_contour, hull)
            if defects is None:
                return HandGesture.NONE

            finger_count = 0
            for i in range(defects.shape[0]):
                s, e, f, d = defects[i, 0]
                start = tuple(hand_contour[s][0])
                end = tuple(hand_contour[e][0])
                far = tuple(hand_contour[f][0])

                # Calculate triangle edges
                a = math.sqrt((end[0] - start[0])**2 + (end[1] - start[1])**2)
                b = math.sqrt((far[0] - start[0])**2 + (far[1] - start[1])**2)
                c = math.sqrt((end[0] - far[0])**2 + (end[1] - far[1])**2)

                # Cosine rule for angle
                if b * c > 0:
                    angle = math.acos((b**2 + c**2 - a**2) / (2 * b * c)) * 57.29
                    # A sharp angle (< 90 degrees) indicates spacing between open fingers
                    if angle <= 90 and d > 12000: # Distance threshold to eliminate skin creases
                        finger_count += 1

            # 5. Map defect count to recognizable gestures
            if finger_count >= 4:
                return HandGesture.PALM_OPEN
            elif finger_count == 2:
                return HandGesture.PEACE_SIGN
            elif finger_count == 1:
                return HandGesture.THUMBS_UP
            elif finger_count == 0:
                # Differentiate between closed fist and flat arm using solidity
                hull_points = cv2.convexHull(hand_contour)
                hull_area = cv2.contourArea(hull_points)
                if hull_area > 0:
                    solidity = float(area) / hull_area
                    if solidity > 0.85:
                        return HandGesture.FIST_CLOSED

            return HandGesture.NONE

        except Exception as e:
            self.logger.debug(f"Error in gesture classification: {e}", "GESTURE")
            return HandGesture.NONE

    def _trigger_gesture_action(self, gesture: HandGesture) -> None:
        self.logger.info(f"Gesture detected: {gesture.value}", "GESTURE", "#ff00ff")
        handler = self._gesture_callbacks.get(gesture)
        if handler:
            try:
                handler()
            except Exception as e:
                self.logger.error(f"Error executing gesture handler for {gesture.value}: {e}", "GESTURE")


def get_gesture_controller() -> GestureController:
    return GestureController()
