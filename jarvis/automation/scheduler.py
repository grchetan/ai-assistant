"""
================================================================================
                    JARVIS SCHEDULER, TIMERS & ALARMS
================================================================================
Background task scheduler handling countdown timers, specific-time alarms,
recurring productivity alerts, and spoken notifications.
================================================================================
"""

import time
import threading
from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass, field

from jarvis.core.logger import get_logger
from jarvis.audio.sound_fx import get_sound_fx


@dataclass
class ScheduledTask:
    id: int
    label: str
    target_time: float
    callback: Optional[Callable[[], None]] = None
    recurring_secs: float = 0.0
    is_active: bool = True


class TaskScheduler:
    """Manages scheduled alarms and countdown timers."""

    _instance: Optional["TaskScheduler"] = None
    _lock = threading.RLock()

    def __new__(cls) -> "TaskScheduler":
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(TaskScheduler, cls).__new__(cls)
                cls._instance._init_scheduler()
            return cls._instance

    def _init_scheduler(self) -> None:
        self.logger = get_logger()
        self.sfx = get_sound_fx()
        self._tasks: List[ScheduledTask] = []
        self._task_counter = 0
        self._running = True

        self._thread = threading.Thread(
            target=self._scheduler_loop,
            name="JarvisSchedulerThread",
            daemon=True
        )
        self._thread.start()

    def _scheduler_loop(self) -> None:
        while self._running:
            now = time.time()
            triggered = []
            with self._lock:
                for task in self._tasks:
                    if task.is_active and now >= task.target_time:
                        triggered.append(task)
                        if task.recurring_secs > 0:
                            task.target_time = now + task.recurring_secs
                        else:
                            task.is_active = False

            for task in triggered:
                self.logger.success(f"Alarm triggered: '{task.label}'", "SCHEDULER")
                self.sfx.play_alert()
                if task.callback:
                    try:
                        task.callback()
                    except Exception as e:
                        self.logger.error(f"Error in task callback: {e}", "SCHEDULER")

            time.sleep(0.5)

    def set_timer(self, minutes: float, label: str = "Timer", callback: Optional[Callable[[], None]] = None) -> int:
        """Set a countdown timer in minutes."""
        with self._lock:
            self._task_counter += 1
            task_id = self._task_counter
            target = time.time() + (minutes * 60.0)
            task = ScheduledTask(
                id=task_id,
                label=label,
                target_time=target,
                callback=callback
            )
            self._tasks.append(task)
            self.logger.info(f"Timer #{task_id} set for {minutes:.1f} minutes ('{label}').", "SCHEDULER")
            return task_id

    def list_active_timers(self) -> List[Dict[str, Any]]:
        with self._lock:
            now = time.time()
            return [
                {
                    "id": t.id,
                    "label": t.label,
                    "remaining_seconds": max(0, int(t.target_time - now))
                }
                for t in self._tasks if t.is_active
            ]

    def cancel_timer(self, task_id: int) -> bool:
        with self._lock:
            for t in self._tasks:
                if t.id == task_id:
                    t.is_active = False
                    return True
        return False


def get_scheduler() -> TaskScheduler:
    return TaskScheduler()
