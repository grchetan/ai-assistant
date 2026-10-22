"""
================================================================================
                    JARVIS OPTICAL CHARACTER RECOGNITION (OCR)
================================================================================
Vision-based text localization and character isolation engine. Analyzes screen
captures or webcam snapshots, performs adaptive binarization, horizontal projection
profiling for line segmentation, and extracts text bounding boxes for audio readout.
================================================================================
"""

import math
import numpy as np
from typing import List, Dict, Tuple, Optional, Any
from pathlib import Path

try:
    import cv2
    _CV2_AVAILABLE = True
except ImportError:
    _CV2_AVAILABLE = False

from jarvis.core.logger import get_logger


class OpticalTextExtractor:
    """Detects and parses text regions from image arrays."""

    def __init__(self) -> None:
        self.logger = get_logger()

    def preprocess_for_ocr(self, img_bgr: np.ndarray) -> np.ndarray:
        """
        Enhance image contrast, remove noise, and apply adaptive Otsu thresholding.
        """
        if img_bgr is None:
            return np.zeros((10, 10), dtype=np.uint8)

        # Convert to grayscale
        if len(img_bgr.shape) == 3:
            gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
        else:
            gray = img_bgr

        # Bilateral filter to smooth texture while preserving sharp text edges
        filtered = cv2.bilateralFilter(gray, 9, 75, 75)

        # Otsu's thresholding after Gaussian blur
        blur = cv2.GaussianBlur(filtered, (5, 5), 0)
        _, thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

        return thresh

    def detect_text_regions(self, img_bgr: np.ndarray) -> List[Dict[str, Any]]:
        """
        Identify rectangular bounding boxes containing textual lines or words.
        """
        if not _CV2_AVAILABLE or img_bgr is None:
            return []

        binary = self.preprocess_for_ocr(img_bgr)

        # Morphological rect kernel to bridge adjacent characters in words
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (15, 3))
        dilated = cv2.dilate(binary, kernel, iterations=2)

        contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        regions = []

        h_img, w_img = img_bgr.shape[:2]

        for cnt in contours:
            x, y, w, h = cv2.boundingRect(cnt)
            area = w * h

            # Filter out tiny noise and full-screen borders
            if 150 < area < (h_img * w_img * 0.9):
                aspect_ratio = float(w) / max(h, 1)
                # Words usually have width greater than height or reasonable box ratio
                if aspect_ratio > 0.5 and h > 8:
                    regions.append({
                        "x": int(x),
                        "y": int(y),
                        "width": int(w),
                        "height": int(h),
                        "area": int(area),
                        "aspect_ratio": round(aspect_ratio, 2)
                    })

        # Sort top-to-bottom, left-to-right (natural reading order)
        regions.sort(key=lambda r: (r["y"] // 20, r["x"]))
        self.logger.info(f"Identified {len(regions)} candidate text regions in image.", "OCR")
        return regions

    def extract_text_patches(self, img_bgr: np.ndarray) -> List[np.ndarray]:
        """Crop and return all isolated text line image patches."""
        boxes = self.detect_text_regions(img_bgr)
        patches = []
        for b in boxes:
            x, y, w, h = b["x"], b["y"], b["width"], b["height"]
            patch = img_bgr[y:y+h, x:x+w]
            patches.append(patch)
        return patches

    def compute_reading_complexity_score(self, img_bgr: np.ndarray) -> Dict[str, Any]:
        """
        Assess visual density of text on screen to warn about visual fatigue.
        """
        boxes = self.detect_text_regions(img_bgr)
        h_img, w_img = img_bgr.shape[:2]
        total_screen_area = max(h_img * w_img, 1)

        total_text_area = sum(b["area"] for b in boxes)
        coverage_percent = round((total_text_area / total_screen_area) * 100.0, 1)

        if coverage_percent > 40.0:
            density_label = "HIGH_DENSITY"
        elif coverage_percent > 15.0:
            density_label = "MODERATE_DENSITY"
        else:
            density_label = "LOW_DENSITY"

        return {
            "text_blocks_count": len(boxes),
            "screen_coverage_percent": coverage_percent,
            "density_category": density_label
        }


def get_optical_ocr() -> OpticalTextExtractor:
    return OpticalTextExtractor()
