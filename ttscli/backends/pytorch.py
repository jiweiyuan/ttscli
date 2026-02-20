"""PyTorch backend for TTS using Qwen3-TTS."""

from typing import Optional, List, Tuple
import asyncio
import hashlib
import torch
import numpy as np
from pathlib import Path


# Simple in-memory voice prompt cache
_prompt_cache: dict[str, dict] = {}


def _cache_key(audio_path: str, text: str) -> str:
    with open(audio_path, "rb") as f:
        return hashlib.md5(f.read() + text.encode()).hexdigest()


class PyTorchTTSBackend:
    """PyTorch-based TTS backend using Qwen3-TTS."""

    def __init__(self, model_size: str = "1.7B"):
        self.model = None
        self.model_size = model_size
        self._current_model_size = None
        self.device = self._get_device()

    def _get_device(self) -> str:
        if torch.cuda.is_available():
            return "cuda"
        return "cpu"

    def is_loaded(self) -> bool:
        return self.model is not None

    def _get_model_path(self, model_size: str) -> str:
        models = {
            "1.7B": "Qwen/Qwen3-TTS-12Hz-1.7B-Base",
            "0.6B": "Qwen/Qwen3-TTS-12Hz-0.6B-Base",
        }
        if model_size not in models:
            raise ValueError(f"Unknown model size: {model_size}")
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
        from qwen_tts import Qwen3TTSModel

        model_path = self._get_model_path(model_size)
        print(f"Loading TTS model {model_size} on {self.device}...")

        self.model = Qwen3TTSModel.from_pretrained(
            model_path,
            device_map=self.device,
            torch_dtype=torch.float32 if self.device == "cpu" else torch.bfloat16,
        )
        self._current_model_size = model_size
        self.model_size = model_size
        print(f"TTS model {model_size} loaded successfully")

    def unload_model(self):
        if self.model is not None:
            del self.model
            self.model = None
            self._current_model_size = None
            if torch.cuda.is_available():
                torch.cuda.empty_cache()

    async def create_voice_prompt(
        self, audio_path: str, reference_text: str, use_cache: bool = True,
    ) -> Tuple[dict, bool]:
        await self.load_model_async(None)

        if use_cache:
            key = _cache_key(audio_path, reference_text)
            if key in _prompt_cache:
                return _prompt_cache[key], True

        def _sync():
            return self.model.create_voice_clone_prompt(
                ref_audio=str(audio_path),
                ref_text=reference_text,
                x_vector_only_mode=False,
            )

        prompt = await asyncio.to_thread(_sync)

        if use_cache:
            _prompt_cache[_cache_key(audio_path, reference_text)] = prompt

        return prompt, False

    async def generate(
        self, text: str, voice_prompt: dict,
        language: str = "en", seed: Optional[int] = None, instruct: Optional[str] = None,
    ) -> Tuple[np.ndarray, int]:
        await self.load_model_async(None)

        def _sync():
            if seed is not None:
                torch.manual_seed(seed)
                if torch.cuda.is_available():
                    torch.cuda.manual_seed(seed)

            wavs, sample_rate = self.model.generate_voice_clone(
                text=text, voice_clone_prompt=voice_prompt, instruct=instruct,
            )
            return wavs[0], sample_rate

        return await asyncio.to_thread(_sync)

    async def generate_stream(
        self, text: str, voice_prompt: dict,
        language: str = "en", seed: Optional[int] = None, instruct: Optional[str] = None,
    ):
        """Yield (chunk, sample_rate, is_final) tuples.

        If the model supports native streaming, use it. Otherwise fall back
        to generating all audio at once and yielding it as a single chunk.
        """
        await self.load_model_async(None)

        has_streaming = hasattr(self.model, "generate_voice_clone_streaming")

        if has_streaming:
            import queue, threading

            q = queue.Queue()
            DONE = object()

            def _produce():
                if seed is not None:
                    torch.manual_seed(seed)
                    if torch.cuda.is_available():
                        torch.cuda.manual_seed(seed)
                try:
                    for chunk, sr in self.model.generate_voice_clone_streaming(
                        text=text, voice_clone_prompt=voice_prompt, instruct=instruct,
                    ):
                        q.put((np.asarray(chunk, dtype=np.float32), sr))
                except Exception as e:
                    print(f"Streaming error: {e}")
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
                is_final = not q.empty() and q.queue[0] is DONE
                yield chunk, sr, is_final

            t.join(timeout=5.0)
        else:
            audio, sr = await self.generate(text, voice_prompt, language, seed, instruct)
            yield audio, sr, True


class PyTorchSTTBackend:
    """PyTorch-based STT backend using Whisper."""

    def __init__(self, model_size: str = "base"):
        self.model = None
        self.processor = None
        self.model_size = model_size
        self.device = "cuda" if torch.cuda.is_available() else "cpu"

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
        from transformers import WhisperProcessor, WhisperForConditionalGeneration

        name = f"openai/whisper-{model_size}"
        print(f"Loading Whisper {model_size} on {self.device}...")
        self.processor = WhisperProcessor.from_pretrained(name)
        self.model = WhisperForConditionalGeneration.from_pretrained(name)
        self.model.to(self.device)
        self.model_size = model_size
        print(f"Whisper {model_size} loaded")

    def unload_model(self):
        if self.model is not None:
            del self.model
            del self.processor
            self.model = None
            self.processor = None
            if torch.cuda.is_available():
                torch.cuda.empty_cache()

    async def transcribe(self, audio_path: str, language: Optional[str] = None) -> str:
        await self.load_model_async(None)

        def _sync():
            import librosa
            audio, _ = librosa.load(audio_path, sr=16000, mono=True)

            inputs = self.processor(audio, sampling_rate=16000, return_tensors="pt").to(self.device)

            forced = None
            if language:
                forced = self.processor.get_decoder_prompt_ids(language=language, task="transcribe")

            with torch.no_grad():
                ids = self.model.generate(inputs["input_features"], forced_decoder_ids=forced)

            return self.processor.batch_decode(ids, skip_special_tokens=True)[0].strip()

        return await asyncio.to_thread(_sync)
