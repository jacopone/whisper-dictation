"""
Configuration management for whisper-dictation
"""

from pathlib import Path
from typing import Any

import yaml
from evdev import ecodes


class Config:
    """Manages configuration with sensible defaults"""

    DEFAULT_CONFIG = {
        "hotkey": {"modifiers": ["super"], "key": "period"},  # super, ctrl, alt, shift
        "whisper": {"model": "medium", "language": "en", "threads": 4},
        "ui": {"show_waveform": False, "theme": "dark"},  # Not implemented yet
        "processing": {
            "remove_filler_words": True,
            "auto_capitalize": True,
            "auto_punctuate": False,
        },
    }

    # Map modifier names to ecodes
    MODIFIER_MAP = {
        "super": [ecodes.KEY_LEFTMETA, ecodes.KEY_RIGHTMETA],
        "ctrl": [ecodes.KEY_LEFTCTRL, ecodes.KEY_RIGHTCTRL],
        "alt": [ecodes.KEY_LEFTALT, ecodes.KEY_RIGHTALT],
        "shift": [ecodes.KEY_LEFTSHIFT, ecodes.KEY_RIGHTSHIFT],
    }

    # Map key names to ecodes
    KEY_MAP = {
        "period": ecodes.KEY_DOT,
        "comma": ecodes.KEY_COMMA,
        "space": ecodes.KEY_SPACE,
        "slash": ecodes.KEY_SLASH,
        "semicolon": ecodes.KEY_SEMICOLON,
        # Add more as needed
    }

    def __init__(self, config_path: Path = None):
        self.config_path = config_path or Path.home() / ".config/whisper-dictation/config.yaml"
        self.config = self._load_config()

    def _load_config(self) -> dict[str, Any]:
        """Load config from file or create default"""
        if self.config_path.exists():
            with open(self.config_path) as f:
                user_config = yaml.safe_load(f)
                # Merge with defaults
                config = self.DEFAULT_CONFIG.copy()
                config.update(user_config)
                return config
        else:
            # Create default config
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, "w") as f:
                yaml.dump(self.DEFAULT_CONFIG, f, default_flow_style=False)
            return self.DEFAULT_CONFIG.copy()

    def get_hotkey_modifiers(self) -> list[int]:
        """Get list of modifier keycodes"""
        modifiers = self.config["hotkey"]["modifiers"]
        keycodes = []
        for mod in modifiers:
            if mod in self.MODIFIER_MAP:
                keycodes.extend(self.MODIFIER_MAP[mod])
        return keycodes

    def get_hotkey_key(self) -> int:
        """Get hotkey keycode"""
        key_name = self.config["hotkey"]["key"]
        return self.KEY_MAP.get(key_name, ecodes.KEY_DOT)

    def get_hotkey_display(self) -> str:
        """Get human-readable hotkey string"""
        modifiers = self.config["hotkey"]["modifiers"]
        key = self.config["hotkey"]["key"]
        mod_str = "+".join([m.capitalize() for m in modifiers])
        return f"{mod_str}+{key.capitalize()}"

    def get_model_path(self) -> Path:
        """Get path to whisper model"""
        model_name = self.config["whisper"]["model"]
        model_dir = Path.home() / ".local/share/whisper/models"
        model_file = model_dir / f"ggml-{model_name}.bin"

        # Fallback to old location
        if not model_file.exists():
            alt_dir = Path.home() / ".local/share/whisper-models"
            model_file = alt_dir / f"ggml-{model_name}.bin"

        return model_file

    def get(self, key: str, default=None):
        """Get config value by dot-notation key"""
        keys = key.split(".")
        value = self.config
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default
        return value if value is not None else default
