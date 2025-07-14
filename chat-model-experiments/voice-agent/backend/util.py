"""
Utility functions for audio handling in the backend.
Simplified version without curses dependency.
"""
import numpy as np
import numpy.typing as npt


class AudioPlayer:
    """Simple audio player for backend use."""
    
    def __init__(self):
        self.audio_chunks = []
    
    def add_audio(self, audio_data):
        """Add audio data to the player."""
        self.audio_chunks.append(audio_data)
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        # In a real implementation, you might want to play the audio
        # For now, we'll just log that audio was collected
        pass


def record_audio() -> npt.NDArray[np.float32]:
    """
    Simplified record_audio function for backend use.
    In the actual backend, audio will come from WebSocket.
    """
    # This is a placeholder - in the backend, audio comes from WebSocket
    return np.array([], dtype=np.float32)
