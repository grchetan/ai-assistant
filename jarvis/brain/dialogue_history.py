"""
================================================================================
                    JARVIS DIALOGUE TRANSCRIPT & EXPORT ENGINE
================================================================================
Persists rich multi-session interaction transcripts, generates formatted Markdown
summaries, and provides keyword search indexing across past interactions.
================================================================================
"""

import time
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path

from jarvis.core.logger import get_logger
from jarvis.brain.memory import get_memory

TRANSCRIPTS_DIR = Path(__file__).resolve().parent.parent.parent / "jarvis" / "data" / "transcripts"
TRANSCRIPTS_DIR.mkdir(parents=True, exist_ok=True)


class DialogueExporter:
    """Exports and searches conversational logs."""

    def __init__(self) -> None:
        self.logger = get_logger()
        self.memory = get_memory()

    def export_session_markdown(self, limit: int = 50) -> Tuple[bool, str, Optional[Path]]:
        """Generate a clean Markdown log of recent conversation history."""
        turns = self.memory.get_recent_turns(limit=limit)
        if not turns:
            return False, "Koi past conversation turns nahi mile.", None

        filename = f"session_{time.strftime('%Y%m%d_%H%M%S')}.md"
        out_path = TRANSCRIPTS_DIR / filename

        try:
            with open(out_path, "w", encoding="utf-8") as f:
                f.write(f"# J.A.R.V.I.S. Conversation Transcript\n")
                f.write(f"**Generated:** {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n---\n\n")

                for t in turns:
                    t_str = time.strftime("%H:%M:%S", time.localtime(t["timestamp"]))
                    role_badge = "👤 **USER**" if t["role"].lower() == "user" else "🤖 **JARVIS**"
                    intent_tag = f" `[{t['intent']}]`" if t.get("intent") else ""
                    f.write(f"### {role_badge} ({t_str}){intent_tag}\n")
                    f.write(f"> {t['message']}\n\n")

            self.logger.success(f"Exported transcript: {out_path.name}", "DIALOGUE")
            return True, f"Transcript exported successfully to {out_path.name} sir.", out_path

        except Exception as e:
            return False, f"Failed to export transcript: {e}", None

    def search_transcripts(self, keyword: str) -> List[Dict[str, Any]]:
        """Search past turns matching keyword query."""
        all_turns = self.memory.get_recent_turns(limit=200)
        q = keyword.lower().strip()
        return [t for t in all_turns if q in t["message"].lower()]


def get_dialogue_exporter() -> DialogueExporter:
    return DialogueExporter()
