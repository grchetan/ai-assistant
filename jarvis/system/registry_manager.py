"""
================================================================================
                    JARVIS WINDOWS REGISTRY & SYSTEM TWEAKS
================================================================================
Controls system-level Windows configuration using winreg: System Dark/Light
mode switching, File Explorer hidden files / extensions visibility toggles,
and startup program inspection.
================================================================================
"""

import winreg
import subprocess
from typing import Tuple, List, Dict, Any

from jarvis.core.logger import get_logger


class RegistryManager:
    """Manages Windows system registry settings safely."""

    def __init__(self) -> None:
        self.logger = get_logger()

    def set_system_dark_mode(self, enable_dark: bool = True) -> Tuple[bool, str]:
        """Toggle Windows Apps and System theme between Dark and Light mode."""
        val = 0 if enable_dark else 1
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize"

        try:
            # Apps theme
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE)
            winreg.SetValueEx(key, "AppsUseLightTheme", 0, winreg.REG_DWORD, val)
            winreg.SetValueEx(key, "SystemUsesLightTheme", 0, winreg.REG_DWORD, val)
            winreg.CloseKey(key)

            mode_str = "Dark Mode" if enable_dark else "Light Mode"
            self.logger.success(f"Windows theme set to {mode_str}.", "REGISTRY")
            return True, f"Windows theme {mode_str} me switch kar diya sir."
        except Exception as e:
            self.logger.error(f"Error setting theme in registry: {e}", "REGISTRY")
            return False, f"Registry error: {e}"

    def toggle_file_extensions(self, show: bool = True) -> Tuple[bool, str]:
        """Show or hide known file extensions in Windows File Explorer."""
        val = 0 if show else 1
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced"

        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE)
            winreg.SetValueEx(key, "HideFileExt", 0, winreg.REG_DWORD, val)
            winreg.CloseKey(key)

            # Restart explorer to reflect changes
            subprocess.run(["taskkill", "/f", "/im", "explorer.exe"], check=False)
            subprocess.Popen("explorer.exe")

            status = "visible" if show else "hidden"
            return True, f"File extensions ab {status} hain sir."
        except Exception as e:
            return False, f"Failed to toggle file extensions: {e}"

    def list_startup_programs(self) -> List[Dict[str, str]]:
        """Query user startup applications registered in Registry."""
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        programs = []
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_READ)
            idx = 0
            while True:
                try:
                    name, val, _ = winreg.EnumValue(key, idx)
                    programs.append({"name": name, "path": val})
                    idx += 1
                except OSError:
                    break
            winreg.CloseKey(key)
        except Exception:
            pass
        return programs


def get_registry_manager() -> RegistryManager:
    return RegistryManager()
