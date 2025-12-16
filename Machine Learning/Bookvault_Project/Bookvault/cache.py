import os
import sqlite3
import json
import time
from abc import ABC, abstractmethod
from typing import Optional, Any, Dict
from .logger import get_logger

logger = get_logger(__name__)


class CacheProvider(ABC):
    @abstractmethod
    def get(self, key: str) -> Optional[Any]: ...
    @abstractmethod
    def set(self, key: str, value: Any) -> None: ...
    @abstractmethod
    def clear(self) -> None: ...


class SQLiteCache(CacheProvider):
    def __init__(self, db_path: str, max_age_hours: int = 24):
        os.makedirs(os.path.dirname(db_path) or ".", exist_ok=True)
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.max_age_hours = max_age_hours
        logger.info(f"Initializing SQLite cache at {db_path} with {max_age_hours}h TTL")
        self._init_db()
        self._clean_old_entries()

    def _init_db(self):
        # Add timestamp column if it doesn't exist
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS cache (
                key TEXT PRIMARY KEY,
                value TEXT,
                timestamp REAL DEFAULT 0
            )
        """)
        self.conn.execute("CREATE TABLE IF NOT EXISTS embeddings (book_id TEXT PRIMARY KEY, embedding TEXT)")

        # Check if timestamp column exists, if not add it
        cursor = self.conn.execute("PRAGMA table_info(cache)")
        columns = [column[1] for column in cursor.fetchall()]
        if 'timestamp' not in columns:
            self.conn.execute("ALTER TABLE cache ADD COLUMN timestamp REAL DEFAULT 0")

        self.conn.commit()

    def get(self, key: str) -> Optional[Any]:
        try:
            row = self.conn.execute("SELECT value FROM cache WHERE key=? LIMIT 1", (key,)).fetchone()
            if row:
                try:
                    logger.debug(f"Cache HIT for key: {key[:50]}")
                    return json.loads(row[0])
                except json.JSONDecodeError as e:
                    logger.error(f"JSON decode error for key {key[:50]}: {e}")
                    return None
            logger.debug(f"Cache MISS for key: {key[:50]}")
            return None
        except Exception as e:
            logger.error(f"Cache get error for key {key[:50]}: {e}")
            return None

    def set(self, key: str, value: Any) -> None:
        try:
            timestamp = time.time()
            self.conn.execute(
                "INSERT OR REPLACE INTO cache (key, value, timestamp) VALUES (?, ?, ?)",
                (key, json.dumps(value), timestamp)
            )
            self.conn.commit()
            logger.debug(f"Cache SET for key: {key[:50]}")
        except Exception as e:
            logger.error(f"Cache set error for key {key[:50]}: {e}")

    def clear(self) -> None:
        """Clear all cache entries"""
        self.conn.execute("DELETE FROM cache")
        self.conn.commit()

    def _clean_old_entries(self) -> None:
        """Remove cache entries older than max_age_hours"""
        cutoff_time = time.time() - (self.max_age_hours * 3600)
        self.conn.execute("DELETE FROM cache WHERE timestamp < ?", (cutoff_time,))
        self.conn.commit()

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        cursor = self.conn.execute("SELECT COUNT(*) FROM cache")
        total_entries = cursor.fetchone()[0]

        cursor = self.conn.execute("SELECT SUM(LENGTH(value)) FROM cache")
        total_size = cursor.fetchone()[0] or 0

        return {
            "total_entries": total_entries,
            "total_size_kb": round(total_size / 1024, 2),
            "max_age_hours": self.max_age_hours
        }

    def clear_old_entries(self) -> int:
        """Manually clear old entries and return count of deleted entries"""
        cutoff_time = time.time() - (self.max_age_hours * 3600)
        cursor = self.conn.execute("SELECT COUNT(*) FROM cache WHERE timestamp < ?", (cutoff_time,))
        count = cursor.fetchone()[0]
        self.conn.execute("DELETE FROM cache WHERE timestamp < ?", (cutoff_time,))
        self.conn.commit()
        return count
