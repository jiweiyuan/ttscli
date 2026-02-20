"""Data directory management."""

from pathlib import Path

_data_dir = Path.home() / "tts"


def set_data_dir(path, silent=False):
    """Set data directory."""
    global _data_dir
    _data_dir = Path(path)
    _data_dir.mkdir(parents=True, exist_ok=True)
    if not silent:
        print(f"Data directory set to: {_data_dir}")


def get_data_dir() -> Path:
    """Get data directory."""
    _data_dir.mkdir(parents=True, exist_ok=True)
    return _data_dir
