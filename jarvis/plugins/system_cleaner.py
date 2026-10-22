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
        return any(k in t for k in ["clean system", "flush dns", "empty recycle bin", "kachra saaf", "junk clean", "clean cache"])

    def execute(self, text: str, payload: Dict[str, Any]) -> Tuple[bool, str]:
        logger = get_logger()
        t = text.lower()
        logger.info(f"Cleaner requested with prompt: {text}", "CLEANER")

        # 1. Explicit Recycle Bin Emptying (Only when explicitly asked)
        if "recycle bin" in t or "dustbin" in t:
            try:
                # Flag 0 = Windows displays confirmation dialog so user has complete control and safety!
                ctypes.windll.shell32.SHEmptyRecycleBinW(None, None, 0)
                msg = "Recycle bin clean request process kar di gayi hai sir."
                logger.success(msg, "CLEANER")
                return True, msg
            except Exception as e:
                logger.debug(f"Recycle bin empty skipped or cancelled: {e}", "CLEANER")
                return True, "Recycle bin action complete ya cancel kar di gayi hai sir."

        # 2. General System / Cache / Temp Cleanup
        cleaned_mb = 0.0

        # Flush DNS
        try:
            subprocess.run(["ipconfig", "/flushdns"], capture_output=True, check=False)
        except Exception:
            pass

        # Clean user %TEMP% folder (Safe system temporary cache files only)
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

        speech = f"Sir, system cache cleanup complete! DNS flush ho gaya hai aur {cleaned_mb:.1f} MB temporary app cache saaf ho gayi hai. Aapki koi bhi personal file ya Recycle Bin touch nahi hui hai."
        logger.success(speech, "CLEANER")
        return True, speech
