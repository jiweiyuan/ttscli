"""MLX backend for TTS using mlx-audio (optimized for Apple Silicon)."""

from typing import Optional, List, Tuple
import asyncio
import hashlib
import io
import os
import sys
import time
import warnings
import numpy as np
from pathlib import Path


# Simple in-memory voice prompt cache
_prompt_cache: dict[str, dict] = {}

# Default streaming interval (seconds per chunk)
STREAMING_INTERVAL = 2.0


def _cache_key(audio_path: str, text: str) -> str:
    with open(audio_path, "rb") as f:
        return hashlib.md5(f.read() + text.encode()).hexdigest()


def _suppress_library_noise():
    """Suppress noisy warnings from transformers/tokenizers/mlx_audio."""
    os.environ["TOKENIZERS_PARALLELISM"] = "false"
    warnings.filterwarnings("ignore", message=".*incorrect regex pattern.*")
    warnings.filterwarnings("ignore", message=".*model of type.*to instantiate.*")
    warnings.filterwarnings("ignore", message=".*not supported for all configurations.*")
    # Suppress transformers logging
    try:
        import logging
        logging.getLogger("transformers").setLevel(logging.ERROR)
        logging.getLogger("huggingface_hub").setLevel(logging.ERROR)
    except Exception:
        pass


class _QuietOutput:
    """Context manager to suppress stdout/stderr including C-level output."""
    def __enter__(self):
        os.environ["HF_HUB_DISABLE_PROGRESS_BARS"] = "1"
        # Save Python-level streams
        self._old_out = sys.stdout
        self._old_err = sys.stderr
        sys.stdout = io.StringIO()
        sys.stderr = io.StringIO()
        # Save and redirect OS-level file descriptors
        try:
            self._devnull = open(os.devnull, "w")
            self._orig_fd_out = os.dup(1)
            self._orig_fd_err = os.dup(2)
            os.dup2(self._devnull.fileno(), 1)
            os.dup2(self._devnull.fileno(), 2)
            self._fd_redirected = True
        except Exception:
            self._fd_redirected = False
        return self

    def __exit__(self, *args):
        # Restore OS-level file descriptors
        if self._fd_redirected:
            os.dup2(self._orig_fd_out, 1)
            os.dup2(self._orig_fd_err, 2)
            os.close(self._orig_fd_out)
            os.close(self._orig_fd_err)
            self._devnull.close()
        # Restore Python-level streams
        sys.stdout = self._old_out
        sys.stderr = self._old_err
        os.environ.pop("HF_HUB_DISABLE_PROGRESS_BARS", None)


