"""
Tests for configuration management
"""

from pathlib import Path

from whisper_dictation.config import Config


def test_default_config_creation(tmp_path):
    """Test that default config is created if file doesn't exist"""
    config_path = tmp_path / "config.yaml"
    config = Config(config_path)

    assert config_path.exists()
    assert config.get("whisper.model") == "medium"
    assert config.get("hotkey.key") == "period"


def test_config_loading(tmp_path):
    """Test loading existing config file"""
    config_path = tmp_path / "config.yaml"
    config_path.write_text(
        """
hotkey:
  key: comma
  modifiers: [ctrl, alt]
whisper:
  model: large
  language: es
"""
    )

    config = Config(config_path)

    assert config.get("hotkey.key") == "comma"
    assert config.get("whisper.model") == "large"
    assert config.get("whisper.language") == "es"


def test_hotkey_display():
    """Test hotkey display string generation"""
    config = Config()

    display = config.get_hotkey_display()

    assert "Super" in display
    assert "Period" in display


def test_model_path():
    """Test model path resolution"""
    config = Config()

    model_path = config.get_model_path()

    assert isinstance(model_path, Path)
    # Config now uses base model (changed for speed optimization)
    assert "ggml-base.bin" in str(model_path)


def test_config_get_with_default():
    """Test get method with default value"""
    config = Config()

    assert config.get("nonexistent.key", "default") == "default"
    # Config now uses base model (changed for speed optimization)
    assert config.get("whisper.model") == "base"
