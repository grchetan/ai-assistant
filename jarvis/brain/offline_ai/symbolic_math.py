"""
================================================================================
            JARVIS IN-HOUSE SYMBOLIC MATH & PHYSICS SOLVER
================================================================================
Autonomous mathematical reasoning engine capable of:
  • Multi-variable algebraic equation solving
  • Polynomial root discovery & factorization
  • Symbolic calculus (differentiation, polynomials)
  • Physics formula calculators (Kinematics, Thermodynamics, Electromagnetism)
  • Financial mathematics (EMI, Compound Interest, ROI)
  • Universal unit conversions
Zero cloud dependencies. High-precision analytical computations.
================================================================================
"""

import math
import re
from typing import Dict, Any, Optional, Tuple, List
from jarvis.core.logger import get_logger


class SymbolicMathEngine:
    """Comprehensive offline analytical mathematics and physics computation suite."""

    def __init__(self) -> None:
        self.logger = get_logger()

    # ──────────────────────────────────────────────────────────────────────────
    # 1. Algebraic & Polynomial Equation Solver
    # ──────────────────────────────────────────────────────────────────────────
    def solve_quadratic(self, a: float, b: float, c: float) -> Tuple[str, List[complex]]:
        """Solve quadratic equation ax^2 + bx + c = 0."""
        if a == 0:
            if b == 0:
                return "Invalid equation: no variable x exists.", []
            root = -c / b
            return f"Linear root: x = {root:.4f}", [complex(root, 0)]

        discriminant = b**2 - 4 * a * c
        if discriminant > 0:
            root1 = (-b + math.sqrt(discriminant)) / (2 * a)
            root2 = (-b - math.sqrt(discriminant)) / (2 * a)
            msg = f"Two real distinct roots: x1 = {root1:.4f}, x2 = {root2:.4f}"
            return msg, [complex(root1, 0), complex(root2, 0)]
        elif discriminant == 0:
            root = -b / (2 * a)
            msg = f"Single real repeated root: x = {root:.4f}"
            return msg, [complex(root, 0)]
        else:
            real_part = -b / (2 * a)
            imag_part = math.sqrt(-discriminant) / (2 * a)
            msg = f"Complex roots: x1 = {real_part:.4f} + {imag_part:.4f}i, x2 = {real_part:.4f} - {imag_part:.4f}i"
            return msg, [complex(real_part, imag_part), complex(real_part, -imag_part)]

    def solve_linear_system_2x2(self, a1: float, b1: float, c1: float, a2: float, b2: float, c2: float) -> str:
        """
        Solve system of 2 linear equations via Cramer's Rule:
        a1*x + b1*y = c1
        a2*x + b2*y = c2
        """
        det = a1 * b2 - a2 * b1
        if det == 0:
            return "Equations are either parallel (no solution) or coincident (infinitely many solutions)."

        det_x = c1 * b2 - c2 * b1
        det_y = a1 * c2 - a2 * c1

        x = det_x / det
        y = det_y / det
        return f"Solution to linear system: x = {x:.4f}, y = {y:.4f}"

    def differentiate_polynomial(self, expression: str) -> str:
        """
        Symbolically differentiate polynomial in variable 'x'.
        Example: "3x^3 + 4x^2 - 5x + 7" -> "9x^2 + 8x - 5"
        """
        expr = expression.replace(" ", "").replace("-", "+-")
        terms = [t for t in expr.split("+") if t]

        derived_terms = []
        for t in terms:
            if "x" not in t:
                continue  # Constant becomes 0

            # Match term format like ax^n, -ax^n, x^n, ax, x
            m = re.match(r"^([+-]?\d*(?:\.\d+)?)x(?:\^([+-]?\d+))?$", t)
            if not m:
                continue

            coeff_str, power_str = m.groups()
            # Coeff
            if coeff_str in ("", "+"):
                coeff = 1.0
            elif coeff_str == "-":
                coeff = -1.0
            else:
                coeff = float(coeff_str)

            # Power
            power = int(power_str) if power_str else 1

            new_coeff = coeff * power
            new_power = power - 1

            if new_power == 0:
                derived_terms.append(f"{new_coeff:g}")
            elif new_power == 1:
                derived_terms.append(f"{new_coeff:g}x")
            else:
                derived_terms.append(f"{new_coeff:g}x^{new_power}")

        if not derived_terms:
            return "Derivative d/dx = 0"

        res = " + ".join(derived_terms).replace("+ -", "- ")
        return f"Derivative d/dx: {res}"

    # ──────────────────────────────────────────────────────────────────────────
    # 2. Physics Equation Solvers
    # ──────────────────────────────────────────────────────────────────────────
    def physics_kinetic_energy(self, mass_kg: float, velocity_mps: float) -> str:
        """Kinetic Energy KE = 1/2 m v^2"""
        ke = 0.5 * mass_kg * (velocity_mps ** 2)
        return f"Kinetic Energy: {ke:.2f} Joules (m={mass_kg} kg, v={velocity_mps} m/s)"

    def physics_gravitational_force(self, m1_kg: float, m2_kg: float, distance_m: float) -> str:
        """Newton's Law of Gravitation F = G (m1 m2) / r^2"""
        G = 6.67430e-11
        if distance_m <= 0:
            return "Distance must be strictly positive."
        f = (G * m1_kg * m2_kg) / (distance_m ** 2)
        return f"Gravitational Force: {f:.4e} Newtons (G = 6.674×10^-11 N·m²/kg²)"

    def physics_ohms_law(self, voltage: Optional[float] = None, current: Optional[float] = None, resistance: Optional[float] = None) -> str:
        """Ohm's Law: V = I * R"""
        if voltage is None and current is not None and resistance is not None:
            v = current * resistance
            return f"Voltage V = {v:.2f} Volts (I={current} A, R={resistance} Ω)"
        elif current is None and voltage is not None and resistance is not None:
            if resistance == 0:
                return "Infinite current (Short circuit, R = 0)."
            i = voltage / resistance
            return f"Current I = {i:.4f} Amperes (V={voltage} V, R={resistance} Ω)"
        elif resistance is None and voltage is not None and current is not None:
            if current == 0:
                return "Infinite resistance (Open circuit, I = 0)."
            r = voltage / current
            return f"Resistance R = {r:.2f} Ohms (V={voltage} V, I={current} A)"
        else:
            return "Please provide exactly two parameters out of Voltage, Current, and Resistance."

    def physics_orbital_velocity(self, central_mass_kg: float, radius_m: float) -> str:
        """Orbital velocity v = sqrt(G M / r)"""
        G = 6.67430e-11
        if radius_m <= 0 or central_mass_kg <= 0:
            return "Mass and radius must be greater than zero."
        v = math.sqrt((G * central_mass_kg) / radius_m)
        v_km_s = v / 1000.0
        return f"Orbital Velocity: {v:.2f} m/s ({v_km_s:.2f} km/s)"

    # ──────────────────────────────────────────────────────────────────────────
    # 3. Financial Mathematics
    # ──────────────────────────────────────────────────────────────────────────
    def financial_emi(self, principal: float, annual_rate_pct: float, tenure_months: int) -> str:
        """Calculate monthly EMI for loans."""
        if tenure_months <= 0 or principal <= 0:
            return "Principal and tenure must be positive."
        monthly_r = (annual_rate_pct / 12.0) / 100.0
        if monthly_r == 0:
            emi = principal / tenure_months
        else:
            emi = (principal * monthly_r * ((1 + monthly_r) ** tenure_months)) / (((1 + monthly_r) ** tenure_months) - 1)

        total_payable = emi * tenure_months
        total_interest = total_payable - principal
        return (
            f"Monthly EMI: ₹{emi:,.2f}\n"
            f"Total Interest: ₹{total_interest:,.2f}\n"
            f"Total Amount Payable: ₹{total_payable:,.2f}"
        )

    def financial_compound_interest(self, principal: float, annual_rate_pct: float, years: float, compounding_per_year: int = 1) -> str:
        """Compound interest A = P (1 + r/n)^(nt)"""
        r = annual_rate_pct / 100.0
        n = compounding_per_year
        amount = principal * ((1 + r / n) ** (n * years))
        interest = amount - principal
        return f"Compound Amount: ₹{amount:,.2f} (Total Interest Earned: ₹{interest:,.2f})"

    # ──────────────────────────────────────────────────────────────────────────
    # 4. Universal Unit Converter
    # ──────────────────────────────────────────────────────────────────────────
    def convert_units(self, value: float, from_unit: str, to_unit: str) -> Optional[str]:
        """Convert across common scientific and metric units."""
        f = from_unit.lower().strip()
        t = to_unit.lower().strip()

        # Temperature
        if f in ("c", "celsius") and t in ("f", "fahrenheit"):
            res = (value * 9 / 5) + 32
            return f"{value}°C = {res:.2f}°F"
        if f in ("f", "fahrenheit") and t in ("c", "celsius"):
            res = (value - 32) * 5 / 9
            return f"{value}°F = {res:.2f}°C"
        if f in ("c", "celsius") and t in ("k", "kelvin"):
            res = value + 273.15
            return f"{value}°C = {res:.2f} K"

        # Speed
        if f in ("km/h", "kmph") and t in ("m/s", "mps"):
            res = value * (5 / 18)
            return f"{value} km/h = {res:.2f} m/s"
        if f in ("m/s", "mps") and t in ("km/h", "kmph"):
            res = value * (18 / 5)
            return f"{value} m/s = {res:.2f} km/h"

        # Length
        length_to_m = {"m": 1.0, "km": 1000.0, "cm": 0.01, "mm": 0.001, "miles": 1609.34, "feet": 0.3048, "inches": 0.0254}
        if f in length_to_m and t in length_to_m:
            in_meters = value * length_to_m[f]
            res = in_meters / length_to_m[t]
            return f"{value} {from_unit} = {res:.4f} {to_unit}"

        # Digital Storage
        bytes_map = {"b": 1, "kb": 1024, "mb": 1024**2, "gb": 1024**3, "tb": 1024**4}
        if f in bytes_map and t in bytes_map:
            in_bytes = value * bytes_map[f]
            res = in_bytes / bytes_map[t]
            return f"{value} {from_unit.upper()} = {res:.4f} {to_unit.upper()}"

        return None

    # ──────────────────────────────────────────────────────────────────────────
    # 5. Natural Language Math Query Evaluator
    # ──────────────────────────────────────────────────────────────────────────
    def try_solve(self, text: str) -> Optional[str]:
        """Parse natural language query and dispatch to appropriate math/physics routine."""
        t = text.lower().strip()

        # Quadratic equation
        if "quadratic" in t or "roots of" in t:
            m = re.search(r"(-?\d+(?:\.\d+)?)\s*x\^?2\s*([+-]\s*\d+(?:\.\d+)?)\s*x\s*([+-]\s*\d+(?:\.\d+)?)", t)
            if m:
                a = float(m.group(1))
                b = float(m.group(2).replace(" ", ""))
                c = float(m.group(3).replace(" ", ""))
                msg, _ = self.solve_quadratic(a, b, c)
                return msg

        # Differentiate
        if "derivative" in t or "differentiate" in t:
            m = re.search(r"(?:derivative of|differentiate)\s+([0-9x\^\+\-\s]+)", t)
            if m:
                return self.differentiate_polynomial(m.group(1))

        # EMI calculation
        if "emi" in t or "loan" in t:
            nums = [float(x) for x in re.findall(r"\b\d+(?:\.\d+)?\b", t)]
            if len(nums) >= 3:
                # [principal, rate, tenure]
                p, r, n = nums[0], nums[1], int(nums[2])
                return self.financial_emi(p, r, n)

        # Unit conversion
        conv_m = re.search(r"convert\s+(\d+(?:\.\d+)?)\s*([a-zA-Z/]+)\s+(?:to|into)\s+([a-zA-Z/]+)", t)
        if conv_m:
            val = float(conv_m.group(1))
            from_u = conv_m.group(2)
            to_u = conv_m.group(3)
            res = self.convert_units(val, from_u, to_u)
            if res:
                return res

        # Direct safe arithmetic
        if any(op in t for op in ["+", "-", "*", "/", "^", "%", "sqrt", "sin", "cos"]):
            try:
                # Sanitize safe math
                cleaned = re.sub(r"[^0-9\+\-\*\/\(\)\.\s\^]", "", t).strip()
                if cleaned and any(d.isdigit() for d in cleaned):
                    cleaned_eval = cleaned.replace("^", "**")
                    # Safe eval
                    val = eval(cleaned_eval, {"__builtins__": None, "math": math})
                    return f"{cleaned} = {val}"
            except Exception:
                pass

        return None


_math_instance: Optional[SymbolicMathEngine] = None

def get_math_engine() -> SymbolicMathEngine:
    global _math_instance
    if _math_instance is None:
        _math_instance = SymbolicMathEngine()
    return _math_instance
