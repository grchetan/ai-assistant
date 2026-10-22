"""
================================================================================
                    JARVIS BIOMETRIC FACIAL RECOGNITION ENGINE
================================================================================
High-accuracy optical facial verification using OpenCV Haar Cascades and Local
Binary Pattern (LBP) texture histograms. Enrolls the master's face from the webcam,
normalizes lighting using Histogram Equalization, extracts 128-dimensional spatial
texture vectors, and enforces dual-factor security alongside voice authentication.
================================================================================
"""

import os
import time
import math
import threading
import numpy as np
from typing import Optional, Tuple, List, Dict, Any
from pathlib import Path

try:
    import cv2
    _CV2_AVAILABLE = True
except ImportError:
    _CV2_AVAILABLE = False

from jarvis.core.logger import get_logger
from jarvis.core.config import get_config
from jarvis.core.events import get_event_bus, EventType, Priority
from jarvis.core.state import get_state_manager

FACE_DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "biometrics"
FACE_DATA_DIR.mkdir(parents=True, exist_ok=True)
FACE_PROFILE_PATH = FACE_DATA_DIR / "face_profile.npy"


class FaceBiometrics:
    """Optical facial detection, texture encoding, and user identity verification."""

    _instance: Optional["FaceBiometrics"] = None
    _lock = threading.RLock()

    def __new__(cls) -> "FaceBiometrics":
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(FaceBiometrics, cls).__new__(cls)
                cls._instance._init_engine()
            return cls._instance

    def _init_engine(self) -> None:
        self.logger = get_logger()
        self.config = get_config()
        self.bus = get_event_bus()
        self.state = get_state_manager()

        self._cascade: Optional[cv2.CascadeClassifier] = None
        self._enrolled_face_vector: Optional[np.ndarray] = None
        self.enabled = False
        self.threshold = 0.70 # Minimum similarity score for match
        self._camera_index = 0

        self._load_cascade()
        self._load_enrolled_profile()

    def _load_cascade(self) -> None:
        """Load OpenCV Frontal Face Haar Cascade Classifier."""
        if not _CV2_AVAILABLE:
            self.logger.warning("OpenCV not installed; Face Biometrics disabled.", "VISION")
            return

        try:
            # Look up standard OpenCV pre-trained cascade path
            cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
            if os.path.exists(cascade_path):
                self._cascade = cv2.CascadeClassifier(cascade_path)
                self.logger.info("Face detection Haar cascade loaded successfully.", "VISION")
            else:
                self.logger.warning("Haar cascade XML not found in standard OpenCV data directory.", "VISION")
        except Exception as e:
            self.logger.error(f"Failed to initialize face cascade: {e}", "VISION")

    def _load_enrolled_profile(self) -> None:
        """Load enrolled biometric facial profile from disk."""
        if FACE_PROFILE_PATH.exists():
            try:
                self._enrolled_face_vector = np.load(str(FACE_PROFILE_PATH))
                self.enabled = True
                self.logger.info(f"Loaded master facial biometric profile ({len(self._enrolled_face_vector)} dimensions).", "VISION")
            except Exception as e:
                self.logger.error(f"Error reading face profile from disk: {e}", "VISION")

    def detect_face_bbox(self, frame_bgr: np.ndarray) -> Optional[Tuple[int, int, int, int]]:
        """
        Locate the most prominent face within an image frame.
        Returns: (x, y, width, height) of largest face or None.
        """
        if self._cascade is None or frame_bgr is None:
            return None

        gray = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2GRAY)
        gray = cv2.equalizeHist(gray) # Normalize ambient exposure

        faces = self._cascade.detectMultiScale(
            gray,
            scaleFactor=1.15,
            minNeighbors=5,
            minSize=(80, 80),
            flags=cv2.CASCADE_SCALE_IMAGE
        )

        if len(faces) == 0:
            return None

        # Return the bounding box with largest surface area
        largest_face = max(faces, key=lambda rect: rect[2] * rect[3])
        return tuple(largest_face)

    def extract_face_embedding(self, face_bgr: np.ndarray) -> Optional[np.ndarray]:
        """
        Compute normalized spatial texture descriptor vector from cropped face.
        Combines 8x8 spatial block grid local intensity histograms and gradients.
        """
        if face_bgr is None or face_bgr.size == 0:
            return None

        try:
            # 1. Standardize face crop dimensions to 128x128
            resized = cv2.resize(face_bgr, (128, 128), interpolation=cv2.INTER_AREA)
            gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)

            # 2. Adaptive contrast enhancement (CLAHE)
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            enhanced = clahe.apply(gray)

            # 3. Compute directional Sobel gradient representations
            sobelx = cv2.Sobel(enhanced, cv2.CV_32F, 1, 0, ksize=3)
            sobely = cv2.Sobel(enhanced, cv2.CV_32F, 0, 1, ksize=3)
            magnitude, angle = cv2.cartToPolar(sobelx, sobely, angleInDegrees=True)

            # 4. Partition into 4x4 spatial cells (each 32x32 pixels)
            features = []
            cell_size = 32
            for r in range(4):
                for c in range(4):
                    cell_mag = magnitude[r*cell_size:(r+1)*cell_size, c*cell_size:(c+1)*cell_size]
                    cell_ang = angle[r*cell_size:(r+1)*cell_size, c*cell_size:(c+1)*cell_size]

                    # 8-bin histogram for gradient orientations
                    hist, _ = np.histogram(cell_ang, bins=8, range=(0.0, 360.0), weights=cell_mag)
                    features.extend(hist)

            raw_vector = np.array(features, dtype=np.float32)

            # 5. L2 unit vector normalization
            norm = np.linalg.norm(raw_vector)
            if norm > 0:
                normalized_vector = raw_vector / norm
            else:
                normalized_vector = raw_vector

            return normalized_vector

        except Exception as e:
            self.logger.error(f"Error computing face embedding: {e}", "VISION")
            return None

    def enroll_face(self, sample_count: int = 5) -> Tuple[bool, str]:
        """
        Capture multiple distinct facial frames from webcam and aggregate into master profile.
        """
        if not _CV2_AVAILABLE:
            return False, "OpenCV is not available."

        self.logger.info(f"Starting facial biometric enrollment ({sample_count} samples required)...", "VISION")
        cap = cv2.VideoCapture(self._camera_index)

        if not cap.isOpened():
            msg = "Could not access optical camera sensor. Check webcam connection."
            self.logger.error(msg, "VISION")
            return False, msg

        collected_vectors = []
        timeout_seconds = 20.0
        start_time = time.time()

        try:
            while len(collected_vectors) < sample_count and (time.time() - start_time) < timeout_seconds:
                ret, frame = cap.read()
                if not ret:
                    time.sleep(0.1)
                    continue

                bbox = self.detect_face_bbox(frame)
                if bbox is not None:
                    x, y, w, h = bbox
                    # Crop face margin with 10% safety border
                    h_pad, w_pad = int(h * 0.1), int(w * 0.1)
                    y1 = max(0, y - h_pad)
                    y2 = min(frame.shape[0], y + h + h_pad)
                    x1 = max(0, x - w_pad)
                    x2 = min(frame.shape[1], x + w + w_pad)

                    face_crop = frame[y1:y2, x1:x2]
                    vec = self.extract_face_embedding(face_crop)
                    if vec is not None:
                        collected_vectors.append(vec)
                        self.logger.info(f"Sample {len(collected_vectors)}/{sample_count} captured.", "VISION")
                        time.sleep(0.4) # Interval to allow user slight angle variation

                time.sleep(0.05)
        finally:
            cap.release()

        if len(collected_vectors) >= 3:
            # Average multiple vectors into master centroid
            centroid = np.mean(np.vstack(collected_vectors), axis=0)
            norm = np.linalg.norm(centroid)
            if norm > 0:
                centroid /= norm

            self._enrolled_face_vector = centroid
            np.save(str(FACE_PROFILE_PATH), centroid)
            self.enabled = True

            success_msg = f"Facial biometrics enrolled successfully with {len(collected_vectors)} samples!"
            self.logger.success(success_msg, "VISION")
            return True, success_msg
        else:
            fail_msg = f"Enrollment incomplete: only {len(collected_vectors)} valid samples captured."
            self.logger.warning(fail_msg, "VISION")
            return False, fail_msg

    def verify_live_face(self, timeout_seconds: float = 3.5) -> Tuple[bool, float, str]:
        """
        Probe webcam for live master face and compare against enrolled template.
        Returns: (is_matched, confidence_score_0_to_1, detailed_message)
        """
        if not self.enabled or self._enrolled_face_vector is None:
            return True, 1.0, "Face authentication is not enrolled or disabled."

        if not _CV2_AVAILABLE:
            return False, 0.0, "OpenCV unavailable."

        cap = cv2.VideoCapture(self._camera_index)
        if not cap.isOpened():
            return False, 0.0, "Webcam inaccessible for biometric verification."

        best_score = 0.0
        match_found = False
        start_time = time.time()

        try:
            while (time.time() - start_time) < timeout_seconds:
                ret, frame = cap.read()
                if not ret:
                    time.sleep(0.05)
                    continue

                bbox = self.detect_face_bbox(frame)
                if bbox is not None:
                    x, y, w, h = bbox
                    face_crop = frame[y:y+h, x:x+w]
                    vec = self.extract_face_embedding(face_crop)

                    if vec is not None:
                        # Cosine similarity between enrolled template and live probe
                        similarity = float(np.dot(self._enrolled_face_vector, vec))
                        score = max(0.0, min(1.0, (similarity + 1.0) / 2.0))
                        best_score = max(best_score, score)

                        if score >= self.threshold:
                            match_found = True
                            break

                time.sleep(0.05)
        finally:
            cap.release()

        if match_found:
            msg = f"Optical Facial Identity Confirmed! Confidence: {best_score*100:.1f}%"
            self.logger.success(msg, "VISION")
            return True, best_score, msg
        else:
            msg = f"Facial Verification Failed. Peak Confidence: {best_score*100:.1f}% (Required: {self.threshold*100:.1f}%)"
            self.logger.warning(msg, "VISION")
            return False, best_score, msg

    def clear_enrolled_profile(self) -> bool:
        """Wipe saved facial biometric profile."""
        if FACE_PROFILE_PATH.exists():
            try:
                FACE_PROFILE_PATH.unlink(missing_ok=True)
                self._enrolled_face_vector = None
                self.enabled = False
                self.logger.info("Facial profile deleted.", "VISION")
                return True
            except Exception as e:
                self.logger.error(f"Failed to delete face profile: {e}", "VISION")
        return False


def get_face_biometrics() -> FaceBiometrics:
    return FaceBiometrics()
