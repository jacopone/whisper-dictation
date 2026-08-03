"""
Tests for whisper transcription
"""

from unittest.mock import MagicMock, patch

import pytest

from whisper_dictation.config import Config
from whisper_dictation.transcriber import WhisperTranscriber


@pytest.fixture
def config(tmp_path):
    """Create test configuration"""
    return Config(tmp_path / "config.yaml")


@pytest.fixture
def transcriber(config, tmp_path):
    """Create transcriber with a fake model file, keeping temp files in tmp_path"""
    with patch("whisper_dictation.transcriber.Path.mkdir"):
        t = WhisperTranscriber(config)
    t.temp_dir = tmp_path
    model_path = tmp_path / "ggml-test.bin"
    model_path.touch()
    t.model_path = model_path
    return t


def _run_transcribe(transcriber, tmp_path):
    """Run transcribe with subprocess mocked, return whisper-cli argv"""
    audio_file = tmp_path / "audio.wav"
    audio_file.touch()

    with patch("whisper_dictation.transcriber.subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=0)
        transcriber.transcribe(audio_file)
        return mock_run.call_args[0][0]


def test_gpu_enabled_by_default(transcriber, tmp_path):
    """No --no-gpu flag when use_gpu is enabled (default)"""
    cmd = _run_transcribe(transcriber, tmp_path)

    assert "--no-gpu" not in cmd


def test_gpu_disabled_via_config(transcriber, tmp_path):
    """--no-gpu flag passed when use_gpu is false"""
    transcriber.config.config["whisper"]["use_gpu"] = False

    cmd = _run_transcribe(transcriber, tmp_path)

    assert "--no-gpu" in cmd
