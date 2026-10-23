"""
================================================================================
            JARVIS IN-HOUSE MATHEMATICAL & PHYSICAL FORMULA SHEET
================================================================================
Curated repository of standard scientific, geometric, and algebraic formulas:
  • Geometry: Areas, Perimeters, Surface Areas, Volumes
  • Trigonometric Identities: Pythagorean, Double-angle, Half-angle
  • Classical Physics: Newton's Gravitation, Lorentz Force, Ideal Gas
  • Calculus & Series: Taylor series, Power rule, Chain rule, Quotient rule
================================================================================
"""

from typing import Dict, List, Any, Optional
from jarvis.core.logger import get_logger

FORMULAS: List[Dict[str, Any]] = [
    {"name": "Circle Area & Circumference", "category": "Geometry", "formula": "Area = π * r², Circumference = 2 * π * r", "desc": "Calculates two-dimensional circle planar bounds based on radius r."},
    {"name": "Sphere Volume & Surface Area", "category": "Geometry", "formula": "Volume = (4/3) * π * r³, Surface Area = 4 * π * r²", "desc": "Three-dimensional spherical measurements."},
    {"name": "Cylinder Volume", "category": "Geometry", "formula": "Volume = π * r² * h, Lateral Area = 2 * π * r * h", "desc": "Volume of cylindrical solid with radius r and height h."},
    {"name": "Pythagorean Theorem", "category": "Trigonometry", "formula": "a² + b² = c²", "desc": "Fundamental relation in Euclidean geometry among three sides of a right triangle."},
    {"name": "Euler's Identity", "category": "Mathematics", "formula": "e^(i * π) + 1 = 0", "desc": "Profound equation linking five fundamental mathematical constants (e, i, π, 1, 0)."},
    {"name": "Quadratic Formula", "category": "Algebra", "formula": "x = (-b ± √(b² - 4ac)) / (2a)", "desc": "Solutions for standard polynomial equation ax² + bx + c = 0."},
    {"name": "Newton's Second Law", "category": "Classical Physics", "formula": "F = m * a", "desc": "Net external force on mass m results in proportional acceleration a."},
    {"name": "Kinetic Energy", "category": "Classical Physics", "formula": "KE = (1/2) * m * v²", "desc": "Energy possessed by object of mass m moving with speed v."},
    {"name": "Gravitational Potential Energy", "category": "Classical Physics", "formula": "PE = m * g * h", "desc": "Energy stored by mass m elevated to height h in gravity field g (9.81 m/s²)."},
    {"name": "Ohm's Law", "category": "Electromagnetism", "formula": "V = I * R", "desc": "Voltage drop across an ideal resistor equals current multiplied by electrical resistance."},
    {"name": "Coulomb's Law", "category": "Electromagnetism", "formula": "F = k_e * (|q1 * q2| / r²)", "desc": "Electrostatic force between two stationary electric point charges separated by distance r."},
    {"name": "Lorentz Force", "category": "Electromagnetism", "formula": "F = q * (E + v × B)", "desc": "Total force exerted on electric charge q moving in electric field E and magnetic field B."},
    {"name": "Ideal Gas Law", "category": "Thermodynamics", "formula": "P * V = n * R * T", "desc": "Equation of state for a hypothetical ideal gas (P: pressure, V: volume, T: temperature)."},
    {"name": "Calculus Chain Rule", "category": "Calculus", "formula": "(f ∘ g)'(x) = f'(g(x)) * g'(x)", "desc": "Differentiating composite functions by chaining derivatives."}
]


class MathFormulaSheetEngine:
    """Formula lookup and explanation engine."""

    def __init__(self) -> None:
        self.logger = get_logger()
        self.formulas = FORMULAS

    def search_formula(self, query: str) -> Optional[Dict[str, Any]]:
        q = query.lower()
        for f in self.formulas:
            if f["name"].lower() in q or f["category"].lower() in q:
                return f
        return None

    def format_speech(self, f: Dict[str, Any]) -> str:
        return f"Sir, [{f['name']}] ({f['category']}): Formula is '{f['formula']}'. {f['desc']}"


_formula_instance: Optional[MathFormulaSheetEngine] = None

def get_formula_sheet() -> MathFormulaSheetEngine:
    global _formula_instance
    if _formula_instance is None:
        _formula_instance = MathFormulaSheetEngine()
    return _formula_instance
