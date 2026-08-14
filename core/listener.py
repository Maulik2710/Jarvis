# core/listener.py
import speech_recognition as sr

class Listener:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = 300
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 0.8  # Gives enough time between words

    def listen(self) -> str:
        with sr.Microphone() as source:
            print("\n🎙️ [Listening...]: Speak now.")
            try:
                audio = self.recognizer.listen(source, timeout=6, phrase_time_limit=10)
                print("⚡ [Processing Speech...]")
                text = self.recognizer.recognize_google(audio)
                print(f"👤 [You Said]: {text}")
                return text.strip()
            except (sr.WaitTimeoutError, sr.UnknownValueError):
                return ""
            except sr.RequestError as e:
                print(f"❌ [Listener Error]: {e}")
                return ""