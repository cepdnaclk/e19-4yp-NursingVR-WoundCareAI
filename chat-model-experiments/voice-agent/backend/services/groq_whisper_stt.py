# Groq Whisper STT Model Implementation
import asyncio
import io
import os
from collections.abc import AsyncIterator
from typing import Any

import numpy as np
import httpx

from agents.voice.model import STTModel, STTModelSettings, StreamedTranscriptionSession, TTSModel, TTSModelSettings
from agents.voice.input import AudioInput, StreamedAudioInput


class GroqPlayAITTSModel(TTSModel):
    """Groq PlayAI TTS model implementation using Groq's API."""
    
    def __init__(
        self, 
        api_key: str,
        model: str = "playai-tts",
        voice: str = "Fritz-PlayAI",
        base_url: str = "https://api.groq.com/openai/v1",
        default_speed: float = 1  # Default slower speed
    ):
        """Initialize Groq PlayAI TTS model.
        
        Args:
            api_key: Groq API key
            model: TTS model to use (currently only "playai-tts")
            voice: Voice to use (e.g., "Fritz-PlayAI", see Groq docs for more)
            base_url: Groq API base URL
            default_speed: Default speech speed (0.25 to 4.0, where 1.0 is normal)
        """
        self.api_key = api_key
        self._model_name = model
        self.voice = voice
        self.base_url = base_url
        self.default_speed = default_speed
        
        # Available voices (this list may expand)
        self.available_voices = [
            "Fritz-PlayAI",
            # Add more voices as they become available
        ]
    
    @property
    def model_name(self) -> str:
        return self._model_name
    
    async def run(self, text: str, settings: TTSModelSettings) -> AsyncIterator[bytes]:
        """Convert text to speech using Groq PlayAI TTS."""
        
        # Use voice from settings if provided, otherwise use default
        voice_to_use = settings.voice or self.voice
        
        # Map standard voice names to PlayAI voices if needed
        voice_mapping = {
            "alloy": "Fritz-PlayAI",
            "ash": "Fritz-PlayAI", 
            "coral": "Fritz-PlayAI",
            "echo": "Fritz-PlayAI",
            "fable": "Fritz-PlayAI",
            "onyx": "Fritz-PlayAI",
            "nova": "Fritz-PlayAI",
            "sage": "Fritz-PlayAI",
            "shimmer": "Fritz-PlayAI"
        }
        
        if voice_to_use in voice_mapping:
            voice_to_use = voice_mapping[voice_to_use]
        
        url = f"{self.base_url}/audio/speech"
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # Prepare request data
        data = {
            "model": self._model_name,
            "input": text,
            "voice": voice_to_use,
            "response_format": "wav",  # Use WAV for better compatibility
            "sample_rate": 24000,  # 24kHz for AI audio
            "speed": settings.speed or self.default_speed  # Use default slower speed
        }
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(url, headers=headers, json=data)
            
            if response.status_code != 200:
                error_text = response.text
                raise Exception(f"Groq TTS API error {response.status_code}: {error_text}")
            
            # Stream the audio data in chunks
            audio_data = response.content
            chunk_size = settings.buffer_size or 1024
            
            for i in range(0, len(audio_data), chunk_size):
                chunk = audio_data[i:i + chunk_size]
                if chunk:
                    yield chunk


