"""All CLI commands."""

import typer
from pathlib import Path
from typing import Optional
import shutil
import uuid
import asyncio
import toml
import json
import sys
import subprocess
import time
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, TimeElapsedColumn
from contextlib import contextmanager

from . import voices
from .backends import get_tts_backend
from .output_format import OutputFormat, get_output_format
from .config import get_settings, reload_settings
from .platform import is_apple_silicon, is_mlx_available

console = Console()


# ============================================
# Output helpers
# ============================================

def print_success(msg):
    console.print(f"Done: {msg}")

def print_error(msg):
    console.print(f"Error: {msg}")

def output_json(data):
    from . import __version__
    if isinstance(data, dict):
        data.setdefault('cli_version', __version__)
        data.setdefault('timestamp', str(uuid.uuid4()))
    print(json.dumps(data, indent=2, default=str))

def output_result(data, resource_name=None):
    if get_output_format() == OutputFormat.JSON:
        if isinstance(data, list) and resource_name:
            data = {resource_name: data}
        output_json(data)
    else:
        console.print(data)

def output_success(message, data=None):
    if get_output_format() == OutputFormat.JSON:
        result = {"status": "success", "message": message}
        if data:
            result["data"] = data
        output_json(result)
    else:
        print_success(message)

def output_error(message, code="ERROR"):
    if get_output_format() == OutputFormat.JSON:
        print(json.dumps({"error": {"code": code, "message": message}}, indent=2), file=sys.stderr)
    else:
        print_error(message)

@contextmanager
def show_progress(description):
    if get_output_format() == OutputFormat.JSON:
        class Dummy:
            def add_task(self, *args, **kwargs): return None
        yield Dummy()
    else:
        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), TimeElapsedColumn(), console=console, transient=True) as p:
            p.add_task(description, total=None)
            yield p

