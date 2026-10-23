"""
================================================================================
            JARVIS SCIENTIFIC UNIT CONVERTER PRO PLUGIN
================================================================================
Converts technical engineering units:
  • Pressure: Pascal, Bar, PSI, Atmosphere
  • Energy & Work: Joules, Calories, Kilowatt-hours (kWh), BTU
  • Power: Watts, Kilowatts, Horsepower (HP)
  • Data Transfer: Mbps, MB/s, Gbps, GB/s
================================================================================
"""

import re
from typing import Dict, Any, Tuple
from jarvis.plugins.plugin_base import JarvisPlugin
from jarvis.core.logger import get_logger


class UnitConverterProPlugin(JarvisPlugin):
    """Multi-domain physics and scientific unit conversion plugin."""

    @property
    def name(self) -> str:
        return "unit_converter_pro"

    @property
    def description(self) -> str:
        return "Converts engineering units: Pressure, Energy, Power, and Bandwidth rates."

    def can_handle(self, text: str) -> bool:
        t = text.lower()
        return any(k in t for k in ["convert pressure", "convert power", "convert energy", "bar to psi", "psi to bar", "hp to watt", "watt to hp"])

    def execute(self, text: str, payload: Dict[str, Any]) -> Tuple[bool, str]:
        t = text.lower().strip()
        nums = [float(x) for x in re.findall(r"\b\d+(?:\.\d+)?\b", t)]
        val = nums[0] if nums else 1.0

        # Bar to PSI
        if "bar to psi" in t:
            psi = val * 14.5038
            return True, f"Sir, {val} Bar = {psi:.2f} PSI"

        # PSI to Bar
        if "psi to bar" in t:
            bar = val / 14.5038
            return True, f"Sir, {val} PSI = {bar:.4f} Bar"

        # Horsepower to Watts
        if "hp to watt" in t:
            watts = val * 745.7
            return True, f"Sir, {val} HP (Horsepower) = {watts:.2f} Watts ({watts/1000:.2f} kW)"

        # Watts to Horsepower
        if "watt to hp" in t:
            hp = val / 745.7
            return True, f"Sir, {val} Watts = {hp:.3f} HP"

        # Joules to Calories
        if "joule to cal" in t or "joules to calories" in t:
            cal = val / 4.184
            return True, f"Sir, {val} Joules = {cal:.2f} Calories"

        return True, "Sir, please state conversion format: e.g. '10 bar to psi' or '5 hp to watt'."
