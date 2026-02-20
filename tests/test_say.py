"""Tests for the 'say' command with streaming playback."""

import asyncio
import numpy as np
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from pathlib import Path
from click.exceptions import Exit as ClickExit




class TestGenerateStream:
    """Test the streaming generation interface."""

    @pytest.mark.asyncio
    async def test_mlx_generate_stream_yields_chunks(self):
        from ttscli.backends.mlx import MLXTTSBackend

        backend = MLXTTSBackend()
        results = []
        for _ in range(3):
            r = MagicMock()
            r.audio = np.random.randn(2400).astype(np.float32)
            r.sample_rate = 24000
            results.append(r)

        backend.model = MagicMock()
        backend.model.generate = MagicMock(return_value=iter(results))
        backend._current_model_size = "1.7B"

        chunks = []
        async for chunk, sr, is_final in backend.generate_stream(
            text="Hello", voice_prompt={"ref_audio": "/tmp/f.wav", "ref_text": "x"},
        ):
            chunks.append((chunk, sr, is_final))

        assert len(chunks) == 3
        for c, sr, _ in chunks:
            assert sr == 24000
            assert isinstance(c, np.ndarray)
            assert len(c) == 2400

    @pytest.mark.asyncio
    async def test_mlx_generate_stream_single_chunk(self):
        from ttscli.backends.mlx import MLXTTSBackend

        backend = MLXTTSBackend()
        r = MagicMock()
        r.audio = np.random.randn(4800).astype(np.float32)
        r.sample_rate = 24000

        backend.model = MagicMock()
        backend.model.generate = MagicMock(return_value=iter([r]))
        backend._current_model_size = "1.7B"

        chunks = []
        async for chunk, sr, _ in backend.generate_stream(
            text="Hi", voice_prompt={"ref_audio": "/tmp/f.wav", "ref_text": "x"},
        ):
            chunks.append((chunk, sr))

        assert len(chunks) == 1
        assert len(chunks[0][0]) == 4800

    @pytest.mark.asyncio
    async def test_pytorch_generate_stream_fallback(self):
        from ttscli.backends.pytorch import PyTorchTTSBackend

        backend = PyTorchTTSBackend()
        full_audio = np.random.randn(48000).astype(np.float32)

        class FakeModel:
            def generate_voice_clone(self, text, voice_clone_prompt, instruct=None):
                pass

        mock = MagicMock(spec=FakeModel)
        mock.generate_voice_clone = MagicMock(return_value=([full_audio], 24000))
        backend.model = mock
        backend._current_model_size = "1.7B"

        chunks = []
        async for chunk, sr, is_final in backend.generate_stream(
            text="Hello", voice_prompt={"prompt": "fake"},
        ):
            chunks.append((chunk, sr, is_final))

        assert len(chunks) == 1
        assert chunks[0][1] == 24000
        assert chunks[0][2] is True
        np.testing.assert_array_equal(chunks[0][0], full_audio)