class GroqWhisperSTTModel(STTModel):
    """Groq Whisper STT model implementation using Groq's API."""
    
    def __init__(
        self, 
        api_key: str,
        model: str = "whisper-large-v3-turbo",
        base_url: str = "https://api.groq.com/openai/v1"
    ):
        """Initialize Groq Whisper STT model.
        
        Args:
            api_key: Groq API key
            model: Whisper model to use ("whisper-large-v3" or "whisper-large-v3-turbo")
            base_url: Groq API base URL
        """
        self.api_key = api_key
        self._model_name = model
        self.base_url = base_url
        
        # Validate model name
        valid_models = ["whisper-large-v3", "whisper-large-v3-turbo"]
        if model not in valid_models:
            raise ValueError(f"Model {model} not supported. Use one of: {valid_models}")
    
    @property
    def model_name(self) -> str:
        return self._model_name
    
    async def transcribe(
        self,
        input: AudioInput,
        settings: STTModelSettings,
        trace_include_sensitive_data: bool,
        trace_include_sensitive_audio_data: bool,
    ) -> str:
        """Transcribe audio using Groq Whisper API."""
        
        # The agents framework gives us audio data as numpy array
        audio_data = input.buffer
        
        # Convert numpy array to bytes for API upload
        if isinstance(audio_data, np.ndarray):
            # Convert to PCM WAV format bytes (simpler than creating temp files)
            audio_bytes = self._numpy_to_wav_bytes(audio_data, sample_rate=16000)
        else:
            # If it's already bytes, use as-is
            audio_bytes = audio_data
        
        # Make API request directly with audio bytes
        result = await self._make_transcription_request(audio_bytes, settings)
        return result.strip()
    
    def _numpy_to_wav_bytes(self, audio_data: np.ndarray, sample_rate: int) -> bytes:
        """Convert numpy array directly to WAV bytes without temp files."""
        import io
        import wave
        import struct
        
        # Ensure audio_data is int16
        if audio_data.dtype == np.float32:
            # Convert float32 (-1 to 1) to int16
            audio_data = (audio_data * 32767).astype(np.int16)
        elif audio_data.dtype != np.int16:
            audio_data = audio_data.astype(np.int16)
        
        # Create WAV bytes in memory
        buffer = io.BytesIO()
        with wave.open(buffer, 'wb') as wav_file:
            wav_file.setnchannels(1)  # Mono
            wav_file.setsampwidth(2)  # 16-bit
            wav_file.setframerate(sample_rate)
            wav_file.writeframes(audio_data.tobytes())
        
        return buffer.getvalue()
    
    async def _make_transcription_request(self, audio_bytes: bytes, settings: STTModelSettings) -> str:
        """Make transcription request to Groq API with audio bytes."""
        
        url = f"{self.base_url}/audio/transcriptions"
        
        headers = {
            "Authorization": f"Bearer {self.api_key}"
        }
        
        # Prepare form data
        data = {
            "model": self._model_name,
            "response_format": "text",  # Simple text response
            "temperature": settings.temperature or 0.0,
        }
        
        # Add optional parameters
        if settings.language:
            data["language"] = settings.language
        
        if settings.prompt:
            data["prompt"] = settings.prompt
        
        # Create multipart form data with audio bytes
        files = {
            "file": ("audio.wav", audio_bytes, "audio/wav")
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, headers=headers, data=data, files=files)
            
            if response.status_code != 200:
                error_text = response.text
                raise Exception(f"Groq STT API error {response.status_code}: {error_text}")
            
            return response.text
    
    async def create_session(
        self,
        input: StreamedAudioInput,
        settings: STTModelSettings,
        trace_include_sensitive_data: bool,
        trace_include_sensitive_audio_data: bool,
    ) -> StreamedTranscriptionSession:
        """Create a streaming transcription session."""
        # For now, implement a simple session that doesn't support true streaming
        # Groq API doesn't support streaming transcription, so we batch process
        return GroqWhisperTranscriptionSession(
            self, input, settings, trace_include_sensitive_data, trace_include_sensitive_audio_data
        )


class GroqWhisperTranscriptionSession(StreamedTranscriptionSession):
    """Simple transcription session for Groq Whisper."""
    
    def __init__(
        self, 
        model: GroqWhisperSTTModel,
        input: StreamedAudioInput,
        settings: STTModelSettings,
        trace_include_sensitive_data: bool,
        trace_include_sensitive_audio_data: bool
    ):
        self.model = model
        self.input = input
        self.settings = settings
        self.trace_include_sensitive_data = trace_include_sensitive_data
        self.trace_include_sensitive_audio_data = trace_include_sensitive_audio_data
        self._closed = False
    
    async def transcribe_turns(self) -> AsyncIterator[str]:
        """Yield transcriptions for each turn."""
        # This is a simplified implementation
        # In practice, you'd want to implement proper turn detection
        
        while not self._closed:
            # Wait for some audio data to accumulate
            await asyncio.sleep(1.0)
            
            # Get current audio buffer
            current_audio = self.input.get_buffer()  # This method may not exist in the real API
            
            if len(current_audio) > 0:
                # Create AudioInput from current buffer
                audio_input = AudioInput(buffer=current_audio)
                
                # Transcribe
                try:
                    transcription = await self.model.transcribe(
                        audio_input,
                        self.settings,
                        self.trace_include_sensitive_data,
                        self.trace_include_sensitive_audio_data
                    )
                    
                    if transcription.strip():
                        yield transcription
                        
                except Exception as e:
                    print(f"Transcription error: {e}")
                    continue
            
            # Check if we should stop
            if self._closed:
                break
    
    async def close(self) -> None:
        """Close the session."""
        self._closed = True


