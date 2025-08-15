#!/usr/bin/env bash
set -euo pipefail

INSTALL_BASE="${INSTALL_BASE:-/tmp/inscopix}"
MARKER="$INSTALL_BASE/.installed"
OUTPUT_FOLDER=/output
EXPECTED_OUTPUT=${EXPECTED_OUTPUT_FILE:-"${OUTPUT_FOLDER}/done.marker"}
INSTALLER="${ISX_INSTALLER_PATH:-/opt/installer.sh}"

echo "[entrypoint] Python: $(which python) ($(python --version 2>&1))"
echo "[entrypoint] INSTALL_BASE=$INSTALL_BASE"

mkdir -p "$INSTALL_BASE" "$OUTPUT_FOLDER"

# 1) Install ISX once into the named volume (if not present)
if [ ! -e "$MARKER" ]; then
  if [ -f "$INSTALLER" ]; then
    echo "[entrypoint] Running ISX installer: $INSTALLER"
    # If the installer supports silent flags, add them here
    bash "$INSTALLER"
    touch "$MARKER"
  else
    echo "[entrypoint] No installer found at $INSTALLER. Skipping install."
  fi
else
  echo "[entrypoint] ISX already installed (marker found)."
fi

# 2) Locate ISX Python API dir (two strategies)
#    A) Prefer a wheel and pip install it (best isolation)
ISX_WHL="$(find "$INSTALL_BASE" -type f -name 'isx-*.whl' | head -n1 || true)"
if [ -n "$ISX_WHL" ]; then
  echo "[entrypoint] Installing ISX wheel: $ISX_WHL"
  python -m pip install --no-cache-dir "$ISX_WHL"
else
  #    B) Fallback: add the dir that contains the 'isx' package to PYTHONPATH
  echo "[entrypoint] Trying PYTHONPATH approach for ISX..."
  ISX_API_DIR="$(find "$INSTALL_BASE" -type d -name 'isx' -printf '%h\n' | head -n1 || true)"
  if [ -n "${ISX_API_DIR:-}" ]; then
    export PYTHONPATH="$ISX_API_DIR:${PYTHONPATH:-}"
    echo "[entrypoint] ISX API directory added to PYTHONPATH: $ISX_API_DIR"
  else
    echo "[entrypoint] WARNING: Could not locate ISX Python package under $INSTALL_BASE"
  fi
fi

# 3) Optionally install your local lib editable (if mounted)
#    Set LOCAL_EDITABLE_DIR to the folder containing pyproject.toml/setup.cfg/setup.py
if [ -n "${LOCAL_EDITABLE_DIR:-}" ] && [ -f "${LOCAL_EDITABLE_DIR}/pyproject.toml" -o -f "${LOCAL_EDITABLE_DIR}/setup.cfg" -o -f "${LOCAL_EDITABLE_DIR}/setup.py" ]; then
  echo "[entrypoint] Installing your library editable from $LOCAL_EDITABLE_DIR"
  python -m pip install --no-cache-dir -e "$LOCAL_EDITABLE_DIR"
else
  echo "[entrypoint] Skipping editable install. Set LOCAL_EDITABLE_DIR to your package dir if desired."
fi

# 4) Sanity check: import isx (and your lib if given)
python - <<'PY'
import os, traceback
print("[python] sys.path ready. Checking imports...")
try:
    import isx
    print("[python] isx import OK; version:", getattr(isx, "__version__", "unknown"))
except Exception:
    print("[python] isx import FAILED:")
    traceback.print_exc()

lib_dir = os.environ.get("LOCAL_EDITABLE_DIR")
if lib_dir:
    # Try to infer package name (very naively). Optional.
    import pathlib, re, sys
    pkg_name = None
    p = pathlib.Path(lib_dir)
    # look for top-level package folder with __init__.py
    for child in p.iterdir():
        if child.is_dir() and (child / "__init__.py").exists():
            pkg_name = child.name
            break
    if pkg_name:
        try:
            __import__(pkg_name)
            print(f"[python] '{pkg_name}' import OK (editable).")
        except Exception:
            print(f"[python] '{pkg_name}' import FAILED:")
            traceback.print_exc()
    else:
        print("[python] Could not infer package name for sanity check.")
PY

# 5) Done marker (useful for compose 'depends_on' or scripting)
touch "$EXPECTED_OUTPUT"
echo "[entrypoint] Done. Created sentinel at $EXPECTED_OUTPUT."

# Keep container alive if interactive; otherwise exit 0
if [ -t 1 ]; then
  exec bash
fi