def format_duration(seconds):
    if seconds < 60:
        return f"{seconds:.2f}s"
    mins = int(seconds // 60)
    secs = seconds % 60
    return f"{mins}m {secs:.0f}s" if secs > 0 else f"{mins}m"


# ============================================
# INIT - Setup backend & download models
# ============================================

# Model registry: backend -> model_size -> model_id
MODEL_REGISTRY = {
    "mlx": {
        "0.6B": "mlx-community/Qwen3-TTS-12Hz-0.6B-Base-4bit",
        "1.7B": "mlx-community/Qwen3-TTS-12Hz-1.7B-Base-8bit",
    },
    "pytorch": {
        "0.6B": "Qwen/Qwen3-TTS-12Hz-0.6B-Base",
        "1.7B": "Qwen/Qwen3-TTS-12Hz-1.7B-Base",
    },
}

# Pip extras per backend
BACKEND_PACKAGES = {
    "mlx": ["mlx", "mlx-audio>=0.3.0", "librosa"],
    "pytorch": ["torch>=2.1.0", "qwen-tts>=0.1.0", "transformers", "accelerate", "sentencepiece"],
}


def _pip_install(packages: list[str]) -> bool:
    """Install pip packages, return True on success."""
    cmd = [sys.executable, "-m", "pip", "install", "--quiet"] + packages
    console.print(f"[dim]  $ pip install {' '.join(packages)}[/dim]")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        console.print(f"[red]  pip install failed:[/red]\n{result.stderr[:500]}")
        return False
    return True


def _check_packages_installed(packages: list[str]) -> list[str]:
    """Return list of packages that are NOT importable."""
    missing = []
    # Map pip names to importable names
    import_map = {
        "mlx-audio": "mlx_audio",
        "mlx-audio>=0.3.0": "mlx_audio",
        "qwen-tts>=0.1.0": "qwen_tts",
        "qwen-tts": "qwen_tts",
        "torch>=2.1.0": "torch",
        "transformers": "transformers",
        "accelerate": "accelerate",
        "sentencepiece": "sentencepiece",
        "librosa": "librosa",
        "mlx": "mlx",
    }
    for pkg in packages:
        import_name = import_map.get(pkg, pkg.split(">=")[0].split("==")[0].replace("-", "_"))
        try:
            __import__(import_name)
        except ImportError:
            missing.append(pkg)
    return missing


def _download_model(model_id: str) -> str:
    """Download model from HuggingFace Hub. Returns local path."""
    from huggingface_hub import snapshot_download
    return snapshot_download(model_id)


def cmd_init(
    model: Optional[str] = typer.Option(
        None, "--model", "-m",
        help="Model size to download: 0.6B, 1.7B, or 'all' (default: from config)",
    ),
    backend: Optional[str] = typer.Option(
        None, "--backend", "-b",
        help="Force backend: mlx or pytorch (auto-detected by default)",
    ),
    skip_deps: bool = typer.Option(
        False, "--skip-deps",
        help="Skip dependency installation",
    ),
    skip_model: bool = typer.Option(
        False, "--skip-model",
        help="Skip model download",
    ),
    skip_warmup: bool = typer.Option(
        False, "--skip-warmup",
        help="Skip model warmup",
    ),
):
    """
    Initialize TTS: install dependencies, download models, and warm up.

    Auto-detects your platform and installs the optimal backend:
    - Apple Silicon (M1/M2/M3/M4): MLX (fastest)
    - NVIDIA GPU: PyTorch + CUDA
    - Other: PyTorch CPU

    Examples:

        tts init                      # Auto-detect, download default model
        tts init --model 1.7B         # Download the larger model
        tts init --model all          # Download all models
        tts init --backend pytorch    # Force PyTorch backend
        tts init --skip-deps          # Only download models
    """
    t_start = time.time()

    # ── Step 1: Detect platform ──
    console.print("\n[bold]Detecting platform...[/bold]")

    if backend:
        if backend not in ("mlx", "pytorch"):
            print_error(f"Unknown backend: {backend}. Use 'mlx' or 'pytorch'.")
            raise typer.Exit(1)
        chosen_backend = backend
    elif is_apple_silicon():
        chosen_backend = "mlx"
    else:
        chosen_backend = "pytorch"

    platform_info = {
        "mlx": "Apple Silicon → [green]MLX[/green] (GPU-accelerated)",
        "pytorch": "→ [yellow]PyTorch[/yellow]",
    }
    console.print(f"  {platform_info[chosen_backend]}")

    if is_apple_silicon() and chosen_backend == "pytorch":
        console.print("  [dim](Tip: MLX is faster on Apple Silicon. Use --backend mlx)[/dim]")

    # ── Step 2: Install dependencies ──
    if not skip_deps:
        console.print(f"\n[bold]Checking dependencies ({chosen_backend})...[/bold]")
        required = BACKEND_PACKAGES[chosen_backend]
        missing = _check_packages_installed(required)

        if missing:
            console.print(f"  Installing {len(missing)} package(s)...")
            if not _pip_install(missing):
                print_error("Failed to install dependencies. Try manually:")
                console.print(f"  pip install {' '.join(missing)}")
                raise typer.Exit(1)
            console.print("  Done: Dependencies installed")
        else:
            console.print("  Done: All dependencies already installed")
    else:
        console.print("\n[dim]Skipping dependency check (--skip-deps)[/dim]")

    # ── Step 3: Download models ──
    default_model = get_settings().default_model
    if not skip_model:
        models_to_download = []
        if model == "all":
            models_to_download = list(MODEL_REGISTRY[chosen_backend].keys())
        else:
            model_size = model or default_model
            if model_size not in MODEL_REGISTRY[chosen_backend]:
                print_error(
                    f"Unknown model: {model_size}. "
                    f"Available: {', '.join(MODEL_REGISTRY[chosen_backend].keys())}"
                )
                raise typer.Exit(1)
            models_to_download = [model_size]

        console.print(f"\n[bold]Downloading model(s): {', '.join(models_to_download)}...[/bold]")

        for m in models_to_download:
            model_id = MODEL_REGISTRY[chosen_backend][m]
            console.print(f"  {m}: [dim]{model_id}[/dim]")

            try:
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    TimeElapsedColumn(),
                    console=console,
                    transient=True,
                ) as progress:
                    progress.add_task(f"Downloading {m}...", total=None)
                    local_path = _download_model(model_id)
                console.print(f"  Done: {m} ready ({local_path})")
            except Exception as e:
                print_error(f"Failed to download {m}: {e}")
                raise typer.Exit(1)
    else:
        console.print("\n[dim]Skipping model download (--skip-model)[/dim]")

    # ── Step 4: Warmup (MLX JIT compile) ──
    if not skip_warmup and chosen_backend == "mlx":
        console.print(f"\n[bold]Warming up MLX (JIT compilation)...[/bold]")
        console.print("  [dim]First run compiles GPU kernels — subsequent runs are instant.[/dim]")

        try:
            model_size = model if model and model != "all" else default_model
            backend_obj = get_tts_backend()
            asyncio.run(_warmup_backend(backend_obj, model_size))
            console.print("  Done: Warmup complete")
        except Exception as e:
            console.print(f"  [yellow]Warmup failed (non-fatal): {e}[/yellow]")
    elif not skip_warmup:
        console.print(f"\n[dim]Skipping warmup (PyTorch doesn't need it)[/dim]")

    # ── Step 5: Create data directory & save config ──
    data_dir = get_settings().data_dir
    data_dir.mkdir(parents=True, exist_ok=True)
    (data_dir / "samples").mkdir(exist_ok=True)
    (data_dir / "generations").mkdir(exist_ok=True)

    # Save the chosen model as default so `tts say` uses the same one
    if not skip_model and model != "all":
        chosen_model = model or default_model
        config_file = Path.home() / ".config" / "tts" / "config.toml"
        config_file.parent.mkdir(parents=True, exist_ok=True)
        data = toml.load(config_file) if config_file.exists() else {}
        data["default_model"] = chosen_model
        config_file.write_text(toml.dumps(data))
        reload_settings()

    # ── Done ──
    elapsed = time.time() - t_start
    chosen_model = model if model and model != "all" else default_model
    console.print(f"\n[bold green]TTS initialized![/bold green] ({elapsed:.1f}s)")
    console.print(f"  Backend:  {chosen_backend}")
    console.print(f"  Model:    {chosen_model}")
    console.print(f"  Data dir: {data_dir}")
    console.print(f"\n  [dim]Get started:[/dim]")
    console.print(f"    tts voice add sample.wav -t 'transcript of the audio'")
    console.print(f"    tts say 'Hello world!'")
    console.print()


