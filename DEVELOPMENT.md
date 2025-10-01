# Development Guide

## Quick Start

### Enter Development Environment

```bash
cd ~/whisper-dictation

# Option 1: Automatic with direnv
direnv allow          # Once, then automatic on cd

# Option 2: Manual
devenv shell
```

### First-Time Setup

```bash
# Setup git hooks and Cursor AI
setup-dev

# Run test suite
test

# Check all quality gates
quality-check
```

### Development Workflow

```bash
# Start ydotoold (required for text pasting - run once per session)
ydotoold --socket-path=/run/user/1000/.ydotool_socket --socket-perm=0600 &

# Run the daemon with auto language detection (most convenient)
run-daemon-auto

# Run daemon with specific language (fastest)
run-daemon-en        # English only
run-daemon-it        # Italian only

# Run daemon with full debug logging (shows all key events)
run-daemon-debug

# Run tests with coverage
test

# Format code
format

# Check quality before commit
quality-check
```

### Language Selection

**Option 1: Use convenience commands** (recommended):
```bash
run-daemon-auto      # Auto-detect language (Italian, English, Spanish, etc.)
run-daemon-en        # English only (fastest)
run-daemon-it        # Italian only (Italiano)
```

**Option 2: Use command-line flags** (temporary override):
```bash
python -m whisper_dictation.daemon --verbose --language auto
python -m whisper_dictation.daemon --verbose --language en
python -m whisper_dictation.daemon --verbose --language it
python -m whisper_dictation.daemon --verbose --model base
```

**Option 3: Legacy switcher scripts** (updates config file):
```bash
dictate-it           # Sets config to Italian
dictate-en           # Sets config to English
run-daemon           # Then restart daemon
```

**Option 4: Edit config file directly**:
```bash
vim ~/.config/whisper-dictation/config.yaml
# Change: language: auto  (or en, it, es, fr, etc.)
# Change: model: base     (or tiny, small, medium, large)
```

## Quality Gates

All commits are automatically checked for:

| Gate | Tool | Threshold | Auto-Fix |
|------|------|-----------|----------|
| **Formatting** | Black | 100% | ✅ Yes |
| **Linting** | Ruff | Zero issues | ✅ Yes |
| **Complexity** | Lizard | CCN < 10 | ❌ Manual |
| **Security** | Gitleaks | No secrets | ❌ Manual |
| **Security** | Semgrep | Auto patterns | ❌ Manual |
| **Tests** | Pytest | Must pass | ❌ Fix tests |
| **Coverage** | Pytest-cov | >75% | ❌ Add tests |
| **Commits** | Commitizen | Conventional | ❌ Manual |

## Project Structure

```
whisper-dictation/
├── src/whisper_dictation/     # Python source code
│   ├── daemon.py              # Main event loop
│   ├── recorder.py            # Audio recording
│   ├── transcriber.py         # Whisper integration
│   ├── ui.py                  # GTK notifications
│   ├── paste.py               # Text insertion
│   └── config.py              # Configuration
├── tests/                     # Test suite
│   ├── test_config.py
│   ├── test_recorder.py
│   └── test_paste.py
├── .cursor/rules/             # AI development rules
│   ├── index.mdc             # Core Python/audio patterns
│   └── security.mdc          # Security/privacy rules
├── devenv.nix                 # Development environment
├── flake.nix                  # NixOS packaging
└── pyproject.toml             # Python project config
```

## Testing

### Run Tests

```bash
# All tests with coverage
test

# Specific test file
pytest tests/test_config.py -v

# With debug output
pytest tests/ -vv -s

# Coverage report
pytest --cov=src/whisper_dictation --cov-report=html
open htmlcov/index.html
```

### Writing Tests

```python
import pytest
from whisper_dictation.module import YourClass

@pytest.fixture
def config():
    """Fixture for test configuration"""
    return Config()

def test_your_feature(config):
    """Test description"""
    # Arrange
    instance = YourClass(config)

    # Act
    result = instance.method()

    # Assert
    assert result == expected
```

## Cursor AI Integration

### Available Rules

- **index.mdc** - Core Python/audio development patterns
- **security.mdc** - Privacy/security for keyboard monitoring

### Using Cursor AI

1. **Agent Mode** (Ctrl+I): Complex tasks
   - "Implement streaming transcription"
   - "Add test coverage for transcriber module"
   - "Refactor recorder for better error handling"

2. **Background Mode** (Ctrl+E): Continuous assistance
   - Code suggestions while typing
   - Automatic error detection
   - Pattern recognition

3. **Chat** (Ctrl+K): Questions and guidance
   - "How should I handle audio device errors?"
   - "What's the best pattern for async transcription?"

### AI Quality Awareness

Cursor AI automatically enforces:
- CCN < 10 complexity limit
- No logging of keyboard events
- Secure subprocess usage
- Type hints and docstrings
- Test coverage requirements

## Common Tasks

### Adding a New Feature

```bash
# 1. Create feature branch
git checkout -b feature/streaming-stt

# 2. Implement with tests
# Edit src/whisper_dictation/*.py
# Add tests/test_*.py

# 3. Run quality checks
format              # Auto-fix formatting
test                # Verify tests pass
quality-check       # Full quality scan

# 4. Commit with conventional format
git add .
git commit -m "feat: add streaming transcription support"
```

### Fixing a Bug

```bash
# 1. Write failing test first (TDD)
# Add to tests/test_*.py

# 2. Fix the bug
# Edit src/whisper_dictation/*.py

# 3. Verify fix
test                # Test passes now
quality-check       # No regressions

# 4. Commit
git commit -m "fix: handle SIGTERM gracefully in recorder"
```

### Improving Performance

```bash
# 1. Profile first
python -m cProfile -s cumtime -m whisper_dictation.daemon

# 2. Optimize
# Focus on hot paths

# 3. Verify no regressions
test
quality-check

# 4. Commit
git commit -m "perf: optimize audio transcription pipeline"
```

## Troubleshooting

### Tests Failing

```bash
# Run with verbose output
pytest tests/ -vv -s

# Run specific test
pytest tests/test_config.py::test_default_config_creation -vv

# Check coverage gaps
pytest --cov=src/whisper_dictation --cov-report=term-missing
```

### Quality Gate Failures

```bash
# Black formatting
black src/ tests/

# Ruff linting
ruff check --fix src/ tests/

# Complexity issues
lizard src/ --CCN 10
# Refactor functions with CCN > 10

# Security issues
gitleaks detect --source .
semgrep --config=auto src/
```

### DevEnv Issues

```bash
# Rebuild environment
devenv shell

# Update dependencies
devenv update

# Clear cache
rm -rf .devenv/
devenv shell
```

## Git Hooks

Pre-commit hooks run automatically on `git commit`:

```bash
# Test hooks without committing
devenv test

# Skip hooks (emergency only)
git commit --no-verify

# Reinstall hooks
setup-git-hooks
```

## CI/CD (Future)

Planned GitHub Actions:

- ✅ Run test suite
- ✅ Check code quality
- ✅ Security scanning
- ✅ Build NixOS package
- ✅ Release automation

## Resources

- [DevEnv Documentation](https://devenv.sh/)
- [Pytest Documentation](https://docs.pytest.org/)
- [Black Code Style](https://black.readthedocs.io/)
- [Ruff Linter](https://docs.astral.sh/ruff/)
- [Cursor AI](https://cursor.sh/)

---

**Happy hacking! 🎤**