# Custom Voice Model Provider that uses Groq for both STT and TTS
class GroqVoiceModelProvider:
    """Voice model provider that uses Groq for both STT and TTS."""
    
    def __init__(
        self,
        groq_api_key: str,
        stt_model: str = "whisper-large-v3-turbo",
        tts_model: str = "playai-tts",
        tts_voice: str = "Fritz-PlayAI",
        tts_provider: str = "groq",
        tts_speed: float = 1  # Default slower speed
    ):
        """Initialize Groq voice model provider.
        
        Args:
            groq_api_key: Groq API key
            stt_model: Whisper model to use for STT
            tts_model: TTS model to use (playai-tts)
            tts_voice: Voice to use for TTS
            tts_provider: TTS provider ("groq" or "openai" for fallback)
            tts_speed: Default TTS speed (0.25 to 4.0, where 1.0 is normal)
        """
        self.groq_api_key = groq_api_key
        self.stt_model = stt_model
        self.tts_model = tts_model
        self.tts_voice = tts_voice
        self.tts_provider = tts_provider
        self.tts_speed = tts_speed
    
    def get_stt_model(self, model_name: str | None):
        """Get Groq Whisper STT model."""
        model = model_name or self.stt_model
        return GroqWhisperSTTModel(
            api_key=self.groq_api_key,
            model=model
        )
    
    def get_tts_model(self, model_name: str | None):
        """Get TTS model (Groq PlayAI or OpenAI fallback)."""
        if self.tts_provider == "groq":
            model = model_name or self.tts_model
            return GroqPlayAITTSModel(
                api_key=self.groq_api_key,
                model=model,
                voice=self.tts_voice,
                default_speed=self.tts_speed  # Pass the configured speed
            )
        elif self.tts_provider == "openai":
            from agents.voice.models.openai_model_provider import OpenAIVoiceModelProvider
            return OpenAIVoiceModelProvider().get_tts_model(model_name)
        else:
            raise NotImplementedError(f"TTS provider {self.tts_provider} not implemented")


# Example usage function
def create_groq_full_pipeline():
    """Example of how to create a pipeline with Groq for both STT and TTS."""
    
    # Get Groq API key from environment
    groq_api_key = os.getenv("GROQ_API_KEY")
    if not groq_api_key:
        raise ValueError("GROQ_API_KEY environment variable is required")
    
    # Create provider with both Groq STT and TTS
    groq_provider = GroqVoiceModelProvider(
        groq_api_key=groq_api_key,
        stt_model="whisper-large-v3-turbo",  # Fast Whisper model
        tts_model="playai-tts",              # PlayAI TTS model
        tts_voice="Fritz-PlayAI",            # PlayAI voice
        tts_provider="groq"                  # Use Groq for TTS
    )
    
    return groq_provider


def create_groq_whisper_pipeline():
    """Example of how to create a pipeline with Groq Whisper STT + OpenAI TTS."""
    
    # Get Groq API key from environment
    groq_api_key = os.getenv("GROQ_API_KEY")
    if not groq_api_key:
        raise ValueError("GROQ_API_KEY environment variable is required")
    
    # Create provider with Groq STT + OpenAI TTS
    groq_provider = GroqVoiceModelProvider(
        groq_api_key=groq_api_key,
        stt_model="whisper-large-v3-turbo",  # Fast Whisper model
        tts_provider="openai"                # Fallback to OpenAI TTS
    )
    
    return groq_provider


# Standalone function to test Groq models
async def test_groq_models(api_key: str):
    """Test both Groq Whisper STT and PlayAI TTS."""
    
    print("Testing Groq STT and TTS models...")
    
    # Test STT
    stt_model = GroqWhisperSTTModel(api_key=api_key)
    
    # Create dummy audio input (replace with real audio loading)
    dummy_audio = np.random.randint(-32768, 32767, size=16000, dtype=np.int16)  # 1 second of dummy audio
    audio_input = AudioInput(buffer=dummy_audio)
    
    stt_settings = STTModelSettings(
        language="en",
        temperature=0.0
    )
    
    try:
        stt_result = await stt_model.transcribe(
            audio_input, 
            stt_settings, 
            trace_include_sensitive_data=True,
            trace_include_sensitive_audio_data=False
        )
        print(f"STT result: {stt_result}")
    except Exception as e:
        print(f"STT Error: {e}")
    
    # Test TTS
    tts_model = GroqPlayAITTSModel(api_key=api_key)
    tts_settings = TTSModelSettings(
        voice="Fritz-PlayAI",
        buffer_size=1024,
        speed=1.0
    )
    
    try:
        print("Testing TTS with sample text...")
        audio_chunks = []
        async for chunk in tts_model.run("Hello, this is a test of Groq PlayAI TTS.", tts_settings):
            audio_chunks.append(chunk)
        
        total_audio_bytes = sum(len(chunk) for chunk in audio_chunks)
        print(f"TTS result: Generated {len(audio_chunks)} chunks, {total_audio_bytes} bytes total")
        
    except Exception as e:
        print(f"TTS Error: {e}")


async def test_groq_whisper(audio_file_path: str, api_key: str):
    """Test Groq Whisper transcription with an audio file (backward compatibility)."""
    return await test_groq_models(api_key)


if __name__ == "__main__":
    # Test with your Groq API key
    import os
    api_key = os.getenv("GROQ_API_KEY")
    if api_key:
        asyncio.run(test_groq_whisper("test.wav", api_key))
    else:
        print("Set GROQ_API_KEY environment variable to test")
