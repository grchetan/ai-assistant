"""
================================================================================
                    JARVIS BREAKING NEWS & HEADLINES PLUGIN
================================================================================
Retrieves top news headlines from public RSS / API feeds.
================================================================================
"""

import xml.etree.ElementTree as ET
import urllib.request
from typing import Dict, Any, Tuple, List

from jarvis.plugins.plugin_base import JarvisPlugin


class NewsPlugin(JarvisPlugin):
    """Fetches top breaking headlines."""

    @property
    def name(self) -> str:
        return "news"

    @property
    def description(self) -> str:
        return "Reads current breaking headlines."

    def can_handle(self, text: str) -> bool:
        t = text.lower()
        return any(k in t for k in ["news", "samachar", "khabar", "headlines"])

    def execute(self, text: str, payload: Dict[str, Any]) -> Tuple[bool, str]:
        # Google News RSS for India/Global
        url = "https://news.google.com/rss?hl=en-IN&gl=IN&ceid=IN:en"
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'JARVIS/4.0'})
            with urllib.request.urlopen(req, timeout=5) as resp:
                xml_data = resp.read()

            root = ET.fromstring(xml_data)
            items = root.findall(".//item")
            headlines: List[str] = []

            for item in items[:3]:
                title = item.find("title")
                if title is not None and title.text:
                    # Clean title (remove source suffix if any)
                    h = title.text.split(" - ")[0].strip()
                    headlines.append(h)

            if headlines:
                speech = "Sir, aaj ki top headlines hain: " + ". Agli khabar: ".join(headlines)
                return True, speech
            else:
                return False, "Sir, abhi headlines fetch nahi ho payi."
        except Exception:
            return False, "Sir, news service se connect karne me problem hui."
