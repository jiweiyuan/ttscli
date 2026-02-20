"""Pytest configuration and fixtures."""

import pytest
from pathlib import Path
import shutil


@pytest.fixture
def sample_audio(tmp_path):
    """Create sample audio file for testing."""
    # Try to copy from examples/clip1.wav
    example_audio = Path(__file__).parent.parent / "examples" / "clip1.wav"

    if example_audio.exists():
        audio_path = tmp_path / "sample.wav"
        shutil.copy(example_audio, audio_path)
        return audio_path
    else:
        # Create a simple test WAV file if example doesn't exist
        import numpy as np
        import soundfile as sf

        audio_path = tmp_path / "sample.wav"
        # Generate 1 second of 440Hz tone
        sample_rate = 24000
        duration = 1.0
        t = np.linspace(0, duration, int(sample_rate * duration))
        audio = np.sin(2 * np.pi * 440 * t).astype(np.float32)

        sf.write(audio_path, audio, sample_rate)
        return audio_path


@pytest.fixture
def temp_data_dir(tmp_path, monkeypatch):
    """Set up temporary data directory for tests.

    Patches both ``ttscli.storage`` and ``ttscli.voices`` so that all
    file-based operations happen inside a throwaway directory.
    """
    data_dir = tmp_path / "tts_data"
    data_dir.mkdir(parents=True, exist_ok=True)

    import ttscli.storage as storage_mod
    import ttscli.voices as voices_mod

    monkeypatch.setattr(storage_mod, "_data_dir", data_dir)

    # voices module has its own get_data_dir; patch it to return temp dir
    monkeypatch.setattr(voices_mod, "get_data_dir", lambda: data_dir)

    return data_dir
