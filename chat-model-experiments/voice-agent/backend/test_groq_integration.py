#!/usr/bin/env python3
"""
Test script for Groq Whisper STT integration
"""
import asyncio
import os
import numpy as np
from services.groq_whisper_stt import (
    GroqWhisperSTTModel, 
    GroqPlayAITTSModel, 
    GroqVoiceModelProvider
)
from agents.voice.input import AudioInput
from agents.voice.model import STTModelSettings, TTSModelSettings


async def test_groq_whisper():
    """Test Groq Whisper STT model."""
    
    # Check for API key
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        print("❌ GROQ_API_KEY environment variable is required")
        print("Get your API key from: https://console.groq.com/keys")
        return False
    
    print("🧪 Testing Groq Whisper STT...")
    
    try:
        # Create Groq Whisper model
        model = GroqWhisperSTTModel(
            api_key=api_key,
            model="whisper-large-v3-turbo"  # Faster model
        )
        
        print(f"✅ STT Model created: {model.model_name}")
        
        # Create dummy audio data (1 second of sine wave at 440Hz)
        sample_rate = 16000
        duration = 1.0
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        frequency = 440  # A4 note
        audio_data = np.sin(2 * np.pi * frequency * t)
        
        # Convert to int16
        audio_data = (audio_data * 32767 * 0.5).astype(np.int16)
        
        # Create audio input
        audio_input = AudioInput(buffer=audio_data)
        
        # Create settings
        settings = STTModelSettings(
            language="en",
            temperature=0.0,
            prompt="This is a test audio with a sine wave tone."
        )
        
        print("🎵 Transcribing test audio (sine wave)...")
        
        # Transcribe
        result = await model.transcribe(
            audio_input,
            settings,
            trace_include_sensitive_data=True,
            trace_include_sensitive_audio_data=False
        )
        
        print(f"📝 STT Transcription result: '{result}'")
        
        if result.strip():
            print("✅ Groq Whisper STT is working!")
            return True
        else:
            print("⚠️ STT returned empty result (expected for sine wave)")
            print("✅ Groq STT API connection successful!")
            return True
            
    except Exception as e:
        print(f"❌ Error testing Groq Whisper STT: {e}")
        return False


async def test_groq_playai_tts():
    """Test Groq PlayAI TTS model."""
    
    # Check for API key
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        print("❌ GROQ_API_KEY environment variable is required")
        return False
    
    print("\n🧪 Testing Groq PlayAI TTS...")
    
    try:
        # Create Groq PlayAI TTS model
        model = GroqPlayAITTSModel(
            api_key=api_key,
            model="playai-tts",
            voice="Fritz-PlayAI"
        )
        
        print(f"✅ TTS Model created: {model.model_name}")
        
        # Create TTS settings
        settings = TTSModelSettings(
            voice="Fritz-PlayAI",
            buffer_size=1024,
            speed=1.0
        )
        
        print("🔊 Generating test audio...")
        
        # Generate speech
        test_text = "Hello! This is a test of Groq PlayAI text-to-speech synthesis."
        audio_chunks = []
        
        async for chunk in model.run(test_text, settings):
            audio_chunks.append(chunk)
        
        total_bytes = sum(len(chunk) for chunk in audio_chunks)
        
        print(f"🎵 TTS Audio generated: {len(audio_chunks)} chunks, {total_bytes} bytes")
        
        if audio_chunks and total_bytes > 0:
            print("✅ Groq PlayAI TTS is working!")
            return True
        else:
            print("❌ TTS generated no audio")
            return False
            
    except Exception as e:
        print(f"❌ Error testing Groq PlayAI TTS: {e}")
        return False


async def test_voice_provider():
    """Test the complete Groq voice provider with both STT and TTS."""
    
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        print("❌ GROQ_API_KEY environment variable is required")
        return False
    
    print("\n🧪 Testing Groq Voice Provider (STT + TTS)...")
    
    try:
        # Create provider with both Groq STT and TTS
        provider = GroqVoiceModelProvider(
            groq_api_key=api_key,
            stt_model="whisper-large-v3-turbo",
            tts_model="playai-tts",
            tts_voice="Fritz-PlayAI",
            tts_provider="groq"  # Use Groq for TTS
        )
        
        # Test STT model
        stt_model = provider.get_stt_model(None)
        print(f"✅ STT Model: {stt_model.model_name}")
        
        # Test TTS model
        tts_model = provider.get_tts_model(None)
        print(f"✅ TTS Model: {tts_model.model_name}")
        
        print("✅ Groq Voice Provider (Full Stack) is ready!")
        return True
        
    except Exception as e:
        print(f"❌ Error testing voice provider: {e}")
        return False


