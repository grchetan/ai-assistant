"""
================================================================================
                    JARVIS WINDOW & DESKTOP MANAGER
================================================================================
Controls open application windows on Windows using native Win32 User32 APIs
and PyAutoGUI: minimize all, maximize, snap to split-screen, close active,
and focus windows by title.
================================================================================
"""

import time
import ctypes
from typing import List, Dict, Optional, Any

try:
    import pyautogui
    _PYAUTOGUI_AVAILABLE = True
except ImportError:
    _PYAUTOGUI_AVAILABLE = False

from jarvis.core.logger import get_logger

user32 = ctypes.windll.user32


class WindowManager:
    """Manipulates desktop application windows."""

    def __init__(self) -> None:
        self.logger = get_logger()

    def minimize_all(self) -> None:
        """Show Desktop by minimizing all active windows (Win+D)."""
        self.logger.info("Minimizing all windows (Show Desktop).", "WINDOW")
        if _PYAUTOGUI_AVAILABLE:
            pyautogui.hotkey('win', 'd')
        else:
            # Fallback to Shell32 ToggleDesktop
            ctypes.windll.shell32.ToggleDesktop()

    def maximize_active(self) -> None:
        """Maximize the currently active focused window (Win+Up)."""
        self.logger.info("Maximizing active window.", "WINDOW")
        if _PYAUTOGUI_AVAILABLE:
            pyautogui.hotkey('win', 'up')
        else:
            hwnd = user32.GetForegroundWindow()
            user32.ShowWindow(hwnd, 3) # SW_MAXIMIZE = 3

    def close_active(self) -> None:
        """Gracefully close the foreground window (Alt+F4)."""
        self.logger.info("Closing active window.", "WINDOW")
        if _PYAUTOGUI_AVAILABLE:
            pyautogui.hotkey('alt', 'f4')
        else:
            hwnd = user32.GetForegroundWindow()
            # Send WM_CLOSE (0x0010)
            user32.PostMessageA(hwnd, 0x0010, 0, 0)

    def snap_left(self) -> None:
        """Snap the active window to the left half of the screen (Win+Left)."""
        self.logger.info("Snapping window to left half.", "WINDOW")
        if _PYAUTOGUI_AVAILABLE:
            pyautogui.hotkey('win', 'left')

    def snap_right(self) -> None:
        """Snap the active window to the right half of the screen (Win+Right)."""
        self.logger.info("Snapping window to right half.", "WINDOW")
        if _PYAUTOGUI_AVAILABLE:
            pyautogui.hotkey('win', 'right')

    def switch_window(self) -> None:
        """Quick task switch to previous application (Alt+Tab)."""
        self.logger.info("Switching active window.", "WINDOW")
        if _PYAUTOGUI_AVAILABLE:
            pyautogui.hotkey('alt', 'tab')

    def get_active_window_title(self) -> str:
        """Get the title text of the currently focused window."""
        hwnd = user32.GetForegroundWindow()
        length = user32.GetWindowTextLengthW(hwnd)
        if length > 0:
            buff = ctypes.create_unicode_buffer(length + 1)
            user32.GetWindowTextW(hwnd, buff, length + 1)
            return buff.value
        return "Desktop"

    def list_visible_windows(self) -> List[Dict[str, Any]]:
        """Enumerate all visible top-level windows with title strings."""
        windows = []

        def _enum_callback(hwnd, extra):
            if user32.IsWindowVisible(hwnd):
                length = user32.GetWindowTextLengthW(hwnd)
                if length > 0:
                    buff = ctypes.create_unicode_buffer(length + 1)
                    user32.GetWindowTextW(hwnd, buff, length + 1)
                    title = buff.value.strip()
                    if title and title not in ["Program Manager", "Default IME", "MSCTFIME UI"]:
                        windows.append({"hwnd": hwnd, "title": title})
            return True

        WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)
        user32.EnumWindows(WNDENUMPROC(_enum_callback), 0)
        return windows

    def focus_window_by_name(self, query: str) -> bool:
        """Find and bring a window matching query substring to the foreground."""
        q_lower = query.lower()
        windows = self.list_visible_windows()
        for w in windows:
            if q_lower in w["title"].lower():
                hwnd = w["hwnd"]
                user32.ShowWindow(hwnd, 9) # SW_RESTORE
                user32.SetForegroundWindow(hwnd)
                self.logger.success(f'Focused window: "{w["title"]}"', "WINDOW")
                return True
        return False


def get_window_manager() -> WindowManager:
    return WindowManager()
