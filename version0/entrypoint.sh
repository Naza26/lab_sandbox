#!/usr/bin/env bash
set -euo pipefail

# -------- Config (overridable via env) --------
INSTALL_BASE="${INSTALL_BASE:-/tmp/inscopix}"                  # persistent named volume mount
EXPECTED_OUTPUT="${EXPECTED_OUTPUT_FILE:-/output/done.marker}"
OUTPUT_FOLDER="$(dirname "$EXPECTED_OUTPUT")"

# ISX installer behavior
ISX_INSTALLER_PATH="${ISX_INSTALLER_PATH:-/opt/installer.sh}"  # file or directory (we'll resolve)
ISX_INSTALLER_ARGS="${ISX_INSTALLER_ARGS:-}"                   # e.g., --target /tmp/inscopix (if supported)
ISX_AUTO_ACCEPT="${ISX_AUTO_ACCEPT:-0}"                        # 0=interactive, 1=auto "yes"
FORCE_REINSTALL="${FORCE_REINSTALL:-0}"

# Where to look for ISX (wheel or Python API)
ISX_SEARCH_ROOTS="${ISX_SEARCH_ROOTS:-$INSTALL_BASE:/app}"

# Optional: install your local project in editable mode after setup
# Set LOCAL_EDITABLE_DIR to a dir containing pyproject.toml/setup.cfg/setup.py

# Optional: command to run after setup (e.g., "python /app/main.py")
RUN_AFTER_SETUP="${RUN_AFTER_SETUP:-}"

echo "[entrypoint] Python: $(python -V 2>&1)"
echo "[entrypoint] INSTALL_BASE=${INSTALL_BASE}"
mkdir -p "${INSTALL_BASE}" "${OUTPUT_FOLDER}"

# -------- Normalize installer path --------
INSTALLER="$ISX_INSTALLER_PATH"
if [ -d "$INSTALLER" ]; then
  echo "[entrypoint] ISX_INSTALLER_PATH is a directory: $INSTALLER"
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

# -------- Helper: can we import isx right now? --------
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
if ! _can_import_isx; then
  echo "[entrypoint] Running ISX installer: ${INSTALLER}"
  echo "[entrypoint] Auto-accept=${ISX_AUTO_ACCEPT} | Args='${ISX_INSTALLER_ARGS}'"
  # Many installers ignore CWD; extract in /app then relocate
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
# Prefer bundles that actually contain API/Python/isx
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

# Also relocate top-level Inscopix*.linux (older layouts)
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
  if [ -n "$cand" ]; then
    found_whl="$cand"; break
  fi
done

ISX_API_PARENT=""

if [ -n "$found_whl" ]; then
  echo "[entrypoint] Installing ISX wheel: $found_whl"
  python -m pip install --no-cache-dir "$found_whl"
else
  echo "[entrypoint] No wheel found; trying PYTHONPATH approach..."
  for r in "${roots[@]}"; do
    p="$(find "$r" -type f -name '__init__.py' -path '*/isx/__init__.py' -print -quit 2>/dev/null || true)"
    if [ -n "$p" ]; then
      ISX_API_PARENT="$(dirname "$(dirname "$p")")"   # …/Contents/API/Python (parent of 'isx')
      break
    fi
  done
  if [ -n "$ISX_API_PARENT" ]; then
    export PYTHONPATH="${ISX_API_PARENT}:${PYTHONPATH:-}"
    echo "[entrypoint] ISX API added to PYTHONPATH: ${ISX_API_PARENT}"
  else
    echo "[entrypoint] WARNING: Could not locate ISX Python package under ${ISX_SEARCH_ROOTS}"
  fi
fi

# -------- Persist path (pth) & native libs so new execs work too --------
if [ -n "${ISX_API_PARENT:-}" ]; then
  export ISX_API_PARENT  # for Python to read

  # Write a .pth file into ALL site/dist-packages that this interpreter sees
  python - <<'PY'
