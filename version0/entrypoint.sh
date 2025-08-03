#!/usr/bin/env bash
set -euo pipefail

INSTALL_BASE=/tmp/inscopix
MARKER="$INSTALL_BASE/.installed"
OUTPUT_FOLDER=/output
EXPECTED_OUTPUT=${EXPECTED_OUTPUT_FILE:-"${OUTPUT_FOLDER}/done.marker"}

echo "[entrypoint] glibc: $(ldd --version | head -1)"
echo "[entrypoint] Using Python: $(which python) ($(python --version 2>&1))"

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

    if [ ! -f /opt/installer.sh ]; then
        echo "ERROR: installer missing at /opt/installer.sh"
        ls -la /opt
        exit 1
    fi

    pushd "$INSTALL_BASE" >/dev/null
    bash /opt/installer.sh --skip-license || {
        echo "ERROR: ISX installer failed; check its output above."
        exit 1
    }
    popd >/dev/null

    touch "$MARKER"
    echo "[entrypoint] ISX installed."
else
    echo "[entrypoint] Using existing ISX installation."
fi

# 2. Resolve canonical installation path to avoid issues with spaces/nesting
INSTALL_ROOT=$(realpath "$INSTALL_BASE/Inscopix Data Processing.linux")
API_DIR="$INSTALL_ROOT/Contents/API/Python"
EXPECTED_SO="$API_DIR/libisxpublicapi.so"

echo "[entrypoint] Resolved INSTALL_ROOT as: $INSTALL_ROOT"
echo "[entrypoint] API_DIR is: $API_DIR"
echo "[entrypoint] Checking native library at: $EXPECTED_SO"

if [ ! -d "$API_DIR" ]; then
    echo "ERROR: expected Python API directory missing at $API_DIR"
    ls -R "$INSTALL_ROOT/Contents/API" | head -n 200
    exit 2
fi

if [ ! -r "$EXPECTED_SO" ]; then
    echo "FATAL: native API library missing or unreadable at $EXPECTED_SO"
    ls -l "$API_DIR"
    exit 3
fi

# 3. Upgrade pip/tooling
python -m pip install --upgrade pip setuptools wheel

# 4. Install the editable isx API
pip install -e "$API_DIR"

# 5. Install immediate dependencies that isx needs
pip install numpy scipy pandas scikit-learn matplotlib tifffile imagecodecs

# 6. Echo installed versions for visibility
echo "[entrypoint] Installed key Python package versions:"
python - <<'PY'
import importlib
pkgs = ["numpy", "scipy", "pandas", "sklearn", "matplotlib", "tifffile"]
for pkg in pkgs:
    try:
        m = importlib.import_module(pkg)
        ver = getattr(m, "__version__", "unknown")
        print(f"{pkg}: {ver}")
    except ImportError:
        print(f"{pkg}: MISSING")
PY

# 7. Run bootstrap/pipeline
export PYTHONPATH="$API_DIR:${PYTHONPATH:-}"
echo "[entrypoint] Running bootstrap pipeline..."
if ! python /app/bootstrap.py; then
    echo "ERROR: bootstrap.py failed. Performing direct import diagnostic for isx..."
    python - <<'PY'
import traceback
try:
    import isx
    print("isx import succeeded, version:", getattr(isx, "__version__", "unknown"))
except Exception:
    traceback.print_exc()
    raise
PY
    exit 4
fi

# 8. Signal completion
mkdir -p "$OUTPUT_FOLDER"
touch "$EXPECTED_OUTPUT"
echo "[entrypoint] Done. Created sentinel at $EXPECTED_OUTPUT."
