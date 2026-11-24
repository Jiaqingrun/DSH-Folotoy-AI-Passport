#!/usr/bin/env bash
# Thin launcher: macOS/Linux wrapper around doctor.py (Windows uses doctor.ps1).
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PY="${PYTHON:-}"
if [[ -z "$PY" ]]; then
  if command -v python3 >/dev/null 2>&1; then
    PY=python3
  elif command -v python >/dev/null 2>&1; then
    PY=python
  else
    printf 'python 3.10+ not found (set PYTHON)\n' >&2
    exit 127
  fi
fi
exec "$PY" "$SCRIPT_DIR/doctor.py" "$@"
