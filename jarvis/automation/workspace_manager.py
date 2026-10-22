"""
================================================================================
                    JARVIS WORKSPACE & DESKTOP PROFILES
================================================================================
Automated multi-application workspace orchestra: Coding Mode, Gaming Mode,
Focus / Productivity Mode, and Research Mode setup with single commands.
================================================================================
"""

import time
import webbrowser
from typing import Tuple

from jarvis.core.logger import get_logger
from jarvis.automation.app_launcher import get_app_launcher
from jarvis.system.power_control import get_power_controller
from jarvis.system.volume_brightness import get_volume_controller
from jarvis.system.window_manager import get_window_manager


class WorkspaceManager:
    """Configures multi-application environments."""

    def __init__(self) -> None:
        self.logger = get_logger()
        self.apps = get_app_launcher()
        self.power = get_power_controller()
        self.volume = get_volume_controller()
        self.window = get_window_manager()

    def launch_coding_workspace(self) -> str:
        """Launch Code, Terminal, and developer references."""
        self.logger.info("Initializing Coding Workspace...", "WORKSPACE")
        self.apps.launch("code")
        time.sleep(0.5)
        self.apps.launch("terminal")
        webbrowser.open("https://github.com")
        return "Coding workspace activate ho gaya sir! VS Code, Terminal aur GitHub open hain."

    def launch_gaming_mode(self) -> str:
        """Optimize system for gaming."""
        self.logger.info("Engaging Gaming Mode...", "WORKSPACE")
        from jarvis.system.battery_optimizer import get_battery_optimizer
        get_battery_optimizer().set_power_scheme("high_performance")
        self.apps.launch("discord")
        self.apps.launch("steam")
        return "Gaming mode engaged sir! High Performance power profile active hai aur Steam launch ho raha hai."

    def launch_focus_mode(self) -> str:
        """Enable distraction-free study and coding environment."""
        self.logger.info("Activating Focus Mode...", "WORKSPACE")
        self.window.minimize_all()
        webbrowser.open("https://www.youtube.com/watch?v=jfKfPfyJRdk") # Lofi girl live
        return "Focus mode enabled sir. Sabhi windows minimize kar di gayi hain aur relaxing Lofi music chalu hai."

    def launch_research_mode(self) -> str:
        """Open web research portals."""
        self.logger.info("Opening Research Mode portals...", "WORKSPACE")
        webbrowser.open("https://scholar.google.com")
        webbrowser.open("https://arxiv.org")
        webbrowser.open("https://chat.openai.com")
        return "Research workspace ready sir. Scholar, ArXiv aur AI portal ready hain."


def get_workspace_manager() -> WorkspaceManager:
    return WorkspaceManager()
