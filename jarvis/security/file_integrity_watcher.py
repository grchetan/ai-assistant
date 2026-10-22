"""
================================================================================
                    JARVIS FILE INTEGRITY MONITOR (FIM)
================================================================================
Real-time cryptographic file integrity supervisor. Computes baseline SHA-256
hashes of critical system configuration files (e.g. hosts file, startup registry,
system scripts) and detects unauthorized tampering or rapid bulk encryption.
================================================================================
"""

import os
import time
import hashlib
import threading
from typing import Dict, List, Optional, Tuple, Set, Any
from pathlib import Path

from jarvis.core.logger import get_logger
from jarvis.core.events import get_event_bus, EventType, Priority

# Critical files that must maintain strict integrity
CRITICAL_WATCH_TARGETS: List[Path] = [
    Path(r"C:\Windows\System32\drivers\etc\hosts"),
    Path(os.environ.get("APPDATA", "")) / r"Microsoft\Windows\Start Menu\Programs\Startup",
    Path(os.environ.get("PROGRAMDATA", "")) / r"Microsoft\Windows\Start Menu\Programs\Startup",
]


class FileIntegrityWatcher:
    """Detects unauthorized modification of critical system files."""

    _instance: Optional["FileIntegrityWatcher"] = None
    _lock = threading.RLock()

    def __new__(cls) -> "FileIntegrityWatcher":
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(FileIntegrityWatcher, cls).__new__(cls)
                cls._instance._init_fim()
            return cls._instance

    def _init_fim(self) -> None:
        self.logger = get_logger()
        self.bus = get_event_bus()
        self._baselines: Dict[str, str] = {}
        self._is_watching = False
        self._thread: Optional[threading.Thread] = None

        self._build_initial_baseline()

    def _hash_file(self, file_path: Path) -> Optional[str]:
        if not file_path.exists() or not file_path.is_file():
            return None
        try:
            h = hashlib.sha256()
            with open(file_path, "rb") as f:
                while chunk := f.read(65536):
                    h.update(chunk)
            return h.hexdigest()
        except Exception:
            return None

    def _build_initial_baseline(self) -> None:
        """Establish baseline cryptographic checksums."""
        for target in CRITICAL_WATCH_TARGETS:
            if target.exists():
                if target.is_file():
                    sha = self._hash_file(target)
                    if sha:
                        self._baselines[str(target)] = sha
                elif target.is_dir():
                    for item in target.iterdir():
                        if item.is_file():
                            sha = self._hash_file(item)
                            if sha:
                                self._baselines[str(item)] = sha

        self.logger.info(f"FIM: Cryptographic baseline established for {len(self._baselines)} system targets.", "SECURITY")

    def check_integrity(self) -> List[Dict[str, Any]]:
        """Compare current target hashes against established baseline."""
        violations = []

        for path_str, original_hash in list(self._baselines.items()):
            p = Path(path_str)
            if not p.exists():
                violations.append({
                    "file": path_str,
                    "event": "FILE_DELETED",
                    "severity": "HIGH"
                })
                self.logger.warning(f"Integrity alert: Watched file was DELETED: {path_str}", "SECURITY")
                continue

            current_hash = self._hash_file(p)
            if current_hash != original_hash:
                violations.append({
                    "file": path_str,
                    "event": "MODIFIED_TAMPERED",
                    "original_sha256": original_hash,
                    "new_sha256": current_hash,
                    "severity": "CRITICAL"
                })
                self.logger.critical(
                    f"CRITICAL INTEGRITY BREACH: File modified without authorization: {p.name}",
                    "SECURITY"
                )

        return violations

    def start_background_audit(self, interval_seconds: float = 10.0) -> None:
        if self._is_watching:
            return
        self._is_watching = True

        def _watcher_loop():
            while self._is_watching:
                self.check_integrity()
                time.sleep(interval_seconds)

        self._thread = threading.Thread(target=_watcher_loop, name="JarvisFIMThread", daemon=True)
        self._thread.start()
        self.logger.info("File Integrity Monitor background daemon active.", "SECURITY")

    def stop(self) -> None:
        self._is_watching = False


def get_file_integrity_watcher() -> FileIntegrityWatcher:
    return FileIntegrityWatcher()
