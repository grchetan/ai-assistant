"""
================================================================================
                    JARVIS BATTERY OPTIMIZER & POWER SCHEMES
================================================================================
Windows power plan manager (High Performance, Balanced, Power Saver) and
battery degradation diagnostics generator via powercfg.
================================================================================
"""

import os
import subprocess
from pathlib import Path
from typing import Tuple, Dict, Any, Optional

from jarvis.core.logger import get_logger

POWER_SCHEMES = {
    "high_performance": "8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c",
    "balanced": "381b4222-f694-41f0-9685-ff5bb260df2e",
    "power_saver": "a1841308-3541-4fab-bc81-f71556f20b4a"
}


class BatteryOptimizer:
    """Controls Windows power schemes and generates battery telemetry."""

    def __init__(self) -> None:
        self.logger = get_logger()

    def set_power_scheme(self, scheme_name: str) -> Tuple[bool, str]:
        """Switch active Windows power scheme."""
        target = scheme_name.lower().replace(" ", "_").strip()
        guid = POWER_SCHEMES.get(target)

        if not guid:
            # Fallback alias check
            if "high" in target or "turbo" in target or "game" in target:
                guid = POWER_SCHEMES["high_performance"]
                target = "high_performance"
            elif "save" in target or "eco" in target:
                guid = POWER_SCHEMES["power_saver"]
                target = "power_saver"
            else:
                guid = POWER_SCHEMES["balanced"]
                target = "balanced"

        try:
            subprocess.run(["powercfg", "/setactive", guid], check=True)
            msg = f"Power plan '{target.replace('_', ' ').capitalize()}' activate kar diya sir."
            self.logger.success(msg, "POWER")
            return True, msg
        except Exception as e:
            err = f"Failed to set power scheme: {e}"
            self.logger.error(err, "POWER")
            return False, err

    def generate_battery_report(self) -> Tuple[bool, str, Optional[Path]]:
        """Generate official Windows battery health report HTML."""
        report_path = Path(__file__).resolve().parent.parent.parent / "jarvis" / "data" / "battery_report.html"
        try:
            subprocess.run(["powercfg", "/batteryreport", "/output", str(report_path)], check=True)
            self.logger.success(f"Battery report generated at: {report_path.name}", "POWER")
            return True, "Battery health report generate ho gaya sir.", report_path
        except Exception as e:
            return False, f"Battery report failed: {e}", None


def get_battery_optimizer() -> BatteryOptimizer:
    return BatteryOptimizer()
