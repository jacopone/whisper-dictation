#!/usr/bin/env bash
# Pytest hook wrapper that runs within devenv shell
# This ensures all Python dependencies are available

set -e

# Run pytest within devenv shell (which has all Python packages)
exec devenv shell pytest tests/ -q "$@"