async def _warmup_backend(backend, model_size: str):
    """Load model and run warmup generation."""
    await backend.load_model(model_size)
    # For MLX backend, _warmup() is called automatically on first generate
    # Just do a quick generate to trigger it
    if hasattr(backend, '_warmup'):
        import asyncio
        await asyncio.to_thread(backend._warmup)


# ============================================
# SAY - Main speech command
# ============================================

def _get_sounddevice():
    """Import sounddevice lazily. Returns module or None."""
    try:
        import sounddevice
        return sounddevice
    except ImportError:
        return None


def cmd_say(
    text: Optional[str] = typer.Argument(None, help="Text to speak (omit to read stdin)"),
    file: Optional[Path] = typer.Option(None, "--file", "-f", help="Read text from file"),
    save: Optional[Path] = typer.Option(None, "--save", "-s", help="Save audio to WAV file"),
    voice: Optional[str] = typer.Option(None, "--voice", help="Voice name"),
    model: Optional[str] = typer.Option(None, "--model", "-m", help="Model size: 0.6B or 1.7B"),
    instruct: Optional[str] = typer.Option(None, "--instruct", "-i", help="Speaking style instruction"),
    language: Optional[str] = typer.Option(None, "--language", help="Language code"),
    seed: Optional[int] = typer.Option(None, "--seed", help="Random seed"),
    no_play: bool = typer.Option(False, "--no-play", help="Save only, don't play"),
    no_stream: bool = typer.Option(False, "--no-stream", help="Generate all audio before playing"),
):
    """
    Speak text aloud or save to file.

    Examples:

        tts say "Hello world"
        tts say --file article.txt
        tts say "Hello" --save hello.wav
        echo "text with <special> chars" | tts say
    """
    # Priority: --file > argument > stdin
    if file is not None:
        if not file.exists():
            print_error(f"File not found: {file}")
            raise typer.Exit(1)
        text = file.read_text().strip()
    elif text is None or text == "-":
        if sys.stdin.isatty():
            print("Enter text (Ctrl-D to finish):", file=sys.stderr)
        text = sys.stdin.read().strip()

    if not text:
        print_error("No text provided.")
        raise typer.Exit(1)

    asyncio.run(_async_say(text, voice, language, model, save, seed, instruct, no_play, no_stream))


