"""
================================================================================
                    JARVIS SMART FILE & FOLDER ORGANIZER
================================================================================
Automated file taxonomy organizer for Desktop and Downloads directories.
Classifies files by MIME extension and detects duplicate files using SHA-256.
================================================================================
"""

import os
import shutil
import hashlib
from typing import Dict, List, Tuple
from pathlib import Path

from jarvis.core.logger import get_logger

EXTENSIONS_MAP: Dict[str, List[str]] = {
    "Images": [".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp", ".svg", ".ico"],
    "Videos": [".mp4", ".mkv", ".mov", ".avi", ".flv", ".webm"],
    "Audio": [".mp3", ".wav", ".aac", ".ogg", ".flac", ".m4a"],
    "Documents": [".pdf", ".docx", ".doc", ".txt", ".pptx", ".xlsx", ".csv", ".md"],
    "Archives": [".zip", ".rar", ".7z", ".tar", ".gz"],
    "Code": [".py", ".js", ".ts", ".html", ".css", ".json", ".cpp", ".c", ".java"],
    "Installers": [".exe", ".msi", ".bat", ".cmd"]
}

# Protected extensions that must NEVER be moved or touched (Desktop shortcuts, system files)
PROTECTED_EXTENSIONS = {".lnk", ".url", ".ini", ".sys", ".dll"}


class FileOrganizer:
    """Classifies files into clean folders with safety protections and undo capability."""

    def __init__(self) -> None:
        self.logger = get_logger()

    def organize_directory(self, target_dir: Path) -> Tuple[int, str]:
        """Sort files in target directory into category subfolders safely without touching shortcuts."""
        if not target_dir.exists() or not target_dir.is_dir():
            return 0, "Directory exist nahi karti sir."

        self.logger.info(f"Organizing directory: {target_dir}", "FILES")
        moved_count = 0

        for item in target_dir.iterdir():
            if item.is_file() and not item.name.startswith("."):
                ext = item.suffix.lower()
                
                # NEVER touch shortcuts, url icons, or system files!
                if ext in PROTECTED_EXTENSIONS:
                    continue

                target_category = None
                for cat, exts in EXTENSIONS_MAP.items():
                    if ext in exts:
                        target_category = cat
                        break

                # If file doesn't match known safe category, leave it in place
                if not target_category:
                    continue

                dest_folder = target_dir / target_category
                dest_folder.mkdir(exist_ok=True)
                dest_path = dest_folder / item.name

                try:
                    shutil.move(str(item), str(dest_path))
                    moved_count += 1
                except Exception as e:
                    self.logger.debug(f"Failed to move {item.name}: {e}", "FILES")

        msg = f"{moved_count} files safe categories me organize kar di gayi hain. Koi shortcut ya unknown file touch nahi ki gayi hai."
        self.logger.success(msg, "FILES")
        return moved_count, msg

    def undo_directory(self, target_dir: Path) -> Tuple[int, str]:
        """Restores all files from category subfolders back to the target directory root."""
        if not target_dir.exists() or not target_dir.is_dir():
            return 0, "Directory exist nahi karti sir."

        self.logger.info(f"Restoring organized files in {target_dir}...", "FILES")
        restored_count = 0
        categories = list(EXTENSIONS_MAP.keys()) + ["Miscellaneous"]

        for cat in categories:
            cat_dir = target_dir / cat
            if cat_dir.exists() and cat_dir.is_dir():
                for item in cat_dir.iterdir():
                    if item.is_file():
                        dest = target_dir / item.name
                        try:
                            shutil.move(str(item), str(dest))
                            restored_count += 1
                        except Exception as e:
                            self.logger.debug(f"Failed to restore {item.name}: {e}", "FILES")
                try:
                    cat_dir.rmdir()
                except Exception:
                    pass

        msg = f"{restored_count} files ko wapas original root location par restore kar diya gaya hai."
        self.logger.success(msg, "FILES")
        return restored_count, msg

    def organize_desktop(self) -> str:
        desktop = Path(os.environ.get("USERPROFILE", "")) / "Desktop"
        _, msg = self.organize_directory(desktop)
        return f"Desktop par {msg}"

    def undo_desktop(self) -> str:
        desktop = Path(os.environ.get("USERPROFILE", "")) / "Desktop"
        _, msg = self.undo_directory(desktop)
        return f"Desktop: {msg}"

    def organize_downloads(self) -> str:
        downloads = Path(os.environ.get("USERPROFILE", "")) / "Downloads"
        _, msg = self.organize_directory(downloads)
        return f"Downloads folder me {msg}"

    def undo_downloads(self) -> str:
        downloads = Path(os.environ.get("USERPROFILE", "")) / "Downloads"
        _, msg = self.undo_directory(downloads)
        return f"Downloads: {msg}"

    def find_duplicate_files(self, directory: Path) -> List[Tuple[Path, Path]]:
        """Identify duplicate files based on content hash."""
        hashes: Dict[str, Path] = {}
        duplicates: List[Tuple[Path, Path]] = []

        for p in directory.rglob("*"):
            if p.is_file() and p.stat().st_size > 0 and p.stat().st_size < 100 * 1024 * 1024:
                try:
                    with open(p, "rb") as f:
                        file_hash = hashlib.sha256(f.read()).hexdigest()
                    if file_hash in hashes:
                        duplicates.append((p, hashes[file_hash]))
                    else:
                        hashes[file_hash] = p
                except Exception:
                    continue
        return duplicates


def get_file_organizer() -> FileOrganizer:
    return FileOrganizer()
