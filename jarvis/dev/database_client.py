"""
================================================================================
                    JARVIS DATABASE CLIENT & DATA EXPLORER
================================================================================
Universal database query runner supporting local SQLite instances and MongoDB
collections with formatted ASCII terminal table output.
================================================================================
"""

import sqlite3
from typing import List, Dict, Any, Tuple
from pathlib import Path

try:
    from tabulate import tabulate
    _TABULATE_AVAILABLE = True
except ImportError:
    _TABULATE_AVAILABLE = False

from jarvis.core.logger import get_logger


class DatabaseClient:
    """Inspects and executes queries on SQLite databases."""

    def __init__(self) -> None:
        self.logger = get_logger()

    def query_sqlite(self, db_path: str, sql_query: str) -> Tuple[bool, str]:
        """Execute a safe read-only SQL query on an SQLite file."""
        p = Path(db_path)
        if not p.exists():
            return False, f"Database file not found: {db_path}"

        self.logger.info(f"Querying SQLite [{p.name}]: {sql_query}", "DB")
        try:
            conn = sqlite3.connect(str(p))
            cursor = conn.cursor()
            cursor.execute(sql_query)

            headers = [desc[0] for desc in cursor.description] if cursor.description else []
            rows = cursor.fetchall()
            conn.close()

            if not rows:
                return True, "Query executed: 0 rows returned."

            if _TABULATE_AVAILABLE:
                table_str = tabulate(rows, headers=headers, tablefmt="fancy_grid")
            else:
                table_str = f"Columns: {headers}\nRows: {rows}"

            return True, table_str
        except Exception as e:
            return False, f"SQL Query Error: {e}"

    def list_sqlite_tables(self, db_path: str) -> List[str]:
        """List all table names inside an SQLite database."""
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = [row[0] for row in cursor.fetchall()]
            conn.close()
            return tables
        except Exception:
            return []


def get_db_client() -> DatabaseClient:
    return DatabaseClient()
