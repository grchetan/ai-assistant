"""
================================================================================
                    JARVIS PROCESS & TASK CONTROLLER
================================================================================
Manages Windows processes and running services: graceful termination, safe
guards against killing critical OS components, task search, and memory cleanup.
================================================================================
"""

import os
import psutil
from typing import List, Dict, Optional, Tuple, Any

from jarvis.core.logger import get_logger

# System-critical processes that must never be terminated by voice commands
PROTECTED_PROCESSES = {
    "system", "system idle process", "smss.exe", "csrss.exe", "wininit.exe",
    "services.exe", "lsass.exe", "svchost.exe", "winlogon.exe", "dwm.exe",
    "fontdrvhost.exe", "explorer.exe", "python.exe" # protect self
}


class ProcessManager:
    """Safely manages application processes."""

    def __init__(self) -> None:
        self.logger = get_logger()

    def kill_process(self, process_name: str) -> Tuple[bool, str]:
        """Terminate all instances matching a process name (e.g. 'chrome', 'spotify')."""
        target = process_name.lower().strip()
        if not target.endswith(".exe"):
            target += ".exe"

        if target in PROTECTED_PROCESSES:
            msg = f"Security Alert: '{target}' is a critical OS component and cannot be terminated."
            self.logger.warning(msg, "PROCESS")
            return False, msg

        terminated_count = 0
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                name = proc.info['name'].lower()
                if name == target or target.replace(".exe", "") in name:
                    proc.kill()
                    terminated_count += 1
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        if terminated_count > 0:
            msg = f"Band kar diya sir! {terminated_count} instances of '{process_name}' terminated."
            self.logger.success(msg, "PROCESS")
            return True, msg
        else:
            msg = f"Sir, '{process_name}' process running nahi mila."
            self.logger.info(msg, "PROCESS")
            return False, msg

    def kill_by_pid(self, pid: int) -> Tuple[bool, str]:
        try:
            p = psutil.Process(pid)
            name = p.name()
            if name.lower() in PROTECTED_PROCESSES:
                return False, "Cannot terminate protected system process."
            p.kill()
            return True, f"Process {name} (PID: {pid}) terminated."
        except Exception as e:
            return False, f"Failed to terminate PID {pid}: {e}"

    def get_process_stats(self, process_name: str) -> Optional[Dict[str, Any]]:
        target = process_name.lower().strip()
        total_mem_mb = 0.0
        instance_count = 0
        for proc in psutil.process_iter(['name', 'memory_info']):
            try:
                if target in proc.info['name'].lower():
                    total_mem_mb += proc.info['memory_info'].rss / (1024 * 1024)
                    instance_count += 1
            except Exception:
                continue

        if instance_count > 0:
            return {
                "name": process_name,
                "instances": instance_count,
                "total_memory_mb": round(total_mem_mb, 1)
            }
        return None


def get_process_manager() -> ProcessManager:
    return ProcessManager()
