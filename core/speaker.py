# core/speaker.py
import asyncio
import os
import edge_tts
import pygame
from config import TEMP_AUDIO_PATH

# Voice options: 'en-US-ChristopherNeural', 'en-US-EricNeural', 'en-GB-RyanNeural'
VOICE = "en-US-ChristopherNeural"

class Speaker:
    def __init__(self):
        pygame.mixer.init()

    async def _generate_audio(self, text: str):
        """Generates audio file asynchronously using Edge-TTS."""
        communicate = edge_tts.Communicate(text, VOICE)
        await communicate.save(str(TEMP_AUDIO_PATH))

    def speak(self, text: str):
        """Converts text to speech and plays it back."""
        if not text or not text.strip():
            return

        print(f"🔊 [Jarvis Speaking]: {text}")
        try:
            # Generate TTS audio file
            asyncio.run(self._generate_audio(text))

            # Play audio using pygame
            pygame.mixer.music.load(str(TEMP_AUDIO_PATH))
            pygame.mixer.music.play()

            # Wait for playback to finish
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)

            pygame.mixer.music.unload()

        except Exception as e:
            print(f"❌ [Speaker Error]: {e}")
        finally:
            # Cleanup temporary audio file
            if os.path.exists(TEMP_AUDIO_PATH):
                try:
                    os.remove(TEMP_AUDIO_PATH)
                except Exception:
                    pass