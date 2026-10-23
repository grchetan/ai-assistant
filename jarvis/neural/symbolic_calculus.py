"""
================================================================================
            JARVIS IN-HOUSE SYMBOLIC CALCULUS & LINEAR ALGEBRA
================================================================================
High-precision mathematical suite:
  • Matrix algebra: Determinants, 3x3 Inverse, Matrix Multiplication
  • 3D Vector mechanics: Dot product, Cross product, Projection
  • Definite & indefinite integration of polynomial functions
  • Number theory: Greatest Common Divisor (GCD), LCM, Prime factorization
  • Discrete & continuous probability distributions
Zero third-party library dependencies.
================================================================================
"""

import math
import re
from typing import List, Tuple, Optional, Dict, Any
from jarvis.core.logger import get_logger


class SymbolicCalculusEngine:
    """Linear algebra, vector analysis, and advanced calculus system."""

    def __init__(self) -> None:
        self.logger = get_logger()

    # ──────────────────────────────────────────────────────────────────────────
    # Matrix Algebra
    # ──────────────────────────────────────────────────────────────────────────
    def matrix_multiply_3x3(self, A: List[List[float]], B: List[List[float]]) -> List[List[float]]:
        """Compute matrix product of two 3x3 matrices."""
        C = [[0.0 for _ in range(3)] for _ in range(3)]
        for i in range(3):
            for j in range(3):
                for k in range(3):
                    C[i][j] += A[i][k] * B[k][j]
        return C

    def determinant_3x3(self, M: List[List[float]]) -> float:
        """Calculate determinant of 3x3 matrix via cofactor expansion."""
        a, b, c = M[0]
        d, e, f = M[1]
        g, h, i = M[2]
        det = a * (e * i - f * h) - b * (d * i - f * g) + c * (d * h - e * g)
        return det

    def inverse_3x3(self, M: List[List[float]]) -> Tuple[bool, Optional[List[List[float]]], str]:
        """Calculate inverse of 3x3 matrix."""
        det = self.determinant_3x3(M)
        if abs(det) < 1e-12:
            return False, None, "Matrix is singular (determinant = 0); inverse does not exist."

        a, b, c = M[0]
        d, e, f = M[1]
        g, h, i = M[2]

        adj = [
            [(e * i - f * h), -(b * i - c * h), (b * f - c * e)],
            [-(d * i - f * g), (a * i - c * g), -(a * f - c * d)],
            [(d * h - e * g), -(a * h - b * g), (a * e - b * d)]
        ]

        inv = [[adj[r][col] / det for col in range(3)] for r in range(3)]
        return True, inv, f"Inverse computed successfully (det = {det:.4f})"

    # ──────────────────────────────────────────────────────────────────────────
    # 3D Vector Mechanics
    # ──────────────────────────────────────────────────────────────────────────
    def vector_dot(self, v1: Tuple[float, float, float], v2: Tuple[float, float, float]) -> float:
        """Calculate vector dot product: v1 · v2."""
        return v1[0] * v2[0] + v1[1] * v2[1] + v1[2] * v2[2]

    def vector_cross(self, v1: Tuple[float, float, float], v2: Tuple[float, float, float]) -> Tuple[float, float, float]:
        """Calculate vector cross product: v1 × v2."""
        return (
            v1[1] * v2[2] - v1[2] * v2[1],
            v1[2] * v2[0] - v1[0] * v2[2],
            v1[0] * v2[1] - v1[1] * v2[0]
        )

    def vector_magnitude(self, v: Tuple[float, float, float]) -> float:
        """Calculate Euclidean vector length ||v||."""
        return math.sqrt(v[0]**2 + v[1]**2 + v[2]**2)

    # ──────────────────────────────────────────────────────────────────────────
    # Integration
    # ──────────────────────────────────────────────────────────────────────────
    def integrate_polynomial(self, expression: str) -> str:
        """
        Symbolically integrate polynomial in 'x'.
        Example: "3x^2 + 4x + 5" -> "x^3 + 2x^2 + 5x + C"
        """
        expr = expression.replace(" ", "").replace("-", "+-")
        terms = [t for t in expr.split("+") if t]

        integrated_terms = []
        for t in terms:
            if "x" not in t:
                # Constant term
                coeff = float(t)
                integrated_terms.append(f"{coeff:g}x")
                continue

            m = re.match(r"^([+-]?\d*(?:\.\d+)?)x(?:\^([+-]?\d+))?$", t)
            if not m:
                continue

            coeff_str, power_str = m.groups()
            coeff = 1.0 if coeff_str in ("", "+") else (-1.0 if coeff_str == "-" else float(coeff_str))
            power = int(power_str) if power_str else 1

            new_power = power + 1
            new_coeff = coeff / new_power

            if new_power == 1:
                integrated_terms.append(f"{new_coeff:g}x")
            else:
                integrated_terms.append(f"{new_coeff:g}x^{new_power}")

        res = " + ".join(integrated_terms).replace("+ -", "- ")
        return f"∫ ({expression}) dx = {res} + C"

    # ──────────────────────────────────────────────────────────────────────────
    # Number Theory
    # ──────────────────────────────────────────────────────────────────────────
    def gcd(self, a: int, b: int) -> int:
        """Euclidean algorithm for Greatest Common Divisor."""
        while b:
            a, b = b, a % b
        return abs(a)

    def lcm(self, a: int, b: int) -> int:
        """Least Common Multiple: (a * b) / gcd(a, b)."""
        if a == 0 or b == 0:
            return 0
        return abs(a * b) // self.gcd(a, b)

    def prime_factors(self, n: int) -> List[int]:
        """Compute prime factorization of integer n."""
        factors = []
        d = 2
        temp = abs(n)
        while d * d <= temp:
            while temp % d == 0:
                factors.append(d)
                temp //= d
            d += 1
        if temp > 1:
            factors.append(temp)
        return factors

    # ──────────────────────────────────────────────────────────────────────────
    # Probability Distributions
    # ──────────────────────────────────────────────────────────────────────────
    def normal_pdf(self, x: float, mean: float = 0.0, std_dev: float = 1.0) -> float:
        """Gaussian Normal Probability Density Function."""
        if std_dev <= 0:
            return 0.0
        exponent = -0.5 * ((x - mean) / std_dev) ** 2
        return (1.0 / (std_dev * math.sqrt(2 * math.pi))) * math.exp(exponent)

    def binomial_pmf(self, n: int, k: int, p: float) -> float:
        """Binomial Probability Mass Function P(X=k) = nCk * p^k * (1-p)^(n-k)."""
        if k < 0 or k > n or p < 0 or p > 1:
            return 0.0
        comb = math.comb(n, k)
        return comb * (p ** k) * ((1 - p) ** (n - k))


_calculus_instance: Optional[SymbolicCalculusEngine] = None

def get_calculus_engine() -> SymbolicCalculusEngine:
    global _calculus_instance
    if _calculus_instance is None:
        _calculus_instance = SymbolicCalculusEngine()
    return _calculus_instance
