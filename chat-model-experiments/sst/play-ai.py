import os 
from dotenv import load_dotenv
from groq import Groq
import datetime

from audio import *

load_dotenv()
api_key = os.getenv("GROQ_API_KEY")

unique_id = datetime.datetime.now().strftime("%Y_%m%d_%H_%M")
unique_filename = f"speeches/audio_{unique_id}.wav"

filepath= os.path.join(os.path.dirname(__file__), unique_filename)

speech_file_path = filepath
model = "playai-tts"
voice = "Angelo-PlayAI"
text = "I love building and shipping new features for our users!"
response_format = "wav"

client = Groq(api_key=api_key)

response = client.audio.speech.create(
    model=model,
    voice=voice,
    input=text,
    response_format=response_format
)

response.write_to_file(speech_file_path)
