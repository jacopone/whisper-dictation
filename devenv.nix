{ pkgs, lib, config, inputs, ... }:

{
  # https://devenv.sh/basics/
  env = {
    GREET = "Whisper Dictation - Voice-to-Text Development";
    PYTHONPATH = "./src";
  };

  # Fix dotenv integration warning
  dotenv.disableHint = true;

  # https://devenv.sh/packages/
  packages = with pkgs; [
    # Python development
    python312
    python312Packages.pytest
    python312Packages.pytest-cov
    python312Packages.pytest-asyncio
    python312Packages.black
    ruff

    # Speech-to-text and system integration
    whisper-cpp
    ffmpeg
    ydotool
    libnotify
    gtk4
    gobject-introspection

    # Audio utilities
    sox
    pulseaudio

    # Git and security
    git
    gh
    gitleaks
    semgrep
    python3Packages.commitizen

    # Quality gates (system-wide tools)
    # Note: lizard, jscpd, radon available system-wide
  ];

  # https://devenv.sh/languages/
  languages.python = {
    enable = true;
  };

  # https://devenv.sh/scripts/
  scripts = {
    hello.exec = ''
      echo "🎤 Welcome to Whisper Dictation Development!"
      echo ""
      echo "📦 Environment:"
      echo "  Python: $(python --version)"
      echo "  Whisper: $(whisper-cli --help 2>&1 | head -1 || echo 'Available')"
      echo "  FFmpeg: $(ffmpeg -version 2>&1 | head -1)"
      echo ""
      echo "🔧 Quality Tools:"
      echo "  Pytest: $(pytest --version)"
      echo "  Black: $(black --version)"
      echo "  Ruff: $(ruff --version)"
      echo "  Gitleaks: $(gitleaks version 2>/dev/null || echo 'Available')"
      echo "  Semgrep: $(semgrep --version 2>/dev/null | head -1)"
      echo "  Lizard: $(lizard --version 2>/dev/null || echo 'Available (system-wide)')"
      echo ""
      echo "📋 Quick Start:"
      echo "  setup-dev         - Setup git hooks and project"
      echo "  test              - Run test suite"
      echo "  quality-check     - Run all quality gates"
      echo "  run-daemon        - Run dictation daemon"
      echo ""
      echo "🎯 AI Development:"
      echo "  Cursor AI rules: .cursor/rules/*.mdc"
      echo "  Use Ctrl+I for Agent mode, Ctrl+E for background"
    '';

    # Run the daemon in development mode
    run-daemon.exec = ''
      echo "🎤 Starting Whisper Dictation daemon..."
      echo "📋 Monitoring keyboard for Super+Period"
      python -m whisper_dictation.daemon
    '';

    # Run tests with coverage
    test.exec = ''
      echo "🧪 Running test suite..."
      pytest tests/ -v --cov=src/whisper_dictation --cov-report=term-missing --cov-report=html
      echo ""
      echo "📊 Coverage report generated: htmlcov/index.html"
    '';

    # Comprehensive quality check
    quality-check.exec = ''
      echo "🔍 Running comprehensive quality check..."
      echo ""
      echo "📋 Step 1: Code formatting"
      black --check src/ tests/ || echo "⚠️ Run 'black src/ tests/' to fix"
      ruff check src/ tests/ || echo "⚠️ Run 'ruff check --fix src/ tests/' to fix"
      echo ""
      echo "📋 Step 2: Security scanning"
      gitleaks detect --source . --no-git || echo "⚠️ Secrets detected!"
      semgrep --config=auto --severity=WARNING src/ || echo "⚠️ Security patterns found"
      echo ""
      echo "📋 Step 3: Code complexity"
      lizard --CCN 10 --length 50 src/ || echo "⚠️ Complexity threshold exceeded"
      echo ""
      echo "📋 Step 4: Test suite"
      pytest tests/ -v --cov=src/whisper_dictation --cov-fail-under=75 || echo "⚠️ Tests failed or coverage below 75%"
      echo ""
      echo "✅ Quality check complete"
    '';

    quality-report.exec = ''
      echo "🔍 Whisper Dictation Quality Gates Report"
      echo ""
      echo "📋 Security:"
      echo "  - Gitleaks: No secrets in code"
      echo "  - Semgrep: No security anti-patterns"
      echo "  - Rationale: Keyboard monitoring is security-sensitive"
      echo ""
      echo "📋 Complexity:"
      echo "  - Lizard: CCN < 10, Length < 50 lines"
      echo "  - Rationale: Audio/event processing must stay maintainable"
      echo ""
      echo "📋 Testing:"
      echo "  - Pytest: >75% code coverage"
      echo "  - Rationale: Reliability critical for system-level daemon"
      echo ""
      echo "📋 Code Quality:"
      echo "  - Black: Python formatting"
      echo "  - Ruff: Python linting"
      echo "  - Rationale: Consistent codebase for contributors"
      echo ""
      echo "✅ All quality gates active"
      echo "🤖 Run 'devenv test' to verify all gates"
      echo "🔍 Run 'quality-check' for comprehensive analysis"
    '';

    setup-dev.exec = ''
      echo "🔧 Setting up Whisper Dictation development environment..."
      echo ""

      # Setup git hooks
      echo "📋 Installing git hooks..."
      devenv shell git-hooks.installationScript

      # Create Cursor AI rules
      echo "📋 Setting up Cursor AI integration..."
      mkdir -p .cursor/rules

      # Create .cursorignore
      cat > .cursorignore << 'EOF'
# Build artifacts
.devenv/
result
result-*
dist/
build/
__pycache__/
*.pyc
*.pyo

# Testing
.pytest_cache/
.coverage
htmlcov/
.tox/

# Environment
.env
.env.*

# Temporary files
/tmp/
*.wav
*.mp3

# IDE
.vscode/
.idea/
EOF

      echo ""
      echo "✅ Development environment ready!"
      echo ""
      echo "📋 Next steps:"
      echo "  1. Review Cursor AI rules in .cursor/rules/"
      echo "  2. Run 'test' to verify test suite"
      echo "  3. Run 'run-daemon' to test dictation"
      echo "  4. Run 'quality-check' before commits"
    '';

    setup-git-hooks.exec = ''
      echo "🔧 Setting up git hooks..."
      devenv shell git-hooks.installationScript
      echo "✅ Git hooks installed"
      echo "📋 Hooks will run automatically on commit/push"
    '';

    # Format all code
    format.exec = ''
      echo "🎨 Formatting code..."
      black src/ tests/
      ruff check --fix src/ tests/
      echo "✅ Code formatted"
    '';
  };

  # https://devenv.sh/pre-commit-hooks/
  git-hooks.hooks = {
    # Python formatting and linting
    black = {
      enable = true;
      files = "\\.py$";
      excludes = [ ".devenv/" "result" ];
    };

    ruff = {
      enable = true;
      files = "\\.py$";
      excludes = [ ".devenv/" "result" ];
    };

    # Security scanning
    gitleaks = {
      enable = true;
      name = "gitleaks-security-scan";
      entry = "${pkgs.gitleaks}/bin/gitleaks detect --source .";
      excludes = [ ".devenv/" "result" ];
    };

    # Code complexity check (system-wide tool)
    complexity-check = {
      enable = true;
      name = "complexity-check";
      entry = "lizard --CCN 10 --length 50";
      files = "\\.py$";
      excludes = [ ".devenv/" "result" "tests/" ];
    };

    # Security pattern detection
    semgrep = {
      enable = true;
      name = "security-patterns";
      entry = "${pkgs.semgrep}/bin/semgrep --config=auto --error";
      files = "\\.py$";
      excludes = [ ".devenv/" "result" "tests/" ];
    };

    # Run tests before commit
    pytest = {
      enable = true;
      name = "pytest-check";
      entry = "${pkgs.python312Packages.pytest}/bin/pytest tests/ -q";
      pass_filenames = false;
    };

    # Commit message formatting
    commitizen = {
      enable = true;
      name = "commitizen-check";
      entry = "${pkgs.python3Packages.commitizen}/bin/cz check --commit-msg-file";
      stages = [ "commit-msg" ];
    };
  };

  enterShell = ''
    hello
  '';
}