def cmd_generate(
    text: Optional[str] = typer.Argument(None, help="Text to speak (omit to read stdin)"),
    file: Optional[Path] = typer.Option(None, "--file", "-f", help="Read text from file"),
    output: Path = typer.Option(..., "--output", "-o", help="Output WAV file path"),
    voice: Optional[str] = typer.Option(None, "--voice", help="Voice name"),
    model: Optional[str] = typer.Option(None, "--model", "-m", help="Model size: 0.6B or 1.7B"),
    instruct: Optional[str] = typer.Option(None, "--instruct", "-i", help="Speaking style instruction"),
    language: Optional[str] = typer.Option(None, "--language", help="Language code"),
    seed: Optional[int] = typer.Option(None, "--seed", help="Random seed"),
):
    """
    Generate speech and save to file (no playback).

    Examples:

        tts generate "Hello world" -o hello.wav
        tts generate --file article.txt -o article.wav
        echo "Hello" | tts generate -o out.wav
    """
    if file is not None:
        if not file.exists():
            print_error(f"File not found: {file}")
            raise typer.Exit(1)
        text = file.read_text().strip()
    elif text is None or text == "-":
        if sys.stdin.isatty():
            print("Enter text (Ctrl-D to finish):", file=sys.stderr)
        text = sys.stdin.read().strip()

    if not text:
        print_error("No text provided.")
        raise typer.Exit(1)

    asyncio.run(_async_say(text, voice, language, model, output, seed, instruct, no_play=True, no_stream=True))