class TestSayCommand:

    @pytest.mark.asyncio
    async def test_say_no_voice_errors(self):
        from ttscli.commands import _async_say

        with pytest.raises((SystemExit, ClickExit)):
            await _async_say(
                text="Hello", voice="nonexistent_xyz_99",
                language=None, model="1.7B", output=None,
                seed=None, instruct=None, no_play=False, no_stream=False,
            )

    @pytest.mark.asyncio
    async def test_say_no_stream_with_mock_backend(self):
        from ttscli.commands import _async_say
        from ttscli import voices
        import tempfile, soundfile as sf

        try:
            voices.delete_voice("_test_say_ns")
        except Exception:
            pass

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            sf.write(f.name, np.random.randn(48000).astype(np.float32) * 0.1, 24000)
            tmp = f.name

        try:
            voices.create_voice("_test_say_ns", language="en")
            voices.add_sample_to_voice("_test_say_ns", tmp, "Test")

            audio = np.random.randn(24000).astype(np.float32) * 0.1
            mock_be = AsyncMock()
            mock_be.load_model = AsyncMock()
            mock_be.create_voice_prompt = AsyncMock(return_value=({"ref": "x"}, False))
            mock_be.generate = AsyncMock(return_value=(audio, 24000))

            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as out:
                out_path = Path(out.name)

            try:
                with patch("ttscli.commands.get_tts_backend", return_value=mock_be), \
                     patch("ttscli.commands._get_sounddevice", return_value=MagicMock()):
                    await _async_say(
                        text="Hello", voice="_test_say_ns", language=None,
                        model="1.7B", output=out_path, seed=None,
                        instruct=None, no_play=False, no_stream=True,
                    )

                assert out_path.exists()
                info = sf.info(str(out_path))
                assert info.samplerate == 24000
                assert info.frames == 24000

                mock_be.load_model.assert_awaited_once()
                mock_be.generate.assert_awaited_once()
            finally:
                out_path.unlink(missing_ok=True)
        finally:
            voices.delete_voice("_test_say_ns")
            Path(tmp).unlink(missing_ok=True)

    @pytest.mark.asyncio
    async def test_say_streaming_with_mock_backend(self):
        from ttscli.commands import _async_say
        from ttscli import voices
        import tempfile, soundfile as sf

        try:
            voices.delete_voice("_test_say_st")
        except Exception:
            pass

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            sf.write(f.name, np.random.randn(48000).astype(np.float32) * 0.1, 24000)
            tmp = f.name

        try:
            voices.create_voice("_test_say_st", language="en")
            voices.add_sample_to_voice("_test_say_st", tmp, "Test")

            c1 = np.random.randn(12000).astype(np.float32) * 0.1
            c2 = np.random.randn(12000).astype(np.float32) * 0.1

            mock_be = AsyncMock()
            mock_be.load_model = AsyncMock()
            mock_be.create_voice_prompt = AsyncMock(return_value=({"ref": "x"}, False))

            async def mock_stream(*a, **kw):
                yield c1, 24000, False
                yield c2, 24000, True
            mock_be.generate_stream = mock_stream

            mock_sd = MagicMock()
            mock_os = MagicMock()
            mock_sd.OutputStream = MagicMock(return_value=mock_os)

            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as out:
                out_path = Path(out.name)

            try:
                with patch("ttscli.commands.get_tts_backend", return_value=mock_be), \
                     patch("ttscli.commands._get_sounddevice", return_value=mock_sd):
                    await _async_say(
                        text="Hello", voice="_test_say_st", language=None,
                        model="1.7B", output=out_path, seed=None,
                        instruct=None, no_play=False, no_stream=False,
                    )

                assert out_path.exists()
                data, sr = sf.read(str(out_path))
                assert sr == 24000
                assert len(data) == 24000  # 12000 + 12000

                mock_sd.OutputStream.assert_called_once()
                mock_os.start.assert_called_once()
                mock_os.stop.assert_called_once()
                mock_os.close.assert_called_once()
            finally:
                out_path.unlink(missing_ok=True)
        finally:
            voices.delete_voice("_test_say_st")
            Path(tmp).unlink(missing_ok=True)


class TestStreamingBridge:

    @pytest.mark.asyncio
    async def test_queue_bridge_delivers_in_order(self):
        import queue, threading

        q = queue.Queue()
        DONE = object()
        expected = [np.ones(100, dtype=np.float32) * i for i in range(5)]

        def producer():
            import time
            for c in expected:
                q.put((c, 24000))
                time.sleep(0.01)
            q.put(DONE)

        t = threading.Thread(target=producer, daemon=True)
        t.start()

        got = []
        while True:
            while q.empty():
                await asyncio.sleep(0.005)
            item = q.get()
            if item is DONE:
                break
            got.append(item[0])

        t.join(timeout=2)
        assert len(got) == 5
        for i, c in enumerate(got):
            np.testing.assert_array_equal(c, expected[i])

    @pytest.mark.asyncio
    async def test_queue_bridge_single_chunk(self):
        import queue, threading

        q = queue.Queue()
        DONE = object()

        def producer():
            q.put((np.ones(100, dtype=np.float32), 24000))
            q.put(DONE)

        t = threading.Thread(target=producer, daemon=True)
        t.start()

        got = []
        while True:
            while q.empty():
                await asyncio.sleep(0.005)
            item = q.get()
            if item is DONE:
                break
            got.append(item[0])

        t.join(timeout=2)
        assert len(got) == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
