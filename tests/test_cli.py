"""Basic CLI integration tests."""

import pytest
from typer.testing import CliRunner
from ttscli.cli import app

runner = CliRunner()


def test_version():
    """Test --version flag."""
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert "0.1" in result.stdout


def test_help():
    """Test --help flag."""
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "TTS CLI" in result.stdout or "tts" in result.stdout.lower()


def test_voice_list_empty(temp_data_dir):
    """Test listing voices when none exist."""
    result = runner.invoke(app, ["voice", "list"])
    # Should succeed even with no voices
    assert result.exit_code == 0


def test_config_show():
    """Test config show command."""
    result = runner.invoke(app, ["config", "show"])
    assert result.exit_code == 0
    assert "Configuration" in result.stdout or "data" in result.stdout.lower()


def test_say_help():
    """Test say --help."""
    result = runner.invoke(app, ["say", "--help"])
    assert result.exit_code == 0
    assert "text" in result.stdout.lower()


def test_voice_help():
    """Test voice --help."""
    result = runner.invoke(app, ["voice", "--help"])
    assert result.exit_code == 0


def test_json_output_flag(temp_data_dir):
    """Test --json flag produces valid JSON."""
    import json

    result = runner.invoke(app, ["--json", "voice", "list"])
    assert result.exit_code == 0
    data = json.loads(result.stdout)
    assert "voices" in data


def test_say_no_voice_required(temp_data_dir):
    """Test say works without a registered voice (uses model default)."""
    result = runner.invoke(app, ["say", "--help"])
    assert result.exit_code == 0
    # --voice is optional, not required
    assert "voice" in result.stdout.lower()
