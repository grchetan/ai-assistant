"""
================================================================================
                    JARVIS EXECUTIVE BRIEFING ANNOUNCER
================================================================================
Synthesizes comprehensive contextual audio briefings:
  - Time-sensitive formal greeting and calendar date
  - Local weather conditions and temperature
  - Hardware health metrics (CPU, RAM, Battery charge)
  - Pending actionable To-Do items
  - Top breaking tech headline
  - Inspiring technological motivation thought
================================================================================
"""

import time
import random
from typing import Dict, Any

from jarvis.core.logger import get_logger
from jarvis.system.hardware_monitor import get_hardware_monitor
from jarvis.plugins.weather_plugin import WeatherPlugin
from jarvis.plugins.news_plugin import NewsPlugin
from jarvis.automation.notes_todo import get_notes_manager

QUOTES = [
    "The best way to predict the future is to invent it. — Alan Kay",
    "Simplicity is the soul of efficiency. — Austin Freeman",
    "Code is like humor. When you have to explain it, it's bad. — Cory House",
    "Any sufficiently advanced technology is indistinguishable from magic. — Arthur C. Clarke",
    "Talk is cheap. Show me the code. — Linus Torvalds"
]


class ExecutiveBriefing:
    """Aggregates all system components into a master spoken briefing."""

    def __init__(self) -> None:
        self.logger = get_logger()
        self.hardware = get_hardware_monitor()
        self.weather_plugin = WeatherPlugin()
        self.news_plugin = NewsPlugin()
        self.notes_mgr = get_notes_manager()

    def generate_full_briefing(self, user_name: str = "Sir", city: str = "Delhi") -> str:
        """Construct multi-part comprehensive morning/daily briefing text."""
        self.logger.info("Assembling Executive Briefing speech...", "BRIEFING")

        parts = []

        # 1. Greeting & Date
        hour = time.localtime().tm_hour
        salutation = "Good morning" if hour < 12 else ("Good afternoon" if hour < 17 else "Good evening")
        date_str = time.strftime("%A, %d of %B")
        parts.append(f"{salutation} {user_name}! Today is {date_str}.")

        # 2. Weather
        try:
            success, w_text = self.weather_plugin.execute("", {"city": city})
            if success:
                parts.append(w_text)
        except Exception:
            pass

        # 3. Hardware status
        try:
            hw_text = self.hardware.get_summary_speech()
            parts.append(hw_text)
        except Exception:
            pass

        # 4. Pending Tasks
        try:
            todo_text = self.notes_mgr.list_todos()
            parts.append(todo_text)
        except Exception:
            pass

        # 5. Daily Motivation Quote
        parts.append(f"Thought for today: '{random.choice(QUOTES)}'")
        parts.append("All quantum systems are ready. What is your command, sir?")

        return " ".join(parts)


def get_executive_briefing() -> ExecutiveBriefing:
    return ExecutiveBriefing()
