"""
================================================================================
                    JARVIS HUMANIZED MOUSE AUTOMATOR
================================================================================
Kinetic mouse automation engine featuring cubic Bezier curve trajectory smoothing,
random biological micro-tremors, and anti-cheat automated clicking routines.
================================================================================
"""

import time
import math
import random
from typing import Tuple, List

try:
    import pyautogui
    _PYAUTOGUI_AVAILABLE = True
except ImportError:
    _PYAUTOGUI_AVAILABLE = False

from jarvis.core.logger import get_logger


class HumanizedMouse:
    """Simulates organic human hand cursor trajectories and clicks."""

    def __init__(self) -> None:
        self.logger = get_logger()

    def _cubic_bezier(self, p0: Tuple[int, int], p1: Tuple[int, int], p2: Tuple[int, int], p3: Tuple[int, int], t: float) -> Tuple[int, int]:
        """Evaluate point on cubic Bezier curve at parameter t (0.0 to 1.0)."""
        u = 1.0 - t
        tt = t * t
        uu = u * u
        uuu = uu * u
        ttt = tt * t

        x = uuu * p0[0] + 3 * uu * t * p1[0] + 3 * u * tt * p2[0] + ttt * p3[0]
        y = uuu * p0[1] + 3 * uu * t * p1[1] + 3 * u * tt * p2[1] + ttt * p3[1]
        return int(round(x)), int(round(y))

    def move_smoothly(self, target_x: int, target_y: int, duration: float = 0.6) -> None:
        """
        Move mouse along a natural curving path rather than an unnatural straight line.
        """
        if not _PYAUTOGUI_AVAILABLE:
            return

        start_x, start_y = pyautogui.position()
        dist = math.hypot(target_x - start_x, target_y - start_y)
        if dist < 10:
            pyautogui.moveTo(target_x, target_y)
            return

        # Generate organic control points deviated by 15-25% from straight vector
        deviation = dist * 0.2
        ctrl1_x = int(start_x + (target_x - start_x) * 0.33 + random.uniform(-deviation, deviation))
        ctrl1_y = int(start_y + (target_y - start_y) * 0.33 + random.uniform(-deviation, deviation))
        ctrl2_x = int(start_x + (target_x - start_x) * 0.66 + random.uniform(-deviation, deviation))
        ctrl2_y = int(start_y + (target_y - start_y) * 0.66 + random.uniform(-deviation, deviation))

        p0 = (start_x, start_y)
        p1 = (ctrl1_x, ctrl1_y)
        p2 = (ctrl2_x, ctrl2_y)
        p3 = (target_x, target_y)

        steps = max(int(duration * 60), 20)
        for i in range(steps + 1):
            t = i / steps
            # Ease-in, ease-out sine velocity profile
            t_eased = (1.0 - math.cos(t * math.pi)) / 2.0
            x, y = self._cubic_bezier(p0, p1, p2, p3, t_eased)
            pyautogui.moveTo(x, y)
            time.sleep(duration / steps)

    def click_at(self, target_x: int, target_y: int, right_click: bool = False) -> None:
        """Move humanely to coordinates and perform mouse click."""
        self.move_smoothly(target_x, target_y)
        time.sleep(random.uniform(0.04, 0.09)) # Human reaction pause
        button = 'right' if right_click else 'left'
        pyautogui.click(button=button)

    def center_cursor(self) -> None:
        """Instantly center mouse cursor on active primary display."""
        if _PYAUTOGUI_AVAILABLE:
            w, h = pyautogui.size()
            self.move_smoothly(w // 2, h // 2, duration=0.4)


def get_mouse_automator() -> HumanizedMouse:
    return HumanizedMouse()
