"""
================================================================================
                    JARVIS VOICE SHORTCUT & MACRO ENGINE
================================================================================
Configurable desktop workflow automation engine. Chains multiple voice intents,
keystrokes, terminal operations, and pauses into named triggers executable by
a single command (e.g. "run macro morning briefing").
================================================================================
"""

import os
import json
import time
import threading
from typing import Dict, List, Any, Tuple, Optional, Callable
from pathlib import Path

from jarvis.core.logger import get_logger

MACROS_FILE = Path(__file__).resolve().parent.parent / "data" / "user_macros.json"

DEFAULT_MACROS: Dict[str, List[Dict[str, Any]]] = {
    "morning_routine": [
        {"action": "say", "text": "Good morning sir! Starting your daily routine."},
        {"action": "command", "cmd": "weather report"},
        {"action": "pause", "seconds": 1.5},
        {"action": "command", "cmd": "battery status"},
        {"action": "command", "cmd": "open chrome"}
    ],
    "clean_and_lock": [
        {"action": "command", "cmd": "minimize all"},
        {"action": "command", "cmd": "empty recycle bin"},
        {"action": "command", "cmd": "lock screen"}
    ],
    "dev_standup": [
        {"action": "command", "cmd": "open code"},
        {"action": "command", "cmd": "open terminal"},
        {"action": "command", "cmd": "git status"}
    ]
}


class MacroEngine:
    """Stores, loads, and executes multi-step desktop automation macros."""

    _instance: Optional["MacroEngine"] = None
    _lock = threading.RLock()

    def __new__(cls) -> "MacroEngine":
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(MacroEngine, cls).__new__(cls)
                cls._instance._init_macros()
            return cls._instance

    def _init_macros(self) -> None:
        self.logger = get_logger()
        self._macros: Dict[str, List[Dict[str, Any]]] = {}
        self._command_dispatcher: Optional[Callable[[str], None]] = None
        self._load()

    def set_dispatcher(self, dispatcher: Callable[[str], None]) -> None:
        self._command_dispatcher = dispatcher

    def _load(self) -> None:
        if MACROS_FILE.exists():
            try:
                with open(MACROS_FILE, "r", encoding="utf-8") as f:
                    self._macros = json.load(f)
            except Exception as e:
                self.logger.warning(f"Error loading macros file: {e}", "MACRO")
                self._macros = DEFAULT_MACROS.copy()
        else:
            self._macros = DEFAULT_MACROS.copy()
            self._save()

    def _save(self) -> None:
        try:
            with open(MACROS_FILE, "w", encoding="utf-8") as f:
                json.dump(self._macros, f, indent=2)
        except Exception as e:
            self.logger.error(f"Failed to persist macros: {e}", "MACRO")

    def register_macro(self, name: str, steps: List[Dict[str, Any]]) -> None:
        """Register a new custom sequence of automated steps."""
        key = name.lower().replace(" ", "_").strip()
        self._macros[key] = steps
        self._save()
        self.logger.success(f"Macro '{name}' registered with {len(steps)} steps.", "MACRO")

    def execute_macro(self, macro_name: str) -> Tuple[bool, str]:
        """Execute all steps within a named macro sequentially."""
        key = macro_name.lower().replace(" ", "_").replace("macro_", "").strip()
        steps = self._macros.get(key)

        if not steps:
            # Fuzzy match
            for k, v in self._macros.items():
                if key in k or k in key:
                    steps = v
                    key = k
                    break

        if not steps:
            return False, f"Sir, '{macro_name}' macro nahi mila."

        self.logger.info(f"Executing macro '{key}' ({len(steps)} steps)...", "MACRO")

        def _worker():
            for idx, step in enumerate(steps):
                action = step.get("action")
                if action == "command" and self._command_dispatcher:
                    cmd_text = step.get("cmd", "")
                    self._command_dispatcher(cmd_text)
                elif action == "pause":
                    secs = step.get("seconds", 1.0)
                    time.sleep(secs)
                elif action == "say" and self._command_dispatcher:
                    phrase = step.get("text", "")
                    self._command_dispatcher(f"echo {phrase}")
                time.sleep(0.5)

        threading.Thread(target=_worker, daemon=True).start()
        return True, f"Macro '{key}' execute ho raha hai sir."

    def list_macro_names(self) -> List[str]:
        return list(self._macros.keys())


def get_macro_engine() -> MacroEngine:
    return MacroEngine()
