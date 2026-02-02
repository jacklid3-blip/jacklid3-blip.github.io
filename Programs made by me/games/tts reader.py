import pyttsx3

def create_tts_reader():
    """Create and configure a TTS engine"""
    engine = pyttsx3.init()
    
    # Configure voice settings
    engine.setProperty('rate', 150)    # Speed of speech (words per minute)
    engine.setProperty('volume', 1.0)  # Volume (0.0 to 1.0)
    
    return engine

def speak(engine, text):
    """Speak the given text"""
    engine.say(text)
    engine.runAndWait()

def list_voices(engine):
    """List all available voices"""
    voices = engine.getProperty('voices')
    for i, voice in enumerate(voices):
        print(f"{i}: {voice.name}")
    return voices

def set_voice(engine, voice_index):
    """Set voice by index"""
    voices = engine.getProperty('voices')
    if 0 <= voice_index < len(voices):
        engine.setProperty('voice', voices[voice_index].id)

# Create the TTS engine
engine = create_tts_reader()

# List available voices
print("Available voices:")
voices = list_voices(engine)

# Example: Read a message
message = "Hello! This is a simple text to speech message reader."
print(f"\nReading: {message}")
speak(engine, message)