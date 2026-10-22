"""
================================================================================
                    JARVIS APPLICATION LAUNCHER & INDEXER
================================================================================
Intelligent desktop application launcher indexing Windows Start Menu shortcuts,
Program Files binaries, Windows Apps (UWP), and common developer environments.
================================================================================
"""

import os
import sys
import glob
import subprocess
from typing import Dict, List, Optional, Tuple
from pathlib import Path

from jarvis.core.config import get_config
from jarvis.core.logger import get_logger

# Common well-known application aliases mapped to process launch commands
KNOWN_APP_MAP: Dict[str, List[str]] = {
    "chrome": ["chrome.exe", "Google Chrome", r"C:\Program Files\Google\Chrome\Application\chrome.exe"],
    "code": ["code.cmd", "code.exe", "Visual Studio Code"],
    "vs code": ["code.cmd", "code.exe"],
    "terminal": ["wt.exe", "powershell.exe", "cmd.exe"],
    "cmd": ["cmd.exe"],
    "powershell": ["powershell.exe"],
    "notepad": ["notepad.exe"],
    "calculator": ["calc.exe"],
    "spotify": ["spotify.exe", r"C:\Users\%USERNAME%\AppData\Roaming\Spotify\Spotify.exe"],
    "discord": ["discord.exe", r"C:\Users\%USERNAME%\AppData\Local\Discord\Update.exe --processStart Discord.exe"],
    "steam": ["steam.exe", r"C:\Program Files (x86)\Steam\steam.exe"],
    "task_manager": ["taskmgr.exe"],
    "file_explorer": ["explorer.exe"],
    "edge": ["msedge.exe"],
    "word": ["winword.exe"],
    "excel": ["excel.exe"],
    "powerpoint": ["powerpnt.exe"],
    "paint": ["mspaint.exe"],
    "vlc": ["vlc.exe", r"C:\Program Files\VideoLAN\VLC\vlc.exe"]
}


class AppLauncher:
    """Discovers and starts applications on Windows."""

    def __init__(self) -> None:
        self.config = get_config()
        self.logger = get_logger()
        self._index: Dict[str, str] = {}
        self._build_index()

    def _build_index(self) -> None:
        """Index user and system start menu shortcuts for rapid search."""
        paths = [
            Path(os.environ.get("APPDATA", "")) / r"Microsoft\Windows\Start Menu\Programs",
            Path(os.environ.get("PROGRAMDATA", "")) / r"Microsoft\Windows\Start Menu\Programs",
        ]

        for p in paths:
            if p.exists():
                for shortcut in p.rglob("*.lnk"):
                    name = shortcut.stem.lower()
                    self._index[name] = str(shortcut)

    def launch(self, app_alias: str) -> Tuple[bool, str]:
        """Launch an application by spoken name or alias."""
        target = app_alias.lower().strip()
        self.logger.info(f"Attempting to launch app: '{target}'", "LAUNCHER")

        # 1. Check known app mapping
        if target in KNOWN_APP_MAP:
            for cmd in KNOWN_APP_MAP[target]:
                expanded_cmd = os.path.expandvars(cmd)
                try:
                    subprocess.Popen(expanded_cmd, shell=True)
                    self.logger.success(f"Launched '{target}' via binary command.", "LAUNCHER")
                    return True, f"{target.capitalize()} open kar diya sir!"
                except Exception:
                    continue

        # 2. Check indexed start menu shortcuts
        for name, shortcut_path in self._index.items():
            if target in name:
                try:
                    os.startfile(shortcut_path)
                    self.logger.success(f"Launched '{name}' from Start Menu.", "LAUNCHER")
                    return True, f"{name.capitalize()} khol diya sir!"
                except Exception as e:
                    self.logger.warning(f"Error launching shortcut {shortcut_path}: {e}", "LAUNCHER")

        # 3. Fallback: try raw startfile or shell execute
        try:
            os.system(f"start {target}")
            return True, f"{target} start karne ki koshish ki hai sir."
        except Exception as e:
            msg = f"Sir, '{target}' application nahi mil payi: {e}"
            self.logger.error(msg, "LAUNCHER")
            return False, msg


def get_app_launcher() -> AppLauncher:
    return AppLauncher()
