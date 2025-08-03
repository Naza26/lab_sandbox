# Inscopix Dockerized Pipeline Infrastructure

## Overview & Motivation

This repository encapsulates a self-contained, reproducible pipeline for using the **Inscopix Data Processing** software and its Python API (`isx`) inside a container. The goal is to make onboarding and execution trivial: a new engineer or CI system should be able to drop in the installer and data, run `docker compose up`, and have everything assemble, execute, and signal completion with minimal friction.

Key motivations:
- **Hermeticity / reproducibility:** All required system-level dependencies, the ISX product, and Python bindings are installed inside a controlled container with a known glibc/Python stack to avoid host inconsistencies.  
- **Idempotent installation:** The entrypoint safely reuses an existing installation unless corrupted or missing, speeding up repeated runs.  
- **Dependency resolution:** `isx` has native and Python dependencies; we ensure those are present and surfaced clearly.  
- **Minimal operator burden:** No manual install steps — drop the installer, mount input/output, and run. Completion is signaled by a marker file for orchestration.  
- **Diagnostics built-in:** The entrypoint emits versioning info, validates critical pieces (native shared object, Python packages), and falls back to direct import diagnostics on failure.

## Repo Components

### 1. `docker-compose.yml`

Defines the service and its runtime wiring.

```yaml
version: "3.9"

services:
  isx_job:
    build: .
    volumes:
      - isx_install:/tmp/inscopix                     # persistent installation cache
      - ./Inscopix_Data_Processing_1.9.6.sh:/opt/installer.sh:ro  # official installer stub
      - ./input:/data:ro                              # read-only input data
      - ./output:/output                              # outputs / sentinel
    environment:
      - EXPECTED_OUTPUT_FILE=/output/done.marker
    tty: true
    restart: "no"

volumes:
  isx_install:
````

**Purpose:**

* `isx_install` volume caches the extracted ISX software so subsequent runs don’t re-download/unpack unnecessarily.
* The installer is mounted read-only; the pipeline drives its execution.
* Input/output are externalized for easy data injection and result collection.
* The environment variable `EXPECTED_OUTPUT_FILE` controls where success is signaled.

### 2. `Dockerfile`

Builds the base environment with a compatible system (glibc ≥ 2.32), Python 3.9, and tooling.

Key points:

* **Base image:** `ubuntu:22.04` ensures the native shared library requirement (`GLIBC_2.32`) is satisfied.
* **Python 3.9:** Installed explicitly; `python` is symlinked to ensure scripts using `python` work.
* **Retry logic:** Installation of packages is retried to tolerate transient network glitches.
* **Tooling upgrade:** `pip`, `setuptools`, and `wheel` are upgraded for reliable package handling.
* **No assumptions about host Python:** All requirements live inside the container.

### 3. `entrypoint.sh`

Central coordinator script invoked when the container starts. Responsibilities:

1. **Environment introspection:** Logs glibc version and Python interpreter to help catch mismatches early.
2. **ISX installation:**

    * Installs the Inscopix Data Processing software if not already present in the persistent volume (`/tmp/inscopix`).
    * Uses a marker file to avoid reinstallation on subsequent runs unless the installation is missing/corrupted.
3. **Path resolution:**

    * Canonically resolves the installation path with `realpath` to avoid issues with spaces or nested directories.
4. **Validation:**

    * Ensures the native shared library (`libisxpublicapi.so`) exists and is readable.
5. **Python API setup:**

    * Upgrades pip tooling.
    * Installs the `isx` API in editable mode.
    * Installs critical Python dependencies (`numpy`, `scipy`, `pandas`, `scikit-learn`, `matplotlib`, `tifffile`, `imagecodecs`).
    * Emits installed versions for visibility.
6. **Pipeline execution:**

    * Sets `PYTHONPATH` so that `isx` can be imported.
    * Runs `bootstrap.py`, which is the adapter for downstream work.
    * On failure, performs a direct diagnostic import to help debug.
7. **Completion signaling:**

    * Touches the sentinel file specified by `EXPECTED_OUTPUT_FILE` to allow orchestrators to detect success.

### 4. `bootstrap.py`

Minimal example “adapter” that:

* Defensively ensures the Python API directory is on `PYTHONPATH`.
* Imports `isx` and fails early if the import fails.
* Logs available attributes (sanity).
* Stubs in example pipeline behavior by listing shipped example scripts.

You should replace the contents of this script with your real processing logic or hook it into higher-level orchestration.

## How to Use

1. **Place prerequisites:**

    * Drop the official installer stub (`Inscopix_Data_Processing_1.9.6.sh`) at the repo root.
    * Populate `./input` with whatever data your pipeline should consume.
    * Ensure `./output` exists or will be created (Docker will create it).

2. **Build and run:**

   ```sh
   docker compose up --build
   ```

3. **Success signal:**

    * After a successful run, you’ll see `/output/done.marker` created.
    * Check logs with `docker compose logs isx_job` for details.

## Core Design Principles

* **Idempotency:** The marker file and persistent volume ensure repeat executions don’t redo heavy installs unless needed.
* **Compatibility:** Using Ubuntu 22.04 + Python 3.9 aligns with the ISX API’s expectations (glibc, supported Python versions).
* **Visibility:** Early logs expose versions and presence of critical pieces; failures stop with actionable diagnostics.
* **Simplicity for new users:** One command (`docker compose up --build`) is all that’s needed to start the pipeline.

## Extending / Optimizing

* **Preinstall Python dependencies in the image:** Move the `pip install numpy ...` into the Dockerfile to avoid re-running them at container startup, reducing latency.
* **Healthcheck:** Add a `HEALTHCHECK` to the Dockerfile to probe `python -c "import isx"` so orchestrators can detect broken runtime without parsing logs.
* **Version pinning:** After determining compatible versions, create a `requirements.txt` or pinned install for deterministic builds.
* **Replace bootstrap stub:** Swap `bootstrap.py` for the real adapter or orchestrator that consumes input data, invokes `isx` logic, and writes outputs.

## Example Invocation (shell)

```sh
# Fresh start
docker compose up --build

# Inspect logs if something goes wrong
docker compose logs isx_job

# Clean rebuild
docker compose build --no-cache
docker compose up
```

## Environment Variables

* `EXPECTED_OUTPUT_FILE`: Path to the sentinel that signals successful completion. Default is `/output/done.marker` if not overridden.

## Volume Roles

* `isx_install` (`/tmp/inscopix`): Caches the installed ISX product between runs.
* `./input`: Read-only input data for the pipeline.
* `./output`: Where results and the completion marker appear.

```
