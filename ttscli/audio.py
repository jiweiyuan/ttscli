"""Audio utilities."""

import soundfile as sf


def save_audio(audio, path: str, sample_rate: int = 24000):
    """Save audio to WAV file."""
    sf.write(path, audio, sample_rate)