class MLXTTSBackend:
    """MLX-based TTS backend using mlx-audio (Apple Silicon accelerated)."""

    # Set to True for verbose output (e.g. during `tts init`)
    verbose = False

    def __init__(self, model_size: str = "0.6B"):
        self.model = None
        self.model_size = model_size
        self._current_model_size = None
        self._warmed_up = False

    def is_loaded(self) -> bool:
        return self.model is not None

    def _get_model_path(self, model_size: str) -> str:
        """Get the MLX-community model path for a given size."""
        models = {
            "0.6B": "mlx-community/Qwen3-TTS-12Hz-0.6B-Base-4bit",
            "1.7B": "mlx-community/Qwen3-TTS-12Hz-1.7B-Base-8bit",
        }
        if model_size not in models:
            return model_size
        return models[model_size]

    async def load_model_async(self, model_size: Optional[str] = None):
        if model_size is None:
            model_size = self.model_size
        if self.model is not None and self._current_model_size == model_size:
            return
        if self.model is not None:
            self.unload_model()
        await asyncio.to_thread(self._load_model_sync, model_size)

    load_model = load_model_async

    def _load_model_sync(self, model_size: str):
        import logging
        import warnings as _w

        _suppress_library_noise()
        model_path = self._get_model_path(model_size)

        # Silence everything during model load
        _w.filterwarnings("ignore")
        logging.disable(logging.CRITICAL)
        try:
            from mlx_audio.tts.utils import load_model
            with _QuietOutput():
                self.model = load_model(model_path)
        finally:
            logging.disable(logging.NOTSET)
            _w.resetwarnings()

        self._current_model_size = model_size
        self.model_size = model_size
        self._warmed_up = False

    def _warmup(self):
        """Run a short generation to trigger MLX JIT compilation."""
        if self._warmed_up or self.model is None:
            return
        try:
            with _QuietOutput():
                for _ in self.model.generate(
                    text="Hello.",
                    stream=True,
                    streaming_interval=STREAMING_INTERVAL,
                    verbose=False,
                    max_tokens=20,
                ):
                    pass
        except Exception:
            pass
        self._warmed_up = True

    @property
    def sample_rate(self) -> int:
        return self.model.sample_rate if self.model else 24000

    def unload_model(self):
        if self.model is not None:
            del self.model
            self.model = None
            self._current_model_size = None
            self._warmed_up = False
            try:
                import mlx.core as mx
                mx.clear_cache()
            except Exception:
                pass

    async def create_voice_prompt(
        self, audio_path: str, reference_text: str, use_cache: bool = True,
    ) -> Tuple[dict, bool]:
        await self.load_model_async(None)

        if use_cache:
            key = _cache_key(audio_path, reference_text)
            if key in _prompt_cache:
                cached = _prompt_cache[key]
                ref = cached.get("ref_audio")
                if ref and Path(ref).exists():
                    return cached, True

        prompt = {"ref_audio": str(audio_path), "ref_text": reference_text}

        if use_cache:
            _prompt_cache[_cache_key(audio_path, reference_text)] = prompt

        return prompt, False

    async def combine_voice_prompts(
        self,
        audio_paths: List[str],
        reference_texts: List[str],
    ) -> Tuple[np.ndarray, str]:
        if not audio_paths:
            raise ValueError("No audio paths provided")
        combined_text = " ".join(reference_texts)
        return audio_paths[0], combined_text

    async def generate(
        self, text: str, voice_prompt: dict,
        language: str = "en", seed: Optional[int] = None, instruct: Optional[str] = None,
    ) -> Tuple[np.ndarray, int]:
        await self.load_model_async(None)

        def _sync():
            self._warmup()

            audio_chunks = []
            sr = self.sample_rate

            if seed is not None:
                import mlx.core as mx
                np.random.seed(seed)
                mx.random.seed(seed)

            ref_audio = voice_prompt.get("ref_audio")
            ref_text = voice_prompt.get("ref_text", "")
            if ref_audio and not Path(ref_audio).exists():
                ref_audio = None

            gen_kwargs = dict(text=text, verbose=False, max_tokens=4096)
            if ref_audio:
                gen_kwargs["ref_audio"] = ref_audio
                gen_kwargs["ref_text"] = ref_text
            if instruct:
                gen_kwargs["instruct"] = instruct

            for result in self.model.generate(**gen_kwargs):
                audio_chunks.append(np.array(result.audio))
                sr = result.sample_rate

            if audio_chunks:
                return np.concatenate([c.astype(np.float32) for c in audio_chunks]), sr
            return np.array([], dtype=np.float32), sr

        return await asyncio.to_thread(_sync)

    async def generate_stream(
        self, text: str, voice_prompt: dict,
        language: str = "en", seed: Optional[int] = None, instruct: Optional[str] = None,
    ):
        """Yield (chunk, sample_rate, is_final) as model generates."""
        await self.load_model_async(None)

        import queue, threading

        q: queue.Queue = queue.Queue()
        DONE = object()

        def _produce():
            self._warmup()

            if seed is not None:
                import mlx.core as mx
                np.random.seed(seed)
                mx.random.seed(seed)

            ref_audio = voice_prompt.get("ref_audio")
            ref_text = voice_prompt.get("ref_text", "")
            if ref_audio and not Path(ref_audio).exists():
                ref_audio = None

            gen_kwargs = dict(
                text=text, stream=True,
                streaming_interval=STREAMING_INTERVAL,
                verbose=False, max_tokens=4096,
            )
            if ref_audio:
                gen_kwargs["ref_audio"] = ref_audio
                gen_kwargs["ref_text"] = ref_text
            if instruct:
                gen_kwargs["instruct"] = instruct

            try:
                for result in self.model.generate(**gen_kwargs):
                    audio = np.asarray(result.audio, dtype=np.float32)
                    if len(audio) > 0:
                        q.put((audio, result.sample_rate))
            except Exception:
                pass
            q.put(DONE)

        t = threading.Thread(target=_produce, daemon=True)
        t.start()

        while True:
            while q.empty():
                await asyncio.sleep(0.01)
            item = q.get()
            if item is DONE:
                break
            chunk, sr = item
            is_final = False
            try:
                is_final = not q.empty() and q.queue[0] is DONE
            except (IndexError, AttributeError):
                pass
            yield chunk, sr, is_final

        t.join(timeout=5.0)


class MLXSTTBackend:
    """MLX-based STT backend using mlx-audio Whisper."""

    def __init__(self, model_size: str = "base"):
        self.model = None
        self.model_size = model_size

    def is_loaded(self) -> bool:
        return self.model is not None

    async def load_model_async(self, model_size: Optional[str] = None):
        if model_size is None:
            model_size = self.model_size
        if self.model is not None and self.model_size == model_size:
            return
        await asyncio.to_thread(self._load_sync, model_size)

    load_model = load_model_async

    def _load_sync(self, model_size: str):
        _suppress_library_noise()
        from mlx_audio.stt import load
        with _QuietOutput():
            self.model = load(f"openai/whisper-{model_size}")
        self.model_size = model_size

    def unload_model(self):
        if self.model is not None:
            del self.model
            self.model = None

    async def transcribe(self, audio_path: str, language: Optional[str] = None) -> str:
        await self.load_model_async(None)

        def _sync():
            opts = {}
            if language:
                opts["language"] = language
            result = self.model.generate(str(audio_path), **opts)
            if isinstance(result, str):
                return result.strip()
            if isinstance(result, dict):
                return result.get("text", "").strip()
            if hasattr(result, "text"):
                return result.text.strip()
            return str(result).strip()

        return await asyncio.to_thread(_sync)
