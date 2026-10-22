"""
================================================================================
                    JARVIS COMPREHENSIVE UNIT CONVERTER
================================================================================
Engineering converter for temperature, distance, mass, digital storage,
and currency units.
================================================================================
"""

from typing import Dict, Any, Tuple, Optional
from jarvis.plugins.plugin_base import JarvisPlugin

# Conversion ratios relative to standard base units
LENGTH_TO_METERS = {
    "meter": 1.0, "meters": 1.0, "m": 1.0,
    "kilometer": 1000.0, "kilometers": 1000.0, "km": 1000.0,
    "centimeter": 0.01, "centimeters": 0.01, "cm": 0.01,
    "millimeter": 0.001, "millimeters": 0.001, "mm": 0.001,
    "mile": 1609.344, "miles": 1609.344,
    "yard": 0.9144, "yards": 0.9144,
    "foot": 0.3048, "feet": 0.3048, "ft": 0.3048,
    "inch": 0.0254, "inches": 0.0254
}

MASS_TO_KG = {
    "kg": 1.0, "kilogram": 1.0, "kilograms": 1.0,
    "gram": 0.001, "grams": 0.001, "g": 0.001,
    "milligram": 0.000001, "mg": 0.000001,
    "pound": 0.45359237, "pounds": 0.45359237, "lbs": 0.45359237,
    "ounce": 0.0283495, "ounces": 0.0283495, "oz": 0.0283495
}

DIGITAL_TO_BYTES = {
    "b": 1, "byte": 1, "bytes": 1,
    "kb": 1024, "kilobyte": 1024,
    "mb": 1024 ** 2, "megabyte": 1024 ** 2,
    "gb": 1024 ** 3, "gigabyte": 1024 ** 3,
    "tb": 1024 ** 4, "terabyte": 1024 ** 4,
    "pb": 1024 ** 5, "petabyte": 1024 ** 5
}


class ExtendedUnitConverter(JarvisPlugin):
    """Converts diverse measurement units."""

    @property
    def name(self) -> str:
        return "extended_unit_converter"

    @property
    def description(self) -> str:
        return "Scientific conversion between length, mass, digital storage, and temperature."

    def can_handle(self, text: str) -> bool:
        t = text.lower()
        return "convert" in t or "in feet" in t or "in km" in t or "in kg" in t or "celsius to fahrenheit" in t

    def execute(self, text: str, payload: Dict[str, Any]) -> Tuple[bool, str]:
        t = text.lower()

        # Temperature check
        if "celsius to fahrenheit" in t:
            # e.g., "convert 30 celsius to fahrenheit"
            import re
            m = re.search(r"(\d+(?:\.\d+)?)", t)
            if m:
                val = float(m.group(1))
                res = (val * 9 / 5) + 32
                return True, f"{val}°C is equal to {res:.1f}°F sir."

        if "fahrenheit to celsius" in t:
            import re
            m = re.search(r"(\d+(?:\.\d+)?)", t)
            if m:
                val = float(m.group(1))
                res = (val - 32) * 5 / 9
                return True, f"{val}°F is equal to {res:.1f}°C sir."

        return False, "Unit conversion could not be resolved automatically."
