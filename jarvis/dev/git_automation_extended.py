"""
================================================================================
                    JARVIS EXTENDED GIT VERSION CONTROL AUTOMATION
================================================================================
Deep Git automation suite: branch management, commit generator, remote origin
sync, stash utilities, and commit history graphs.
================================================================================
"""

import os
import subprocess
from typing import List, Dict, Tuple, Optional
from pathlib import Path

from jarvis.core.logger import get_logger


class GitAutomationSuite:
    """Automates complex Git workflows."""

    def __init__(self, repo_path: Optional[str] = None) -> None:
        self.logger = get_logger()
        self.repo_path = repo_path or os.getcwd()

    def _run_git(self, args: List[str]) -> Tuple[bool, str]:
        try:
            res = subprocess.run(
                ["git"] + args,
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            return True, res.stdout.strip()
        except subprocess.CalledProcessError as e:
            err = e.stderr.strip() if e.stderr else str(e)
            return False, err
        except Exception as e:
            return False, str(e)

    def create_branch(self, branch_name: str) -> Tuple[bool, str]:
        """Create and checkout a new git branch."""
        self.logger.info(f"Creating git branch: {branch_name}", "GIT")
        success, out = self._run_git(["checkout", "-b", branch_name])
        if success:
            return True, f"Branch '{branch_name}' create karke switch kar diya sir."
        return False, f"Branch create nahi ho paayi: {out}"

    def stage_and_commit(self, commit_message: str) -> Tuple[bool, str]:
        """Stage all modified files and commit with message."""
        self.logger.info(f"Staging and committing: '{commit_message}'", "GIT")
        s1, out1 = self._run_git(["add", "."])
        if not s1:
            return False, f"Git add failed: {out1}"

        s2, out2 = self._run_git(["commit", "-m", commit_message])
        if s2:
            return True, f"Changes commit ho gaye sir: '{commit_message}'"
        return False, f"Git commit failed: {out2}"

    def push_current_branch(self) -> Tuple[bool, str]:
        """Push current branch to origin."""
        # Get active branch name
        s, branch = self._run_git(["branch", "--show-current"])
        if not s or not branch:
            return False, "Active branch detect nahi hui."

        self.logger.info(f"Pushing branch '{branch}' to origin...", "GIT")
        s2, out2 = self._run_git(["push", "origin", branch])
        if s2:
            return True, f"Branch '{branch}' origin par push ho gayi sir."
        return False, f"Push fail hua: {out2}"

    def get_recent_commits(self, count: int = 5) -> List[Dict[str, str]]:
        """Retrieve recent commit log."""
        s, out = self._run_git(["log", f"-{count}", "--pretty=format:%h|%an|%s|%ar"])
        if not s or not out:
            return []

        commits = []
        for line in out.splitlines():
            parts = line.split("|")
            if len(parts) == 4:
                commits.append({
                    "hash": parts[0],
                    "author": parts[1],
                    "message": parts[2],
                    "time": parts[3]
                })
        return commits


def get_git_suite() -> GitAutomationSuite:
    return GitAutomationSuite()
