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
  inputs.whisper-dictation.url = "github:jacopone/whisper-dictation";

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
git clone https://github.com/jacopone/whisper-dictation.git
cd whisper-dictation

# Enter development environment
nix develop

# Run directly
python -m whisper_dictation.daemon
```

## Quick Start

### First-Time Setup

1. **Ensure you're in the `input` group** (required for keyboard monitoring):
   ```bash
   sudo usermod -aG input $USER
   # ⚠️ Logout and login required (not just reboot!)

   # Verify group membership
   groups | grep input
   ```

2. **Download Whisper model** (first time only):
   ```bash
   # Create models directory
   mkdir -p ~/.local/share/whisper-models
   cd ~/.local/share/whisper-models

   # For fast dictation (recommended - 4-6s processing):
   curl -L -o ggml-base.bin https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-base.bin

   # Or for better accuracy (20-30s processing):
   curl -L -o ggml-medium.bin https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-medium.bin
   ```

3. **Start ydotoold daemon** (required for text pasting):
   ```bash
   ydotoold --socket-path=/run/user/1000/.ydotool_socket --socket-perm=0600 &

   # Verify it's running
   pgrep -a ydotoold
   ```

### Daily Usage

**Enter development environment:**
```bash
cd ~/whisper-dictation
devenv shell  # Or use direnv if configured
```

**Start the dictation daemon** (choose one option):

**Option A: Auto-detect language** (most convenient):
```bash
run-daemon-auto      # Detects Italian, English, Spanish, etc.
# Note: Adds ~1-2s processing time for detection
```

**Option B: Choose specific language** (fastest):
```bash
run-daemon-en        # English only
run-daemon-it        # Italian only (Italiano)
run-daemon           # Use config file language
```

**Option C: Command-line flags** (temporary override):
```bash
python -m whisper_dictation.daemon --verbose --language auto  # Auto-detect
python -m whisper_dictation.daemon --verbose --language en
python -m whisper_dictation.daemon --verbose --language it
python -m whisper_dictation.daemon --verbose --model base  # Override model too
```

**Option D: Edit config file** (persistent setting):
```bash
vim ~/.config/whisper-dictation/config.yaml
# Change: language: auto  (or en, it, es, fr, etc.)
# Change: model: base     (or tiny, small, medium, large)
run-daemon
```

### Using Dictation

1. Click in any text field (browser, editor, terminal, etc.)
2. Press and hold **Super+Period** (⊞ + .)
3. Speak clearly in your chosen language
4. Release key → text appears instantly!

**Tips:**
- Speak naturally, no need to pause between words
- Works in any application (Wayland-compatible)
- Auto-detect mode handles mixed Italian/English seamlessly
- Use `run-daemon-debug` to troubleshoot hotkey detection

## Configuration

Edit `~/.config/whisper-dictation/config.yaml`:

```yaml
# Hotkey configuration
hotkey:
  key: period           # Any key from evdev.ecodes (e.g., period, comma, space)
  modifiers:
    - super             # Can use: super, ctrl, alt, shift

# Whisper settings
whisper:
  model: base           # Options: tiny (1-2s), base (4-6s), small (10-15s), medium (20-30s), large (40-60s)
  language: auto        # Options: auto, en, it, es, fr, de, etc. (99+ languages supported)
  threads: 4            # CPU threads for transcription (adjust based on your system)

# UI settings
ui:
  show_waveform: false  # Show visual waveform during recording
  theme: dark           # Options: dark, light, auto

# Post-processing
processing:
  remove_filler_words: true   # Remove "um", "uh", etc.
  auto_capitalize: true       # Capitalize first letter of sentences
  auto_punctuate: false       # Auto-add punctuation (experimental)
```

**Quick config changes:**
```bash
# Change language to auto-detect
sed -i 's/language: .*/language: auto/' ~/.config/whisper-dictation/config.yaml

# Change model to base (faster)
sed -i 's/model: .*/model: base/' ~/.config/whisper-dictation/config.yaml

