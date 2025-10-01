"""
Tests for audio recording functionality
"""

from unittest.mock import MagicMock, patch

import pytest

from whisper_dictation.config import Config
from whisper_dictation.recorder import AudioRecorder


@pytest.fixture
def config():
    """Create test configuration"""
    return Config()


@pytest.fixture
def recorder(config):
    """Create AudioRecorder instance"""
    return AudioRecorder(config)


def test_recorder_initialization(recorder):
    """Test recorder initializes correctly"""
    assert recorder.temp_dir.exists()
    assert recorder.audio_file.parent == recorder.temp_dir
    assert recorder.process is None


@patch("subprocess.Popen")
def test_start_recording(mock_popen, recorder):
    """Test starting audio recording"""
    mock_process = MagicMock()
    mock_popen.return_value = mock_process

    recorder.start()

    assert recorder.process == mock_process
    mock_popen.assert_called_once()

    # Verify ffmpeg command
    call_args = mock_popen.call_args[0][0]
    assert "ffmpeg" in call_args
    assert "-f" in call_args
    assert "pulse" in call_args


@patch("subprocess.Popen")
def test_stop_recording(mock_popen, recorder, tmp_path):
    """Test stopping audio recording"""
    # Create fake audio file
    audio_file = tmp_path / "recording.wav"
    audio_file.write_bytes(b"fake audio data" * 1000)  # Make it substantial
    recorder.audio_file = audio_file

    # Mock process
    mock_process = MagicMock()
    mock_process.wait = MagicMock()
    recorder.process = mock_process

    result = recorder.stop()

    mock_process.terminate.assert_called_once()
    mock_process.wait.assert_called()
    assert result == audio_file
    assert recorder.process is None


def test_stop_without_start(recorder):
    """Test stopping recording that was never started"""
    result = recorder.stop()

    assert result is None


@patch("subprocess.Popen")
def test_stop_with_empty_file(mock_popen, recorder, tmp_path):
    """Test stopping recording that produced empty file"""
    audio_file = tmp_path / "recording.wav"
    audio_file.write_bytes(b"")  # Empty file
    recorder.audio_file = audio_file

    mock_process = MagicMock()
    recorder.process = mock_process

    result = recorder.stop()

    # Should return None for empty file
    assert result is None
