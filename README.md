# Whisper Dictation

Privacy-first local speech-to-text for NixOS -- whisper.cpp powered, push-to-talk, paste anywhere.

## Features

- **100% local and private** -- no cloud, no telemetry, works fully offline
- **Push-to-talk** -- hold Super+Period, speak, release to paste text
- **Real-time feedback** -- floating GTK4 window shows transcription status
- **Multilingual** -- supports 99 languages with auto-detection
- **Wayland native** -- built for GNOME on Wayland, works in any application
- **Optimized for technical speech** -- tuned for developer and AI workflows

## Requirements

- NixOS or any Linux distribution with Nix
- Wayland compositor (GNOME recommended)
- PulseAudio or PipeWire
- User must be in the `input` group for keyboard monitoring

## Installation

### NixOS (recommended)

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

### Manual

```bash
git clone https://github.com/jacopone/whisper-dictation.git
cd whisper-dictation
nix develop
python -m whisper_dictation.daemon
```

**First-time setup:** ensure your user is in the `input` group (`sudo usermod -aG input $USER`, then log out and back in), download a Whisper model to `~/.local/share/whisper-models/`, and start the `ydotoold` daemon. See the [first-time setup section in DEVELOPMENT.md](DEVELOPMENT.md) for details.

## Usage

Start the daemon and dictate:

```bash
run-daemon          # use config file settings
run-daemon-en       # English only (fastest)
run-daemon-it       # Italian only
run-daemon-auto     # auto-detect language (adds ~1-2s)
```

Then in any application:

1. Click in a text field
2. Hold **Super+Period**
3. Speak naturally
4. Release the key -- text is pasted instantly

Override settings per-session with command-line flags:

```bash
python -m whisper_dictation.daemon --verbose --language auto --model base
```

## Configuration

Edit `~/.config/whisper-dictation/config.yaml`. Key settings:

- `whisper.model` -- model size: `tiny`, `base` (recommended), `small`, `medium`, `large`
- `whisper.language` -- language code (`en`, `it`, `auto`, etc.)
- `hotkey.key` / `hotkey.modifiers` -- push-to-talk keybinding

See `config.yaml` in the repository for all available options.

<details>
<summary>Model selection guide</summary>

| Model  | Size   | Speed    | Accuracy | Use Case                  |
|--------|--------|----------|----------|---------------------------|
| tiny   | 39 MB  | ~1-2s    | 60%      | Quick notes, testing      |
| base   | 142 MB | ~4-6s    | 70%      | Recommended for speed     |
| small  | 466 MB | ~10-15s  | 80%      | Balanced performance      |
| medium | 1.5 GB | ~20-30s  | 85%      | High accuracy             |
| large  | 2.9 GB | ~40-60s  | 90%      | Maximum accuracy          |

Times measured on CPU (4 threads). GPU acceleration can reduce times by 5-10x.

</details>

## How It Works

1. **Keyboard monitoring** -- `evdev` captures low-level key events
2. **Audio recording** -- `ffmpeg` records microphone input while the key is held
3. **Transcription** -- `whisper.cpp` processes audio locally on your machine
4. **Text insertion** -- `ydotool` pastes transcribed text into the active window
5. **UI feedback** -- GTK4 floating window shows real-time status

## Comparison

| Feature           | Whisper Dictation | Aqua Voice  | Talon Voice  |
|-------------------|-------------------|-------------|--------------|
| Privacy           | Local             | Cloud       | Local        |
| Cost              | Free              | $8/mo       | $15/mo       |
| NixOS support     | Native            | No          | Manual       |
| Technical terms   | 65-85%            | 97%         | 95%          |
| Wayland           | Yes               | Limited     | X11 only     |
| Real-time         | Yes               | Yes         | Yes          |

## Development

See [DEVELOPMENT.md](DEVELOPMENT.md) for the full development guide.

## Troubleshooting

See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for solutions to common issues (audio, keyboard detection, ydotool, hotkeys, performance).

## Contributing

Contributions welcome. See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

MIT License -- see [LICENSE](LICENSE).
