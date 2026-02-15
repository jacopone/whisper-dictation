# Troubleshooting

Common issues and solutions for Whisper Dictation.

## No audio recording

```bash
# Test microphone directly
ffmpeg -f pulse -i default -t 1 test.wav

# List available audio sources
pactl list sources short
```

## Keyboard events not detected

```bash
# Add user to input group
sudo usermod -aG input $USER
# Logout and login required (not just reboot)

# Verify group membership
groups | grep input
```

## ydotool not working

```bash
# Start ydotool daemon manually
ydotoold --socket-path=/run/user/1000/.ydotool_socket --socket-perm=0600 &

# Verify socket exists
ls -la /run/user/1000/.ydotool_socket

# Check if ydotoold is running
pgrep -a ydotoold
```

## Slow transcription

```bash
# Switch to a faster model in config
vim ~/.config/whisper-dictation/config.yaml
# Change: model: base  (4-6s) or tiny (1-2s)

# Or override with a command-line flag
python -m whisper_dictation.daemon --verbose --model base

# Or download a faster model
cd ~/.local/share/whisper-models
curl -L -o ggml-base.bin https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-base.bin
```

## Virtual keyboard detected instead of real keyboard

The daemon automatically filters out virtual devices (ydotoold, xdotool). If issues persist, run `run-daemon-debug` to see which devices are detected.

As a last resort, manually set your input device in `~/.config/whisper-dictation/config.yaml`:

```yaml
input_device: "/dev/input/event25"
```

## Language not detected correctly

```bash
# Use auto-detection mode
run-daemon-auto

# Or specify language explicitly
run-daemon-en        # English
run-daemon-it        # Italian

# Check current config
cat ~/.config/whisper-dictation/config.yaml
# Should show: language: auto (or en, it, etc.)
```

## Hotkey not working

```bash
# Test with debug mode
run-daemon-debug

# Check for keybinding conflicts in GNOME
gnome-control-center keyboard

# Verify you see "HOTKEY COMBO DETECTED" when pressing Super+Period
# If you see "has_mods=False", the Super key is not being detected
```

## DevEnv issues

```bash
# Rebuild environment
devenv shell

# If packages are missing, update inputs
nix flake update

# Clear cache and rebuild
rm -rf .devenv/
devenv shell
```