import os, sys, sysconfig, site, pathlib
api = os.environ["ISX_API_PARENT"]
candidates = set()

# primary locations for this interpreter
for key in ("purelib", "platlib"):
    p = sysconfig.get_paths().get(key)
    if p: candidates.add(p)

# global site-packages if available
try:
    for p in site.getsitepackages():
        candidates.add(p)
except Exception:
    pass

# any sys.path entries that look like site/dist-packages
for p in sys.path:
    if p and (p.endswith("site-packages") or p.endswith("dist-packages")):
        candidates.add(p)

for p in sorted(candidates):
    try:
        pathlib.Path(p).mkdir(parents=True, exist_ok=True)
        with open(pathlib.Path(p, "inscopix_api.pth"), "w") as f:
            f.write(api + "\n")
        print(f"[entrypoint] wrote {p}/inscopix_api.pth -> {api}")
    except Exception as e:
        print(f"[entrypoint] skip {p}: {e}")
PY

  # Register likely native lib dirs in the bundle so fresh processes resolve .so files
  contents_dir="$(dirname "$(dirname "${ISX_API_PARENT}")")"   # …/Contents
  ldc_conf="/etc/ld.so.conf.d/inscopix.conf"
  touch "$ldc_conf"
  updated=0
  for sub in Frameworks Runtime Linux lib; do
    d="${contents_dir}/${sub}"
    if [ -d "$d" ] && ! grep -qxF "$d" "$ldc_conf"; then
      echo "$d" >> "$ldc_conf"
      echo "[entrypoint] Added to ld.so.conf: $d"
      updated=1
    fi
  done
  [ "$updated" = "1" ] && ldconfig || true
fi

# -------- Ensure Python deps exist (when using PYTHONPATH path) --------
# (If we installed a wheel, pip would have handled deps already.)
missing="$(python - <<'PY'
import pkgutil
need=[p for p in ["numpy","scipy","h5py","pandas","matplotlib","tifffile","openpyxl","seaborn"] if pkgutil.find_loader(p) is None]
print(" ".join(need))
PY
)"
if [ -n "$missing" ]; then
  echo "[entrypoint] Installing missing Python deps: $missing"
  python -m pip install --no-cache-dir $missing
fi

# -------- Optional: install your local project editable --------
if [ -n "${LOCAL_EDITABLE_DIR:-}" ] && { [ -f "${LOCAL_EDITABLE_DIR}/pyproject.toml" ] || [ -f "${LOCAL_EDITABLE_DIR}/setup.cfg" ] || [ -f "${LOCAL_EDITABLE_DIR}/setup.py" ]; }; then
  echo "[entrypoint] Installing your library editable from $LOCAL_EDITABLE_DIR"
  python -m pip install --no-cache-dir -e "$LOCAL_EDITABLE_DIR"
else
  echo "[entrypoint] Skipping editable install. Set LOCAL_EDITABLE_DIR to your package dir if desired."
fi

# -------- Sanity check --------
python - <<'PY'
import os, sys, traceback
print("[python] sys.executable:", sys.executable)
print("[python] sys.path[0:3]:", sys.path[0:3])
try:
    import isx
    print("[python] isx import OK; file:", getattr(isx,"__file__",None))
except Exception:
    print("[python] isx import FAILED:")
    traceback.print_exc()
PY

# -------- Done marker --------
mkdir -p "${OUTPUT_FOLDER}"
touch "$EXPECTED_OUTPUT"
echo "[entrypoint] Done. Created sentinel at $EXPECTED_OUTPUT."

# -------- Optional: run a command after setup --------
if [ -n "${RUN_AFTER_SETUP:-}" ]; then
  echo "[entrypoint] Running post-setup command: $RUN_AFTER_SETUP"
  exec bash -lc "$RUN_AFTER_SETUP"
fi

# Keep container alive if interactive; otherwise exit
if [ -t 1 ]; then
  exec bash
fi
