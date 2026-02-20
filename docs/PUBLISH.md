# Publishing Guide — TTS CLI

Step-by-step SOP for building, packaging, and publishing the TTS CLI after code updates.

---

## Table of Contents

- [Prerequisites](#prerequisites)
- [Step 1: Update Version](#step-1-update-version)
- [Step 2: Run Tests](#step-2-run-tests)
- [Step 3: Build Standalone Binary (PyInstaller)](#step-3-build-standalone-binary-pyinstaller)
- [Step 4: Test the Binary](#step-4-test-the-binary)
- [Step 5: Publish to PyPI](#step-5-publish-to-pypi)
- [Step 6: Create GitHub Release](#step-6-create-github-release)
- [CI/CD: Automated Cross-Platform Builds](#cicd-automated-cross-platform-builds)
- [Reducing Binary Size](#reducing-binary-size)
- [Troubleshooting](#troubleshooting)
- [Checklist](#checklist)

---

## Prerequisites

Make sure you have the following installed:

```bash
# Python 3.11+
python3.11 --version

# Create virtual environment (if not exists)
cd /path/to/voicebox/cli
python3.11 -m venv .venv
source .venv/bin/activate

# Install project + dev dependencies
pip install -e ".[dev]"

# Install packaging tools
pip install pyinstaller build twine
```

---

## Step 1: Update Version

You must bump the version in **two files** before publishing:

### 1a. `src/ttscli/__init__.py`

```python
__version__ = "0.2.0"  # Update this
```

### 1b. `pyproject.toml`

```toml
[project]
version = "0.2.0"  # Must match __init__.py
```

### Version Convention

Follow [Semantic Versioning](https://semver.org/):

| Change Type        | Example          |
|--------------------|------------------|
| Bug fix            | `0.1.0` → `0.1.1` |
| New feature        | `0.1.0` → `0.2.0` |
| Breaking change    | `0.1.0` → `1.0.0` |

---

## Step 2: Run Tests

Always run the full test suite before publishing:

```bash
source .venv/bin/activate

# Run all tests
pytest

# Run with coverage
pytest --cov=ttscli --cov-report=term-missing

# Lint check
ruff check src/
black --check src/
```

✅ **Do NOT publish if any test fails.**

---

## Step 3: Build Standalone Binary (PyInstaller)

### 3a. Ensure the entry point file exists

The file `entry_point.py` in the project root is required (PyInstaller cannot handle relative imports in `__main__.py`):

```python
# entry_point.py
"""PyInstaller entry point for tts CLI."""
from ttscli.cli import main

if __name__ == "__main__":
    main()
```

### 3b. Clean previous builds

```bash
rm -rf build/ dist/ *.spec
```

### 3c. Build the binary

```bash
source .venv/bin/activate

pyinstaller \
  --onefile \
  --name tts \
  --paths src \
  --collect-submodules ttscli \
  entry_point.py
```

### 3d. Verify the output

```bash
ls -lh dist/tts
# Expected: dist/tts — a standalone Mach-O binary (~200MB)

file dist/tts
# Expected: Mach-O 64-bit executable arm64 (on Apple Silicon)
#       or: Mach-O 64-bit executable x86_64 (on Intel Mac)
```

> **Note:** The binary is platform-specific. A macOS build only runs on macOS. See [CI/CD section](#cicd-automated-cross-platform-builds) for cross-platform builds.

---

## Step 4: Test the Binary

Run these commands to verify the binary works correctly **without** the virtual environment:

```bash
# Deactivate venv to ensure binary is truly standalone
deactivate

# Version
./dist/tts --version
# Expected: tts version 0.2.0

# Help
./dist/tts --help
# Expected: Shows all options and commands

# Subcommands
./dist/tts generate --help
./dist/tts voice --help
./dist/tts config --help

# Functional test (if you have a voice set up)
./dist/tts voice list
./dist/tts config show
```

✅ **All commands must work before proceeding.**

---

## Step 5: Publish to PyPI

This lets users install via `pip install tts-cli`.

### 5a. First-time setup (one-time only)

1. Create an account at [https://pypi.org/account/register/](https://pypi.org/account/register/)
2. Create an API token at [https://pypi.org/manage/account/#api-tokens](https://pypi.org/manage/account/#api-tokens)
3. Save the token in `~/.pypirc`:

```ini
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = pypi-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### 5b. Build the Python package

```bash
source .venv/bin/activate

# Clean previous builds
rm -rf dist/ build/ *.egg-info

# Build source distribution and wheel
python -m build
```

This produces:
```
dist/
├── tts_cli-0.2.0.tar.gz     # Source distribution
└── tts_cli-0.2.0-py3-none-any.whl  # Wheel
```

### 5c. Test upload (recommended)

```bash
# Upload to TestPyPI first
twine upload --repository testpypi dist/*.tar.gz dist/*.whl

# Test install from TestPyPI
pip install --index-url https://test.pypi.org/simple/ tts-cli
```

### 5d. Publish to PyPI

```bash
twine upload dist/*.tar.gz dist/*.whl
```

### 5e. Verify

```bash
# Install from PyPI
pip install tts-cli

# Test
tts --version
```

---

## Step 6: Create GitHub Release

### 6a. Tag the release

```bash
git add -A
git commit -m "Release v0.2.0"
git tag v0.2.0
git push origin main --tags
```

### 6b. Create release on GitHub

1. Go to **GitHub → Releases → Draft a new release**
2. Select tag `v0.2.0`
3. Title: `v0.2.0`
4. Attach the binary: upload `dist/tts`
5. Add release notes (what changed)
6. Publish

Users can then download the binary directly from the Releases page.

---

## CI/CD: Automated Cross-Platform Builds

To automatically build binaries for **macOS, Linux, and Windows** on every release, add this GitHub Actions workflow:

Create `.github/workflows/release.yml`:

```yaml
name: Build & Release

on:
  push:
    tags:
      - "v*"

permissions:
  contents: write

jobs:
  build:
    strategy:
      matrix:
        include:
          - os: macos-latest
            artifact_name: tts-macos-arm64
          - os: macos-13
            artifact_name: tts-macos-x86_64
          - os: ubuntu-latest
            artifact_name: tts-linux-x86_64
          - os: windows-latest
            artifact_name: tts-windows-x86_64.exe
    runs-on: ${{ matrix.os }}

    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install dependencies
        run: |
          cd cli
          pip install -e .
          pip install pyinstaller

      - name: Build binary
        run: |
          cd cli
          pyinstaller --onefile --name ${{ matrix.artifact_name }} --paths src --collect-submodules ttscli entry_point.py

      - name: Upload artifact
        uses: actions/upload-artifact@v4
        with:
          name: ${{ matrix.artifact_name }}
          path: cli/dist/${{ matrix.artifact_name }}

  release:
    needs: build
    runs-on: ubuntu-latest
    steps:
      - name: Download all artifacts
        uses: actions/download-artifact@v4
        with:
          path: artifacts/

      - name: Create GitHub Release
        uses: softprops/action-gh-release@v2
        with:
          files: artifacts/**/*
          generate_release_notes: true
```

With this workflow, pushing a version tag triggers automatic builds:

```bash
git tag v0.2.0
git push origin v0.2.0
# → GitHub Actions builds binaries for all platforms
# → Attaches them to the release automatically
```

---

## Reducing Binary Size

The binary is ~222MB because it bundles PyTorch, Transformers, etc. Here are ways to reduce it:

### Exclude unused modules

```bash
pyinstaller \
  --onefile \
  --name tts \
  --paths src \
  --collect-submodules ttscli \
  --exclude-module torch.cuda \
  --exclude-module torch.distributed \
  --exclude-module matplotlib \
  --exclude-module tkinter \
  --exclude-module unittest \
  --exclude-module test \
  entry_point.py
```

### Use UPX compression

```bash
# Install UPX
brew install upx   # macOS

# Build with UPX
pyinstaller --onefile --name tts --paths src --collect-submodules ttscli --upx-dir $(which upx | xargs dirname) entry_point.py
```

### Use Nuitka (alternative to PyInstaller)

```bash
pip install nuitka
nuitka --standalone --onefile --output-filename=tts --include-package=ttscli src/ttscli/__main__.py
```

Nuitka compiles Python → C → native binary, often producing smaller and faster binaries.

---

## Troubleshooting

### `ImportError: attempted relative import with no known parent package`

PyInstaller cannot run `__main__.py` with relative imports. Use `entry_point.py` instead:

```python
from ttscli.cli import main
if __name__ == "__main__":
    main()
```

### `ModuleNotFoundError: No module named 'ttscli'`

Add `--paths src` to the PyInstaller command so it can find the source package.

### Binary crashes with hidden import errors

Some dynamic imports aren't detected by PyInstaller. Add them explicitly:

```bash
pyinstaller ... --hidden-import some_module
```

Check the build warnings in `build/tts/warn-tts.txt` for clues.

### `codesign` errors on macOS

If macOS blocks the binary, allow it in System Settings → Privacy & Security, or sign it:

```bash
codesign --force --sign - dist/tts
```

### PyPI upload rejected: version already exists

You cannot overwrite a published version on PyPI. Bump the version number and rebuild.

---

## Checklist

Use this checklist for every release:

```
Pre-Release:
  [ ] Version bumped in src/ttscli/__init__.py
  [ ] Version bumped in pyproject.toml
  [ ] Both versions match
  [ ] All tests pass (pytest)
  [ ] Linting passes (ruff check, black --check)
  [ ] CHANGELOG/release notes written

Build Binary:
  [ ] Clean build (rm -rf build/ dist/ *.spec)
  [ ] PyInstaller build succeeds
  [ ] Binary runs: ./dist/tts --version
  [ ] Binary runs: ./dist/tts --help
  [ ] All subcommands work (generate, voice, config)

Publish to PyPI:
  [ ] python -m build succeeds
  [ ] Tested on TestPyPI first
  [ ] twine upload to PyPI succeeds
  [ ] pip install tts-cli works
  [ ] tts --version shows correct version

GitHub Release:
  [ ] Code committed and pushed
  [ ] Git tag created (vX.Y.Z)
  [ ] GitHub Release created with binary attached
  [ ] Release notes added
```

---

## Quick Reference

| Action | Command |
|--------|---------|
| Run tests | `pytest` |
| Build binary | `pyinstaller --onefile --name tts --paths src --collect-submodules ttscli entry_point.py` |
| Test binary | `./dist/tts --version` |
| Build Python package | `python -m build` |
| Upload to TestPyPI | `twine upload --repository testpypi dist/*` |
| Upload to PyPI | `twine upload dist/*` |
| Tag release | `git tag v0.2.0 && git push origin v0.2.0` |

---

## Distribution Methods Summary

| Method | Command for Users | Python Required? |
|--------|-------------------|------------------|
| **PyPI** | `pip install tts-cli` | ✅ Yes |
| **pipx** | `pipx install tts-cli` | ✅ Yes (isolated) |
| **Binary (GitHub Release)** | Download & run `./tts` | ❌ No |
| **Homebrew (future)** | `brew install tts-cli` | ❌ No |
