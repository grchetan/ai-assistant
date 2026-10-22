"""
================================================================================
                    JARVIS ARC REACTOR & AUDIO HUD CANVAS
================================================================================
High-performance 60 FPS Tkinter vector canvas rendering:
  - Concentric rotating Arc Reactor energy rings with particle physics
  - Reactive multi-harmonic audio waveform visualizer tied to live microphone RMS
  - Radar sweep scanlines and pulsing quantum core
================================================================================
"""

import math
import time
import tkinter as tk
from typing import Dict, Any, Optional

from jarvis.core.state import AssistantMode


class ArcReactorHUD(tk.Canvas):
    """Futuristic Iron Man Arc Reactor and Audio Reactive Canvas."""

    def __init__(self, master, width: int = 340, height: int = 340, **kwargs):
        super().__init__(master, width=width, height=height, highlightthickness=0, **kwargs)
        self.width = width
        self.height = height
        self.cx = width // 2
        self.cy = height // 2

        # Color themes (defaults to Arc Cyan)
        self.ring_color = "#00f0ff"
        self.core_color = "#33f5ff"
        self.dim_color  = "#0a2d4d"
        self.bg_color   = "#040914"

        # Animation states
        self.angle_outer = 0.0
        self.angle_inner = 0.0
        self.pulse_phase = 0.0
        self.current_rms = 0.0
        self.current_mode = AssistantMode.STANDBY
        self._is_animating = True

        self.configure(bg=self.bg_color)
        self._start_animation()

    def set_theme_colors(self, ring_color: str, core_color: str, bg_color: str) -> None:
        self.ring_color = ring_color
        self.core_color = core_color
        self.bg_color   = bg_color
        self.configure(bg=bg_color)

    def update_telemetry(self, rms: float, mode: AssistantMode) -> None:
        """Update live audio energy and assistant state."""
        # Exponential smoothing for RMS
        self.current_rms = self.current_rms * 0.7 + rms * 0.3
        self.current_mode = mode

    def _start_animation(self) -> None:
        """Render loop running at ~50-60 FPS."""
        self._draw_frame()

    def _draw_frame(self) -> None:
        if not self._is_animating:
            return

        self.delete("all")
        cx, cy = self.cx, self.cy

        # Determine rotation speeds based on mode
        speed = 0.03
        if self.current_mode == AssistantMode.LISTENING:
            speed = 0.06
        elif self.current_mode == AssistantMode.PROCESSING:
            speed = 0.12
        elif self.current_mode == AssistantMode.SPEAKING:
            speed = 0.05

        self.angle_outer = (self.angle_outer + speed) % (2 * math.pi)
        self.angle_inner = (self.angle_inner - speed * 1.4) % (2 * math.pi)
        self.pulse_phase = (self.pulse_phase + 0.05) % (2 * math.pi)

        # Pulse scale factor based on mode & mic energy
        rms_boost = min(self.current_rms / 600.0, 1.2)
        pulse = 1.0 + 0.08 * math.sin(self.pulse_phase) + (rms_boost * 0.25)

        # 1. Background decorative grid circles
        r_grid = 150
        self.create_oval(cx - r_grid, cy - r_grid, cx + r_grid, cy + r_grid,
                         outline=self.dim_color, width=1, dash=(2, 6))

        # 2. Outer segmented rotating ring
        r_outer = int(120 * pulse)
        num_segments = 16
        seg_len = (2 * math.pi) / num_segments
        for i in range(num_segments):
            start_ang = self.angle_outer + i * seg_len
            end_ang = start_ang + seg_len * 0.55
            x1 = cx + r_outer * math.cos(start_ang)
            y1 = cy + r_outer * math.sin(start_ang)
            x2 = cx + r_outer * math.cos(end_ang)
            y2 = cy + r_outer * math.sin(end_ang)
            self.create_line(x1, y1, x2, y2, fill=self.ring_color, width=3)

        # 3. Middle counter-rotating notched ring
        r_mid = int(85 * pulse)
        num_notches = 8
        for i in range(num_notches):
            ang = self.angle_inner + i * (2 * math.pi / num_notches)
            x1 = cx + (r_mid - 8) * math.cos(ang)
            y1 = cy + (r_mid - 8) * math.sin(ang)
            x2 = cx + (r_mid + 8) * math.cos(ang)
            y2 = cy + (r_mid + 8) * math.sin(ang)
            self.create_line(x1, y1, x2, y2, fill=self.ring_color, width=2)

        self.create_oval(cx - r_mid, cy - r_mid, cx + r_mid, cy + r_mid,
                         outline=self.ring_color, width=1)

        # 4. Audio reactive waveform circle
        r_wave = 55 + int(rms_boost * 30)
        num_wave_points = 32
        coords = []
        for i in range(num_wave_points + 1):
            ang = i * (2 * math.pi / num_wave_points)
            # Harmonic noise simulation
            offset = 6 * math.sin(ang * 4 + self.pulse_phase * 2) * (rms_boost + 0.2)
            r = r_wave + offset
            px = cx + r * math.cos(ang)
            py = cy + r * math.sin(ang)
            coords.extend([px, py])

        if len(coords) >= 6:
            self.create_polygon(coords, fill="", outline=self.core_color, width=2)

        # 5. Glowing Central Reactor Core
        r_core = int(24 + 6 * math.sin(self.pulse_phase) + rms_boost * 15)
        # Core color shifts by state
        core_fill = self.core_color
        if self.current_mode == AssistantMode.LISTENING:
            core_fill = "#ffaa00"
        elif self.current_mode == AssistantMode.PROCESSING:
            core_fill = "#00e1ff"
        elif self.current_mode == AssistantMode.SPEAKING:
            core_fill = "#00ff99"

        self.create_oval(cx - r_core, cy - r_core, cx + r_core, cy + r_core,
                         fill=core_fill, outline="#ffffff", width=2)

        # 6. Central State Label
        state_text = self.current_mode.value
        self.create_text(cx, cy + r_outer + 25, text=f"• {state_text} •",
                         fill=self.ring_color, font=("Consolas", 10, "bold"))

        # Schedule next frame (60 FPS ~ 16ms)
        self.after(18, self._draw_frame)

    def stop(self) -> None:
        self._is_animating = False
