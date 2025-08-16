#!/usr/bin/env bash
set -euo pipefail

# -------- Config (overridable via environment) --------
INSTALL_BASE="${INSTALL_BASE:-/tmp/inscopix}"     # persistent named volume mount
EXPECTED_OUTPUT=${EXPECTED_OUTPUT_FILE:-/output/done.marker}
OUTPUT_FOLDER="$(dirname "$EXPECTED_OUTPUT")"

# Installer location & behavior
ISX_INSTALLER_PATH="${ISX_INSTALLER_PATH:-/opt/installer.sh}"
ISX_INSTALLER_ARGS="${ISX_INSTALLER_ARGS:-}"      # e.g. --target /tmp/inscopix (if supported)
ISX_AUTO_ACCEPT="${ISX_AUTO_ACCEPT:-0}"           # 0=require interaction, 1=auto "yes"
FORCE_REINSTALL="${FORCE_REINSTALL:-0}"

# Where we’ll search for ISX bits (a wheel or the Python API)
ISX_SEARCH_ROOTS="${ISX_SEARCH_ROOTS:-$INSTALL_BASE:/app}"

echo "[entrypoint] Python: $(python -V 2>&1)"
echo "[entrypoint] INSTALL_BASE=${INSTALL_BASE}"
mkdir -p "${INSTALL_BASE}" "${OUTPUT_FOLDER}"

# -------- Normalize installer path --------
INSTALLER="$ISX_INSTALLER_PATH"
if [ -d "$INSTALLER" ]; then
  echo "[entrypoint] ISX_INSTALLER_PATH points to a directory: $INSTALLER"
  cand="$(find "$INSTALLER" -maxdepth 1 -type f \( -name '*.sh' -o -name '*.run' -o -name '*.bin' \) -print -quit || true)"
  if [ -n "${cand:-}" ]; then
    INSTALLER="$cand"
    echo "[entrypoint] Resolved installer file: ${INSTALLER}"
  fi
fi
if [ ! -f "$INSTALLER" ]; then
  echo "[entrypoint] ERROR: installer not found at '$INSTALLER'"; exit 1
fi
chmod +x "$INSTALLER" || true

# -------- Optional force reset --------
if [ "$FORCE_REINSTALL" = "1" ]; then
  echo "[entrypoint] FORCE_REINSTALL=1: wiping ${INSTALL_BASE}"
  shopt -s dotglob; rm -rf "${INSTALL_BASE:?}"/* || true; shopt -u dotglob
fi

# -------- Helper: can we import isx? --------
_can_import_isx() {
  python - <<'PY' >/dev/null 2>&1 || return 1
try:
    import isx  # noqa
except Exception:
    raise SystemExit(1)
PY
  return 0
}

# -------- Install ISX (interactive or auto) if needed --------
NEED_INSTALL=0
if ! _can_import_isx; then
  NEED_INSTALL=1
fi

if [ "$NEED_INSTALL" = "1" ]; then
  echo "[entrypoint] Running ISX installer: ${INSTALLER}"
  echo "[entrypoint] Auto-accept=${ISX_AUTO_ACCEPT} | Args='${ISX_INSTALLER_ARGS}'"
  # NOTE: Many installers ignore CWD and always extract to /app; we’ll relocate afterwards.
  if [ "$ISX_AUTO_ACCEPT" = "1" ]; then
    ( cd /app && yes | bash "${INSTALLER}" ${ISX_INSTALLER_ARGS} )
  else
    ( cd /app && bash "${INSTALLER}" ${ISX_INSTALLER_ARGS} )
  fi
else
  echo "[entrypoint] isx already importable; skipping install."
fi

# -------- Relocate from /app into INSTALL_BASE (persistent volume) --------
echo "[entrypoint] Scanning /app for Inscopix payloads to relocate..."
# Find any bundle roots by looking for .../Contents that actually contains API/Python/isx
while IFS= read -r -d '' contents_dir; do
  if [ -f "${contents_dir}/API/Python/isx/__init__.py" ]; then
    root_dir="$(dirname "$contents_dir")"  # parent of Contents
    base="$(basename "$root_dir")"
    dest="${INSTALL_BASE}/${base}"
    if [ -e "$dest" ]; then
      echo "[entrypoint]   Skipping '${base}' (already in ${INSTALL_BASE})"
    else
      echo "[entrypoint]   Copying '${root_dir}' -> '${dest}'"
      cp -a "$root_dir" "$dest"
    fi
  fi
done < <(find /app -maxdepth 3 -type d -name Contents -print0 2>/dev/null || true)

# Also relocate any top-level Inscopix*.linux dirs (covers older installer layouts)
while IFS= read -r -d '' src; do
  base="$(basename "$src")"
  dest="${INSTALL_BASE}/${base}"
  if [ -e "$dest" ]; then
    echo "[entrypoint]   Skipping '${base}' (already in ${INSTALL_BASE})"
  else
    echo "[entrypoint]   Copying '${src}' -> '${dest}'"
    cp -a "$src" "$dest"
  fi
done < <(find /app -maxdepth 2 -type d -iname 'Inscopix*linux*' -print0 2>/dev/null || true)

# -------- Prefer wheel; else add API path to PYTHONPATH --------
echo "[entrypoint] Searching for ISX under: ${ISX_SEARCH_ROOTS}"
found_whl=""
IFS=':' read -r -a roots <<< "$ISX_SEARCH_ROOTS"
for r in "${roots[@]}"; do
  cand="$(find "$r" -type f -name 'isx-*.whl' -print -quit 2>/dev/null || true)"
  if [ -n "$cand" ]; then found_whl="$cand"; break; fi
done

if [ -n "$found_whl" ]; then
  echo "[entrypoint] Installing ISX wheel: $found_whl"
  python -m pip install --no-cache-dir "$found_whl"
else
  echo "[entrypoint] No wheel found; trying PYTHONPATH approach..."
  found_api_parent=""
  for r in "${roots[@]}"; do
    p="$(find "$r" -type f -name '__init__.py' -path '*/isx/__init__.py' -print -quit 2>/dev/null || true)"
    if [ -n "$p" ]; then
      found_api_parent="$(dirname "$(dirname "$p")")"   # parent dir that contains 'isx'
      break
    fi
  done
  if [ -n "$found_api_parent" ]; then
    export PYTHONPATH="${found_api_parent}:${PYTHONPATH:-}"
    echo "[entrypoint] ISX API added to PYTHONPATH: ${found_api_parent}"
  else
    echo "[entrypoint] WARNING: Could not locate ISX Python package under ${ISX_SEARCH_ROOTS}"
  fi
