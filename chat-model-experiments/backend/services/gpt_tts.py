from pathlib import Path
from openai import OpenAI
import os
import tempfile

import services.audio as audio

API_KEY = os.environ.get("OPENAI_API_KEY")

client = OpenAI(
    api_key=API_KEY
)

def text_to_speech_and_play_openai(text, model="gpt-4o-mini-tts", voice="sage", instructions="Speak in a cheerful and positive tone. when answer is correct, otherwise negative tone"):
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        speech_file_path = tmp.name
        with client.audio.speech.with_streaming_response.create(
            model=model,
            voice=voice,
            input=text,
            instructions=instructions,
            response_format="wav", 
        ) as response:
            response.stream_to_file(speech_file_path)

        audio.play_audio(speech_file_path)