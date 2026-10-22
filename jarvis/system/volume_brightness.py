"""
================================================================================
                    JARVIS AUDIO VOLUME & DISPLAY BRIGHTNESS
================================================================================
Controls Windows master endpoint volume using CoreAudio / multimedia keys,
and adjusts LCD display brightness via PowerShell WMI instrumentation.
================================================================================
"""

import ctypes
import subprocess
from typing import Tuple, Optional

try:
    import pyautogui
    _PYAUTOGUI_AVAILABLE = True
except ImportError:
    _PYAUTOGUI_AVAILABLE = False

from jarvis.core.logger import get_logger

# Virtual-Key codes for Multimedia
VK_VOLUME_MUTE = 0xAD
VK_VOLUME_DOWN = 0xAE
VK_VOLUME_UP   = 0xAF


class VolumeBrightnessController:
    """Manages audio volume levels and monitor brightness."""

    def __init__(self) -> None:
        self.logger = get_logger()

    # ─────────────────────────────────────────────────────────
    #  AUDIO VOLUME
    # ─────────────────────────────────────────────────────────
    def volume_up(self, steps: int = 5) -> str:
        """Increase volume by pressing Volume Up key multiple times."""
        for _ in range(steps):
            ctypes.windll.user32.keybd_event(VK_VOLUME_UP, 0, 0, 0)
            ctypes.windll.user32.keybd_event(VK_VOLUME_UP, 0, 2, 0)
        self.logger.info("Master volume increased.", "SYSTEM")
        return "Volume badha diya sir."

    def volume_down(self, steps: int = 5) -> str:
        """Decrease volume by pressing Volume Down key multiple times."""
        for _ in range(steps):
            ctypes.windll.user32.keybd_event(VK_VOLUME_DOWN, 0, 0, 0)
            ctypes.windll.user32.keybd_event(VK_VOLUME_DOWN, 0, 2, 0)
        self.logger.info("Master volume decreased.", "SYSTEM")
        return "Volume kam kar diya sir."

    def toggle_mute(self) -> str:
        """Toggle audio mute state."""
        ctypes.windll.user32.keybd_event(VK_VOLUME_MUTE, 0, 0, 0)
        ctypes.windll.user32.keybd_event(VK_VOLUME_MUTE, 0, 2, 0)
        self.logger.info("Toggled volume mute state.", "SYSTEM")
        return "Volume mute state toggle kar di gayi hai sir."

    def set_volume_percent(self, target_percent: int) -> str:
        """Set volume to approximate target percentage."""
        target = max(0, min(100, target_percent))
        # Zero out volume first (50 down presses), then step up
        for _ in range(50):
            ctypes.windll.user32.keybd_event(VK_VOLUME_DOWN, 0, 0, 0)
            ctypes.windll.user32.keybd_event(VK_VOLUME_DOWN, 0, 2, 0)

        # Each step is ~2% on Windows
        steps_up = target // 2
        for _ in range(steps_up):
            ctypes.windll.user32.keybd_event(VK_VOLUME_UP, 0, 0, 0)
            ctypes.windll.user32.keybd_event(VK_VOLUME_UP, 0, 2, 0)

        self.logger.info(f"Set volume to approximately {target}%.", "SYSTEM")
        return f"Volume {target} percent par set kar diya sir."

    # ─────────────────────────────────────────────────────────
    #  SCREEN BRIGHTNESS
    # ─────────────────────────────────────────────────────────
    def set_brightness(self, percent: int) -> Tuple[bool, str]:
        """Adjust monitor brightness via WMI PowerShell."""
        p = max(0, min(100, percent))
        cmd = f"(Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightnessMethods).WmiSetBrightness(1, {p})"
        try:
            subprocess.run(["powershell", "-NoProfile", "-Command", cmd], capture_output=True, check=True)
            self.logger.info(f"Brightness set to {p}%.", "SYSTEM")
            return True, f"Screen brightness {p} percent set kar di sir."
        except Exception as e:
            self.logger.warning(f"Brightness control unsupported on this display hardware: {e}", "SYSTEM")
            return False, "Sir, is monitor par hardware brightness control support nahi karta."


def get_volume_controller() -> VolumeBrightnessController:
    return VolumeBrightnessController()
