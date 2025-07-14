import sounddevice as sd
from scipy.io.wavfile import write, read
import numpy as np
import soundfile as sf

def record_audio(duration=5, filename="recordings/recorded_audio.wav", fs=16000):
    """
    Records audio from the default microphone for the given duration (seconds)
    and saves it to the specified filename as a WAV file.
    """
    print(f"Recording for {duration} seconds...")
    audio = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='int16')
    sd.wait()
    write(filename, fs, audio)
    print(f"Recording saved to {filename}")

def play_audio(filename_or_filelike):
    """
    Plays back the specified WAV file or file-like object.
    """
    try:
        if hasattr(filename_or_filelike, 'read'):
            # It's a file-like object (BytesIO)
            print(f"Playing audio from BytesIO object...")
            filename_or_filelike.seek(0)  # Reset to beginning
            data, fs = sf.read(filename_or_filelike)
        else:
            # It's a filename string
            print(f"Playing {filename_or_filelike}...")
            fs, data = read(filename_or_filelike)
        
        # Ensure data is in the correct format
        if len(data.shape) > 1:
            # Convert stereo to mono if needed
            data = data.mean(axis=1)
        
        print(f"Audio info: sample rate={fs}, length={len(data)} samples, duration={len(data)/fs:.2f}s")
        sd.play(data, fs)
        sd.wait()
        print("Audio playback completed")
        
    except Exception as e:
        print(f"Error playing audio: {e}")
        # Try to play with soundfile instead
        try:
            if hasattr(filename_or_filelike, 'read'):
                filename_or_filelike.seek(0)
                data, fs = sf.read(filename_or_filelike)
            else:
                data, fs = sf.read(filename_or_filelike)
            
            if len(data.shape) > 1:
                data = data.mean(axis=1)
            
            print(f"Fallback: playing with soundfile - sample rate={fs}, length={len(data)}")
            sd.play(data, fs)
            sd.wait()
            print("Fallback audio playback completed")
        except Exception as fallback_error:
            print(f"Fallback audio playback also failed: {fallback_error}")


def compress_to_flac(wav_filename, flac_filename=None):
    """
    Compresses a WAV file to FLAC (lossless) format.
    """
    if flac_filename is None:
        flac_filename = wav_filename.rsplit('.', 1)[0] + '.flac'
    data, samplerate = sf.read(wav_filename)
    sf.write(flac_filename, data, samplerate, format='FLAC')
    print(f"Compressed {wav_filename} to {flac_filename}")