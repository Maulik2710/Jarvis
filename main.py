# main.py
import sys
import os
import certifi
import threading
import time

os.environ["SSL_CERT_FILE"] = certifi.where()

from ui.neuro_ball import NeuroBallWidget
from core.brain import Brain
from core.listener import Listener
from core.speaker import Speaker
from tools.app_launcher import launch_application, open_url
from tools.media_control import play_music
from tools.web_search import search_web, fetch_quick_answer

class JarvisApp:
    def __init__(self):
        self.ui = NeuroBallWidget(size=130)
        self.brain = Brain()
        self.listener = Listener()
        self.speaker = Speaker()

        # Register tools
        self.brain.register_tool(launch_application)
        self.brain.register_tool(open_url)
        self.brain.register_tool(play_music)
        self.brain.register_tool(search_web)
        self.brain.register_tool(fetch_quick_answer)

        self.running = True
        self.is_sleeping = False

        # Bind mouse click event
        self.ui.set_on_click(self.toggle_sleep)

        # Start worker thread
        self.worker_thread = threading.Thread(target=self.run_voice_loop, daemon=True)
        self.worker_thread.start()

    def toggle_sleep(self):
        """Click to toggle Sleep <-> Wake"""
        self.is_sleeping = not self.is_sleeping
        if self.is_sleeping:
            self.ui.set_state("SLEEP")
        else:
            self.ui.set_state("LISTENING")

    def run_voice_loop(self):
        time.sleep(0.5)
        self.ui.set_state("SPEAKING")
        self.speaker.speak("Online and ready, sir.")
        self.ui.set_state("LISTENING")

        while self.running:
            if self.is_sleeping:
                time.sleep(0.2)
                continue

            self.ui.set_state("LISTENING")
            user_input = self.listener.listen()

            if not user_input or not self.running:
                continue

            # Sleep commands
            if any(cmd in user_input.lower() for cmd in ["sleep", "go to sleep", "stop listening"]):
                self.is_sleeping = True
                self.ui.set_state("SLEEP")
                self.speaker.speak("Going to sleep. Click me to wake up.")
                continue

            # Shutdown commands
            if any(cmd in user_input.lower() for cmd in ["exit", "shutdown", "quit"]):
                self.ui.set_state("SPEAKING")
                self.speaker.speak("Shutting down. Goodbye!")
                self.running = False
                self.ui.close()
                break

            # Thinking state
            self.ui.set_state("THINKING")
            response = self.brain.process_prompt(user_input)

            # Speaking state
            self.ui.set_state("SPEAKING")
            self.speaker.speak(response)

            self.ui.set_state("LISTENING")

    def start(self):
        self.ui.run()

if __name__ == "__main__":
    app = JarvisApp()
    app.start()