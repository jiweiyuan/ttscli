"""Basic CLI integration tests."""

import pytest
from typer.testing import CliRunner
from ttscli.cli import app

runner = CliRunner()


def test_version():
    """Test --version flag."""
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert "version" in result.stdout.lower()


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


def test_output_json_flag(temp_data_dir):
    """Test --output json flag produces valid JSON."""
    import json

    result = runner.invoke(app, ["--output", "json", "voice", "list"])
    assert result.exit_code == 0
    data = json.loads(result.stdout)
    assert "voices" in data
