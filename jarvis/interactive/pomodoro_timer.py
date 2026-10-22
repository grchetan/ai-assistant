"""
================================================================================
                    JARVIS POMODORO PRODUCTIVITY COACH
================================================================================
Focus interval coach implementing the standard Pomodoro technique:
  - 25-minute uninterrupted work sprints
  - 5-minute physical rest & hydration breaks
  - 15-minute long restorative breaks after 4 cycles
  - Audio chimes and spoken transition alerts
================================================================================
"""

import time
import threading
from typing import Optional, Callable, Dict, Any
from enum import Enum

from jarvis.core.logger import get_logger
from jarvis.audio.sound_fx import get_sound_fx


class PomodoroPhase(Enum):
    IDLE        = "IDLE"
    WORK        = "WORK"
    SHORT_BREAK = "SHORT_BREAK"
    LONG_BREAK  = "LONG_BREAK"


class PomodoroCoach:
    """Manages Pomodoro focus cycles and break reminders."""

    _instance: Optional["PomodoroCoach"] = None
    _lock = threading.RLock()

    def __new__(cls) -> "PomodoroCoach":
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(PomodoroCoach, cls).__new__(cls)
                cls._instance._init_coach()
            return cls._instance

    def _init_coach(self) -> None:
        self.logger = get_logger()
        self.sfx = get_sound_fx()
        self.phase = PomodoroPhase.IDLE
        self.completed_cycles = 0
        self._target_time = 0.0
        self._is_active = False
        self._thread: Optional[threading.Thread] = None
        self._spoken_callback: Optional[Callable[[str], None]] = None

    def set_callback(self, cb: Callable[[str], None]) -> None:
        self._spoken_callback = cb

    def start_session(self, work_mins: int = 25) -> str:
        """Begin a new focus work sprint."""
        self._is_active = True
        self.phase = PomodoroPhase.WORK
        self._target_time = time.time() + (work_mins * 60)

        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()

        msg = f"Pomodoro session started sir! {work_mins} minutes of focused deep work. No distractions!"
        self.logger.info(msg, "POMODORO")
        self.sfx.play_success()
        return msg

    def stop_session(self) -> str:
        """Halt active Pomodoro timer."""
        self._is_active = False
        self.phase = PomodoroPhase.IDLE
        return "Pomodoro session stopped sir."

    def _run_loop(self) -> None:
        while self._is_active:
            now = time.time()
            if now >= self._target_time:
                self.sfx.play_alert()
                if self.phase == PomodoroPhase.WORK:
                    self.completed_cycles += 1
                    if self.completed_cycles % 4 == 0:
                        self.phase = PomodoroPhase.LONG_BREAK
                        self._target_time = now + (15 * 60)
                        msg = "Fantastic work sir! 4 Pomodoro cycles completed. Enjoy a 15 minute long break!"
                    else:
                        self.phase = PomodoroPhase.SHORT_BREAK
                        self._target_time = now + (5 * 60)
                        msg = "Pomodoro work cycle complete sir! Take a 5 minute rest and drink some water."

                    self.logger.success(msg, "POMODORO")
                    if self._spoken_callback:
                        self._spoken_callback(msg)

                elif self.phase in (PomodoroPhase.SHORT_BREAK, PomodoroPhase.LONG_BREAK):
                    self.phase = PomodoroPhase.WORK
                    self._target_time = now + (25 * 60)
                    msg = "Break is over sir! Ready for the next 25-minute focus session?"
                    self.logger.info(msg, "POMODORO")
                    if self._spoken_callback:
                        self._spoken_callback(msg)

            time.sleep(1.0)

    def get_status(self) -> Dict[str, Any]:
        remaining = max(0, int(self._target_time - time.time())) if self._is_active else 0
        return {
            "phase": self.phase.value,
            "completed_cycles": self.completed_cycles,
            "remaining_seconds": remaining
        }


def get_pomodoro_coach() -> PomodoroCoach:
    return PomodoroCoach()
