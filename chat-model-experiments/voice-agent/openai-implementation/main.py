import asyncio
import random  
import os

import numpy as np

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("python-dotenv not installed. Make sure to set OPENAI_API_KEY environment variable manually.")

from agents import Agent, function_tool
from agents.extensions.handoff_prompt import prompt_with_handoff_instructions
from agents.voice import (
    AudioInput,
    SingleAgentVoiceWorkflow,
    SingleAgentWorkflowCallbacks,
    VoicePipeline,
)

from util import AudioPlayer, record_audio

"""
This is a voice agent conversation that allows continuous interaction. Run it via:
`python main.py`

1. Press spacebar to record an audio message.
2. The pipeline automatically transcribes the audio.
3. The agent processes your message and responds with speech.
4. You can continue the conversation by recording more messages.
5. Type 'quit' or 'exit' to end the conversation.

The agent workflow supports:
- General conversation and questions
- Weather queries (will call the `get_weather` tool)
- Spanish language (will handoff to the spanish agent)

Try examples like:
- "Tell me a joke"
- "What's the weather in Tokyo?"
- "Hola, como estas?"
"""


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
    model="gpt-4o-mini",
)

agent = Agent(
    name="Assistant",
    instructions=prompt_with_handoff_instructions(
        "You're speaking to a human, so be polite and concise. If the user speaks in Spanish, handoff to the spanish agent.",
    ),
    model="gpt-4o-mini",
    handoffs=[spanish_agent],
    tools=[get_weather],
)


class WorkflowCallbacks(SingleAgentWorkflowCallbacks):
    def on_run(self, workflow: SingleAgentVoiceWorkflow, transcription: str) -> None:
        print(f"[debug] on_run called with transcription: {transcription}")


async def main():
    print("=== Voice Agent Conversation ===")
    print("Press spacebar to record and send a message.")
    print("Type 'quit' or 'exit' and press Enter to end the conversation.")
    print("=" * 40)
    
    pipeline = VoicePipeline(
        workflow=SingleAgentVoiceWorkflow(agent, callbacks=WorkflowCallbacks())
    )

    while True:
        try:
            print("\nPress spacebar to start recording your message...")
            audio_input = AudioInput(buffer=record_audio())
            
            if len(audio_input.buffer) == 0:
                print("No audio recorded. Please try again.")
                continue

            print("Processing your message...")
            result = await pipeline.run(audio_input)

            print("Playing response...")
            with AudioPlayer() as player:
                async for event in result.stream():
                    if event.type == "voice_stream_event_audio":
                        player.add_audio(event.data)
                    elif event.type == "voice_stream_event_lifecycle":
                        print(f"Received lifecycle event: {event.event}")

                # Add 1 second of silence to the end of the stream to avoid cutting off the last audio.
                player.add_audio(np.zeros(24000 * 1, dtype=np.int16))
            
            print("Response completed. Ready for next message!")
            
            # Check if user wants to continue
            user_input = input("\nPress Enter to continue or type 'quit'/'exit' to end: ").strip().lower()
            if user_input in ['quit', 'exit']:
                print("Ending conversation. Goodbye!")
                break
                
        except KeyboardInterrupt:
            print("\nConversation interrupted. Goodbye!")
            break
        except Exception as e:
            print(f"An error occurred: {e}")
            user_input = input("Press Enter to try again or type 'quit' to exit: ").strip().lower()
            if user_input == 'quit':
                break


if __name__ == "__main__":
    asyncio.run(main())
