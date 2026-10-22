"""
================================================================================
                    JARVIS UNIFIED SYSTEM LOGGER
================================================================================
Multi-destination asynchronous logger supporting formatted ANSI terminal output,
rotating disk log files, and an in-memory ring buffer for live HUD terminal UI.
================================================================================
"""

import os
import sys
import time
import logging
import threading
from typing import List, Dict, Optional, Callable
from collections import deque
from pathlib import Path

from jarvis.core.events import get_event_bus, EventType, Priority

LOGS_DIR = Path(__file__).resolve().parent.parent.parent / "jarvis" / "data" / "logs"
LOGS_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE_PATH = LOGS_DIR / f"jarvis_{time.strftime('%Y%m%d')}.log"

# ANSI Terminal Colors
ANSI_RESET  = "\033[0m"
ANSI_CYAN   = "\033[36m"
ANSI_GREEN  = "\033[32m"
ANSI_YELLOW = "\033[33m"
ANSI_RED    = "\033[31m"
ANSI_PURPLE = "\033[35m"
ANSI_GRAY   = "\033[90m"
ANSI_BOLD   = "\033[1m"


class LogLevel:
    DEBUG    = "DEBUG"
    INFO     = "INFO"
    SUCCESS  = "SUCCESS"
    WARNING  = "WARNING"
    ERROR    = "ERROR"
    CRITICAL = "CRITICAL"


class JarvisLogger:
    """Thread-safe multi-sink logger engine."""
    
    _instance: Optional["JarvisLogger"] = None
    _lock = threading.RLock()

    def __new__(cls) -> "JarvisLogger":
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(JarvisLogger, cls).__new__(cls)
                cls._instance._initialized = False
            return cls._instance

    def __init__(self, max_buffer_lines: int = 500) -> None:
        if getattr(self, "_initialized", False):
            return

        self._max_buffer = max_buffer_lines
        self._buffer: deque = deque(maxlen=max_buffer_lines)
        self._ui_callbacks: List[Callable[[str, str, str], None]] = []
        self._file_handle = None
        self._open_file()
        self._initialized = True

    def _open_file(self) -> None:
        try:
            self._file_handle = open(LOG_FILE_PATH, "a", encoding="utf-8", buffering=1)
        except Exception as e:
            print(f"[JarvisLogger] Could not open log file: {e}")

    def add_ui_sink(self, callback: Callable[[str, str, str], None]) -> None:
        """Register a callback for GUI log updates: callback(timestamp, message, color_hex)."""
        with self._lock:
            if callback not in self._ui_callbacks:
                self._ui_callbacks.append(callback)

    def log(
        self,
        level: str,
        message: str,
        category: str = "SYSTEM",
        color_hex: Optional[str] = None
    ) -> None:
        """Core log emitter."""
        timestamp = time.strftime("%H:%M:%S")
        date_str = time.strftime("%Y-%m-%d")

        # Map level to visual attributes
        color_map = {
            LogLevel.DEBUG:    ("#556677", ANSI_GRAY),
            LogLevel.INFO:     ("#00f0ff", ANSI_CYAN),
            LogLevel.SUCCESS:  ("#00ff99", ANSI_GREEN),
            LogLevel.WARNING:  ("#ffaa00", ANSI_YELLOW),
            LogLevel.ERROR:    ("#ff3355", ANSI_RED),
            LogLevel.CRITICAL: ("#ff0055", ANSI_PURPLE),
        }
        hex_col, ansi_col = color_map.get(level, ("#a0b4cc", ANSI_RESET))
        effective_hex = color_hex or hex_col

        formatted_console = (
            f"{ANSI_GRAY}[{timestamp}]{ANSI_RESET} "
            f"{ansi_col}[{level:<7}]{ANSI_RESET} "
            f"{ANSI_PURPLE}[{category:<8}]{ANSI_RESET} "
            f"{message}"
        )

        formatted_plain = f"[{date_str} {timestamp}] [{level:<7}] [{category:<8}] {message}\n"

        with self._lock:
            # 1. Print to stdout
            print(formatted_console)

            # 2. Append to disk log
            if self._file_handle:
                try:
                    self._file_handle.write(formatted_plain)
                except Exception:
                    pass

            # 3. Store in memory ring buffer
            entry = {
                "timestamp": timestamp,
                "level": level,
                "category": category,
                "message": message,
                "color": effective_hex
            }
            self._buffer.append(entry)

        # 4. Notify UI sinks
        for cb in self._ui_callbacks:
            try:
                cb(timestamp, f"[{category}] {message}", effective_hex)
            except Exception:
                pass

        # 5. Broadcast to EventBus
        try:
            bus = get_event_bus()
            bus.publish(
                EventType.UI_LOG_MESSAGE,
                data={"timestamp": timestamp, "message": message, "color": effective_hex, "level": level},
                priority=Priority.LOW if level == LogLevel.DEBUG else Priority.NORMAL
            )
        except Exception:
            pass

    def debug(self, msg: str, category: str = "DEBUG") -> None:
        self.log(LogLevel.DEBUG, msg, category)

    def info(self, msg: str, category: str = "INFO", color: Optional[str] = None) -> None:
        self.log(LogLevel.INFO, msg, category, color)

    def success(self, msg: str, category: str = "SUCCESS") -> None:
        self.log(LogLevel.SUCCESS, msg, category, "#00ff99")

    def warning(self, msg: str, category: str = "WARN") -> None:
        self.log(LogLevel.WARNING, msg, category, "#ffaa00")

    def error(self, msg: str, category: str = "ERROR") -> None:
        self.log(LogLevel.ERROR, msg, category, "#ff3355")

    def critical(self, msg: str, category: str = "CRIT") -> None:
        self.log(LogLevel.CRITICAL, msg, category, "#ff007f")

    def get_recent_logs(self, limit: int = 100) -> List[Dict[str, str]]:
        with self._lock:
            return list(self._buffer)[-limit:]

    def close(self) -> None:
        with self._lock:
            if self._file_handle:
                try:
                    self._file_handle.flush()
                    self._file_handle.close()
                except Exception:
                    pass


def get_logger() -> JarvisLogger:
    return JarvisLogger()
