"""
================================================================================
                    JARVIS CLIPBOARD & TYPING AUTOMATION
================================================================================
Clipboard reader, text snippet injector, clipboard history buffer, and
voice-dictated clipboard automation using pyperclip / ctypes.
================================================================================
"""

import time
from typing import List, Optional
from collections import deque

try:
    import pyperclip
    _PYPERCLIP_AVAILABLE = True
except ImportError:
    _PYPERCLIP_AVAILABLE = False

try:
    import pyautogui
    _PYAUTOGUI_AVAILABLE = True
except ImportError:
    _PYAUTOGUI_AVAILABLE = False

from jarvis.core.logger import get_logger


class ClipboardManager:
    """Manages clipboard read, write, history stack, and automated typing."""

    _instance: Optional["ClipboardManager"] = None

    def __new__(cls) -> "ClipboardManager":
        if cls._instance is None:
            cls._instance = super(ClipboardManager, cls).__new__(cls)
            cls._instance._init_mgr()
        return cls._instance

    def _init_mgr(self) -> None:
        self.logger = get_logger()
        self._history: deque = deque(maxlen=20)

    def get_text(self) -> str:
        """Fetch current text from clipboard."""
        if not _PYPERCLIP_AVAILABLE:
            return ""
        try:
            content = pyperclip.paste()
            if content and content not in self._history:
                self._history.append(content)
            return content
        except Exception as e:
            self.logger.error(f"Error reading clipboard: {e}", "CLIPBOARD")
            return ""

    def set_text(self, text: str) -> bool:
        """Write text to clipboard."""
        if not _PYPERCLIP_AVAILABLE:
            return False
        try:
            pyperclip.copy(text)
            self._history.append(text)
            self.logger.info("Copied text to clipboard.", "CLIPBOARD")
            return True
        except Exception as e:
            self.logger.error(f"Error copying to clipboard: {e}", "CLIPBOARD")
            return False

    def paste_into_active_window(self) -> bool:
        """Simulate Ctrl+V to paste into current focused field."""
        if _PYAUTOGUI_AVAILABLE:
            pyautogui.hotkey('ctrl', 'v')
            return True
        return False

    def type_text(self, text: str, interval: float = 0.02) -> bool:
        """Type out string as simulated keyboard keypresses."""
        if _PYAUTOGUI_AVAILABLE:
            pyautogui.write(text, interval=interval)
            return True
        return False

    def get_recent_history(self) -> List[str]:
        return list(self._history)


def get_clipboard() -> ClipboardManager:
    return ClipboardManager()
