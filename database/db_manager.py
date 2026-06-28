"""
Database Manager — SQLite + SQLAlchemy
Store, query, and export scraped data
"""

import sqlite3
import json
from typing import List, Dict, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Manage scraped data storage in SQLite."""

    def __init__(self, db_path: str = "scraper_data.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Initialize database with default schema."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS scraped_data (
                    id          INTEGER PRIMARY KEY AUTOINCREMENT,
                    url         TEXT,
                    table_name  TEXT,
                    data        TEXT,
                    created_at  TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS scrape_sessions (
                    id          INTEGER PRIMARY KEY AUTOINCREMENT,
                    url         TEXT,
                    total_items INTEGER,
                    status      TEXT,
                    started_at  TEXT,
                    finished_at TEXT
                )
            """)
            conn.commit()

    def insert_many(self, table: str, records: List[Dict]):
        """Insert multiple records."""
        if not records:
            return
        with sqlite3.connect(self.db_path) as conn:
            for record in records:
                conn.execute(
                    "INSERT INTO scraped_data (table_name, data) VALUES (?, ?)",
                    (table, json.dumps(record, ensure_ascii=False))
                )
            conn.commit()
        logger.info(f"Inserted {len(records)} records into '{table}'")

    def get_all(self, table: str) -> List[Dict]:
        """Retrieve all records from a table."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT data FROM scraped_data WHERE table_name = ?", (table,)
            )
            return [json.loads(row[0]) for row in cursor.fetchall()]

    def get_count(self, table: str) -> int:
        """Count records in a table."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT COUNT(*) FROM scraped_data WHERE table_name = ?", (table,)
            )
            return cursor.fetchone()[0]

    def search(self, table: str, keyword: str) -> List[Dict]:
        """Search records by keyword."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT data FROM scraped_data WHERE table_name = ? AND data LIKE ?",
                (table, f"%{keyword}%")
            )
            return [json.loads(row[0]) for row in cursor.fetchall()]

    def clear_table(self, table: str):
        """Delete all records from a table."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "DELETE FROM scraped_data WHERE table_name = ?", (table,)
            )
            conn.commit()

    def list_tables(self) -> List[str]:
        """List all table names used."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT DISTINCT table_name FROM scraped_data"
            )
            return [row[0] for row in cursor.fetchall()]

    def log_session(self, url: str, total: int, status: str = "success"):
        """Log a scraping session."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO scrape_sessions (url, total_items, status, finished_at) VALUES (?, ?, ?, ?)",
                (url, total, status, datetime.now().isoformat())
            )
            conn.commit()
