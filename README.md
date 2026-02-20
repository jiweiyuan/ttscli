# TTS CLI

A command-line interface for text-to-speech with voice cloning, powered by [Qwen3-TTS](https://huggingface.co/Qwen/Qwen3-TTS-12Hz-1.7B-Base).

Supports **PyTorch** (CUDA / CPU) and **MLX** (Apple Silicon) backends with automatic platform detection.

## Features

- 🎙️ **Voice cloning** — clone any voice from a short audio sample
- 🔊 **Streaming playback** — hear audio as it generates, no waiting
- 🍎 **Apple Silicon native** — MLX backend for fast local inference
- 🎛️ **Two model sizes** — 1.7B (quality) and 0.6B (speed)
- 📝 **JSON output** — machine-readable output for scripting and pipelines
- ⚙️ **Configurable** — TOML config files or CLI flags

## Installation

**Requires Python 3.11+**

```bash
# Basic install
pip install tts-cli

# With PyTorch backend
pip install tts-cli[pytorch]

# With MLX backend (Apple Silicon)
pip install tts-cli[mlx]

# Development
pip install tts-cli[dev]
```

Or install from source:

```bash
git clone https://github.com/your-org/ttscli.git
cd ttscli
pip install -e ".[pytorch]"
```

Verify:

```bash
tts --version
```

## Quick Start

### 1. Add a voice sample

```bash
tts voice add recording.wav --text "The transcript of the recording" --voice myvoice
```

### 2. Speak aloud (streaming)

```bash
tts say "Hello, how are you today?" --voice myvoice
```

### 3. Save to file

```bash
tts say "Hello world" --voice myvoice -o hello.wav --no-play
```

## Commands

### `tts say`

Generate speech from text. Plays aloud with streaming by default.

```bash
tts say "Text to speak" [OPTIONS]

Options:
  -v, --voice TEXT     Voice name (default: configured default)
  -l, --language TEXT  Language code (default: en)
  -m, --model TEXT     Model size: 1.7B or 0.6B (default: 1.7B)
  -o, --output PATH   Save to WAV file
  -i, --instruct TEXT  Speaking style instruction
  --no-play            Don't play audio, only save to file
  --no-stream          Disable streaming (generate all, then play)
  --seed INT           Random seed for reproducibility
```

Examples:

```bash
tts say "Hello, how are you?"                      # play aloud
tts say "Good morning" --voice myvoice             # use specific voice
tts say "Hello world" -o hello.wav                 # play and save
tts say "Hello world" -o hello.wav --no-play       # save only
tts say "Breaking news!" -i "Speak urgently"       # with style instruction
tts say "Slow and steady" --no-stream              # generate all, then play
```

### `tts voice`

Manage voices and audio samples.

```bash
tts voice add <audio_file> [OPTIONS]   # Add sample (creates voice if needed)
tts voice list                          # List all voices
tts voice info [VOICE]                  # Show voice details
tts voice delete <VOICE> [-y]           # Delete a voice
tts voice default [VOICE]               # Set/show default voice
tts voice default --unset               # Unset default voice
```

### `tts config`

View and update configuration.

```bash
tts config show                # Show current config
tts config set <key> <value>   # Set a config value
```

Available config keys: `data_dir`, `default_voice`, `default_language`, `default_model`, `output_format`, `auto_play`

## JSON Output

Use `--json` or `--output json` for machine-readable output:

```bash
tts --json voice list
tts --output json say "Hello" --voice myvoice
```

## Configuration

Configuration is loaded from (in order of priority):

1. CLI flags (`--data-dir`, `--output`)
2. Config files:
   - `./tts.toml` (project-local)
   - `~/.config/tts/config.toml`
   - `~/.tts/config.toml`

Example `config.toml`:

```toml
default_voice = "myvoice"
default_language = "en"
default_model = "1.7B"
output_format = "rich"
data_dir = "~/tts"
```

## Data Storage

All data is stored in `~/tts/` by default:

```text
~/tts/
├── voices.json       # Voice definitions and metadata
├── samples/          # Audio samples for voice cloning
└── generations/      # Generated audio files
```

## Requirements

- Python 3.11+
- **PyTorch backend**: torch, transformers, qwen-tts
- **MLX backend** (Apple Silicon): mlx, mlx-audio
- Audio: soundfile, sounddevice
- **System dependency**: [SoX](https://sox.sourceforge.net/) (required by qwen-tts)

  ```bash
  # macOS
  brew install sox
  # Ubuntu/Debian
  sudo apt install sox
  ```

## License

MIT — see [LICENSE](LICENSE) for details.
