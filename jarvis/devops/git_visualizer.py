"""
================================================================================
                    JARVIS GIT REPOSITORY VISUALIZER
================================================================================
Generates visual ASCII branch topology graphs, calculates author commit shares,
and inspects file modification churn directly in the terminal.
================================================================================
"""

import os
import subprocess
from typing import Dict, List, Any, Optional

from jarvis.core.logger import get_logger


class GitVisualizer:
    """Renders visual Git topology and repository statistics."""

    def __init__(self, repo_dir: Optional[str] = None) -> None:
        self.logger = get_logger()
        self.repo_dir = repo_dir or os.getcwd()

    def _run_git(self, args: List[str]) -> str:
        try:
            res = subprocess.run(
                ["git"] + args,
                cwd=self.repo_dir,
                capture_output=True,
                text=True,
                check=True
            )
            return res.stdout.strip()
        except Exception:
            return ""

    def render_ascii_graph(self, max_commits: int = 15) -> str:
        """Generate ASCII visualization of Git branches and merges."""
        out = self._run_git([
            "log",
            f"-{max_commits}",
            "--graph",
            "--abbrev-commit",
            "--decorate",
            "--format=format:%C(bold blue)%h%C(reset) - %C(bold green)(%ar)%C(reset) %C(white)%s%C(reset) %C(dim white)- %an%C(reset)%C(auto)%d%C(reset)"
        ])
        return out if out else "No git repository commits found."

    def get_author_contributions(self) -> Dict[str, int]:
        """Tally total commits authored by each contributor."""
        out = self._run_git(["shortlog", "-sn", "--no-merges", "HEAD"])
        contributors = {}
        for line in out.splitlines():
            line = line.strip()
            if line:
                parts = line.split("\t")
                if len(parts) == 2:
                    try:
                        count = int(parts[0].strip())
                        author = parts[1].strip()
                        contributors[author] = count
                    except ValueError:
                        continue
        return contributors

    def get_summary_speech(self) -> str:
        authors = self.get_author_contributions()
        if not authors:
            return "Sir, repository me koi author commit history nahi mili."

        top_author, count = max(authors.items(), key=lambda x: x[1])
        total_commits = sum(authors.values())
        return f"Sir, repository me total {total_commits} commits hain. Top contributor '{top_author}' hai with {count} commits."


def get_git_visualizer() -> GitVisualizer:
    return GitVisualizer()
