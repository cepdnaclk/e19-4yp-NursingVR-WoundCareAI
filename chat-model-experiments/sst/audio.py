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

def play_audio(filename):
    """
    Plays back the specified WAV file.
    """
    fs, data = read(filename)
    print(f"Playing {filename}...")
    sd.play(data, fs)
    sd.wait()


def compress_to_flac(wav_filename, flac_filename=None):
    """
    Compresses a WAV file to FLAC (lossless) format.
    """
    if flac_filename is None:
        flac_filename = wav_filename.rsplit('.', 1)[0] + '.flac'
    data, samplerate = sf.read(wav_filename)
    sf.write(flac_filename, data, samplerate, format='FLAC')
    print(f"Compressed {wav_filename} to {flac_filename}")