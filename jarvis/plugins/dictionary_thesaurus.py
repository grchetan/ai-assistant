"""
================================================================================
                    JARVIS VOCABULARY & DICTIONARY PLUGIN
================================================================================
Natural language lexicon providing definitions, synonyms, antonyms, and
vocabulary enrichment.
================================================================================
"""

import json
import urllib.request
from typing import Dict, Any, Tuple

from jarvis.plugins.plugin_base import JarvisPlugin


class DictionaryPlugin(JarvisPlugin):
    """Word definitions and synonyms."""

    @property
    def name(self) -> str:
        return "dictionary"

    @property
    def description(self) -> str:
        return "Fetches English dictionary meanings and synonyms."

    def can_handle(self, text: str) -> bool:
        t = text.lower()
        return any(k in t for k in ["meaning of", "define", "ka matlab kya hai", "synonym of"])

    def execute(self, text: str, payload: Dict[str, Any]) -> Tuple[bool, str]:
        # Extract target word
        t = text.lower().replace("meaning of", "").replace("define", "").replace("ka matlab kya hai", "").strip()
        words = t.split()
        if not words:
            return False, "Kripya word specify karein."
        word = words[0]

        url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'JARVIS/4.0'})
            with urllib.request.urlopen(req, timeout=4) as resp:
                data = json.loads(resp.read().decode('utf-8'))

            meanings = data[0]['meanings'][0]
            part = meanings['partOfSpeech']
            definition = meanings['definitions'][0]['definition']

            speech = f"Sir, '{word}' ({part}) ka definition hai: {definition}"
            return True, speech
        except Exception:
            return False, f"Sir, '{word}' ka meaning online dictionary me nahi mila."