async def test_hybrid_provider():
    """Test Groq STT + OpenAI TTS hybrid provider."""
    
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return False
    
    print("\n🧪 Testing Hybrid Provider (Groq STT + OpenAI TTS)...")
    
    try:
        # Create hybrid provider
        provider = GroqVoiceModelProvider(
            groq_api_key=api_key,
            stt_model="whisper-large-v3-turbo",
            tts_provider="openai"  # Fallback to OpenAI TTS
        )
        
        # Test STT model
        stt_model = provider.get_stt_model(None)
        print(f"✅ STT Model: {stt_model.model_name}")
        
        # Test TTS model  
        tts_model = provider.get_tts_model(None)
        print(f"✅ TTS Model: {tts_model.model_name}")
        
        print("✅ Hybrid Voice Provider is ready!")
        return True
        
    except Exception as e:
        print(f"❌ Error testing hybrid provider: {e}")
        return False


def print_setup_instructions():
    """Print setup instructions."""
    print("\n" + "="*60)
    print("🚀 GROQ WHISPER STT SETUP INSTRUCTIONS")
    print("="*60)
    print()
    print("1. Get your Groq API key:")
    print("   https://console.groq.com/keys")
    print()
    print("2. Set environment variable:")
    print("   # Windows PowerShell:")
    print("   $env:GROQ_API_KEY=\"your_api_key_here\"")
    print()
    print("   # Or add to .env file:")
    print("   GROQ_API_KEY=your_api_key_here")
    print()
    print("3. Install required packages:")
    print("   pip install httpx")
    print()
    print("4. Update your main.py:")
    print("   Uncomment the Groq configuration section")
    print()
    print("5. Available Whisper models:")
    print("   - whisper-large-v3-turbo (faster)")
    print("   - whisper-large-v3 (more accurate)")
    print()
    print("6. Benefits of Groq Whisper:")
    print("   ✅ Very fast inference")
    print("   ✅ High accuracy")
    print("   ✅ Cost-effective")
    print("   ✅ Same API as OpenAI")
    print()


async def main():
    """Main test function."""
    print("🧪 GROQ VOICE AGENT INTEGRATION TEST")
    print("="*60)
    
    # Test individual models
    stt_success = await test_groq_whisper()
    tts_success = await test_groq_playai_tts()
    
    # Test voice providers
    full_provider_success = await test_voice_provider()
    hybrid_provider_success = await test_hybrid_provider()
    
    print("\n" + "="*60)
    print("📊 TEST RESULTS:")
    print(f"   Groq Whisper STT: {'✅ PASS' if stt_success else '❌ FAIL'}")
    print(f"   Groq PlayAI TTS: {'✅ PASS' if tts_success else '❌ FAIL'}")
    print(f"   Full Groq Provider: {'✅ PASS' if full_provider_success else '❌ FAIL'}")
    print(f"   Hybrid Provider: {'✅ PASS' if hybrid_provider_success else '❌ FAIL'}")
    
    all_passed = all([stt_success, tts_success, full_provider_success, hybrid_provider_success])
    
    if all_passed:
        print("\n🎉 All tests passed! Your Groq voice agent is ready!")
        print("\n💡 Configuration options for main.py:")
        print("\n   Option 1 - Full Groq Stack (STT + TTS):")
        print("   groq_provider = GroqVoiceModelProvider(")
        print("       groq_api_key=os.getenv('GROQ_API_KEY'),")
        print("       stt_model='whisper-large-v3-turbo',")
        print("       tts_model='playai-tts',")
        print("       tts_voice='Fritz-PlayAI',")
        print("       tts_provider='groq'")
        print("   )")
        print("\n   Option 2 - Hybrid (Groq STT + OpenAI TTS):")
        print("   groq_provider = GroqVoiceModelProvider(")
        print("       groq_api_key=os.getenv('GROQ_API_KEY'),")
        print("       stt_model='whisper-large-v3-turbo',")
        print("       tts_provider='openai'")
        print("   )")
    else:
        print_setup_instructions()


if __name__ == "__main__":
    asyncio.run(main())
