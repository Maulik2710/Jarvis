import speech_recognition as sr
import webbrowser
import pyttsx3
import plateform
import musiclibrary
import requests


recognizer = sr.Recognizer()
recognizer.dynamic_energy_threshold = False  
recognizer.energy_threshold = 300  
recognizer.pause_threshold = 0.8 

engine = pyttsx3.init()

def speak(text):
    engine.say(text)
    engine.runAndWait()
    
def ProcessCommand(command):
    
    command = command.lower()
    print(f"Processing command: {command}") 
    try:
        
        if command.lower().startswith("open"):
            point  = command.lower().split(" ")[1]
            lnk = plateform.app[point]
            webbrowser.open(lnk)
            
        elif command.lower().startswith("play"):
            point  = command.lower().split(" ")[1]
            lnk = musiclibrary.music[point]
            webbrowser.open(lnk)
        
        elif "news" in command.lower():
        
            response = requests.get("https://newsapi.org/v2/top-headlines?country=in&apiKey=e660c7486d194a9894ce541b58962757")
            # Check if the request was successful
            if response.status_code == 200:
                data = response.json()  # Parse the JSON response
                articles = data.get('articles', [])  # Get the list of articles
                # Extract and print the headlines
                for article in articles:
                    headline = article.get('title')
                    if headline:
                        speak(headline)
        else:
            print("Command not recognized.")
    except Exception as e:
        print(f"Error opening browser: {e}") 
    
        
    
if __name__ == "__main__":
    speak("..Initializing Jarvis..")
    
    
    while  True:

        with sr.Microphone() as source:
            print("Listening...")
            recognizer.adjust_for_ambient_noise(source,duration=0.5)
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=3)
        
        try:
            word = recognizer.recognize_google(audio)
            
            #I have to wait for the wake up call "jarvis"
            
            if(word.lower() == "jarvis"):
                speak("Jarvis Activated..")
                 
                 #Listen for commands!
                 
                with sr.Microphone() as source:
                    print("Jarvis activeted...")
                    print("Give me command...")
                    recognizer.adjust_for_ambient_noise(source,duration=0.5)
                    audio = recognizer.listen(source, timeout=5, phrase_time_limit=5)
                    
                    command = recognizer.recognize_google(audio)
                    print(f"Recognized command: {command}")
                    ProcessCommand(command)
            elif(word.lower() == "stop"):
                break
            
        except Exception as e:
            print("Error; {0}".format(e))
