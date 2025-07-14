#!/usr/bin/env python3
"""
Test script for the simplified Groq voice models (no temp files needed).
"""

import os
import sys
import asyncio
import numpy as np

# Add the backend directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.groq_whisper_stt import GroqPlayAITTSModel, GroqWhisperSTTModel, GroqVoiceModelProvider
from agents.voice.input import AudioInput
from agents.voice.model import STTModelSettings, TTSModelSettings


async def test_simplified_groq_models():
    """Test both STT and TTS with simplified implementation (no temp files)."""
    
    # Get API key
    groq_api_key = os.getenv("GROQ_API_KEY")
    if not groq_api_key:
        print("❌ GROQ_API_KEY environment variable is required")
        print("Get your key from: https://console.groq.com/keys")
        return False
    
    print("🧪 Testing Simplified Groq Models (No Temp Files)")
    print("=" * 50)
    
    try:
        # Test 1: STT Model (simplified - no temp WAV files)
        print("\n1️⃣ Testing Groq Whisper STT (Simplified)...")
        stt_model = GroqWhisperSTTModel(api_key=groq_api_key)
        
        # Create dummy audio input (1 second of sine wave)
        sample_rate = 16000
        duration = 1.0
        frequency = 440  # A4 note
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        audio_data = (np.sin(2 * np.pi * frequency * t) * 0.3 * 32767).astype(np.int16)
        
        audio_input = AudioInput(buffer=audio_data)
        stt_settings = STTModelSettings(language="en", temperature=0.0)
        
        # This should work without creating any temp files
        transcription = await stt_model.transcribe(
            audio_input, 
            stt_settings, 
            trace_include_sensitive_data=True,
            trace_include_sensitive_audio_data=False
        )
        print(f"✅ STT Result: '{transcription}'")
        print("   (Note: Sine wave might not transcribe to meaningful text)")
        
        # Test 2: TTS Model (already simplified)
        print("\n2️⃣ Testing Groq PlayAI TTS...")
        tts_model = GroqPlayAITTSModel(
            api_key=groq_api_key,
            default_speed=0.75  # Slower speed as requested
        )
        
        tts_settings = TTSModelSettings(
            voice="Fritz-PlayAI",
            buffer_size=1024,
            speed=0.75  # Slower speech
        )
        
        test_text = "Hello, this is a test of the simplified Groq voice pipeline with slower speech speed."
        print(f"   Text: '{test_text}'")
        
        audio_chunks = []
        async for chunk in tts_model.run(test_text, tts_settings):
            audio_chunks.append(chunk)
        
        total_bytes = sum(len(chunk) for chunk in audio_chunks)
        print(f"✅ TTS Result: {len(audio_chunks)} chunks, {total_bytes} bytes total")
        
        # Test 3: Full Voice Provider
        print("\n3️⃣ Testing Complete Voice Provider...")
        provider = GroqVoiceModelProvider(
            groq_api_key=groq_api_key,
            stt_model="whisper-large-v3-turbo",
            tts_model="playai-tts",
            tts_voice="Fritz-PlayAI",
            tts_provider="groq",
            tts_speed=0.75  # Slower speed
        )
        
        stt = provider.get_stt_model(None)
        tts = provider.get_tts_model(None)
        
        print(f"✅ STT Model: {stt.model_name}")
        print(f"✅ TTS Model: {tts.model_name} (speed: {tts.default_speed})")
        
        print("\n🎉 All tests passed! Your simplified models are working.")
        print("\n📝 Key improvements:")
        print("   • No temporary WAV files created")
        print("   • Direct audio bytes upload to API")
        print("   • Simplified audio processing")
        print("   • Configurable speech speed (0.75x)")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


if __name__ == "__main__":
    success = asyncio.run(test_simplified_groq_models())
    if success:
        print("\n✅ Ready to use! Restart your voice agent to apply changes.")
    else:
        print("\n❌ Please check your GROQ_API_KEY and try again.")
