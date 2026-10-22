"""
================================================================================
                    JARVIS EPISODIC & LONG-TERM MEMORY
================================================================================
Persistent cognitive store backed by SQLite with tables for user profile facts,
multi-turn conversation logs, scheduled reminders, and habit analytics.
================================================================================
"""

import time
import sqlite3
import threading
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path

from jarvis.core.logger import get_logger

DB_PATH = Path(__file__).resolve().parent.parent.parent / "jarvis" / "data" / "memory.db"
DB_PATH.parent.mkdir(parents=True, exist_ok=True)


class MemoryStore:
    """Thread-safe SQLite episodic memory engine."""

    _instance: Optional["MemoryStore"] = None
    _lock = threading.RLock()

    def __new__(cls) -> "MemoryStore":
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(MemoryStore, cls).__new__(cls)
                cls._instance._init_db()
            return cls._instance

    def _init_db(self) -> None:
        self.logger = get_logger()
        with self._lock:
            try:
                conn = sqlite3.connect(str(DB_PATH))
                cursor = conn.cursor()

                # 1. User facts & knowledge graph
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS user_facts (
                        key TEXT PRIMARY KEY,
                        value TEXT NOT NULL,
                        category TEXT DEFAULT 'general',
                        updated_at REAL NOT NULL
                    )
                """)

                # 2. Conversation history
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS conversation_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp REAL NOT NULL,
                        role TEXT NOT NULL,
                        message TEXT NOT NULL,
                        intent TEXT
                    )
                """)

                # 3. Reminders & Tasks
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS reminders (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        title TEXT NOT NULL,
                        target_time REAL NOT NULL,
                        recurring_interval REAL DEFAULT 0,
                        is_completed INTEGER DEFAULT 0
                    )
                """)

                # 4. Quick notes
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS notes (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp REAL NOT NULL,
                        content TEXT NOT NULL
                    )
                """)

                conn.commit()
                conn.close()
                self.logger.info("SQLite cognitive memory store ready.", "MEMORY")
            except Exception as e:
                self.logger.error(f"Failed to initialize memory DB: {e}", "MEMORY")

    def _get_connection(self) -> sqlite3.Connection:
        return sqlite3.connect(str(DB_PATH))

    # ─────────────────────────────────────────────────────────
    #  USER FACTS
    # ─────────────────────────────────────────────────────────
    def store_fact(self, key: str, value: str, category: str = "general") -> None:
        with self._lock:
            try:
                conn = self._get_connection()
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO user_facts (key, value, category, updated_at)
                    VALUES (?, ?, ?, ?)
                    ON CONFLICT(key) DO UPDATE SET
                        value = excluded.value,
                        category = excluded.category,
                        updated_at = excluded.updated_at
                """, (key.lower().strip(), value.strip(), category, time.time()))
                conn.commit()
                conn.close()
            except Exception as e:
                self.logger.error(f"Error storing fact: {e}", "MEMORY")

    def get_fact(self, key: str) -> Optional[str]:
        with self._lock:
            try:
                conn = self._get_connection()
                cursor = conn.cursor()
                cursor.execute("SELECT value FROM user_facts WHERE key = ?", (key.lower().strip(),))
                row = cursor.fetchone()
                conn.close()
                return row[0] if row else None
            except Exception as e:
                self.logger.error(f"Error reading fact: {e}", "MEMORY")
                return None

    def list_all_facts(self) -> Dict[str, str]:
        with self._lock:
            try:
                conn = self._get_connection()
                cursor = conn.cursor()
                cursor.execute("SELECT key, value FROM user_facts")
                rows = cursor.fetchall()
                conn.close()
                return {r[0]: r[1] for r in rows}
            except Exception:
                return {}

    # ─────────────────────────────────────────────────────────
    #  CONVERSATION HISTORY
    # ─────────────────────────────────────────────────────────
    def log_turn(self, role: str, message: str, intent: Optional[str] = None) -> None:
        with self._lock:
            try:
                conn = self._get_connection()
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO conversation_history (timestamp, role, message, intent)
                    VALUES (?, ?, ?, ?)
                """, (time.time(), role, message, intent))
                conn.commit()
                conn.close()
            except Exception as e:
                self.logger.error(f"Error logging conversation turn: {e}", "MEMORY")

    def get_recent_turns(self, limit: int = 10) -> List[Dict[str, Any]]:
        with self._lock:
            try:
                conn = self._get_connection()
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT timestamp, role, message, intent
                    FROM conversation_history
                    ORDER BY id DESC LIMIT ?
                """, (limit,))
                rows = cursor.fetchall()
                conn.close()
                rows.reverse()
                return [
                    {"timestamp": r[0], "role": r[1], "message": r[2], "intent": r[3]}
                    for r in rows
                ]
            except Exception:
                return []

    # ─────────────────────────────────────────────────────────
    #  NOTES STORAGE
    # ─────────────────────────────────────────────────────────
    def add_note(self, content: str) -> int:
        with self._lock:
            try:
                conn = self._get_connection()
                cursor = conn.cursor()
                cursor.execute("INSERT INTO notes (timestamp, content) VALUES (?, ?)", (time.time(), content))
                conn.commit()
                note_id = cursor.lastrowid
                conn.close()
                return note_id or 0
            except Exception as e:
                self.logger.error(f"Error adding note: {e}", "MEMORY")
                return 0

    def get_all_notes(self) -> List[Tuple[int, float, str]]:
        with self._lock:
            try:
                conn = self._get_connection()
                cursor = conn.cursor()
                cursor.execute("SELECT id, timestamp, content FROM notes ORDER BY id DESC")
                rows = cursor.fetchall()
                conn.close()
                return rows
            except Exception:
                return []

    def clear_notes(self) -> None:
        with self._lock:
            try:
                conn = self._get_connection()
                cursor = conn.cursor()
                cursor.execute("DELETE FROM notes")
                conn.commit()
                conn.close()
            except Exception:
                pass


def get_memory() -> MemoryStore:
    return MemoryStore()
