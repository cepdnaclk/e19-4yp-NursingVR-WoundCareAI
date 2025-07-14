from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import os
import numpy as np

# Import from audio_handler (only what we actually need)
from services.audio_handler import (
    convert_audio_to_numpy,  # Still needed for WebM → numpy conversion
    save_received_audio,
    save_converted_audio,
    save_response_audio,
    validate_audio_format,
    get_audio_files_info,
    get_audio_saving_enabled
)

from services.audio_handler import AUDIO_SAVE_DIR

app = FastAPI(title="Voice Agent Backend", version="1.0.0")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Import voice pipeline components
try:
    from agents import Agent
    from agents.extensions.handoff_prompt import prompt_with_handoff_instructions
    from agents.voice import (
        AudioInput,
        SingleAgentVoiceWorkflow,
        SingleAgentWorkflowCallbacks,
        VoicePipeline,
    )
    
    # Create main agent with handoffs and tools
    agent = Agent(
        name="Assistant",
        instructions=prompt_with_handoff_instructions(
            "You're speaking to a human, so be polite and concise. You should alway talk in English. Not other languages.  If the user's response doesn't make sense you can ask for clarification.",
        ),
        model="gpt-4o",
    )
    
    class WorkflowCallbacks(SingleAgentWorkflowCallbacks):
        def on_run(self, workflow, transcription):
            pass
    
    # OPTION 1: Default OpenAI models
    # pipeline = VoicePipeline(
    #     workflow=SingleAgentVoiceWorkflow(agent, callbacks=WorkflowCallbacks())
    # )
    
    # OPTION 2: Full Groq Stack (Whisper STT + PlayAI TTS) 
    from services.groq_whisper_stt import GroqVoiceModelProvider
    from agents.voice import VoicePipelineConfig
    
    groq_api_key = os.getenv("GROQ_API_KEY")
    if groq_api_key:
        groq_provider = GroqVoiceModelProvider(
            groq_api_key=groq_api_key,
            stt_model="whisper-large-v3-turbo",
            tts_model="playai-tts",
            tts_voice="Arista-PlayAI",
            tts_provider="groq",  # Use Groq for both STT and TTS
            tts_speed=1.0  # Normal speech speed
        )
        config = VoicePipelineConfig(model_provider=groq_provider)
        pipeline = VoicePipeline(
            workflow=SingleAgentVoiceWorkflow(agent, callbacks=WorkflowCallbacks()),
            config=config
        )
        print("✅ Using Full Groq Stack: Whisper STT + PlayAI TTS (Normal Speed)")
    else:
        print("❌ GROQ_API_KEY not found, using default OpenAI models")
        pipeline = VoicePipeline(workflow=SingleAgentVoiceWorkflow(agent, callbacks=WorkflowCallbacks()))
    
    # OPTION 3: Hybrid (Groq STT + OpenAI TTS) - CURRENTLY ACTIVE
    # from services.groq_whisper_stt import GroqVoiceModelProvider
    # from agents.voice import VoicePipelineConfig
    
    # groq_api_key = os.getenv("GROQ_API_KEY")
    # print(f"GROQ_API_KEY: {groq_api_key}")
    # if groq_api_key:
    #     groq_provider = GroqVoiceModelProvider(
    #         groq_api_key=groq_api_key,
    #         stt_model="whisper-large-v3-turbo",  # Fast Groq Whisper
    #         tts_provider="openai"  # Fallback to OpenAI TTS
    #     )
    #     config = VoicePipelineConfig(model_provider=groq_provider)
    #     pipeline = VoicePipeline(
    #         workflow=SingleAgentVoiceWorkflow(agent, callbacks=WorkflowCallbacks()),
    #         config=config
    #     )
    #     print("✅ Using Hybrid: Groq Whisper STT + OpenAI TTS")
    # else:
    #     print("❌ GROQ_API_KEY not found, using default OpenAI models")
    #     pipeline = VoicePipeline(workflow=SingleAgentVoiceWorkflow(agent, callbacks=WorkflowCallbacks()))
    
    VOICE_PIPELINE_AVAILABLE = True
    
except ImportError:
    VOICE_PIPELINE_AVAILABLE = False

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    dialog_count = 0
    
    while True:
        import time
        
        # Start timing
        request_start_time = time.time()
        dialog_count += 1
        
        # Receive audio data
        audio_data = await websocket.receive_bytes()
        
        print(f"Dialog {dialog_count}: Received {len(audio_data)} bytes at {request_start_time:.3f}")
        
        # Validate format
        format_info = validate_audio_format(audio_data)
        if not format_info["is_valid"]:
            await websocket.send_text(f"Error: Invalid audio format")
            continue
        
        # Save the received audio data with detected format
        print(format_info)
        save_received_audio(audio_data, format_info["format"])
        
        # Convert WebM audio to numpy array
        audio_array = await convert_audio_to_numpy(audio_data)
        
        # Save the converted audio
        save_converted_audio(audio_array, sample_rate=16000)
        
        # Skip if no audio data after conversion
        if len(audio_array) == 0:
            await websocket.send_text("Error: No audio data after conversion")
            continue
        
        # Process through pipeline
        audio_input = AudioInput(buffer=audio_array)
        result = await pipeline.run(audio_input)
        
        # Send responses back to client
        chunk_count = 0
        first_chunk_sent = False
        
        async for event in result.stream():
            if event.type == "voice_stream_event_audio":
                chunk_count += 1
                
                # Calculate latency for first chunk
                if not first_chunk_sent:
                    first_response_time = time.time()
                    latency = (first_response_time - request_start_time) * 1000  # Convert to ms
                    print(f"Dialog {dialog_count}: First response latency: {latency:.2f}ms")
                    first_chunk_sent = True
                
                print(f"Chunk {chunk_count}: shape={event.data.shape}, dtype={event.data.dtype}")
                
                # Frontend needs WAV format for AudioContext.decodeAudioData()
                # Create simple WAV format inline (no external function needed)
                import io
                import wave
                
                audio_data = event.data.astype(np.int16) if event.data.dtype != np.int16 else event.data
                buffer = io.BytesIO()
                with wave.open(buffer, 'wb') as wav_file:
                    wav_file.setnchannels(1)  # Mono
                    wav_file.setsampwidth(2)  # 16-bit
                    wav_file.setframerate(24000)  # 24kHz sample rate
                    wav_file.writeframes(audio_data.tobytes())
                audio_bytes = buffer.getvalue()
                
                save_response_audio(audio_bytes, chunk_count)
                await websocket.send_bytes(audio_bytes)
        print(f"Sent {chunk_count} audio chunks back to client")

@app.get("/audio-info")
async def audio_files_info():
    """Get information about saved audio files"""
    return get_audio_files_info()

@app.get("/")
async def home():
    """Serve the HTML page for voice recording"""
    return HTMLResponse(content="""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Voice Agent</title>
    <link rel="stylesheet" href="/static/styles-simple.css">
</head>
<body>
    <div class="container">
        <h1>Voice Agent</h1>
        <button id="recordButton">Hold to Record</button>
        <div id="status">Ready to record</div>
        <audio id="audioPlayer" controls style="display: none;"></audio>
    </div>
                        
    <script src="/static/voice-agent.js"></script>
</body>
</html>
    """)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy", 
        "message": "Voice agent backend is running",
        "voice_pipeline_available": VOICE_PIPELINE_AVAILABLE,
        "audio_saving_enabled": get_audio_saving_enabled()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
