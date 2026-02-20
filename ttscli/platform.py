"""
Platform detection for backend selection.
"""

import platform
import sys
from typing import Literal


def is_apple_silicon() -> bool:
    """
    Check if running on Apple Silicon (arm64 macOS).

    Returns:
        True if on Apple Silicon, False otherwise
    """
    return platform.system() == "Darwin" and platform.machine() == "arm64"


def is_mlx_available() -> bool:
    """
    Check if MLX and mlx-audio are both importable.

    Returns:
        True if MLX stack is ready, False otherwise
    """
    try:
        import mlx  # noqa: F401
        import mlx_audio  # noqa: F401
        return True
    except ImportError:
        return False


def get_backend_type() -> Literal["mlx", "pytorch"]:
    """
    Detect the best backend for the current platform.

    Returns:
        "mlx" on Apple Silicon (if MLX is available), "pytorch" otherwise
    """
    if is_apple_silicon():
        if is_mlx_available():
            return "mlx"
        else:
            # Warn user they're missing out on MLX acceleration
            print(
                "\n⚠️  You're on Apple Silicon but MLX packages are not installed.\n"
                "   PyTorch CPU fallback will be VERY slow.\n"
                "   Install MLX for 10-50x faster inference:\n\n"
                "     pip install 'tts-cli[mlx]'\n"
                "     # or manually:\n"
                "     pip install mlx mlx-audio\n",
                file=sys.stderr,
            )
            return "pytorch"
    return "pytorch"
