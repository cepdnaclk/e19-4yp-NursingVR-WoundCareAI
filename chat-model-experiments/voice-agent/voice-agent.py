import asyncio
import random
import time

import numpy as np
import sounddevice as sd

from agents import (
    Agent,
    function_tool,
    set_tracing_disabled,
)
from agents.voice import (
    AudioInput,
    SingleAgentVoiceWorkflow,
    VoicePipeline,
)
from agents.extensions.handoff_prompt import prompt_with_handoff_instructions


@function_tool
def get_weather(city: str) -> str:
    """Get the weather for a given city."""
    print(f"[debug] get_weather called with city: {city}")
    choices = ["sunny", "cloudy", "rainy", "snowy"]
    return f"The weather in {city} is {random.choice(choices)}."


spanish_agent = Agent(
    name="Spanish",
    handoff_description="A spanish speaking agent.",
    instructions=prompt_with_handoff_instructions(
        "You're speaking to a human, so be polite and concise. Speak in Spanish.",
    ),
    model="gpt-4o",
)

agent = Agent(
    name="Assistant",
    instructions=prompt_with_handoff_instructions(
        "You're speaking to a human, so be polite and concise, only in English.",
    ),
    model="gpt-4o",
    tools=[get_weather],
)

async def main():
    pipeline = VoicePipeline(workflow=SingleAgentVoiceWorkflow(agent))
    
    print("Recording audio for 3 seconds... Speak now!")
    
    # Record audio from microphone
    duration = 3  # seconds
    sample_rate = 24000
    recording = sd.rec(int(duration * sample_rate), 
                      samplerate=sample_rate, 
                      channels=1, 
                      dtype=np.int16)
    sd.wait()  # Wait for recording to complete
    
    t =  time.time()
    print("Recording finished. Processing...")
    
    # Create audio buffer from recording
    buffer = recording.flatten()
    audio_input = AudioInput(buffer=buffer)

    # Process the audio
    result = await pipeline.run(audio_input)

    # Create an audio player using `sounddevice`
    player = sd.OutputStream(samplerate=24000, channels=1, dtype=np.int16)
    player.start()

    # Play the audio stream as it comes in
    async for event in result.stream():
        print("data arrived", time.time()-t)
        if event.type == "voice_stream_event_audio":
            player.write(event.data)

    player.stop()
    player.close()

    print("Conversation completed!")

if __name__ == "__main__":
    asyncio.run(main())