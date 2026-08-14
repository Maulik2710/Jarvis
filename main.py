# main.py
import os
import certifi

# Fix Windows SSL certificate error
os.environ["SSL_CERT_FILE"] = certifi.where()

from core.brain import Brain
from core.listener import Listener
from core.speaker import Speaker
from tools.app_launcher import launch_application, open_url
from tools.media_control import play_music
from tools.web_search import search_web, fetch_quick_answer

def main():
    print("⚡ Jarvis Engine Initializing with Hybrid RAG & Short-Term Memory...")
    
    brain = Brain(max_history_turns=5)
    speaker = Speaker()
    listener = Listener()

    # Register System & Action Tools 
    # (Note: Memory tools save_or_update_memory & forget_memory are registered automatically inside Brain)
    brain.register_tool(launch_application)
    brain.register_tool(open_url)
    brain.register_tool(play_music)
    brain.register_tool(search_web)
    brain.register_tool(fetch_quick_answer)

    speaker.speak("Systems online. Hybrid memory active. How can I assist you today, sir?")

    mode = input("\nSelect Mode -> (1) Voice Mode  (2) Text Mode: ").strip()

    while True:
        try:
            if mode == "1":
                user_input = listener.listen()
                if not user_input:
                    continue
            else:
                user_input = input("\nYou: ")

            # In main.py loop:
            if user_input.lower().strip() in ["exit", "quit", "shutdown", "stop", "bye"]:
                print("Jarvis: Shutting down systems. Goodbye!")
                break

            if not user_input.strip():
                continue

            response = brain.process_prompt(user_input)
            speaker.speak(response)

        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"❌ Error: {e}\n")

if __name__ == "__main__":
    main()