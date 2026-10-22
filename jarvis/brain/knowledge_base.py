"""
================================================================================
                    JARVIS OFFLINE KNOWLEDGE BASE & CHEATSHEET
================================================================================
Encyclopedic reference engine providing instant zero-latency responses for
programming syntax, developer commands, scientific constants, country capitals,
and computing history when offline.
================================================================================
"""

from typing import Optional, Dict, Any, List

# Programming cheatsheet database
DEV_CHEATSHEETS: Dict[str, Dict[str, str]] = {
    "git": {
        "clone": "git clone <url> - Clone a remote repository to local machine",
        "commit": "git commit -m 'message' - Record staged changes to repository",
        "status": "git status - Show working tree status and untracked files",
        "push": "git push origin <branch> - Upload local branch commits to remote",
        "pull": "git pull origin <branch> - Fetch and integrate remote changes",
        "branch": "git branch -d <branch_name> - Delete a local branch safely",
        "stash": "git stash - Temporarily shelve uncommitted working directory changes",
        "log": "git log --oneline --graph - Display concise visual commit history",
        "rebase": "git rebase -i HEAD~N - Interactive rebase of last N commits",
        "reset": "git reset --hard HEAD - Discard all local uncommitted changes"
    },
    "python": {
        "virtualenv": "python -m venv .venv - Create isolated virtual environment",
        "pip_freeze": "pip freeze > requirements.txt - Export installed packages",
        "list_comp": "[x**2 for x in range(10) if x % 2 == 0] - List comprehension",
        "dict_get": "my_dict.get(key, default_value) - Safe dictionary lookup",
        "decorators": "def my_decorator(func): wrap with functools.wraps",
        "generator": "yield item - Produce lazy memory-efficient iterator stream",
        "context_mgr": "with open(path) as f: auto-close resource on exit",
        "lambda": "lambda x, y: x + y - Anonymous inline function expression",
        "asyncio": "async def / await - Asynchronous coroutine event loop syntax"
    },
    "docker": {
        "build": "docker build -t image_name:tag . - Build Dockerfile in current dir",
        "run": "docker run -d -p 8080:80 --name my_app image_name - Run container",
        "ps": "docker ps -a - List all running and stopped containers",
        "stop": "docker stop <container_id> - Gracefully stop container",
        "exec": "docker exec -it <container_id> /bin/bash - Open shell inside container",
        "logs": "docker logs -f <container_id> - Follow container live console logs",
        "prune": "docker system prune -a --volumes - Wipe unused containers and images"
    },
    "linux": {
        "tar": "tar -czvf archive.tar.gz /folder - Compress directory into gzip tarball",
        "grep": "grep -rnwi '/path' -e 'pattern' - Recursive search text in files",
        "find": "find / -type f -name '*.log' - Search filesystem for matching filenames",
        "chmod": "chmod +x script.sh - Grant executable permissions",
        "chown": "chown user:group /path - Change file ownership",
        "df": "df -h - Display disk space usage by partition in human readable format",
        "top": "htop / top - Interactive process viewer and resource monitor"
    }
}

# Scientific and mathematical constants
SCIENCE_CONSTANTS: Dict[str, str] = {
    "speed of light": "Speed of light (c) lagbhag 299,792,458 meters per second hai (approx 3 lakh km/s).",
    "gravitational constant": "Universal gravitational constant (G) hai 6.67430 × 10^-11 N m^2 / kg^2.",
    "planck constant": "Planck constant (h) hai 6.62607 × 10^-34 Joule-seconds.",
    "avogadro number": "Avogadro constant (N_A) hai 6.02214 × 10^23 particles per mole.",
    "charge of electron": "Elementary electric charge (e) hai 1.602176 × 10^-19 Coulombs.",
    "acceleration due to gravity": "Earth par acceleration due to gravity (g) approximately 9.80665 m/s^2 hai."
}

# World capitals reference
WORLD_CAPITALS: Dict[str, str] = {
    "india": "New Delhi",
    "united states": "Washington, D.C.",
    "usa": "Washington, D.C.",
    "united kingdom": "London",
    "uk": "London",
    "japan": "Tokyo",
    "germany": "Berlin",
    "france": "Paris",
    "russia": "Moscow",
    "china": "Beijing",
    "australia": "Canberra",
    "canada": "Ottawa",
    "brazil": "Brasília",
    "south africa": "Pretoria",
    "italy": "Rome",
    "spain": "Madrid",
    "uae": "Abu Dhabi",
    "dubai": "Capital of UAE is Abu Dhabi",
    "singapore": "Singapore City"
}


class KnowledgeBase:
    """Offline reference encyclopedia."""

    @classmethod
    def lookup(cls, query: str) -> Optional[str]:
        q = query.lower().strip()

        # Check capitals
        for country, cap in WORLD_CAPITALS.items():
            if f"capital of {country}" in q or f"{country} ki capital" in q or f"{country} ki rajdhani" in q:
                return f"Sir, {country.capitalize()} ki capital '{cap}' hai."

        # Check scientific constants
        for const_name, desc in SCIENCE_CONSTANTS.items():
            if const_name in q:
                return f"Sir, {desc}"

        # Check programming cheatsheets
        for tech, commands in DEV_CHEATSHEETS.items():
            if tech in q:
                for cmd_name, explanation in commands.items():
                    if cmd_name in q:
                        return f"Sir, {tech.upper()} '{cmd_name}' command syntax hai: {explanation}"

        return None
