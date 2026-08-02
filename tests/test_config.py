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


def test_hotkey_display(tmp_path):
    """Test hotkey display string generation"""
    # Use valid config path to avoid loading from ~/.config
    config_path = tmp_path / "config.yaml"
    config = Config(config_path)

    display = config.get_hotkey_display()

    assert "Super" in display
    assert "Period" in display


def test_model_path(tmp_path):
    """Test model path resolution"""
    config = Config(tmp_path / "config.yaml")

    model_path = config.get_model_path()

    assert isinstance(model_path, Path)
    assert "ggml-medium.bin" in str(model_path)


def test_config_get_with_default(tmp_path):
    """Test get method with default value"""
    config = Config(tmp_path / "config.yaml")

    assert config.get("nonexistent.key", "default") == "default"
    assert config.get("whisper.model") == "medium"


def test_use_gpu_default(tmp_path):
    """Test that GPU use defaults to enabled"""
    config_path = tmp_path / "config.yaml"
    config = Config(config_path)

    assert config.get("whisper.use_gpu") is True


def test_repo_config_yaml_matches_defaults():
    """The reference config.yaml in the repo must stay in sync with DEFAULT_CONFIG"""
    import yaml

    repo_config = Path(__file__).parent.parent / "config.yaml"

    assert repo_config.exists(), "config.yaml missing from repository root"

    with open(repo_config) as f:
        documented = yaml.safe_load(f)

    assert documented == Config.DEFAULT_CONFIG
