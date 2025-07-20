#!/usr/bin/env python3

from services.play_ai import text_to_speech_bytes

# Test the TTS function to see audio properties
if __name__ == "__main__":
    print("Testing TTS audio properties...")
    
    test_text = "Hello, this is a test of the text to speech function."
    audio_data = text_to_speech_bytes(test_text)
    
    print(f"Audio data size: {len(audio_data)} bytes")
