"""
Audio Recorder Module
Records audio from the microphone using sounddevice.
"""

import numpy as np

from .fingerprint import SAMPLE_RATE  # single source of truth


def record(duration: float = 10.0, sr: int = SAMPLE_RATE) -> np.ndarray:
    """
    Record `duration` seconds from the default microphone.
    Returns a mono float32 numpy array.
    (Uses sounddevice — only needed for CLI mode, not Streamlit.)
    """
    import sounddevice as sd  # lazy import: not required by Streamlit app
    print(f"[Recorder] Recording for {duration}s …  (speak/play music now)")
    audio = sd.rec(
        int(duration * sr),
        samplerate=sr,
        channels=1,
        dtype='float32'
    )
    sd.wait()   # block until done
    print("[Recorder] Done.")
    return audio.flatten()


def load_audio_file(path: str, sr: int = SAMPLE_RATE) -> np.ndarray:
    """Load an audio file and return a mono float32 array."""
    import librosa
    audio, _ = librosa.load(path, sr=sr, mono=True)
    return audio
