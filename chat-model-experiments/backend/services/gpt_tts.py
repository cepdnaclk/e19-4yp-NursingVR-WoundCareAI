from pathlib import Path
from openai import OpenAI
import os
import tempfile
import services.audio as audio

# 🔒 SECURE: Use environment variable
API_KEY = os.environ.get("OPENAI_API_KEY")

if not API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable is not set")

print(f"Using OpenAI API Key: {API_KEY[:10]}...{API_KEY[-4:]}")  # Only show partial key

client = OpenAI(
    api_key=API_KEY
)

def text_to_speech_and_play_openai(text, model="tts-1", voice="alloy"):
    """
    Convert text to speech using OpenAI TTS and play it.
    
    Args:
        text: Text to convert to speech
        model: TTS model ("tts-1" or "tts-1-hd")
        voice: Voice to use ("alloy", "echo", "fable", "onyx", "nova", "shimmer")
    """
    try:
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp:
            speech_file_path = tmp.name
            
            with client.audio.speech.with_streaming_response.create(
                model=model,        # ✅ Valid model
                voice=voice,        # ✅ Valid voice
                input=text,
                response_format="mp3", 
            ) as response:
                response.stream_to_file(speech_file_path)

            audio.play_audio(speech_file_path)
            
    except Exception as e:
        print(f"Error in TTS: {e}")
        raise

def text_to_speech_bytes_openai(text, model="tts-1", voice="alloy", response_format="wav"):
    """
    Convert text to speech and return as bytes.
    
    Args:
        text: Text to convert
        model: TTS model ("tts-1" or "tts-1-hd") 
        voice: Voice ("alloy", "echo", "fable", "onyx", "nova", "shimmer")
        response_format: Audio format ("mp3", "opus", "aac", "flac", "wav", "pcm")
        
    Returns:
        bytes: Audio data
    """
    try:
        response = client.audio.speech.create(
            model=model,
            voice=voice,
            input=text,
            response_format=response_format
        )
        
        return response.content
        
    except Exception as e:
        print(f"Error in TTS bytes: {e}")
        raise

def text_to_speech_bytes_openai_with_info(text, model="tts-1", voice="alloy", response_format="pcm"):
    """
    Convert text to speech and return bytes with format info.
    """
    try:
        response = client.audio.speech.create(
            model=model,
            voice=voice,
            input=text,
            response_format=response_format
        )
        
        audio_bytes = response.content
        
        if response_format == "pcm":
            # Analyze PCM data
            samples = len(audio_bytes) // 2  # 16-bit = 2 bytes per sample
            duration = samples / 24000  # 24kHz sample rate
            print(f"PCM Info: {len(audio_bytes)} bytes, {samples} samples, {duration:.2f}s")
            print("✅ Format: 16-bit PCM, 24kHz, Mono")
        
        return audio_bytes
        
    except Exception as e:
        print(f"Error in TTS bytes: {e}")
        raise