# Or use convenience scripts
dictate-en    # Sets language to en
dictate-it    # Sets language to it
```

## How It Works

1. **Keyboard Monitoring** - `evdev` captures low-level key events
2. **Audio Recording** - `ffmpeg` records mic input while key is held
3. **Transcription** - `whisper.cpp` processes audio locally
4. **Text Insertion** - `ydotool` pastes text into active window
5. **UI Feedback** - GTK4 window shows real-time status

## Model Selection Guide

| Model  | Size   | Speed      | Accuracy | Use Case                     |
|--------|--------|------------|----------|------------------------------|
| tiny   | 39 MB  | ~1-2s ⚡   | 60%      | Quick notes, testing         |
| base   | 142 MB | ~4-6s ⚡⚡  | 70%      | **Recommended for speed**    |
| small  | 466 MB | ~10-15s    | 80%      | Balanced performance         |
| medium | 1.5 GB | ~20-30s    | 85%      | High accuracy for LLMs       |
| large  | 2.9 GB | ~40-60s    | 90%      | Maximum accuracy             |

**Performance notes:**
- Times measured on CPU (4 threads)
- GPU acceleration can reduce times by 5-10x
- **base** model recommended for Aqua Voice-like speed
- Switch models by editing `model:` in config.yaml

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

# Check PulseAudio/PipeWire
pactl list sources short
```

### Keyboard events not detected
```bash
# Add user to input group
sudo usermod -aG input $USER
# Logout/login required (not just reboot)

# Verify input group membership
groups | grep input
```

### ydotool not working
```bash
# Start ydotool daemon manually
ydotoold --socket-path=/run/user/1000/.ydotool_socket --socket-perm=0600 &

# Verify socket exists
ls -la /run/user/1000/.ydotool_socket

# Check if ydotoold is running
pgrep -a ydotoold
```

### Slow transcription
```bash
# Option 1: Switch to faster model in config
vim ~/.config/whisper-dictation/config.yaml
# Change: model: base  (4-6s) or tiny (1-2s)

# Option 2: Override with command-line flag
python -m whisper_dictation.daemon --verbose --model base

# Option 3: Download faster model
cd ~/.local/share/whisper-models
curl -L -o ggml-base.bin https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-base.bin
```

### Virtual keyboard detected instead of real keyboard
The daemon automatically filters out virtual devices (ydotoold, xdotool).
If issues persist, check logs with `run-daemon-debug` to see which devices are detected.

### Language not detected correctly
```bash
# Option 1: Use auto-detection mode
run-daemon-auto

# Option 2: Specify language explicitly
run-daemon-en        # English
run-daemon-it        # Italian

# Option 3: Check config file
cat ~/.config/whisper-dictation/config.yaml
# Should show: language: auto (or en, it, etc.)
```

### Hotkey not working
```bash
# Test with debug mode
run-daemon-debug

# Check for keybinding conflicts in GNOME
gnome-control-center keyboard

# Verify you see "HOTKEY COMBO DETECTED" when pressing Super+Period
# If you see "has_mods=False", verify Super key is being detected
```

### DevEnv issues
```bash
# Rebuild environment
devenv shell

# If packages missing, update
nix flake update

# Clear cache
rm -rf .devenv/
devenv shell
```

## Development

See [DEVELOPMENT.md](DEVELOPMENT.md) for comprehensive development guide.

### Quick Commands

```bash
# Enter dev shell
devenv shell

# Run tests with coverage
test

# Format code
format

# Check all quality gates
quality-check

# Build package
nix build
```

### Available Scripts

- `run-daemon-auto` - Auto-detect language (most convenient)
- `run-daemon-en` - English only (fastest)
- `run-daemon-it` - Italian only
- `run-daemon-debug` - Debug mode (shows all key events)
- `test` - Run test suite with coverage
- `format` - Auto-format code (Black + Ruff)
- `quality-check` - Run all quality gates
- `setup-dev` - First-time setup (git hooks, Cursor AI rules)

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
