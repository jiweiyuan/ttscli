"""Configuration and settings management using Pydantic."""

from pydantic_settings import BaseSettings, TomlConfigSettingsSource
from pathlib import Path
from typing import Literal, Optional, Tuple, Type


_TOML_FILES = [
    Path.home() / ".config" / "tts" / "config.toml",
    Path.home() / ".tts" / "config.toml",
    "tts.toml",
]


class TTSSettings(BaseSettings):
    """TTS CLI settings with TOML config file support."""

    # Data storage
    data_dir: Path = Path.home() / "tts"

    # Default voice (for add/say without --voice)
    default_voice: Optional[str] = None

    # Generation defaults
    default_language: str = "en"
    default_model: str = "1.7B"

    # Output
    output_format: Literal["rich", "json", "plain"] = "rich"

    # Audio
    auto_play: bool = False

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: Type[BaseSettings],
        init_settings,
        env_settings,
        dotenv_settings,
        file_secret_settings,
    ) -> Tuple:
        """Use only init settings and TOML config files."""
        existing_toml = [f for f in _TOML_FILES if Path(f).exists()]

        if existing_toml:
            toml_source = TomlConfigSettingsSource(
                settings_cls,
                toml_file=existing_toml,
            )
            return (init_settings, toml_source)

        return (init_settings,)


# Singleton instance
_settings: Optional[TTSSettings] = None


def get_settings() -> TTSSettings:
    """Get or create settings instance."""
    global _settings
    if _settings is None:
        _settings = TTSSettings()
    return _settings


def reload_settings():
    """Reload settings from config files."""
    global _settings
    _settings = None
    return get_settings()
