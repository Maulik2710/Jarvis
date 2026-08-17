# config.py
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
TEMP_AUDIO_PATH = BASE_DIR / "temp_audio.mp3"
DATABASE_PATH = BASE_DIR / "memory" / "jarvis.db"
MEMORY_FILE_PATH = BASE_DIR / "memory" / "explicit_memory.json"

LOCAL_MODEL = "qwen2.5:7b"
OLLAMA_BASE_URL = "http://localhost:11434/v1"

SYSTEM_INSTRUCTION = (
    "You are Jarvis, an advanced AI assistant. "
    "Rules to follow strictly:\n"
    "1. Keep spoken responses concise and direct (under 2 sentences).\n"
    "2. Execute tools efficiently when requested.\n"
    "3. Use stored profile and routines to resolve context before executing actions."
)