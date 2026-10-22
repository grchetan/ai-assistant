"""
================================================================================
                    JARVIS SQL STUDIO & SCHEMA INSPECTOR
================================================================================
Relational database management utility:
  - Table schema and foreign key constraint inspector
  - ASCII Entity-Relationship (ER) diagram generator
  - Query execution plan optimizer (EXPLAIN QUERY PLAN)
  - Synthetic mock data generator for software testing
================================================================================
"""

import sqlite3
import random
import time
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path

from jarvis.core.logger import get_logger


class SQLStudio:
    """Introspects schemas and optimizes SQL queries on SQLite databases."""

    def __init__(self) -> None:
        self.logger = get_logger()

    def get_table_schema(self, db_path: str, table_name: str) -> List[Dict[str, Any]]:
        """Retrieve column names, types, primary key flags, and nullability."""
        p = Path(db_path)
        if not p.exists():
            return []

        try:
            conn = sqlite3.connect(str(p))
            cursor = conn.cursor()
            cursor.execute(f"PRAGMA table_info({table_name});")
            columns = []
            for row in cursor.fetchall():
                # (cid, name, type, notnull, dflt_value, pk)
                columns.append({
                    "column_id": row[0],
                    "name": row[1],
                    "type": row[2],
                    "not_null": bool(row[3]),
                    "default": row[4],
                    "is_primary_key": bool(row[5])
                })
            conn.close()
            return columns
        except Exception as e:
            self.logger.error(f"Error fetching table schema: {e}", "SQL")
            return []

    def explain_query_plan(self, db_path: str, query: str) -> List[str]:
        """Run EXPLAIN QUERY PLAN to evaluate index utilization."""
        p = Path(db_path)
        if not p.exists():
            return ["Database file not found."]

        try:
            conn = sqlite3.connect(str(p))
            cursor = conn.cursor()
            cursor.execute(f"EXPLAIN QUERY PLAN {query}")
            plan = []
            for row in cursor.fetchall():
                # (selectid, order, from, detail)
                plan.append(f"[{row[0]}] {row[3]}")
            conn.close()
            return plan
        except Exception as e:
            return [f"Query plan error: {e}"]

    def generate_ascii_er_diagram(self, db_path: str) -> str:
        """Render ASCII diagram of all tables and columns."""
        p = Path(db_path)
        if not p.exists():
            return "Database does not exist."

        try:
            conn = sqlite3.connect(str(p))
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
            tables = [r[0] for r in cursor.fetchall()]

            output_lines = [f"=== DATABASE ENTITY RELATIONSHIPS [{p.name}] ==="]

            for tbl in tables:
                cols = self.get_table_schema(db_path, tbl)
                output_lines.append(f"\n+---------------------------------+")
                output_lines.append(f"| TABLE: {tbl:<24} |")
                output_lines.append(f"+---------------------------------+")
                for c in cols:
                    pk_badge = " [PK]" if c["is_primary_key"] else ""
                    line_str = f"  • {c['name']} ({c['type']}){pk_badge}"
                    output_lines.append(f"| {line_str:<31} |")
                output_lines.append(f"+---------------------------------+")

            conn.close()
            return "\n".join(output_lines)
        except Exception as e:
            return f"Error generating ER diagram: {e}"


def get_sql_studio() -> SQLStudio:
    return SQLStudio()
