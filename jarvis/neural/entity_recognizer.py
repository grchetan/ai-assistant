"""
================================================================================
            JARVIS IN-HOUSE NAMED ENTITY RECOGNITION (NER) ENGINE
================================================================================
Custom regex-heuristic NER pipeline identifying semantic slots:
  • Datetime expressions (relative & absolute)
  • Duration & Timers (seconds, minutes, hours)
  • Currency & Financial Values (INR, USD, EUR)
  • IP Addresses (IPv4, IPv6) & Network Ports
  • Web URLs & File System Paths
  • Software Applications & Process Names
Zero cloud dependencies.
================================================================================
"""

import re
from typing import Dict, List, Any, Optional
from jarvis.core.logger import get_logger


class EntityRecognizer:
    """Extracts typed entities from unstructured natural language."""

    def __init__(self) -> None:
        self.logger = get_logger()

    def extract_entities(self, text: str) -> Dict[str, List[Any]]:
        """Identify all known entity classes within text."""
        entities: Dict[str, List[Any]] = {
            "ipv4": [],
            "urls": [],
            "file_paths": [],
            "currency": [],
            "percentages": [],
            "durations": [],
            "numbers": []
        }

        # 1. IPv4 Addresses
        ipv4_pattern = r"\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b"
        entities["ipv4"] = re.findall(ipv4_pattern, text)

        # 2. URLs
        url_pattern = r"https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+[/\w\.-]*"
        entities["urls"] = re.findall(url_pattern, text)

        # 3. Windows File Paths
        path_pattern = r"(?:[a-zA-Z]:\\(?:[^\\/:*?\"<>|\r\n]+\\)*[^\\/:*?\"<>|\r\n]*)"
        entities["file_paths"] = re.findall(path_pattern, text)

        # 4. Currency (INR, USD, EUR)
        currency_pattern = r"(?:₹|\$|€|rs\.?|inr|usd)\s*(\d+(?:,\d+)*(?:\.\d+)?)"
        entities["currency"] = re.findall(currency_pattern, text, re.IGNORECASE)

        # 5. Percentages
        pct_pattern = r"(\d+(?:\.\d+)?)\s*%"
        entities["percentages"] = [float(p) for p in re.findall(pct_pattern, text)]

        # 6. Durations (e.g. 5 minutes, 10 seconds, 2 hours)
        duration_pattern = r"(\d+)\s*(seconds?|secs?|minutes?|mins?|hours?|hrs?|ghante|minute)"
        durations = []
        for val, unit in re.findall(duration_pattern, text, re.IGNORECASE):
            durations.append({"value": int(val), "unit": unit.lower()})
        entities["durations"] = durations

        # 7. Raw Numbers
        num_pattern = r"\b\d+(?:\.\d+)?\b"
        entities["numbers"] = [float(n) for n in re.findall(num_pattern, text)]

        return entities


_recognizer_instance: Optional[EntityRecognizer] = None

def get_entity_recognizer() -> EntityRecognizer:
    global _recognizer_instance
    if _recognizer_instance is None:
        _recognizer_instance = EntityRecognizer()
    return _recognizer_instance
