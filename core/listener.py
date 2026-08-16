# core/listener.py
import speech_recognition as sr

class Listener:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        
        # 1. Fixed energy threshold (prevents sudden cutoff mid-speech)
        self.recognizer.energy_threshold = 200
        self.recognizer.dynamic_energy_threshold = False  # Keep false so it doesn't auto-raise threshold
        
        # 2. Allow comfortable pauses between words (1.5 to 2.0 seconds)
        self.recognizer.pause_threshold = 1.6
        
        # 3. Minimum seconds of speech required to register as phrase
        self.recognizer.phrase_threshold = 0.3
        
        # 4. Silence retention buffer before cutting
        self.recognizer.non_speaking_duration = 0.8

    def listen(self) -> str:
        with sr.Microphone() as source:
            print("\n🎙️ [Listening...]: Speak now.")
            try:
                # Generous phrase time limit (up to 20 seconds of continuous speaking)
                audio = self.recognizer.listen(
                    source, 
                    timeout=7, 
                    phrase_time_limit=20
                )
                print("⚡ [Processing Speech...]")
                
                # Transcribe speech
                text = self.recognizer.recognize_google(audio, language="en-IN")
                print(f"👤 [You Said]: {text}")
                return text.strip()

            except (sr.WaitTimeoutError, sr.UnknownValueError):
                return ""
            except sr.RequestError as e:
                print(f"❌ [Listener Error]: {e}")
                return ""