async def _async_say(text, voice, language, model, output, seed, instruct, no_play, no_stream):
    """Async implementation of speech generation and playback."""
    import time
    import numpy as np

    settings = get_settings()
    model = model or settings.default_model
    is_rich = get_output_format() == OutputFormat.RICH
    is_json = get_output_format() == OutputFormat.JSON
    first_chunk_time = None
    sample_rate = 24000
    should_play = not no_play

    # Nudge toward `tts init` if MLX missing on Apple Silicon
    if is_rich and is_apple_silicon() and not is_mlx_available():
        console.print(
            "[yellow]MLX not installed — slow CPU fallback.[/yellow] "
            "Run [bold]tts init[/bold] to fix.\n"
        )

    try:
        # Resolve voice
        voice = voice or settings.default_voice or "default"
        voice_obj = voices.get_voice(voice)
        if not voice_obj:
            output_error(f"Voice not found: {voice}\nRun: tts voice add audio.wav", "NOT_FOUND")
            raise typer.Exit(1)
        if not voice_obj.samples:
            output_error(f"Voice '{voice_obj.name}' has no samples.\nRun: tts voice add audio.wav", "NO_SAMPLES")
            raise typer.Exit(1)

        language = language or voice_obj.language

        # Load model + create voice prompt (single spinner)
        backend = get_tts_backend()

        with show_progress("Loading model..."):
            await backend.load_model(model)
            sample = voice_obj.samples[0]
            voice_prompt, _ = await backend.create_voice_prompt(
                sample.audio_path, sample.text, use_cache=True,
            )

        # Check sounddevice
        sd = None
        if should_play:
            sd = _get_sounddevice()
            if sd is None:
                if is_rich:
                    print_error("sounddevice not installed. Skipping playback.")
                should_play = False
        if not should_play:
            no_stream = True

        t_start = time.time()

        if no_stream:
            # ── Non-streaming ──
            with show_progress("Generating..."):
                audio, sample_rate = await backend.generate(
                    text, voice_prompt, language, seed, instruct,
                )
            duration = len(audio) / sample_rate
            t_gen = time.time() - t_start

            if should_play and sd is not None:
                try:
                    sd.play(audio, sample_rate)
                    sd.wait()
                except Exception as e:
                    print_error(f"Playback failed: {e}")

            if is_rich:
                console.print(f"Done: {format_duration(duration)} audio ({t_gen:.1f}s)")

            all_audio = audio

        else:
            # ── Streaming ──
            all_chunks = []
            stream = None
            audio_buffer = []

            def _audio_callback(outdata, frames, time_info, status):
                needed = frames
                written = 0
                while needed > 0 and audio_buffer:
                    chunk = audio_buffer[0]
                    avail = len(chunk)
                    if avail <= needed:
                        outdata[written:written + avail, 0] = chunk
                        written += avail
                        needed -= avail
                        audio_buffer.pop(0)
                    else:
                        outdata[written:written + needed, 0] = chunk[:needed]
                        audio_buffer[0] = chunk[needed:]
                        written += needed
                        needed = 0
                if needed > 0:
                    outdata[written:, 0] = 0.0

            try:
                async for audio_chunk, sr, is_final in backend.generate_stream(
                    text=text, voice_prompt=voice_prompt,
                    language=language, seed=seed, instruct=instruct,
                ):
                    sample_rate = sr
                    if first_chunk_time is None:
                        first_chunk_time = time.time() - t_start
                        stream = sd.OutputStream(
                            samplerate=sample_rate, channels=1,
                            dtype="float32", callback=_audio_callback,
                            blocksize=1024,
                        )
                        stream.start()

                    chunk_f32 = np.asarray(audio_chunk, dtype=np.float32)
                    all_chunks.append(chunk_f32)
                    audio_buffer.append(chunk_f32.copy())

            except Exception as e:
                print_error(f"Generation error: {e}")
                raise typer.Exit(1)

            # Drain playback
            if stream is not None:
                remaining = sum(len(c) for c in audio_buffer)
                await asyncio.sleep(remaining / sample_rate + 0.1 if remaining > 0 else 0.1)
                stream.stop()
                stream.close()

            all_audio = np.concatenate(all_chunks) if all_chunks else np.array([], dtype=np.float32)
            duration = len(all_audio) / sample_rate if len(all_audio) > 0 else 0.0
            t_total = time.time() - t_start

            if is_rich:
                console.print(f"Done: {format_duration(duration)} audio ({t_total:.1f}s)")

        # Save to file
        duration = len(all_audio) / sample_rate if len(all_audio) > 0 else 0.0

        if output:
            from .audio import save_audio
            save_audio(all_audio, str(output), sample_rate)
            if is_rich:
                console.print(f"[dim]Saved: {output}[/dim]")
            audio_path = output
        else:
            safe_text = "".join(c for c in text[:30] if c.isalnum() or c == " ").strip().replace(" ", "_")
            audio_path = voices.get_generations_dir() / f"{safe_text}_{str(uuid.uuid4())[:8]}.wav"
            from .audio import save_audio
            save_audio(all_audio, str(audio_path), sample_rate)

        # History
        voices.add_generation(voice_obj.name, text, language, str(audio_path), duration, model, seed, instruct)

        # JSON output
        if is_json:
            output_result({
                "voice": voice_obj.name, "text": text, "duration": duration,
                "audio_path": str(audio_path), "streaming": not no_stream,
                "first_chunk_time": first_chunk_time if not no_stream else None,
            }, "generation")

    except typer.Exit:
        raise
    except KeyboardInterrupt:
        raise typer.Exit(130)
    except Exception as e:
        print_error(f"Say failed: {e}")
        raise typer.Exit(1)


