"""Performance tests for TTS CLI."""

import pytest
import time
import json
from typer.testing import CliRunner

from ttscli.cli import app


@pytest.fixture
def runner():
    """CLI test runner."""
    return CliRunner()


class TestCommandStartup:
    """Test command startup performance."""

    def test_help_command_speed(self, runner):
        """Test that help command responds quickly."""
        start = time.time()
        result = runner.invoke(app, ["--help"])
        elapsed = time.time() - start

        assert result.exit_code == 0
        assert elapsed < 1.0, f"Help command took {elapsed:.3f}s (should be < 1s)"

    def test_version_command_speed(self, runner):
        """Test that version command responds quickly."""
        start = time.time()
        result = runner.invoke(app, ["--version"])
        elapsed = time.time() - start

        assert result.exit_code == 0
        assert elapsed < 0.5, f"Version command took {elapsed:.3f}s (should be < 0.5s)"


class TestJSONOutput:
    """Test JSON output correctness."""

    def test_voice_list_json_structure(self, runner, temp_data_dir):
        """Test JSON output has correct structure."""
        from ttscli import voices

        voices.create_voice("PerfTest1", "en", "Test voice 1")
        voices.create_voice("PerfTest2", "en", "Test voice 2")

        result = runner.invoke(app, ["--output", "json", "voice", "list"])
        assert result.exit_code == 0

        data = json.loads(result.stdout)
        assert "voices" in data
        assert len(data["voices"]) >= 2

        voice = data["voices"][0]
        assert "id" in voice
        assert "name" in voice
        assert "language" in voice

        voices.delete_voice("PerfTest1")
        voices.delete_voice("PerfTest2")

    def test_json_alias_flag(self, runner, temp_data_dir):
        """Test --json alias works same as --output json."""
        result1 = runner.invoke(app, ["--output", "json", "voice", "list"])
        result2 = runner.invoke(app, ["--json", "voice", "list"])

        assert result1.exit_code == 0
        assert result2.exit_code == 0

        data1 = json.loads(result1.stdout)
        data2 = json.loads(result2.stdout)

        assert "voices" in data1
        assert "voices" in data2


class TestJSONvsRichSpeed:
    """Compare JSON and Rich output performance."""

    def test_voice_list_json_vs_rich(self, runner, temp_data_dir):
        """Compare JSON vs Rich output speed."""
        from ttscli import voices

        for i in range(10):
            voices.create_voice(f"SpeedTest{i}", "en", f"Voice {i}")

        start = time.time()
        result_json = runner.invoke(app, ["--output", "json", "voice", "list"])
        json_time = time.time() - start

        start = time.time()
        result_rich = runner.invoke(app, ["voice", "list"])
        rich_time = time.time() - start

        assert result_json.exit_code == 0
        assert result_rich.exit_code == 0
        assert json_time < 2.0, f"JSON output too slow: {json_time:.4f}s"
        assert rich_time < 2.0, f"Rich output too slow: {rich_time:.4f}s"

        for i in range(10):
            voices.delete_voice(f"SpeedTest{i}")
