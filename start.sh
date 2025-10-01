#!/usr/bin/env bash
set -euo pipefail

# start.sh - create a virtualenv, install requirements, run migrations, and start the
# Django development server on 0.0.0.0 so the app can be accessed on the LAN.
# Usage: ./start.sh [PORT]

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV="$DIR/.venv"
REQ_FILE="$DIR/requirements.txt"
MANAGE_PY="$DIR/manage.py"

PORT="${1:-8000}"

echo "Project dir: $DIR"

if [ ! -f "$MANAGE_PY" ]; then
  echo "manage.py not found in $DIR. Run this script from the project root." >&2
  exit 2
fi

# Choose python executable
PYTHON_BIN="${PYTHON:-python3}"

echo "Using python: $(command -v "$PYTHON_BIN" || true)"

if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
  echo "Python executable '$PYTHON_BIN' not found. Install Python 3 and try again." >&2
  exit 3
fi

if [ ! -d "$VENV" ]; then
  echo "Creating virtual environment in $VENV..."
  "$PYTHON_BIN" -m venv "$VENV"
fi

# shellcheck source=/dev/null
source "$VENV/bin/activate"

echo "Upgrading pip and installing requirements..."
python -m pip install --upgrade pip setuptools wheel

if [ -f "$REQ_FILE" ]; then
  python -m pip install -r "$REQ_FILE"
else
  echo "requirements.txt not found at $REQ_FILE; skipping pip install." >&2
fi

echo "Applying migrations..."
python "$MANAGE_PY" migrate --noinput

# Collect static if settings configured for it (safe no-op if not configured)
if python - <<'PY' 2>/dev/null
import importlib, sys
try:
    import django
    from django.conf import settings
    print('OK')
except Exception:
    sys.exit(1)
PY
then
  echo "Collecting static files (if configured)..."
  python "$MANAGE_PY" collectstatic --noinput || true
fi

echo "Starting Django development server on 0.0.0.0:$PORT"
exec python "$MANAGE_PY" runserver 0.0.0.0:"$PORT"
