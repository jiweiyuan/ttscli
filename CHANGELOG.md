# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2025-02-19

### Added

- `tts generate` — generate speech from text and save to WAV
- `tts say` — speak text aloud with streaming audio playback
- `tts voice add` — add audio samples to a voice (creates voice if needed)
- `tts voice list` — list all voices
- `tts voice info` — show voice details
- `tts voice delete` — delete a voice
- `tts voice default` — set/show default voice
- `tts config show` — display current configuration
- `tts config set` — update configuration values
- PyTorch backend using Qwen3-TTS models (1.7B and 0.6B)
- MLX backend for Apple Silicon (via mlx-audio)
- Automatic platform detection (Apple Silicon → MLX, otherwise → PyTorch)
- Voice cloning from reference audio samples
- Streaming audio playback with chunked generation
- JSON output mode (`--output json` / `--json`) for scripting
- Rich terminal output with tables and progress spinners
- Configuration via TOML files or CLI flags
- Generation history tracking (last 100 entries)
