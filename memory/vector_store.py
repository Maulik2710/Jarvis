# memory/vector_store.py
import json
from pathlib import Path
from config import BASE_DIR

MEMORY_FILE = BASE_DIR / "memory" / "explicit_memory.json"

class ExplicitMemoryManager:
    def __init__(self):
        MEMORY_FILE.parent.mkdir(parents=True, exist_ok=True)
        if not MEMORY_FILE.exists():
            with open(MEMORY_FILE, "w") as f:
                json.dump({}, f)

    def _read_memory(self) -> dict:
        try:
            with open(MEMORY_FILE, "r") as f:
                return json.load(f)
        except Exception:
            return {}

    def _write_memory(self, data: dict):
        with open(MEMORY_FILE, "w") as f:
            json.dump(data, f, indent=4)

    def save_or_update_memory(self, topic_key: str, detail: str) -> str:
        """
        Saves or updates information the user explicitly asks to remember.
        :param topic_key: Topic name (e.g., 'favorite_song', 'nickname').
        :param detail: The detail to remember.
        """
        data = self._read_memory()
        clean_key = topic_key.lower().strip().replace(" ", "_")
        data[clean_key] = detail
        self._write_memory(data)
        return f"Saved {topic_key.replace('_', ' ')}: '{detail}'."

    def forget_memory(self, topic_key: str) -> str:
        """
        Deletes a specific remembered topic.
        :param topic_key: The topic to forget.
        """
        data = self._read_memory()
        clean_key = topic_key.lower().strip().replace(" ", "_")
        if clean_key in data:
            del data[clean_key]
            self._write_memory(data)
            return f"Removed {topic_key.replace('_', ' ')} from memory."
        return f"No memory found for '{topic_key}'."

    def get_all_memories_string(self) -> str:
        """Returns all remembered facts formatted as a clear list for the LLM."""
        data = self._read_memory()
        if not data:
            return "None."
        return ", ".join([f"{k.replace('_', ' ')}: {v}" for k, v in data.items()])