# ============================================
# VOICE commands
# ============================================

voice_app = typer.Typer(help="Manage voices")

@voice_app.command("add")
def voice_add(
    audio: Path = typer.Argument(..., help="Audio file", exists=True),
    text: Optional[str] = typer.Option(None, "-t", "--text", help="Transcript (optional)"),
    voice: Optional[str] = typer.Option(None, "-v", "--voice", help="Voice name (default: use default)"),
    language: str = typer.Option("en", "-l", "--language", help="Language"),
):
    """Add audio sample to voice (creates if needed)."""
    try:
        voice = voice or get_settings().default_voice or "default"
        text = text or f"Sample from {audio.name}"

        if get_output_format() == OutputFormat.RICH:
            console.print(f"[dim]Voice: {voice} | Text: \"{text}\"[/dim]")

        # Get or create
        voice_obj = voices.get_voice(voice)
        is_new = voice_obj is None

        if is_new:
            voice_obj = voices.create_voice(voice, language, f"Created from {audio.name}")

        # Copy audio
        samples_dir = voices.get_samples_dir()
        voice_dir = samples_dir / voice_obj.id
        voice_dir.mkdir(parents=True, exist_ok=True)
        dest = voice_dir / f"{uuid.uuid4()}.wav"
        shutil.copy(audio, dest)

        # Add sample
        sample = voices.add_sample_to_voice(voice, str(dest), text)
        total = len(voices.get_voice(voice).samples)

        output_success(f"{'Created' if is_new else 'Added to'} '{voice}' ({total} samples)", sample.model_dump() if get_output_format() == OutputFormat.JSON else None)

    except Exception as e:
        output_error(str(e), "ERROR")
        raise typer.Exit(1)

@voice_app.command("list")
def voice_list():
    """List all voices."""
    vlist = voices.list_voices()

    if get_output_format() == OutputFormat.JSON:
        output_result([v.model_dump() for v in vlist], "voices")
    else:
        if not vlist:
            console.print("[yellow]No voices[/yellow]\nAdd: tts voice add audio.wav")
            return

        table = Table(title="Voices")
        table.add_column("Name", style="green")
        table.add_column("Language", style="yellow")
        table.add_column("Samples", style="cyan")
        table.add_column("Description")

        for v in vlist:
            table.add_row(v.name, v.language, str(len(v.samples)), v.description[:40] if v.description else "")

        console.print(table)

@voice_app.command("info")
def voice_info(voice: Optional[str] = typer.Argument(None, help="Voice name")):
    """Show voice details."""
    voice = voice or get_settings().default_voice or "default"

    v = voices.get_voice(voice)
    if not v:
        output_error(f"Voice not found: {voice}", "NOT_FOUND")
        raise typer.Exit(1)

    if get_output_format() == OutputFormat.JSON:
        output_result(v.model_dump(), "voice")
    else:
        console.print(f"\n[bold]Voice:[/bold] {v.name}")
        console.print(f"[bold]Language:[/bold] {v.language}")
        console.print(f"[bold]Samples:[/bold] {len(v.samples)}")
        if v.description:
            console.print(f"[bold]Description:[/bold] {v.description}")

        if v.samples:
            console.print(f"\n[bold]Sample files:[/bold]")
            for i, s in enumerate(v.samples, 1):
                console.print(f"  {i}. {Path(s.audio_path).name} - \"{s.text[:50]}...\"")

