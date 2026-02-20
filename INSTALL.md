# Installation Guide

## Prerequisites

- Python 3.11 or higher
- pip or uv package manager

## Installation

### From PyPI

```bash
# Basic install
pip install tts-cli

# With PyTorch backend (CUDA / CPU)
pip install tts-cli[pytorch]

# With MLX backend (Apple Silicon)
pip install tts-cli[mlx]
```

### From source

```bash
git clone https://github.com/your-org/ttscli.git
cd ttscli
pip install -e ".[pytorch]"
```

Or using uv:

```bash
uv pip install -e ".[pytorch]"
```

### Verify installation

```bash
tts --version
```

You should see:
```
tts version 0.1.0
```

### Test basic commands

```bash
# List voices (should be empty initially)
tts voice list

# Show config
tts config show

# View help
tts --help
tts say --help
```

## Configuration (optional)

### Set custom data directory

```bash
tts config set data_dir /path/to/your/data
```

## Troubleshooting

### Command not found

If `tts` command is not found, ensure your Python scripts directory is in PATH:

```bash
# Add to ~/.bashrc or ~/.zshrc
export PATH="$HOME/.local/bin:$PATH"
```

Or use the module directly:

```bash
python -m ttscli --version
```

### Import errors

Make sure all dependencies are installed:

```bash
pip install -e ".[pytorch]" --force-reinstall
```

### Permission errors

On some systems you may need to install in user mode:

```bash
pip install --user -e .
```

## Development Installation

For development with testing tools:

```bash
pip install -e ".[dev]"
```

This installs additional packages: pytest, black, ruff, etc.

## Uninstallation

```bash
pip uninstall tts-cli
```

## Next Steps

See [README.md](README.md) for usage guide and examples.
