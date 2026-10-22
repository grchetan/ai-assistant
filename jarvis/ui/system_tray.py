"""
================================================================================
                    JARVIS SYSTEM TRAY INTEGRATION
================================================================================
Background taskbar system tray controller providing right-click context menus,
minimize-to-tray handling, quick mute toggles, and status notifications.
================================================================================
"""

import threading
from typing import Optional, Callable
from PIL import Image, ImageDraw

from jarvis.core.logger import get_logger


def create_tray_icon_image(primary_color: str = "#00f0ff") -> Image.Image:
    """Generate a high-resolution Arc Reactor tray icon dynamically in-memory."""
    width, height = 64, 64
    image = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)

    # Outer circle
    draw.ellipse((4, 4, 60, 60), outline=primary_color, width=4)
    # Inner ring
    draw.ellipse((16, 16, 48, 48), outline=primary_color, width=3)
    # Glowing center core
    draw.ellipse((26, 26, 38, 38), fill=primary_color)

    return image


class SystemTrayController:
    """Manages background taskbar system tray presence."""

    def __init__(
        self,
        on_show_gui: Optional[Callable[[], None]] = None,
        on_toggle_mute: Optional[Callable[[], None]] = None,
        on_exit: Optional[Callable[[], None]] = None
    ) -> None:
        self.logger = get_logger()
        self.on_show_gui = on_show_gui
        self.on_toggle_mute = on_toggle_mute
        self.on_exit = on_exit
        self._icon = None
        self._is_running = False

    def start(self) -> None:
        """Start tray icon in background thread."""
        try:
            import pystray
            _PYSTRAY_AVAILABLE = True
        except ImportError:
            _PYSTRAY_AVAILABLE = False

        if not _PYSTRAY_AVAILABLE:
            self.logger.info("pystray not installed; running in standard window mode.", "TRAY")
            return

        def _run_tray():
            menu = pystray.Menu(
                pystray.MenuItem("Open JARVIS HUD", lambda: self.on_show_gui() if self.on_show_gui else None),
                pystray.MenuItem("Toggle Audio Mute", lambda: self.on_toggle_mute() if self.on_toggle_mute else None),
                pystray.Menu.SEPARATOR,
                pystray.MenuItem("Exit System", lambda: self.on_exit() if self.on_exit else None)
            )
            image = create_tray_icon_image()
            self._icon = pystray.Icon("JARVIS", image, "J.A.R.V.I.S. Quantum OS", menu)
            self._is_running = True
            self._icon.run()

        threading.Thread(target=_run_tray, daemon=True).start()

    def stop(self) -> None:
        if self._icon:
            try:
                self._icon.stop()
            except Exception:
                pass


def get_tray_controller(on_show=None, on_mute=None, on_exit=None) -> SystemTrayController:
    return SystemTrayController(on_show, on_mute, on_exit)
