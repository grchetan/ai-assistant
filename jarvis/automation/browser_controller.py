"""
================================================================================
                    JARVIS BROWSER & WEB NAVIGATION
================================================================================
Automates web browsing, searches across Google, YouTube, GitHub, StackOverflow,
and opens specific portals in default or incognito mode.
================================================================================
"""

import urllib.parse
import webbrowser
import subprocess
from typing import Optional, Tuple

from jarvis.core.logger import get_logger


class BrowserController:
    """Manages browser search and tab navigation."""

    def __init__(self) -> None:
        self.logger = get_logger()

    def search_google(self, query: str) -> str:
        """Execute Google search in default browser."""
        self.logger.info(f"Searching Google for: '{query}'", "BROWSER")
        encoded = urllib.parse.quote_plus(query.strip())
        url = f"https://www.google.com/search?q={encoded}"
        webbrowser.open(url)
        return f"Google par '{query}' search kar diya sir."

    def search_youtube(self, query: str) -> str:
        """Execute YouTube search or playback."""
        self.logger.info(f"Searching YouTube for: '{query}'", "BROWSER")
        encoded = urllib.parse.quote_plus(query.strip())
        url = f"https://www.youtube.com/results?search_query={encoded}"
        webbrowser.open(url)
        return f"YouTube par '{query}' open kar diya sir."

    def search_github(self, query: str) -> str:
        """Search repositories on GitHub."""
        self.logger.info(f"Searching GitHub for: '{query}'", "BROWSER")
        encoded = urllib.parse.quote_plus(query.strip())
        url = f"https://github.com/search?q={encoded}"
        webbrowser.open(url)
        return f"GitHub par '{query}' khoj raha hoon sir."

    def search_stackoverflow(self, query: str) -> str:
        """Search programming questions on StackOverflow."""
        self.logger.info(f"Searching StackOverflow for: '{query}'", "BROWSER")
        encoded = urllib.parse.quote_plus(query.strip())
        url = f"https://stackoverflow.com/search?q={encoded}"
        webbrowser.open(url)
        return f"Stack Overflow par solution open kar diya sir."

    def open_url(self, raw_target: str) -> str:
        """Normalize and open any website domain or shortcut."""
        target = raw_target.lower().strip()
        shortcuts = {
            "google": "https://www.google.com",
            "youtube": "https://www.youtube.com",
            "github": "https://www.github.com",
            "chatgpt": "https://chat.openai.com",
            "gemini": "https://gemini.google.com",
            "gmail": "https://mail.google.com",
            "whatsapp": "https://web.whatsapp.com",
            "reddit": "https://www.reddit.com",
            "twitter": "https://twitter.com",
            "x": "https://twitter.com",
            "amazon": "https://www.amazon.in",
            "flipkart": "https://www.flipkart.com",
            "speedtest": "https://fast.com"
        }

        url = shortcuts.get(target)
        if not url:
            if not target.startswith("http://") and not target.startswith("https://"):
                url = f"https://{target}"
            else:
                url = target

        webbrowser.open(url)
        self.logger.info(f"Opening URL: {url}", "BROWSER")
        return f"{target} open kar diya sir."

    def open_incognito(self, url: str = "https://www.google.com") -> str:
        """Open Chrome or Edge in private browsing mode."""
        self.logger.info("Opening private browsing session.", "BROWSER")
        try:
            subprocess.Popen(["chrome.exe", "--incognito", url], shell=True)
            return "Chrome incognito tab khol diya sir."
        except Exception:
            try:
                subprocess.Popen(["msedge.exe", "-inprivate", url], shell=True)
                return "Edge in-private tab khol diya sir."
            except Exception as e:
                webbrowser.open(url)
                return "Default browser me open kar diya sir."


def get_browser_controller() -> BrowserController:
    return BrowserController()
