#!/usr/bin/env bash
set -euo pipefail

# ttscli installer
# Usage: curl -fsSL https://raw.githubusercontent.com/jiweiyuan/ttscli/main/install.sh | bash
# With options: curl -fsSL ... | bash -s -- --backend mlx

REPO="jiweiyuan/ttscli"
BACKEND=""
USE_UV=false

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --backend)
            BACKEND="$2"
            shift 2
            ;;
        --uv)
            USE_UV=true
            shift
            ;;
        --help)
            echo "ttscli installer"
            echo ""
            echo "Usage: curl -fsSL https://raw.githubusercontent.com/${REPO}/main/install.sh | bash"
            echo ""
            echo "Options:"
            echo "  --backend <mlx|pytorch>   Install with specific backend"
            echo "  --uv                      Force using uv instead of pipx"
            echo "  --help                    Show this help"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

info() { printf "\033[1;34m==>\033[0m \033[1m%s\033[0m\n" "$1"; }
warn() { printf "\033[1;33mWarning:\033[0m %s\n" "$1"; }
error() { printf "\033[1;31mError:\033[0m %s\n" "$1"; exit 1; }
success() { printf "\033[1;32m==>\033[0m \033[1m%s\033[0m\n" "$1"; }

# Detect OS and arch
OS="$(uname -s)"
ARCH="$(uname -m)"

info "Installing ttscli..."
echo "  OS: ${OS} / ${ARCH}"

# Check Python
if ! command -v python3 &>/dev/null; then
    error "Python 3 is required but not found. Install it first:
  macOS:   brew install python
  Ubuntu:  sudo apt install python3 python3-pip
  Fedora:  sudo dnf install python3 python3-pip"
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
PYTHON_MAJOR=$(echo "$PYTHON_VERSION" | cut -d. -f1)
PYTHON_MINOR=$(echo "$PYTHON_VERSION" | cut -d. -f2)

if [[ "$PYTHON_MAJOR" -lt 3 ]] || [[ "$PYTHON_MAJOR" -eq 3 && "$PYTHON_MINOR" -lt 11 ]]; then
    error "Python >= 3.11 is required, but found ${PYTHON_VERSION}"
fi

echo "  Python: ${PYTHON_VERSION}"

# Auto-detect backend for Apple Silicon
if [[ -z "$BACKEND" && "$OS" == "Darwin" && "$ARCH" == "arm64" ]]; then
    info "Apple Silicon detected, defaulting to mlx backend"
    BACKEND="mlx"
fi

# Determine package spec
PACKAGE="ttscli"
if [[ -n "$BACKEND" ]]; then
    PACKAGE="ttscli[${BACKEND}]"
fi

# Install using uv, pipx, or pip (in order of preference)
install_with_uv() {
    info "Installing with uv..."
    uv tool install "$PACKAGE"
}

install_with_pipx() {
    info "Installing with pipx..."
    pipx install "$PACKAGE"
}

install_with_pip() {
    info "Installing with pip..."
    python3 -m pip install --user "$PACKAGE"
}

if $USE_UV; then
    if command -v uv &>/dev/null; then
        install_with_uv
    else
        info "uv not found, installing uv first..."
        curl -LsSf https://astral.sh/uv/install.sh | sh
        export PATH="$HOME/.local/bin:$PATH"
        install_with_uv
    fi
elif command -v uv &>/dev/null; then
    install_with_uv
elif command -v pipx &>/dev/null; then
    install_with_pipx
else
    warn "Neither uv nor pipx found. Using pip --user install."
    warn "For better isolation, install pipx: python3 -m pip install --user pipx"
    install_with_pip
fi

# Verify installation
echo ""
if command -v tts &>/dev/null; then
    success "ttscli installed successfully!"
    echo ""
    tts --version
    echo ""
    echo "Get started:"
    echo "  tts --help"
    echo "  tts say \"Hello, world!\""
else
    warn "Installation completed but 'tts' command not found in PATH."
    echo ""
    echo "Add this to your shell profile (~/.bashrc or ~/.zshrc):"
    echo "  export PATH=\"\$HOME/.local/bin:\$PATH\""
    echo ""
    echo "Then restart your shell and run:"
    echo "  tts --help"
fi
