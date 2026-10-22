"""
================================================================================
                    JARVIS SCREEN INTELLIGENCE & VISION
================================================================================
Computer vision engine: high-resolution desktop screen capture, webcam image
acquisition via OpenCV, and Multimodal Vision analysis via Google Gemini.
================================================================================
"""

import time
from typing import Optional, Tuple
from pathlib import Path

try:
    from PIL import Image, ImageGrab
    _PIL_AVAILABLE = True
except ImportError:
    _PIL_AVAILABLE = False

try:
    import cv2
    _CV2_AVAILABLE = True
except ImportError:
    _CV2_AVAILABLE = False

from jarvis.core.logger import get_logger
from jarvis.core.security import SecurityVault

SCREENSHOTS_DIR = Path(__file__).resolve().parent.parent.parent / "jarvis" / "data" / "screenshots"
SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)


class ScreenVision:
    """Manages visual capture and optical scene perception."""

    def __init__(self) -> None:
        self.logger = get_logger()
        self.vault = SecurityVault()

    def capture_screenshot(self, filename: Optional[str] = None) -> Tuple[bool, str, Optional[Path]]:
        """Capture full screen and save as PNG."""
        if not _PIL_AVAILABLE:
            return False, "PIL library not available for screenshot.", None

        try:
            name = filename or f"screenshot_{int(time.time())}.png"
            output_path = SCREENSHOTS_DIR / name
            img = ImageGrab.grab()
            img.save(str(output_path), format="PNG")
            self.logger.success(f"Screenshot saved to: {output_path.name}", "VISION")
            return True, f"Screenshot save ho gaya sir: {output_path.name}", output_path
        except Exception as e:
            msg = f"Screenshot capture error: {e}"
            self.logger.error(msg, "VISION")
            return False, msg, None

    def capture_webcam_frame(self, camera_index: int = 0) -> Tuple[bool, str, Optional[Path]]:
        """Grab a single frame from connected webcam."""
        if not _CV2_AVAILABLE:
            return False, "OpenCV not installed for camera capture.", None

        try:
            cap = cv2.VideoCapture(camera_index)
            if not cap.isOpened():
                return False, "Sir, camera open nahi ho pa raha.", None

            ret, frame = cap.read()
            cap.release()

            if ret:
                output_path = SCREENSHOTS_DIR / f"camera_{int(time.time())}.jpg"
                cv2.imwrite(str(output_path), frame)
                self.logger.success(f"Webcam photo saved: {output_path.name}", "VISION")
                return True, "Photo capture kar li gayi hai sir.", output_path
            else:
                return False, "Camera se frame nahi mila sir.", None
        except Exception as e:
            return False, f"Camera error: {e}", None

    def analyze_current_screen(self, prompt: str = "Describe what is visible on this screen") -> str:
        """Capture current screen and send to Gemini Vision for description."""
        success, _, path = self.capture_screenshot()
        if not success or not path:
            return "Sir, screen capture nahi ho payi."

        api_key = self.vault.get_secret("GEMINI_API_KEY")
        if not api_key:
            return "Sir, vision analysis ke liye Gemini API key save karni hogi."

        try:
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel("gemini-1.5-flash")
            img = Image.open(str(path))
            response = model.generate_content([prompt, img])
            return response.text.strip()
        except Exception as e:
            self.logger.error(f"Screen vision error: {e}", "VISION")
            return f"Vision model error: {e}"


def get_screen_vision() -> ScreenVision:
    return ScreenVision()
