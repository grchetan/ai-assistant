"""
================================================================================
                    JARVIS HABIT & PRODUCTIVITY STREAK TRACKER
================================================================================
Personal habit, health, and developer wellness keeper backed by SQLite:
  - Daily hydration goal (liters logged)
  - Coding session hours logged
  - Workout & physical fitness check-ins
  - Consecutive daily streak analytics
================================================================================
"""

import time
import sqlite3
from typing import Dict, List, Any, Tuple, Optional
from pathlib import Path

from jarvis.core.logger import get_logger

HABIT_DB_PATH = Path(__file__).resolve().parent.parent / "data" / "habits.db"


class HabitTracker:
    """Manages daily wellness and productivity habits."""

    def __init__(self) -> None:
        self.logger = get_logger()
        self._init_db()

    def _init_db(self) -> None:
        try:
            conn = sqlite3.connect(str(HABIT_DB_PATH))
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS habits (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date_str TEXT NOT NULL,
                    water_liters REAL DEFAULT 0.0,
                    coding_hours REAL DEFAULT 0.0,
                    workout_done INTEGER DEFAULT 0,
                    reading_pages INTEGER DEFAULT 0
                )
            """)
            conn.commit()
            conn.close()
        except Exception as e:
            self.logger.error(f"Error initializing habit DB: {e}", "HABIT")

    def _get_today_date(self) -> str:
        return time.strftime("%Y-%m-%d")

    def log_water(self, liters: float = 0.5) -> str:
        """Add water intake."""
        today = self._get_today_date()
        try:
            conn = sqlite3.connect(str(HABIT_DB_PATH))
            cursor = conn.cursor()
            cursor.execute("SELECT id, water_liters FROM habits WHERE date_str = ?", (today,))
            row = cursor.fetchone()

            if row:
                new_total = row[1] + liters
                cursor.execute("UPDATE habits SET water_liters = ? WHERE id = ?", (new_total, row[0]))
            else:
                new_total = liters
                cursor.execute("INSERT INTO habits (date_str, water_liters) VALUES (?, ?)", (today, new_total))

            conn.commit()
            conn.close()
            return f"Great job sir! {liters}L water logged. Today's total: {new_total:.1f} liters."
        except Exception as e:
            return f"Error logging water: {e}"

    def log_coding_hours(self, hours: float = 1.0) -> str:
        """Add productive coding time."""
        today = self._get_today_date()
        try:
            conn = sqlite3.connect(str(HABIT_DB_PATH))
            cursor = conn.cursor()
            cursor.execute("SELECT id, coding_hours FROM habits WHERE date_str = ?", (today,))
            row = cursor.fetchone()

            if row:
                new_total = row[1] + hours
                cursor.execute("UPDATE habits SET coding_hours = ? WHERE id = ?", (new_total, row[0]))
            else:
                new_total = hours
                cursor.execute("INSERT INTO habits (date_str, coding_hours) VALUES (?, ?)", (today, new_total))

            conn.commit()
            conn.close()
            return f"Logged {hours} hours of coding! Today's total: {new_total:.1f} hours."
        except Exception as e:
            return f"Error logging coding: {e}"

    def get_today_summary(self) -> str:
        """Spoken summary of today's progress."""
        today = self._get_today_date()
        try:
            conn = sqlite3.connect(str(HABIT_DB_PATH))
            cursor = conn.cursor()
            cursor.execute("SELECT water_liters, coding_hours, workout_done FROM habits WHERE date_str = ?", (today,))
            row = cursor.fetchone()
            conn.close()

            if not row:
                return "Sir, aaj abhi tak koi habits log nahi hui hain. Water ya coding log karein!"

            water, coding, workout = row
            workout_str = "Workout done ✅" if workout else "Workout pending ⏳"
            return f"Sir, aaj aapne {water:.1f}L paani piya hai, {coding:.1f} hours code kiya hai, aur {workout_str}."
        except Exception:
            return "Could not retrieve habit stats."


def get_habit_tracker() -> HabitTracker:
    return HabitTracker()
