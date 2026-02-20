"""Tests for voice commands."""

import pytest
from typer.testing import CliRunner
from ttscli.cli import app
from ttscli import voices

runner = CliRunner()


def test_voice_add(temp_data_dir, sample_audio):
    """Test adding a sample creates a voice."""
    result = runner.invoke(
        app,
        ["voice", "add", str(sample_audio), "--voice", "TestVoice", "--text", "Hello world"],
    )
    assert result.exit_code == 0

    v = voices.get_voice("TestVoice")
    assert v is not None
    assert len(v.samples) == 1

    # cleanup
    voices.delete_voice("TestVoice")


def test_voice_add_default_name(temp_data_dir, sample_audio):
    """Test adding a sample without --voice uses default name."""
    result = runner.invoke(
        app,
        ["voice", "add", str(sample_audio), "--text", "Test"],
    )
    assert result.exit_code == 0

    # Should create or add to the default voice
    v = voices.get_voice("default")
    assert v is not None
    assert len(v.samples) >= 1

    voices.delete_voice("default")


def test_voice_list(temp_data_dir):
    """Test listing voices."""
    # Create a voice
    voices.create_voice("ListTest", "en", "A test voice")

    result = runner.invoke(app, ["voice", "list"])
    assert result.exit_code == 0
    assert "ListTest" in result.stdout

    voices.delete_voice("ListTest")


def test_voice_list_empty(temp_data_dir):
    """Test listing voices when none exist."""
    result = runner.invoke(app, ["voice", "list"])
    assert result.exit_code == 0


def test_voice_info(temp_data_dir, sample_audio):
    """Test getting voice info."""
    voices.create_voice("InfoTest", "en", "Test description")
    voices.add_sample_to_voice("InfoTest", str(sample_audio), "Hello")

    result = runner.invoke(app, ["voice", "info", "InfoTest"])
    assert result.exit_code == 0
    assert "InfoTest" in result.stdout

    voices.delete_voice("InfoTest")


def test_voice_info_not_found(temp_data_dir):
    """Test voice info for non-existent voice."""
    result = runner.invoke(app, ["voice", "info", "nonexistent_xyz"])
    assert result.exit_code == 1


def test_voice_delete(temp_data_dir):
    """Test deleting a voice."""
    voices.create_voice("DeleteMe", "en")

    result = runner.invoke(app, ["voice", "delete", "DeleteMe", "--yes"])
    assert result.exit_code == 0

    assert voices.get_voice("DeleteMe") is None


def test_voice_delete_not_found(temp_data_dir):
    """Test deleting a non-existent voice."""
    result = runner.invoke(app, ["voice", "delete", "nonexistent_xyz", "--yes"])
    assert result.exit_code == 1
