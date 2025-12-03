import speech_recognition as sr
import webbrowser
import pyttsx3
import plateform
import musiclibrary
import google.generativeai as genai
import dotenv

genai.configure(api_key="API_KEY")


recognizer = sr.Recognizer()
recognizer.dynamic_energy_threshold = False  
recognizer.energy_threshold = 350 
recognizer.pause_threshold = 0.6 


engine = pyttsx3.init()

def ask_gemini(prompt):
    ''' This helps to forward promt to gemini and then return the answer
    -- generate the model
    --give promt to gemini
    -- get answer from gemini and if it;s not able to generate the promt then error messege
    --output the reply'''
    
    print("Sending to Gemini:", prompt)
    try:
        model = genai.GenerativeModel(model_name="gemini-1.5-flash")
        response = model.generate_content(prompt)
        reply = response.text.strip() if response.text else "Sorry, I didn't get an answer."
        print("Gemini replied:", reply)
        speak(reply)
    except Exception as e:
        print(f"Gemini Error: {e}")
        speak("Sorry, I couldn't process that.")
        
def speak(text):
    engine.say(text)
    engine.runAndWait()
    
def ProcessCommand(command):
    ''' Process the command by taking command as input
    -- if the input starts with open then it will process and open that application
    -- if the input starts with play then it will play whatever the user want to hear
    -- if there is news in the sentence then we throw output of news with API key 
    ---else we sent the input to the gemini...'''
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
        else:
            ask_gemini(command)

    except Exception as e:
        print(f"Error opening browser: {e}") 
    
        
    
if __name__ == "__main__":
    speak("...Password Please.")
    for i in range(3):
        with sr.Microphone() as source:
            print("Listening...")
            recognizer.adjust_for_ambient_noise(source,duration=0.5)
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=3)
            password = recognizer.recognize_google(audio)
            print(password)
        correctness = False
        if(password.lower() == "sparky 123"):
            correctness = True
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
            if(correctness == True):
                break;
    
        else:
            speak("..Try again..")
            continue
    if(correctness == False):
        speak("..Security Alert..")
    
    
