# bootstrap.py
import os
import sys

# Ensure the API path is on PYTHONPATH if not already
# (entrypoint already sets PYTHONPATH, this is defensive)
api_dir = "/tmp/inscopix/Inscopix Data Processing.linux/Contents/API/Python"
if api_dir not in sys.path:
    sys.path.insert(0, api_dir)

try:
    import isx
except Exception as e:
    print("Failed to import isx API:", e, file=sys.stderr)
    sys.exit(1)

print("Successfully imported isx. Available attributes sample:", [a for a in dir(isx) if not a.startswith("_")][:30])

# Example stubbed pipeline usage — replace with your real adapter logic
# For demonstration, list the example scripts if present.
examples_dir = os.path.join(api_dir, "isx", "examples")
if os.path.isdir(examples_dir):
    print("Found example scripts:", os.listdir(examples_dir))
else:
    print("No examples directory found at", examples_dir)
