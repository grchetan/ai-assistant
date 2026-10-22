"""
================================================================================
                    JARVIS POWER & WORKSTATION AUTOMATION
================================================================================
Controls Windows power states: immediate workstation lock, standby sleep,
hibernation, scheduled shutdowns with abort capability, and system restarts.
================================================================================
"""

import os
import ctypes
import subprocess
from typing import Tuple

from jarvis.core.logger import get_logger

user32 = ctypes.windll.user32


class PowerController:
    """Automates Windows workstation power transitions."""

    def __init__(self) -> None:
        self.logger = get_logger()

    def lock(self) -> Tuple[bool, str]:
        """Instantly lock the Windows workstation."""
        self.logger.info("Executing workstation lock.", "POWER")
        res = user32.LockWorkStation()
        if res:
            return True, "Workstation locked successfully sir."
        return False, "Failed to lock workstation."

    def sleep(self) -> Tuple[bool, str]:
        """Put Windows into low-power sleep/standby mode."""
        self.logger.info("Entering sleep mode.", "POWER")
        try:
            # Rundll32 power suspension
            subprocess.run(["rundll32.exe", "powrprof.dll,SetSuspendState", "0,1,0"], check=False)
            return True, "System entering sleep mode."
        except Exception as e:
            return False, f"Sleep execution failed: {e}"

    def hibernate(self) -> Tuple[bool, str]:
        """Hibernate Windows PC."""
        self.logger.info("Executing hibernation.", "POWER")
        try:
            subprocess.run(["shutdown", "/h"], check=True)
            return True, "Hibernating system."
        except Exception as e:
            return False, f"Hibernation failed: {e}"

    def restart(self, delay_seconds: int = 5) -> Tuple[bool, str]:
        """Reboot system after delay."""
        self.logger.warning(f"Scheduling system reboot in {delay_seconds}s.", "POWER")
        try:
            subprocess.run(["shutdown", "/r", "/t", str(delay_seconds)], check=True)
            return True, f"System restarting in {delay_seconds} seconds sir."
        except Exception as e:
            return False, f"Restart failed: {e}"

    def shutdown(self, delay_seconds: int = 30) -> Tuple[bool, str]:
        """Schedule PC shutdown with safe grace period."""
        self.logger.warning(f"Scheduling system shutdown in {delay_seconds}s.", "POWER")
        try:
            subprocess.run(["shutdown", "/s", "/t", str(delay_seconds)], check=True)
            return True, f"PC {delay_seconds} seconds me band ho jayega sir. Rokne ke liye 'cancel shutdown' bolein."
        except Exception as e:
            return False, f"Shutdown schedule failed: {e}"

    def cancel_shutdown(self) -> Tuple[bool, str]:
        """Abort a scheduled shutdown."""
        self.logger.info("Aborting scheduled shutdown.", "POWER")
        try:
            subprocess.run(["shutdown", "/a"], check=True)
            return True, "Shutdown cancel kar diya gaya hai sir. PC chalu rahega!"
        except Exception:
            return False, "Koi active scheduled shutdown nahi mila sir."


def get_power_controller() -> PowerController:
    return PowerController()
