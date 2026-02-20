"""Voice storage using JSON files (replaces database)."""

import json
from pathlib import Path
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field
import uuid


class Sample(BaseModel):
    """Audio sample for a voice."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    audio_path: str
    text: str
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


class Voice(BaseModel):
    """Voice configuration."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    language: str = "en"
    description: str = ""
    samples: List[Sample] = []
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


class Generation(BaseModel):
    """Generation history entry."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    voice_name: str
    text: str
    language: str
    audio_path: str
    duration: float
    model_size: str = "1.7B"
    seed: Optional[int] = None
    instruct: Optional[str] = None
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


class DataStore(BaseModel):
    """Main data store for all TTS data."""
    voices: List[Voice] = []
    history: List[Generation] = []


# Storage paths
def get_data_dir() -> Path:
    """Get data directory."""
    path = Path.home() / "tts"
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_voices_file() -> Path:
    """Get path to voices.json file."""
    return get_data_dir() / "voices.json"


def get_samples_dir() -> Path:
    """Get directory for audio samples."""
    path = get_data_dir() / "samples"
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_generations_dir() -> Path:
    """Get directory for generated audio."""
    path = get_data_dir() / "generations"
    path.mkdir(parents=True, exist_ok=True)
    return path


# CRUD operations
def load_data() -> DataStore:
    """Load all data from JSON file."""
    voices_file = get_voices_file()
    if not voices_file.exists():
        return DataStore()

    try:
        data = json.loads(voices_file.read_text())
        return DataStore.model_validate(data)
    except Exception as e:
        print(f"Warning: Failed to load voices.json: {e}")
        print("Creating new data store.")
        return DataStore()


def save_data(store: DataStore):
    """Save all data to JSON file."""
    voices_file = get_voices_file()
    voices_file.write_text(store.model_dump_json(indent=2))


# Voice operations
def list_voices() -> List[Voice]:
    """List all voices."""
    store = load_data()
    return store.voices


def get_voice(name_or_id: str) -> Optional[Voice]:
    """Get voice by name or ID."""
    store = load_data()

    # Try exact ID match
    for voice in store.voices:
        if voice.id == name_or_id:
            return voice

    # Try exact name match
    for voice in store.voices:
        if voice.name == name_or_id:
            return voice

    # Try case-insensitive name match
    name_lower = name_or_id.lower()
    for voice in store.voices:
        if voice.name.lower() == name_lower:
            return voice

    return None


def create_voice(name: str, language: str = "en", description: str = "") -> Voice:
    """Create a new voice."""
    store = load_data()

    # Check if name already exists
    if any(v.name.lower() == name.lower() for v in store.voices):
        raise ValueError(f"Voice '{name}' already exists")

    voice = Voice(name=name, language=language, description=description)
    store.voices.append(voice)
    save_data(store)

    return voice


def add_sample_to_voice(voice_name: str, audio_path: str, text: str) -> Sample:
    """Add a sample to a voice."""
    store = load_data()

    # Find voice
    voice = None
    for v in store.voices:
        if v.name == voice_name or v.id == voice_name:
            voice = v
            break

    if not voice:
        raise ValueError(f"Voice not found: {voice_name}")

    # Create sample
    sample = Sample(audio_path=audio_path, text=text)
    voice.samples.append(sample)
    voice.updated_at = datetime.utcnow().isoformat()

    save_data(store)
    return sample


def delete_voice(name_or_id: str) -> bool:
    """Delete a voice."""
    store = load_data()

    # Find and remove voice
    for i, voice in enumerate(store.voices):
        if voice.name == name_or_id or voice.id == name_or_id:
            # Delete sample files
            for sample in voice.samples:
                sample_path = Path(sample.audio_path)
                if sample_path.exists():
                    sample_path.unlink()

            store.voices.pop(i)
            save_data(store)
            return True

    return False


def update_voice(name_or_id: str, **kwargs) -> Optional[Voice]:
    """Update voice properties."""
    store = load_data()

    for voice in store.voices:
        if voice.name == name_or_id or voice.id == name_or_id:
            for key, value in kwargs.items():
                if hasattr(voice, key):
                    setattr(voice, key, value)
            voice.updated_at = datetime.utcnow().isoformat()
            save_data(store)
            return voice

    return None


# History operations
def add_generation(
    voice_name: str,
    text: str,
    language: str,
    audio_path: str,
    duration: float,
    model_size: str = "1.7B",
    seed: Optional[int] = None,
    instruct: Optional[str] = None,
) -> Generation:
    """Add a generation to history."""
    store = load_data()

    generation = Generation(
        voice_name=voice_name,
        text=text,
        language=language,
        audio_path=audio_path,
        duration=duration,
        model_size=model_size,
        seed=seed,
        instruct=instruct,
    )

    store.history.append(generation)

    # Keep only last 100 generations to prevent file bloat
    if len(store.history) > 100:
        store.history = store.history[-100:]

    save_data(store)
    return generation


def list_history(limit: int = 20) -> List[Generation]:
    """List generation history."""
    store = load_data()
    return store.history[-limit:][::-1]  # Most recent first
