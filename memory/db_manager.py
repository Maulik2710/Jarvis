# memory/db_manager.py
import sqlite3
from typing import List, Tuple
from config import DATABASE_PATH

class DatabaseManager:
    def __init__(self):
        self.db_path = DATABASE_PATH
        self._init_db()

    def _get_connection(self):
        return sqlite3.connect(self.db_path)

    def _init_db(self):
        """Initializes tables for conversation history and user preferences."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Table for logging chat interactions
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS conversation_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    user_input TEXT NOT NULL,
                    assistant_response TEXT NOT NULL
                )
            """)
            
            # Table for key-value user preferences (e.g., favorite tracks, settings)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_preferences (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                )
            """)
            
            conn.commit()

    def log_interaction(self, user_input: str, assistant_response: str):
        """Saves a conversation turn to the database."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO conversation_history (user_input, assistant_response) VALUES (?, ?)",
                (user_input, assistant_response)
            )
            conn.commit()

    def get_recent_history(self, limit: int = 5) -> List[Tuple[str, str]]:
        """Retrieves recent conversation turns for context."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT user_input, assistant_response FROM conversation_history ORDER BY id DESC LIMIT ?",
                (limit,)
            )
            rows = cursor.fetchall()
            return list(reversed(rows))

    def set_preference(self, key: str, value: str) -> str:
        """Saves or updates a user preference."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT OR REPLACE INTO user_preferences (key, value) VALUES (?, ?)",
                (key.lower(), value)
            )
            conn.commit()
        return f"Saved preference: '{key}' = '{value}'"

    def get_preference(self, key: str) -> str:
        """Retrieves a stored user preference."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT value FROM user_preferences WHERE key = ?",
                (key.lower(),)
            )
            row = cursor.fetchone()
            if row:
                return f"Preference '{key}': {row[0]}"
            return f"No preference found for '{key}'."
        
# Create a global instance for tools to reference
db_instance = DatabaseManager()

def save_user_preference(key: str, value: str) -> str:
    """
    Saves a specific user preference or setting into long-term memory.
    :param key: The category or preference title (e.g. 'favorite_music', 'user_nickname').
    :param value: The value to remember.
    """
    return db_instance.set_preference(key, value)

def recall_user_preference(key: str) -> str:
    """
    Retrieves a stored user preference from long-term memory.
    :param key: The preference key to look up.
    """
    return db_instance.get_preference(key)