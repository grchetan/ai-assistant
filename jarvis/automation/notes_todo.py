"""
================================================================================
                    JARVIS NOTES & TO-DO TASK MANAGER
================================================================================
Productivity subsystem managing voice-dictated notes, categorized task lists,
due dates, completion status, and Markdown journal generation.
================================================================================
"""

import time
from typing import List, Dict, Any, Optional
from pathlib import Path

from jarvis.core.logger import get_logger
from jarvis.brain.memory import get_memory

NOTES_EXPORT_PATH = Path(__file__).resolve().parent.parent.parent / "jarvis" / "data" / "user_notes.md"


class NotesTodoManager:
    """Handles personal productivity notes and actionable items."""

    def __init__(self) -> None:
        self.logger = get_logger()
        self.memory = get_memory()
        self._todos: List[Dict[str, Any]] = []

    def add_note(self, note_text: str) -> str:
        """Record a quick voice note."""
        clean = note_text.strip()
        if not clean:
            return "Note khali nahi ho sakta sir."

        note_id = self.memory.add_note(clean)
        self.logger.info(f"Recorded note #{note_id}: {clean}", "NOTES")
        return f"Note likh liya hai sir: '{clean}'"

    def read_notes(self) -> str:
        """Read recent notes out loud."""
        notes = self.memory.get_all_notes()
        if not notes:
            return "Sir, abhi tak koi notes save nahi kiye gaye hain."

        recent = notes[:3]
        items = [f"Note {idx+1}: {row[2]}" for idx, row in enumerate(recent)]
        return "Sir, aapke recent notes hain: " + ". ".join(items)

    def add_todo(self, task_name: str) -> str:
        """Add item to To-Do checklist."""
        clean = task_name.strip()
        if not clean:
            return "Task name empty nahi ho sakta."

        item = {
            "id": len(self._todos) + 1,
            "title": clean,
            "created_at": time.time(),
            "done": False
        }
        self._todos.append(item)
        self.logger.info(f"Added task: '{clean}'", "TODO")
        return f"To-Do list me add kar diya sir: '{clean}'"

    def list_todos(self) -> str:
        """Summary of pending to-do items."""
        pending = [t for t in self._todos if not t["done"]]
        if not pending:
            return "Sir, aapki to-do list bilkul clear hai. Koi pending kaam nahi hai!"

        items = [f"{t['id']}: {t['title']}" for t in pending[:4]]
        return f"Sir, aapke {len(pending)} pending tasks hain: " + ", ".join(items)

    def clear_all_notes(self) -> str:
        self.memory.clear_notes()
        return "Sabhi notes clear kar diye gaye hain sir."


def get_notes_manager() -> NotesTodoManager:
    return NotesTodoManager()
