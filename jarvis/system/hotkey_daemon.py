"""
================================================================================
                    JARVIS GLOBAL HOTKEY LISTENER DAEMON
================================================================================
Low-overhead background keyboard shortcut listener registering global system-wide
hotkeys (Ctrl+Alt+J for voice wake, Ctrl+Alt+M for mute, Ctrl+Alt+S for screen cap)
using Windows Win32 ctypes message pumping.
================================================================================
"""

import time
import ctypes
import threading
from typing import Dict, Callable, Optional

from jarvis.core.logger import get_logger

user32 = ctypes.windll.user32

# Modifiers
MOD_ALT     = 0x0001
MOD_CONTROL = 0x0002
MOD_SHIFT   = 0x0004
MOD_WIN     = 0x0008

# Key virtual codes
VK_J = 0x4A
VK_M = 0x4D
VK_S = 0x53
VK_D = 0x44
VK_Q = 0x51

# Hotkey IDs
HOTKEY_WAKE       = 101
HOTKEY_MUTE       = 102
HOTKEY_SCREENSHOT = 103
HOTKEY_DESKTOP    = 104
HOTKEY_QUIT       = 105


class HotkeyDaemon:
    """Manages system-wide keyboard shortcuts."""

    _instance: Optional["HotkeyDaemon"] = None
    _lock = threading.RLock()

    def __new__(cls) -> "HotkeyDaemon":
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(HotkeyDaemon, cls).__new__(cls)
                cls._instance._init_daemon()
            return cls._instance

    def _init_daemon(self) -> None:
        self.logger = get_logger()
        self._handlers: Dict[int, Callable[[], None]] = {}
        self._running = False
        self._thread: Optional[threading.Thread] = None

    def register_callback(self, hotkey_id: int, callback: Callable[[], None]) -> None:
        self._handlers[hotkey_id] = callback

    def start(self) -> None:
        """Launch Windows message pump thread for hotkeys."""
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(
            target=self._hotkey_pump,
            name="JarvisHotkeyWorker",
            daemon=True
        )
        self._thread.start()
        self.logger.info("Global hotkey daemon started (Ctrl+Alt+J, M, S, D).", "HOTKEY")

    def _hotkey_pump(self) -> None:
        # Register hotkeys on thread
        user32.RegisterHotKey(None, HOTKEY_WAKE, MOD_CONTROL | MOD_ALT, VK_J)
        user32.RegisterHotKey(None, HOTKEY_MUTE, MOD_CONTROL | MOD_ALT, VK_M)
        user32.RegisterHotKey(None, HOTKEY_SCREENSHOT, MOD_CONTROL | MOD_ALT, VK_S)
        user32.RegisterHotKey(None, HOTKEY_DESKTOP, MOD_CONTROL | MOD_ALT, VK_D)
        user32.RegisterHotKey(None, HOTKEY_QUIT, MOD_CONTROL | MOD_ALT, VK_Q)

        msg = ctypes.wintypes.MSG()
        while self._running:
            # Check message queue without blocking indefinitely
            if user32.PeekMessageW(ctypes.byref(msg), None, 0, 0, 1): # PM_REMOVE = 1
                if msg.message == 0x0312: # WM_HOTKEY
                    hk_id = msg.wParam
                    handler = self._handlers.get(hk_id)
                    if handler:
                        try:
                            handler()
                        except Exception as e:
                            self.logger.error(f"Error in hotkey handler: {e}", "HOTKEY")
                user32.TranslateMessage(ctypes.byref(msg))
                user32.DispatchMessageW(ctypes.byref(msg))
            time.sleep(0.05)

        # Unregister on exit
        for hid in [HOTKEY_WAKE, HOTKEY_MUTE, HOTKEY_SCREENSHOT, HOTKEY_DESKTOP, HOTKEY_QUIT]:
            user32.UnregisterHotKey(None, hid)

    def stop(self) -> None:
        self._running = False
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=1.0)


def get_hotkey_daemon() -> HotkeyDaemon:
    return HotkeyDaemon()