fi

# -------- Ensure Python deps exist when using PYTHONPATH (no wheel = no auto-deps) --------
missing="$(python - <<'PY'
import pkgutil
need=[p for p in ["numpy","scipy","h5py","pandas","matplotlib","tifffile","openpyxl"] if pkgutil.find_loader(p) is None]
print(" ".join(need))
PY
)"
if [ -n "$missing" ]; then
  echo "[entrypoint] Installing missing Python deps: $missing"
  python -m pip install --no-cache-dir $missing
fi

# -------- (Optional) extend LD_LIBRARY_PATH to common bundle dirs --------
# Helps if the vendor ships native libs alongside the Python API.
while IFS= read -r -d '' bundle; do
  for sub in Frameworks Runtime Linux lib; do
    [ -d "$bundle/Contents/$sub" ] && export LD_LIBRARY_PATH="$bundle/Contents/$sub:${LD_LIBRARY_PATH:-}"
  done
done < <(find "$INSTALL_BASE" -maxdepth 1 -type d -name 'Inscopix*' -print0 2>/dev/null || true)
echo "[entrypoint] LD_LIBRARY_PATH=${LD_LIBRARY_PATH:-<unset>}"

# -------- Optional: install your local library in editable mode --------
if [ -n "${LOCAL_EDITABLE_DIR:-}" ] && { [ -f "${LOCAL_EDITABLE_DIR}/pyproject.toml" ] || [ -f "${LOCAL_EDITABLE_DIR}/setup.cfg" ] || [ -f "${LOCAL_EDITABLE_DIR}/setup.py" ]; }; then
  echo "[entrypoint] Installing your library editable from $LOCAL_EDITABLE_DIR"
  python -m pip install --no-cache-dir -e "$LOCAL_EDITABLE_DIR"
else
  echo "[entrypoint] Skipping editable install. Set LOCAL_EDITABLE_DIR to your package dir if desired."
fi

# -------- Sanity check --------
python - <<'PY'
import os, sys, traceback
print("[python] sys.path[0:3]:", sys.path[0:3])
try:
    import isx
    print("[python] isx import OK; file:", getattr(isx,"__file__",None))
except Exception:
    print("[python] isx import FAILED:")
    traceback.print_exc()
PY

# -------- Done marker --------
touch "$EXPECTED_OUTPUT"
echo "[entrypoint] Done. Created sentinel at $EXPECTED_OUTPUT."

# Keep container alive for interactive sessions; otherwise exit
if [ -t 1 ]; then
  exec bash
fi
