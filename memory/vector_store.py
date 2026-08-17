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
        Deletes a specific remembered topic. Matches exact keys and partial topic matches.
        :param topic_key: The topic to forget (e.g., 'favorite_song', 'song', 'music').
        """
        data = self._read_memory()
        clean_key = topic_key.lower().strip().replace(" ", "_")

        # 1. Exact match check
        if clean_key in data:
            deleted_val = data.pop(clean_key)
            self._write_memory(data)
            return f"Removed {clean_key.replace('_', ' ')} ('{deleted_val}') from memory."

        # 2. Fuzzy / Partial match check (e.g. user says 'song', key is 'favorite_song')
        keys_to_delete = [
            k for k in data.keys() 
            if clean_key in k or k in clean_key or clean_key.replace("favorite", "fav") in k
        ]

        if keys_to_delete:
            deleted_items = []
            for k in keys_to_delete:
                deleted_items.append(f"{k.replace('_', ' ')} ('{data.pop(k)}')")
            self._write_memory(data)
            return f"Successfully deleted: {', '.join(deleted_items)}."

        return f"No memory found matching '{topic_key}'."

    def get_all_memories_string(self) -> str:
        """Always re-reads directly from disk to prevent stale data."""
        data = self._read_memory()
        if not data:
            return "None."
        return ", ".join([f"{k.replace('_', ' ')}: {v}" for k, v in data.items()])