import pyttsx3

def read_aloud(text):
    engine = pyttsx3.init()
    # Set properties before adding anything to speak
    voices = engine.getProperty('voices')
    engine.setProperty('voice', voices[1].id)  # Change index to select a different voice
    engine.setProperty('rate', 130)  # Reduce the speed of the voice (default is usually around 200)
    engine.say(text)
    engine.runAndWait()
