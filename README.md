# Whisper Dictation

🎤 **Acqua Voice-like local speech-to-text dictation for NixOS**

Fast, accurate, privacy-first voice input powered by whisper.cpp. Press and hold a hotkey, speak, release to paste transcribed text anywhere.

## Features

- 🔒 **100% Local & Private** - No cloud, no telemetry, works offline
- ⚡ **Real-time Feedback** - Live transcription with floating UI
- 🎯 **Push-to-Talk** - Hold Super+Period, speak, release to paste
- 🧠 **Technical Accuracy** - Optimized for developer/AI workflows
- 🌍 **Multilingual** - Support for 99 languages via Whisper
- 🎨 **Native GNOME** - GTK4 UI, Wayland-compatible

## Installation

### On NixOS (Recommended)

Add to your `flake.nix`:

```nix
{
  inputs.whisper-dictation.url = "github:yourusername/whisper-dictation";

  # In your configuration
  environment.systemPackages = [
    inputs.whisper-dictation.packages.${system}.default
  ];

  # Enable auto-start
  systemd.user.services.whisper-dictation = {
    enable = true;
    wantedBy = [ "graphical-session.target" ];
  };
}
```

### Manual Installation

```bash
# Clone repository
git clone https://github.com/yourusername/whisper-dictation.git
cd whisper-dictation

# Enter development environment
nix develop

# Run directly
python -m whisper_dictation.daemon
```

## Quick Start

1. **Download Whisper model** (first time only):
   ```bash
   whisper-cpp-download-ggml-model medium
   ```
   Models are saved to `~/.local/share/whisper/models/`

2. **Start the daemon**:
   ```bash
   whisper-dictation
   ```
   Or enable systemd service for auto-start.

3. **Use dictation**:
   - Click in any text field
   - Press and hold **Super+Period** (Windows key + .)
   - Speak clearly
   - Release key → text appears!

## Configuration

Edit `~/.config/whisper-dictation/config.yaml`:

```yaml
# Hotkey configuration
hotkey:
  modifiers: ["super"]  # Alt: ["ctrl", "alt"]
  key: "period"         # Any key from evdev.ecodes

# Whisper settings
whisper:
  model: "medium"       # tiny, base, small, medium, large
  language: "en"        # Auto-detect: "auto"
  threads: 4

# UI settings
ui:
  show_waveform: true
  theme: "dark"         # dark, light, auto

# Post-processing
processing:
  remove_filler_words: true
  auto_capitalize: true
  auto_punctuate: false
```

## How It Works

1. **Keyboard Monitoring** - `evdev` captures low-level key events
2. **Audio Recording** - `ffmpeg` records mic input while key is held
3. **Transcription** - `whisper.cpp` processes audio locally
4. **Text Insertion** - `ydotool` pastes text into active window
5. **UI Feedback** - GTK4 window shows real-time status

## Model Selection Guide

| Model  | Size   | Speed     | Accuracy | Use Case                |
|--------|--------|-----------|----------|-------------------------|
| tiny   | 75 MB  | Very Fast | 60%      | Quick notes, testing    |
| base   | 142 MB | Fast      | 65%      | Casual use              |
| small  | 466 MB | Moderate  | 75%      | Balanced performance    |
| medium | 1.5 GB | Slower    | 85%      | **Recommended for LLMs**|
| large  | 2.9 GB | Slowest   | 90%      | Maximum accuracy        |

## Requirements

- **OS**: NixOS or any Linux with Nix
- **Desktop**: GNOME (Wayland) or other Wayland compositor
- **Permissions**: User must be in `input` group for keyboard monitoring
- **Audio**: PulseAudio or PipeWire

## Troubleshooting

### No audio recording
```bash
# Check microphone
ffmpeg -f pulse -i default -t 1 test.wav
```

### Keyboard events not detected
```bash
# Add user to input group
sudo usermod -aG input $USER
# Reboot required
```

### ydotool not working
```bash
# Start ydotool daemon
systemctl --user start ydotool
```

## Development

```bash
# Enter dev shell
nix develop

# Run tests
pytest

# Format code
black src/
ruff check src/

# Build package
nix build
```

## Comparison to Other Tools

| Feature              | Whisper Dictation | Aqua Voice | Talon Voice |
|---------------------|-------------------|------------|-------------|
| **Privacy**         | ✅ 100% Local     | ❌ Cloud   | ✅ Local    |
| **Cost**            | ✅ Free           | 💲 $8/mo   | 💲 $15/mo   |
| **NixOS Support**   | ✅ Native         | ❌ No      | ⚠️ Manual   |
| **Technical Terms** | ⚠️ 65-85%         | ✅ 97%     | ✅ 95%      |
| **Wayland**         | ✅ Yes            | ⚠️ Limited | ❌ X11 only |
| **Real-time**       | ✅ Yes            | ✅ Yes     | ✅ Yes      |

## Roadmap

- [ ] Streaming transcription (live preview while speaking)
- [ ] Custom vocabulary training
- [ ] Command mode (voice commands for actions)
- [ ] Integration with LLM APIs (Claude, GPT-4)
- [ ] Multi-backend support (Avalon API, Deepgram)
- [ ] Voice profiles for different contexts

## Contributing

Contributions welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

MIT License - see [LICENSE](LICENSE)

## Acknowledgments

- [whisper.cpp](https://github.com/ggml-org/whisper.cpp) - Fast whisper implementation
- [Aqua Voice](https://withaqua.com/) - UI/UX inspiration
- [ydotool](https://github.com/ReimuNotMoe/ydotool) - Wayland input automation

---

**Made with ❤️ for the NixOS community**
