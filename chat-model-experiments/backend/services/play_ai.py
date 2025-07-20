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
    
    # Analyze audio properties (optional - remove in production)
    analyze_audio_properties(audio_data)
    
    return audio_data

def analyze_audio_properties(audio_data):
    """Analyze the audio properties of the WAV data"""
    import wave
    import io
    
    try:
        # Create a BytesIO object from the audio data
        audio_buffer = io.BytesIO(audio_data)
        
        # Open as WAV file
        with wave.open(audio_buffer, 'rb') as wav_file:
            sample_rate = wav_file.getframerate()
            channels = wav_file.getnchannels()
            sample_width = wav_file.getsampwidth()  # bytes per sample
            bit_depth = sample_width * 8
            duration = wav_file.getnframes() / sample_rate
            
            print(f"Audio Properties:")
            print(f"  Sample Rate: {sample_rate} Hz")
            print(f"  Channels: {channels}")
            print(f"  Bit Depth: {bit_depth} bits")
            print(f"  Sample Width: {sample_width} bytes")
            print(f"  Duration: {duration:.2f} seconds")
            
            return {
                'sample_rate': sample_rate,
                'channels': channels,
                'bit_depth': bit_depth,
                'sample_width': sample_width,
                'duration': duration
            }
    except Exception as e:
        print(f"Error analyzing audio: {e}")
        return None
