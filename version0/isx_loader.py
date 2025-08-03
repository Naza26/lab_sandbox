# isx_loader.py
import os
import sys

def ensure_isx():
    """
    Makes the shipped isx Python API importable by injecting its path.
    Returns the imported isx module, or raises a RuntimeError if it fails.
    """
    install_root = os.environ.get(
        "ISX_INSTALL_ROOT",
        "/tmp/inscopix/Inscopix Data Processing.linux"
    )
    api_dir = os.path.join(install_root, "Contents", "API", "Python")
    if not os.path.isdir(api_dir):
        raise RuntimeError(f"isx API directory not found at expected location: {api_dir}")

    if api_dir not in sys.path:
        sys.path.insert(0, api_dir)

    try:
        import isx
    except ImportError as e:
        raise RuntimeError(f"Failed to import isx from {api_dir}") from e

    return isx
