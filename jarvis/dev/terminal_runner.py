"""
================================================================================
                    JARVIS DEVELOPER TERMINAL & GIT RUNNER
================================================================================
Safe shell execution environment for PowerShell / CMD commands, Git repository
status inspections, commits, and Python scratchpad evaluation.
================================================================================
"""

import os
import subprocess
from typing import Tuple, Dict, Any, Optional

from jarvis.core.logger import get_logger
from jarvis.core.security import SafetyGuard


class TerminalRunner:
    """Executes developer tasks and shell commands."""

    def __init__(self) -> None:
        self.logger = get_logger()

    def run_command(self, cmd: str, timeout: int = 15) -> Tuple[bool, str]:
        """Execute a safe shell command and return stdout/stderr."""
        if not SafetyGuard.is_command_safe(cmd):
            msg = "Command blocked by JARVIS Security Guard: Potentially hazardous execution."
            self.logger.warning(msg, "DEV")
            return False, msg

        self.logger.info(f"Running terminal command: {cmd}", "DEV")
        try:
            res = subprocess.run(
                ["powershell", "-NoProfile", "-Command", cmd],
                capture_output=True,
                text=True,
                timeout=timeout
            )
            out = res.stdout.strip() if res.stdout else res.stderr.strip()
            if not out:
                out = "Command executed successfully with zero output."
            return res.returncode == 0, out
        except subprocess.TimeoutExpired:
            return False, f"Command timed out after {timeout} seconds."
        except Exception as e:
            return False, f"Execution failed: {e}"

    def git_status(self, repo_dir: Optional[str] = None) -> str:
        """Inspect current repository status."""
        cwd = repo_dir or os.getcwd()
        try:
            res = subprocess.run(
                ["git", "status", "--short"],
                cwd=cwd,
                capture_output=True,
                text=True,
                check=True
            )
            lines = res.stdout.strip().splitlines()
            if not lines:
                return "Working directory clean hai sir. Koi uncommitted changes nahi hain."
            return f"Sir, {len(lines)} files modified hain repository me."
        except Exception as e:
            return f"Git status check nahi ho paya: {e}"

    def run_python_snippet(self, code: str) -> str:
        """Evaluate a python expression safely."""
        self.logger.info("Evaluating Python scratchpad snippet.", "DEV")
        try:
            res = subprocess.run(
                ["python", "-c", code],
                capture_output=True,
                text=True,
                timeout=10
            )
            return res.stdout.strip() or res.stderr.strip() or "Done."
        except Exception as e:
            return f"Error running python snippet: {e}"


def get_terminal_runner() -> TerminalRunner:
    return TerminalRunner()
