"""
================================================================================
                    JARVIS DEEP SYSTEM CLEANER & DISK OPTIMIZER
================================================================================
Maintenance engine that flushes temporary caches, wipes obsolete junk files,
purges DNS resolver cache, and empties the Windows Recycle Bin.
================================================================================
"""

import os
import shutil
import ctypes
import subprocess
from pathlib import Path
from typing import Dict, Any, Tuple

from jarvis.plugins.plugin_base import JarvisPlugin
from jarvis.core.logger import get_logger


class SystemCleanerPlugin(JarvisPlugin):
    """Purges junk files and cache."""

    @property
    def name(self) -> str:
        return "system_cleaner"

    @property
    def description(self) -> str:
        return "Cleans Windows temp files, flushes DNS, and empties Recycle Bin."

    def can_handle(self, text: str) -> bool:
        t = text.lower()
        return any(k in t for k in ["clean system", "flush dns", "empty recycle bin", "kachra saaf", "junk clean"])

    def execute(self, text: str, payload: Dict[str, Any]) -> Tuple[bool, str]:
        logger = get_logger()
        logger.info("Starting deep system cleanup...", "CLEANER")

        cleaned_mb = 0.0

        # 1. Empty Recycle Bin
        try:
            # Flags: SHERB_NOCONFIRMATION = 0x00000001, SHERB_NOPROGRESSUI = 0x00000002, SHERB_NOSOUND = 0x00000004
            ctypes.windll.shell32.SHEmptyRecycleBinW(None, None, 7)
        except Exception:
            pass

        # 2. Flush DNS
        try:
            subprocess.run(["ipconfig", "/flushdns"], capture_output=True, check=False)
        except Exception:
            pass

        # 3. Clean user %TEMP% folder
        temp_dir = Path(os.environ.get("TEMP", ""))
        if temp_dir.exists():
            for item in temp_dir.iterdir():
                try:
                    if item.is_file():
                        size = item.stat().st_size
                        item.unlink(missing_ok=True)
                        cleaned_mb += size / (1024 * 1024)
                    elif item.is_dir():
                        shutil.rmtree(str(item), ignore_errors=True)
                except Exception:
                    continue

        speech = f"Sir, system cleanup complete! Recycle Bin empty kar diya hai, DNS flush ho gaya hai, aur {cleaned_mb:.1f} MB temporary cache saaf ho gayi hai."
        logger.success(speech, "CLEANER")
        return True, speech
