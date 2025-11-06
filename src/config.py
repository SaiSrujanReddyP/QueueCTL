"""
Configuration management for QueueCTL
"""

import sqlite3
import threading
from typing import Any, Dict, Optional


class Config:
    def __init__(self, db_path: str = "jobs.db"):
        self.db_path = db_path
        self._lock = threading.Lock()
        self._init_database()
        self._set_defaults()
    
    def _init_database(self):
        """Initialize the configuration table"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS config (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()
    
    def _set_defaults(self):
        """Set default configuration values if they don't exist"""
        defaults = {
            'max-retries': '3',
            'backoff-base': '2'
        }
        
        with self._lock:
            with sqlite3.connect(self.db_path) as conn:
                for key, value in defaults.items():
                    # Only set if key doesn't exist
                    cursor = conn.cursor()
                    cursor.execute("SELECT key FROM config WHERE key = ?", (key,))
                    if not cursor.fetchone():
                        conn.execute(
                            "INSERT INTO config (key, value) VALUES (?, ?)",
                            (key, value)
                        )
                conn.commit()
    
    def set(self, key: str, value: str) -> None:
        """Set a configuration value"""
        with self._lock:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO config (key, value, updated_at)
                    VALUES (?, ?, datetime('now'))
                """, (key, value))
                conn.commit()
    
    def get(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """Get a configuration value"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT value FROM config WHERE key = ?", (key,))
            row = cursor.fetchone()
            return row[0] if row else default
    
    def get_int(self, key: str, default: int = 0) -> int:
        """Get a configuration value as integer"""
        value = self.get(key)
        if value is None:
            return default
        try:
            return int(value)
        except ValueError:
            return default
    
    def get_float(self, key: str, default: float = 0.0) -> float:
        """Get a configuration value as float"""
        value = self.get(key)
        if value is None:
            return default
        try:
            return float(value)
        except ValueError:
            return default
    
    def delete(self, key: str) -> bool:
        """Delete a configuration value"""
        with self._lock:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM config WHERE key = ?", (key,))
                conn.commit()
                return cursor.rowcount > 0
    
    def list_all(self) -> Dict[str, str]:
        """Get all configuration values"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT key, value FROM config ORDER BY key")
            return dict(cursor.fetchall())
    
    def exists(self, key: str) -> bool:
        """Check if a configuration key exists"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM config WHERE key = ?", (key,))
            return cursor.fetchone() is not None