@voice_app.command("delete")
def voice_delete(voice: str = typer.Argument(...), yes: bool = typer.Option(False, "-y", "--yes")):
    """Delete a voice."""
    v = voices.get_voice(voice)
    if not v:
        output_error(f"Voice not found: {voice}", "NOT_FOUND")
        raise typer.Exit(1)

    if not yes and get_output_format() == OutputFormat.RICH:
        console.print(f"\n[yellow]Delete '{v.name}' ({len(v.samples)} samples)?[/yellow]")
        if not typer.confirm("Are you sure?"):
            console.print("Cancelled.")
            raise typer.Exit(0)

    voices.delete_voice(voice)
    output_success(f"Deleted '{v.name}'")

@voice_app.command("default")
def voice_default(voice: Optional[str] = typer.Argument(None), unset: bool = typer.Option(False, "--unset")):
    """Set/show default voice."""
    config_file = Path.home() / ".config" / "tts" / "config.toml"

    if unset:
        if config_file.exists():
            data = toml.load(config_file)
            data.pop('default_voice', None)
            config_file.write_text(toml.dumps(data))
        print_success("Default voice unset")
        reload_settings()
        return

    if not voice:
        settings = get_settings()
        if settings.default_voice:
            console.print(f"\n[bold]Default:[/bold] {settings.default_voice}")
            v = voices.get_voice(settings.default_voice)
            if v:
                console.print(f"[bold]Samples:[/bold] {len(v.samples)}")
        else:
            console.print("\n[yellow]No default set[/yellow]")
        return

    # Set default
    v = voices.get_voice(voice)
    if not v:
        output_error(f"Voice not found: {voice}", "NOT_FOUND")
        raise typer.Exit(1)

    config_file.parent.mkdir(parents=True, exist_ok=True)
    data = toml.load(config_file) if config_file.exists() else {}
    data['default_voice'] = v.name
    config_file.write_text(toml.dumps(data))

    print_success(f"Default voice: {v.name}")
    reload_settings()


# ============================================
# CONFIG commands
# ============================================

config_app = typer.Typer(help="Configuration")

@config_app.command("show")
def config_show():
    """Show configuration."""
    s = get_settings()

    table = Table(title="Configuration")
    table.add_column("Setting", style="cyan")
    table.add_column("Value")

    table.add_row("Data Directory", str(s.data_dir))
    table.add_row("Default Voice", s.default_voice or "(none)")
    table.add_row("Default Language", s.default_language)
    table.add_row("Default Model", s.default_model)
    table.add_row("Output Format", s.output_format)

    console.print(table)

    # Show config file locations
    console.print("\n[bold]Config files:[/bold]")
    for p in [Path.home() / ".config" / "tts" / "config.toml", Path.home() / ".tts" / "config.toml"]:
        exists = "[green]yes[/green]" if p.exists() else "[dim]no[/dim]"
        console.print(f"  {exists} {p}")

@config_app.command("set")
def config_set(key: str = typer.Argument(...), value: str = typer.Argument(...)):
    """Set configuration value."""
    valid = {"data_dir": str, "default_voice": str, "default_language": str, "default_model": str, "output_format": str, "auto_play": bool}

    if key not in valid:
        print_error(f"Invalid key. Valid: {', '.join(valid.keys())}")
        raise typer.Exit(1)

    # Convert bool
    if valid[key] == bool:
        value = value.lower() in ("true", "1", "yes")

    config_file = Path.home() / ".config" / "tts" / "config.toml"
    config_file.parent.mkdir(parents=True, exist_ok=True)

    data = toml.load(config_file) if config_file.exists() else {}
    data[key] = value
    config_file.write_text(toml.dumps(data))

    print_success(f"Set {key} = {value}")
    reload_settings()
