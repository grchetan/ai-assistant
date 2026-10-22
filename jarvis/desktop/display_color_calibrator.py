"""
================================================================================
                    JARVIS DISPLAY COLOR & NIGHT LIGHT CALIBRATOR
================================================================================
Controls monitor color temperature directly via Win32 GDI32 SetDeviceGammaRamp.
Shifts display chromaticity into warm amber to eliminate melatonin-suppressing
blue light at night, and restores balanced cool white for daytime work.
================================================================================
"""

import ctypes
from typing import Tuple, Optional

from jarvis.core.logger import get_logger

gdi32 = ctypes.windll.gdi32
user32 = ctypes.windll.user32


class DisplayColorCalibrator:
    """Modifies monitor hardware gamma ramps."""

    def __init__(self) -> None:
        self.logger = get_logger()
        self._is_night_mode = False

    def set_night_light_warm(self, warmth_factor: float = 0.65) -> Tuple[bool, str]:
        """
        Attenuate blue component and slightly reduce green, boosting warm red
        to relieve late-night ocular strain.
        """
        self.logger.info("Applying warm amber night-light color temperature...", "DISPLAY")
        hdc = user32.GetDC(None)
        if not hdc:
            return False, "Could not acquire screen device context."

        try:
            # 256 entries each for Red, Green, Blue (16-bit WORD array, 3x256 elements)
            ramp = (ctypes.c_ushort * 768)()

            for i in range(256):
                # Standard linear mapping scaled to 0-65535
                base = i * 256
                # Red remains 100%
                ramp[i] = min(65535, base)
                # Green slightly attenuated (warm tone)
                ramp[256 + i] = min(65535, int(base * 0.88))
                # Blue significantly attenuated by warmth factor
                ramp[512 + i] = min(65535, int(base * warmth_factor))

            success = gdi32.SetDeviceGammaRamp(hdc, ctypes.byref(ramp))
            user32.ReleaseDC(None, hdc)

            if success:
                self._is_night_mode = True
                msg = "Night light warm amber filter activate kar diya gaya hai sir."
                self.logger.success(msg, "DISPLAY")
                return True, msg
            else:
                return False, "Hardware gamma ramp update was rejected by display driver."
        except Exception as e:
            user32.ReleaseDC(None, hdc)
            return False, f"Color calibration error: {e}"

    def reset_daylight_cool(self) -> Tuple[bool, str]:
        """
        Restore linear 1:1 natural color temperature.
        """
        self.logger.info("Restoring natural cool daylight gamma ramp...", "DISPLAY")
        hdc = user32.GetDC(None)
        if not hdc:
            return False, "Could not acquire screen DC."

        try:
            ramp = (ctypes.c_ushort * 768)()
            for i in range(256):
                base = i * 256
                ramp[i] = min(65535, base)
                ramp[256 + i] = min(65535, base)
                ramp[512 + i] = min(65535, base)

            success = gdi32.SetDeviceGammaRamp(hdc, ctypes.byref(ramp))
            user32.ReleaseDC(None, hdc)

            if success:
                self._is_night_mode = False
                msg = "Screen color temperature normal daylight par reset kar diya sir."
                self.logger.success(msg, "DISPLAY")
                return True, msg
            else:
                return False, "Gamma reset failed."
        except Exception as e:
            user32.ReleaseDC(None, hdc)
            return False, f"Gamma reset error: {e}"


def get_display_calibrator() -> DisplayColorCalibrator:
    return DisplayColorCalibrator()
