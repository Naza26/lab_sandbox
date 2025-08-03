#!/usr/bin/env bash
set -euo pipefail

INSTALL_BASE=/tmp/inscopix
MARKER="$INSTALL_BASE/.installed"
OUTPUT_FOLDER=/output
EXPECTED_OUTPUT=${EXPECTED_OUTPUT_FILE:-"${OUTPUT_FOLDER}/done.marker"}

# 1. Install ISX if needed
if [ ! -f "$MARKER" ] || [ ! -d "$INSTALL_BASE/Inscopix Data Processing.linux" ]; then
    echo "[entrypoint] Installing ISX into $INSTALL_BASE..."
    if [ -d "$INSTALL_BASE" ]; then
        shopt -s dotglob
        rm -rf "$INSTALL_BASE"/* || true
        shopt -u dotglob
    else
        mkdir -p "$INSTALL_BASE"
    fi

    pushd "$INSTALL_BASE" >/dev/null
    if [ ! -f /opt/installer.sh ]; then
        echo "ERROR: installer missing at /opt/installer.sh"
        ls -la /opt
        exit 1
    fi
    bash /opt/installer.sh --skip-license
    popd >/dev/null

    touch "$MARKER"
    echo "[entrypoint] ISX installed."
else
    echo "[entrypoint] Using existing ISX installation."
fi

# 2. Prepare Python API
API_DIR="$INSTALL_BASE/Inscopix Data Processing.linux/Contents/API/Python"
if [ ! -d "$API_DIR" ]; then
    echo "ERROR: expected Python API directory missing at $API_DIR"
    exit 2
fi

# Upgrade pip tooling and install the isx API editable
python -m pip install --upgrade pip setuptools wheel
pip install -e "$API_DIR"

# 3. Run bootstrap/pipeline
# Safe expansion when PYTHONPATH might be undefined
export PYTHONPATH="$API_DIR:${PYTHONPATH:-}"
echo "[entrypoint] Running bootstrap pipeline..."
python /app/bootstrap.py

# 4. Signal completion
mkdir -p "$OUTPUT_FOLDER"
touch "$EXPECTED_OUTPUT"
echo "[entrypoint] Done. Created sentinel at $EXPECTED_OUTPUT."
