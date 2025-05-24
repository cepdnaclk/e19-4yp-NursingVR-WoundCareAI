import os 
from dotenv import load_dotenv
from groq import Groq
import datetime

from audio import *

load_dotenv()
api_key = os.getenv("GROQ_API_KEY")

unique_id = datetime.datetime.now().strftime("%Y_%m%d_%H_%M")
unique_filename = f"recordings/audio_{unique_id}.wav"

record_audio(duration=20, filename=unique_filename)
play_audio(unique_filename)

flac_filename=unique_filename.rsplit('.', 1)[0] + '.flac'
compress_to_flac(unique_filename, flac_filename=flac_filename)

client = Groq(api_key=api_key)
filename = os.path.join(os.path.dirname(__file__), flac_filename)

print(filename)

with open(filename, "rb") as file:
    transcription = client.audio.transcriptions.create(
      file=(filename, file.read()),
      model="whisper-large-v3-turbo",
      #prompt="This is a medical wound care training. Names: kochasoft, uthsara, mahesha. Use medical terminology. Speakers are talking in Sri Lankan English accent",  # Optional
      response_format="json",  # Optional
      language="si",  # Optional
      temperature=0 # Optional
    )
    print(transcription.text)
