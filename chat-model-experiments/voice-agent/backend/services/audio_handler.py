"""
Simple Audio Handler Service for Voice Agent Backend
- Converts WebM audio to numpy arrays
- Converts numpy arrays to WAV bytes
- Provides basic audio saving for debugging
"""

import os
import numpy as np
import io
import wave
import tempfile
import datetime
from typing import Dict, Any
import subprocess
import scipy
import soundfile as sf

# Audio configuration
AUDIO_SAVE_DIR = "saved_audio"
SAVE_AUDIO_ENABLED = True

# Ensure audio save directory exists
os.makedirs(AUDIO_SAVE_DIR, exist_ok=True)

async def convert_audio_to_numpy(audio_data: bytes) -> np.ndarray:
    """Convert WebM audio (Opus) to a NumPy array using ffmpeg + soundfile"""
    import subprocess, io, soundfile as sf, numpy as np
    ffmpeg_path = r"C:\Program Files\ffmpeg-7.1.1-essentials_build\ffmpeg-7.1.1-essentials_build\bin\ffmpeg.exe"

    # Convert WebM (Opus) to WAV in memory using ffmpeg
    process = subprocess.run(
        [ffmpeg_path, '-i', 'pipe:0', '-f', 'wav', '-ar', '16000', '-ac', '1', 'pipe:1'],
        input=audio_data,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True
    )

    # Read WAV bytes as NumPy array
    wav_io = io.BytesIO(process.stdout)
    audio_array, sr = sf.read(wav_io)

    # Convert to float32 if not already
    return audio_array.astype(np.float32)


def convert_numpy_to_wav_bytes(audio_array: np.ndarray, sample_rate: int = 16000) -> bytes:
    """Convert numpy array to WAV file bytes"""
    # Normalize audio to prevent clipping
    if np.max(np.abs(audio_array)) > 1.0:
        audio_array = audio_array / np.max(np.abs(audio_array))
    
    # Convert to 16-bit PCM
    audio_array_16bit = (audio_array * 32767).astype(np.int16)
    
    # Create WAV file in memory
    wav_buffer = io.BytesIO()
    with wave.open(wav_buffer, 'wb') as wav_file:
        wav_file.setnchannels(1)  # Mono
        wav_file.setsampwidth(2)  # 16 bits
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(audio_array_16bit.tobytes())
    
    # Get bytes
    wav_bytes = wav_buffer.getvalue()
    wav_buffer.close()
    
    return wav_bytes


def save_received_audio(audio_data: bytes, file_format: str = "webm") -> str:
    """Save received audio data to a file"""
    if not SAVE_AUDIO_ENABLED:
        return ""
    
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"received_audio_{timestamp}.{file_format}"
    file_path = os.path.join(AUDIO_SAVE_DIR, filename)
    
    with open(file_path, 'wb') as f:
        f.write(audio_data)
    
    return file_path


def save_converted_audio(audio_array: np.ndarray, sample_rate: int = 16000) -> str:
    """Save numpy audio array as WAV file"""
    if not SAVE_AUDIO_ENABLED:
        return ""
    
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"converted_audio_{timestamp}.wav"
    file_path = os.path.join(AUDIO_SAVE_DIR, filename)
    
    # Convert to WAV bytes
    wav_bytes = convert_numpy_to_wav_bytes(audio_array, sample_rate)
    
    # Save to file
    with open(file_path, 'wb') as f:
        f.write(wav_bytes)
    
    return file_path


def save_response_audio(audio_data: bytes, chunk_number: int = 0) -> str:
    """Save audio response data that will be sent back to client"""
    if not SAVE_AUDIO_ENABLED:
        return ""
    
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"response_audio_{timestamp}_{chunk_number}.wav"
    file_path = os.path.join(AUDIO_SAVE_DIR, filename)
    
    with open(file_path, 'wb') as f:
        f.write(audio_data)
    
    return file_path


def validate_audio_format(audio_data: bytes) -> Dict[str, Any]:
    """Check if the audio data has a valid format"""
    format_info = {
        "is_valid": False,
        "format": "unknown",
        "size_bytes": len(audio_data)
    }
    
    if len(audio_data) < 10:
        return format_info
    
    # Check for WebM format
    if audio_data.startswith(b'\x1a\x45\xdf\xa3'):
        format_info["format"] = "webm"
        format_info["is_valid"] = True
    # Check for WAV format
    elif audio_data.startswith(b'RIFF') and b'WAVE' in audio_data[:20]:
        format_info["format"] = "wav"
        format_info["is_valid"] = True
    # Check for MP3 format
    elif audio_data.startswith(b'ID3') or audio_data.startswith(b'\xff\xfb'):
        format_info["format"] = "mp3"
        format_info["is_valid"] = True
    # Check for OGG format
    elif audio_data.startswith(b'OggS'):
        format_info["format"] = "ogg"
        format_info["is_valid"] = True
    
    return format_info


def cleanup_old_audio_files(max_age_hours: int = 24) -> int:
    """Delete old audio files"""
    if not os.path.exists(AUDIO_SAVE_DIR):
        return 0
    
    deleted_count = 0
    current_time = datetime.datetime.now()
    
    for filename in os.listdir(AUDIO_SAVE_DIR):
        file_path = os.path.join(AUDIO_SAVE_DIR, filename)
        
        if os.path.isfile(file_path):
            file_time = datetime.datetime.fromtimestamp(os.path.getmtime(file_path))
            age_hours = (current_time - file_time).total_seconds() / 3600
            
            if age_hours > max_age_hours:
                os.remove(file_path)
                deleted_count += 1
    
    return deleted_count


def get_audio_files_info() -> Dict[str, Any]:
    """Get basic information about saved audio files"""
    if not os.path.exists(AUDIO_SAVE_DIR):
        return {"total_files": 0}
    
    files = [f for f in os.listdir(AUDIO_SAVE_DIR) if os.path.isfile(os.path.join(AUDIO_SAVE_DIR, f))]
    return {
        "total_files": len(files),
        "files": files
    }


def get_audio_saving_enabled() -> bool:
    """Get whether audio saving is enabled"""
    return SAVE_AUDIO_ENABLED


def set_audio_saving_enabled(enabled: bool) -> None:
    """Set whether audio saving is enabled"""
    global SAVE_AUDIO_ENABLED
    SAVE_AUDIO_ENABLED = enabled