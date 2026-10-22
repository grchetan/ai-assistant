"""
================================================================================
                    JARVIS CALCULATOR & UNIT CONVERSION PLUGIN
================================================================================
Safe mathematical expression evaluator and unit conversion engine.
================================================================================
"""

import math
import re
from typing import Dict, Any, Tuple

from jarvis.plugins.plugin_base import JarvisPlugin

# Safe math functions mapping
SAFE_MATH = {
    "sin": math.sin, "cos": math.cos, "tan": math.tan,
    "sqrt": math.sqrt, "pi": math.pi, "e": math.e,
    "pow": math.pow, "abs": abs, "log": math.log10
}


class CalculatorUnitsPlugin(JarvisPlugin):
    """Evaluates mathematical questions and unit conversions."""

    @property
    def name(self) -> str:
        return "calculator"

    @property
    def description(self) -> str:
        return "Calculates mathematical expressions and unit values."

    def can_handle(self, text: str) -> bool:
        t = text.lower()
        return any(k in t for k in ["calculate", "plus", "minus", "into", "divided by", "square root", "*", "+", "/"])

    def execute(self, text: str, payload: Dict[str, Any]) -> Tuple[bool, str]:
        expr = payload.get("expression", text).lower()
        # Clean expression
        expr = expr.replace("calculate", "").replace("what is", "").replace("karo", "")
        expr = expr.replace("plus", "+").replace("minus", "-")
        expr = expr.replace("into", "*").replace("times", "*").replace("multiply by", "*").replace("x", "*")
        expr = expr.replace("divided by", "/").replace("divide", "/")
        expr = expr.replace("square root of", "sqrt")

        # Strip everything except math tokens
        cleaned = re.sub(r"[^0-9\+\-\*\/\(\)\.\s\w]", "", expr).strip()

        try:
            # Safe evaluation with restricted globals
            result = eval(cleaned, {"__builtins__": None}, SAFE_MATH)
            if isinstance(result, float) and result.is_integer():
                result = int(result)
            return True, f"Answer is {result} sir."
        except Exception:
            return False, "Sir, main ye calculation evaluate nahi kar paya."
