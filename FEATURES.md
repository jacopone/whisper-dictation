# Whisper Dictation Features

## Core Functionality

### Speech-to-Text
- **100% Local Processing** - No cloud, no telemetry, works offline
- **Push-to-Talk Interface** - Hold Super+Period, speak, release to paste
- **Real-time Feedback** - GTK4 desktop notifications show status
- **Universal Compatibility** - Works in any Wayland application

### Language Support
- **99+ Languages** - Full Whisper language support
- **Auto-Detection** - Automatically detects language (Italian, English, Spanish, French, etc.)
- **Manual Selection** - Force specific language for fastest processing
- **Mixed Language** - Auto-detect handles seamless language switching

### Performance Options

| Model  | Size   | Speed      | Accuracy | Use Case                     |
|--------|--------|------------|----------|------------------------------|
| tiny   | 39 MB  | ~1-2s ⚡   | 60%      | Quick notes, testing         |
| base   | 142 MB | ~4-6s ⚡⚡  | 70%      | **Recommended for speed**    |
| small  | 466 MB | ~10-15s    | 80%      | Balanced performance         |
| medium | 1.5 GB | ~20-30s    | 85%      | High accuracy               |
| large  | 2.9 GB | ~40-60s    | 90%      | Maximum accuracy             |

## Developer Features

### Quality Gates
- **Code Formatting** - Black + Ruff auto-formatting
- **Complexity Checks** - CCN < 10 enforced
- **Security Scanning** - Gitleaks + Semgrep
- **Test Coverage** - >75% requirement
- **Pre-commit Hooks** - Automatic quality enforcement

### Development Environment
- **DevEnv Integration** - Pure, reproducible development shell
- **Cursor AI Rules** - Pre-configured code intelligence
- **Convenience Commands** - `run-daemon-auto`, `run-daemon-en`, etc.
- **Debug Mode** - Comprehensive logging with `run-daemon-debug`

## Privacy & Security

### Privacy-First Design
- No network requests during transcription
- Audio files deleted after processing
- No keyboard event logging (only hotkey detection)
- Local model storage (no external dependencies)

### Security Features
- Virtual device filtering (excludes ydotoold, xdotool)
- Input group permission requirements
- Subprocess hardening
- Secret scanning in git commits

## Customization

### Hotkey Configuration
- Customize key combination (default: Super+Period)
- Multiple modifier key support (Super, Ctrl, Alt, Shift)
- Per-device keyboard selection

### Post-Processing
- Remove filler words ("um", "uh", etc.)
- Auto-capitalization
- Auto-punctuation (experimental)

### UI Themes
- Dark mode (default)
- Light mode
- Auto (follows system theme)

## Integration

### System Integration
- Wayland-native (ydotool)
- GNOME desktop notifications
- PulseAudio/PipeWire audio capture
- evdev keyboard monitoring

### Development Integration
- NixOS flakes support
- DevEnv/direnv compatibility
- Git hooks with Commitizen
- Cursor AI workspace rules

## Command Reference

### Daily Usage
```bash
run-daemon-auto      # Auto-detect language
run-daemon-en        # English only
run-daemon-it        # Italian only
run-daemon-debug     # Debug mode
```

### Development
```bash
test                 # Run test suite
format               # Format code
quality-check        # Run all gates
setup-dev            # First-time setup
```

### Configuration
```bash
dictate-en           # Switch to English
dictate-it           # Switch to Italian
vim ~/.config/whisper-dictation/config.yaml
```

## Roadmap

### Planned Features
- [ ] Streaming transcription (live preview)
- [ ] Custom vocabulary training
- [ ] Voice command mode
- [ ] LLM API integration (Claude, GPT-4)
- [ ] Multi-backend support (Avalon, Deepgram)
- [ ] Voice profiles for different contexts
- [ ] GPU acceleration
- [ ] systemd service auto-start

### Potential Enhancements
- [ ] Punctuation learning
- [ ] Speaker diarization
- [ ] Background noise filtering
- [ ] Custom hotkey actions
- [ ] Text-to-speech feedback
- [ ] Multi-device sync

## Comparison to Alternatives

| Feature              | Whisper Dictation | Aqua Voice | Talon Voice |
|---------------------|-------------------|------------|-------------|
| **Privacy**         | ✅ 100% Local     | ❌ Cloud   | ✅ Local    |
| **Cost**            | ✅ Free           | 💲 $8/mo   | 💲 $15/mo   |
| **NixOS Support**   | ✅ Native         | ❌ No      | ⚠️ Manual   |
| **Speed (base)**    | ⚠️ 4-6s          | ✅ 850ms   | ✅ 1-2s     |
| **Technical Terms** | ⚠️ 70%           | ✅ 97%     | ✅ 95%      |
| **Wayland**         | ✅ Yes            | ⚠️ Limited | ❌ X11 only |
| **Multilingual**    | ✅ 99 languages   | ✅ Yes     | ⚠️ Limited  |
| **Offline**         | ✅ Yes            | ❌ No      | ✅ Yes      |
| **Open Source**     | ✅ MIT            | ❌ No      | ❌ No       |

## Known Limitations

### Current Limitations
- Speed slower than commercial solutions (4-6s vs 850ms for Aqua Voice)
- Technical jargon accuracy varies by model (70-90%)
- CPU-only processing (GPU support planned)
- Single-user design (no multi-user profiles yet)
- No streaming transcription (processes after key release)

### System Requirements
- NixOS or Linux with Nix
- Wayland compositor (X11 may work with modifications)
- Minimum 4GB RAM (8GB recommended for medium model)
- User must be in `input` group
- PulseAudio or PipeWire

### Workarounds
- Use `base` model for faster processing (trade-off: lower accuracy)
- Commercial alternatives (Aqua Voice, Avalon API) for maximum speed
- GPU acceleration can reduce times by 5-10x (implementation pending)

---

**For detailed setup instructions, see [README.md](README.md)**
**For development guide, see [DEVELOPMENT.md](DEVELOPMENT.md)**
