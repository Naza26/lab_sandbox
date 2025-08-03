#!/usr/bin/env bash
set -euo pipefail

# --- paths ---
INSTALL_BASE=/tmp/inscopix
GUI_WRAPPER_DIR="$INSTALL_BASE/Inscopix Data Processing 1.9.6"
GUI_BIN="$GUI_WRAPPER_DIR/Inscopix Data Processing"
INPUT_FOLDER=/data
OUTPUT_FOLDER=/output
EXPECTED_OUTPUT=${EXPECTED_OUTPUT_FILE:-"${OUTPUT_FOLDER}/done.marker"}

if [ ! -d "$GUI_WRAPPER_DIR" ]; then
    echo "[entrypoint] Installing ISX into $INSTALL_BASE..."
    mkdir -p "$INSTALL_BASE"
    pushd "$INSTALL_BASE" >/dev/null

    if [ ! -f /opt/installer.sh ]; then
        echo "ERROR: /opt/installer.sh not found inside container. Listing /opt:"
        ls -la /opt
        exit 1
    fi

    # Run installer without chmod since /opt/installer.sh is on read-only mount
    bash /opt/installer.sh

    popd >/dev/null
else
    echo "[entrypoint] ISX already installed."
fi




# 2. Launch GUI headlessly
if [ ! -x "$GUI_BIN" ]; then
    echo "ERROR: GUI launcher not found at '$GUI_BIN'"
    exit 2
fi

echo "[entrypoint] Starting ISX GUI via xvfb..."
xvfb-run -n 99 -s "-screen 0 1920x1080x24" "$GUI_BIN" &
ISX_PID=$!
echo "[entrypoint] ISX GUI PID: $ISX_PID"

# small warm-up
sleep 5

# 3. Wait for completion sentinel
echo "[entrypoint] Waiting for expected output at '$EXPECTED_OUTPUT'..."
MAX_WAIT=${MAX_WAIT_SECONDS:-600}
INTERVAL=5
elapsed=0

while [ ! -f "$EXPECTED_OUTPUT" ]; do
    if [ "$elapsed" -ge "$MAX_WAIT" ]; then
        echo "[entrypoint] Timeout after ${MAX_WAIT}s; killing ISX GUI."
        kill "$ISX_PID" || true
        exit 1
    fi
    sleep "$INTERVAL"
    elapsed=$((elapsed + INTERVAL))
done

echo "[entrypoint] Detected output. Shutting down ISX GUI..."
kill "$ISX_PID" || true
wait "$ISX_PID" 2>/dev/null || true

echo "[entrypoint] Done. Results are in '$OUTPUT_FOLDER'."
