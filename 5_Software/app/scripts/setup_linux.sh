#!/usr/bin/env bash
# Copyright (c) 2026 DDP Engineering
# This software is licensed under the GNU Affero General Public License v3.0
# (AGPL-3.0) with additional Non-Commercial restriction.
# See the LICENSE and LICENSE_NC.txt files for full license details.
#
# Setup script for VoiceToText app on Linux.
# Creates virtual environment, installs Python dependencies,
# and optionally installs ffmpeg from package manager.
#
# Usage:
#   ./setup_linux.sh
#   ./setup_linux.sh --translate
#   ./setup_linux.sh --translate --argos-src=ro --argos-dst=de
#   ./setup_linux.sh --skip-ffmpeg

set -euo pipefail

INSTALL_TRANSLATE=0
SKIP_FFMPEG=0
ARGOS_SRC=""
ARGOS_DST=""

# -----------------------------------------------------------------------------
# Parse arguments
# -----------------------------------------------------------------------------
for arg in "$@"; do
  case "$arg" in
    --translate) INSTALL_TRANSLATE=1 ;;
    --skip-ffmpeg) SKIP_FFMPEG=1 ;;
    --argos-src=*) ARGOS_SRC="${arg#*=}" ;;
    --argos-dst=*) ARGOS_DST="${arg#*=}" ;;
    *)
      echo "ERROR: Unknown argument: $arg"
      echo "Usage: ./setup_linux.sh [--translate] [--argos-src=<lang>] [--argos-dst=<lang>] [--skip-ffmpeg]"
      exit 1
      ;;
  esac
done

# -----------------------------------------------------------------------------
# Resolve paths
# -----------------------------------------------------------------------------
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
VENV_DIR="$PROJECT_ROOT/.venv"
PYTHON_BIN="$VENV_DIR/bin/python"

echo "========================================"
echo "VoiceToText Setup (Linux)"
echo "========================================"
echo "[setup] Project root: $PROJECT_ROOT"

# -----------------------------------------------------------------------------
# Create virtual environment
# -----------------------------------------------------------------------------
if [[ ! -d "$VENV_DIR" ]]; then
  echo "[setup] Creating virtual environment..."
  python3 -m venv "$VENV_DIR"
fi

# -----------------------------------------------------------------------------
# Install dependencies
# -----------------------------------------------------------------------------
echo "[setup] Upgrading pip..."
"$PYTHON_BIN" -m pip install --upgrade pip

echo "[setup] Installing app + dev dependencies..."
"$PYTHON_BIN" -m pip install -e ".[dev]"

if [[ $INSTALL_TRANSLATE -eq 1 ]]; then
  echo "[setup] Installing translation extras..."
  "$PYTHON_BIN" -m pip install -e ".[translate]"

  if [[ -n "$ARGOS_SRC" && -n "$ARGOS_DST" ]]; then
    echo "[setup] Installing Argos package for ${ARGOS_SRC}->${ARGOS_DST} ..."
    "$PYTHON_BIN" -c '
import sys
from argostranslate import package

src = sys.argv[1].strip().lower()
dst = sys.argv[2].strip().lower()

package.update_package_index()
available = package.get_available_packages()
candidate = next((p for p in available if p.from_code == src and p.to_code == dst), None)
if candidate is None:
    print(f"[setup] ERROR: No Argos package found for {src}->{dst}")
    sys.exit(2)

download_path = candidate.download()
package.install_from_path(download_path)
print(f"[setup] Installed Argos package: {src}->{dst}")
' "$ARGOS_SRC" "$ARGOS_DST"
  else
    echo "[setup] Argos language packages not requested. Use --argos-src/--argos-dst to install."
  fi
fi

# -----------------------------------------------------------------------------
# Ensure ffmpeg availability
# -----------------------------------------------------------------------------
if [[ $SKIP_FFMPEG -eq 0 ]]; then
  if ! command -v ffmpeg >/dev/null 2>&1; then
    echo "[setup] ffmpeg not found. Trying package manager installation..."
    if command -v apt-get >/dev/null 2>&1; then
      sudo apt-get update && sudo apt-get install -y ffmpeg
    elif command -v dnf >/dev/null 2>&1; then
      sudo dnf install -y ffmpeg
    elif command -v pacman >/dev/null 2>&1; then
      sudo pacman -Sy --noconfirm ffmpeg
    else
      echo "[setup] No supported package manager found. Install ffmpeg manually."
    fi
  else
    echo "[setup] ffmpeg found: $(command -v ffmpeg)"
  fi
fi

echo "[setup] Done. Start app with: $VENV_DIR/bin/python -m voice_to_text.main"
echo "[setup] Or after activation: voice-to-text"
