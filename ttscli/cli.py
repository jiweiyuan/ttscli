"""TTS CLI - Main application."""

import os
import sys
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

# Suppress C-level DeprecationWarnings (e.g. swig) that fire during cleanup
import atexit
def _suppress_c_warnings():
    try:
        devnull = open(os.devnull, "w")
        os.dup2(devnull.fileno(), 2)
    except Exception:
        pass
atexit.register(_suppress_c_warnings)

import typer
from typing import Optional

from . import __version__
from .output_format import OutputFormat, set_output_format
from . import storage
from .commands import cmd_init, cmd_say, cmd_generate, voice_app, config_app

# Create app
app = typer.Typer(
    name="tts",
    help="Text-to-speech from the command line.",
    add_completion=False,
)

# Register commands
app.command(name="init", help="Install deps, download models, warm up")(cmd_init)
app.command(name="say", help="Speak text aloud")(cmd_say)
app.command(name="generate", help="Generate speech to file")(cmd_generate)
app.add_typer(voice_app, name="voice", help="Manage voices")
app.add_typer(config_app, name="config", help="Configuration")


def version_callback(value: bool):
    if value:
        print(f"tts {__version__}")
        raise typer.Exit()


@app.callback()
def main_callback(
    version: Optional[bool] = typer.Option(
        None, "--version", callback=version_callback, is_eager=True, help="Show version",
    ),
    json_output: bool = typer.Option(
        False, "--json", help="JSON output",
    ),
    data_dir: Optional[str] = typer.Option(
        None, "--data-dir", help="Data directory",
    ),
):
    """Text-to-speech from the command line."""
    if json_output:
        set_output_format(OutputFormat.JSON)

    if data_dir:
        storage.set_data_dir(data_dir, silent=json_output)
    else:
        storage.get_data_dir()


_GLOBAL_FLAGS = {"--json", "--version", "--data-dir"}
_SUBCOMMANDS = {"init", "say", "generate", "voice", "config", "help"}


def _reorder_args(args: list[str]) -> list[str]:
    """
    Move global flags from after a subcommand to before it.

    tts say --json        -> tts --json say
    tts say "hi" --json   -> tts --json say "hi"
    tts --json say "hi"   -> unchanged
    """
    if not args:
        return args

    # Find subcommand position
    cmd_idx = None
    for i, a in enumerate(args):
        if a in _SUBCOMMANDS:
            cmd_idx = i
            break

    if cmd_idx is None:
        return args

    # Collect global flags found after the subcommand
    before = list(args[:cmd_idx])
    cmd = args[cmd_idx]
    after = []
    hoisted = []
    i = cmd_idx + 1
    while i < len(args):
        a = args[i]
        if a in _GLOBAL_FLAGS:
            hoisted.append(a)
            # --data-dir takes a value
            if a == "--data-dir" and i + 1 < len(args):
                i += 1
                hoisted.append(args[i])
        else:
            after.append(a)
        i += 1

    return before + hoisted + [cmd] + after


def main():
    """Entry point."""
    args = sys.argv[1:]

    # `tts help [cmd]` -> `tts [cmd] --help`
    if args and args[0] == "help":
        if len(args) > 1:
            sys.argv = [sys.argv[0], args[1], "--help"]
        else:
            sys.argv = [sys.argv[0], "--help"]
    else:
        sys.argv = [sys.argv[0]] + _reorder_args(args)

    try:
        app()
    except KeyboardInterrupt:
        print("\nInterrupted")
        raise typer.Exit(130)
    except Exception as e:
        print(f"Error: {e}")
        raise typer.Exit(1)


if __name__ == "__main__":
    main()
