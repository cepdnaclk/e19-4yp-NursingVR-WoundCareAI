import os 
from dotenv import load_dotenv
from groq import Groq
import time

import io

import services.audio as audio

load_dotenv()
api_key = os.getenv("GROQ_API_KEY")

model = "playai-tts"
voice = "Adelaide-PlayAI"
response_format = "wav"

client = Groq(api_key=api_key)

def text_to_speech_and_play(text, model="playai-tts", voice="Adelaide-PlayAI", response_format="wav"):
    print("start_T",  time.time())
    response = client.audio.speech.create(
        model=model,
        voice=voice,
        input=text,
        response_format=response_format
    )
    print("end_T",  time.time())
    # If response has a .content or .read() method, use it; otherwise, use response directly
    if hasattr(response, "content"):
        audio_data = response.content
    elif hasattr(response, "read"):
        audio_data = response.read()
    else:
        # If response.write_to_file is the only way, fallback to temp file
        import tempfile
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            response.write_to_file(tmp.name)
            audio.play_audio(tmp.name)
            return

    # Try to play from memory
    audio_file_like = io.BytesIO(audio_data)
    audio.play_audio(audio_file_like)

def text_to_speech_bytes(text, model="playai-tts", voice="Adelaide-PlayAI", response_format="wav"):
    
    print(api_key)
    """Generate text-to-speech audio and return as bytes instead of playing"""
    response = client.audio.speech.create(
        model=model,
        voice=voice,
        input=text,
        response_format=response_format
    )
    
    # If response has a .content or .read() method, use it; otherwise, use response directly
    if hasattr(response, "content"):
        audio_data = response.content
    elif hasattr(response, "read"):
        audio_data = response.read()
    else:
        # If response.write_to_file is the only way, fallback to temp file
        import tempfile
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            response.write_to_file(tmp.name)
            with open(tmp.name, 'rb') as f:
                audio_data = f.read()
            os.unlink(tmp.name)
    
    return audio_data
