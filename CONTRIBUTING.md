# Contributing to Whisper Dictation

Thank you for your interest in contributing! 🎉

## Development Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/whisper-dictation.git
cd whisper-dictation

# Enter development environment
nix develop

# Run in development mode
python -m whisper_dictation.daemon
```

## Project Structure

```
whisper-dictation/
├── src/whisper_dictation/
│   ├── daemon.py         # Main event loop
│   ├── recorder.py       # Audio recording
│   ├── transcriber.py    # Whisper interface
│   ├── ui.py            # GTK notifications
│   ├── paste.py         # Text insertion
│   └── config.py        # Configuration management
├── systemd/             # Systemd service file
├── tests/               # Test suite
└── flake.nix           # Nix package definition
```

## Testing

```bash
# Run tests
pytest

# Run specific test
pytest tests/test_config.py

# With coverage
pytest --cov=whisper_dictation
```

## Code Style

We use:
- **black** for formatting
- **ruff** for linting
- **type hints** where appropriate

```bash
# Format code
black src/

# Lint
ruff check src/

# Fix linting issues
ruff check --fix src/
```

## Submitting Changes

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to your fork (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

## Feature Requests & Bug Reports

Please use GitHub Issues with appropriate labels:
- `enhancement` - New features
- `bug` - Bug reports
- `documentation` - Documentation improvements

## Areas for Contribution

- **Real-time streaming** - Implement WhisperLive integration
- **Custom vocabulary** - Allow users to train on technical terms
- **Multi-backend support** - Add Avalon/Deepgram/AssemblyAI
- **Voice commands** - Execute actions via voice
- **Translations** - Support for more languages
- **Tests** - Expand test coverage

## Questions?

Open a Discussion on GitHub or reach out to the maintainers.

Happy hacking! 🚀
