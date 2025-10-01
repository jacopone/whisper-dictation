"""
Tests for text pasting functionality
"""

from unittest.mock import patch

import pytest

from whisper_dictation.config import Config
from whisper_dictation.paste import TextPaster


@pytest.fixture
def config():
    """Create test configuration"""
    return Config()


@pytest.fixture
def paster(config):
    """Create TextPaster instance"""
    return TextPaster(config)


@patch("subprocess.run")
def test_paste_text(mock_run, paster):
    """Test pasting text via ydotool"""
    text = "Hello world"

    paster.paste(text)

    mock_run.assert_called_once()
    call_args = mock_run.call_args[0][0]

    assert "ydotool" in call_args
    assert "type" in call_args
    assert text in call_args


def test_paste_empty_text(paster):
    """Test pasting empty text does nothing"""
    with patch("subprocess.run") as mock_run:
        paster.paste("")

        mock_run.assert_not_called()


@patch("subprocess.run")
def test_paste_special_characters(mock_run, paster):
    """Test pasting text with special characters"""
    text = "Special: @#$%^&*()"

    paster.paste(text)

    mock_run.assert_called_once()
    call_args = mock_run.call_args[0][0]
    assert text in call_args
