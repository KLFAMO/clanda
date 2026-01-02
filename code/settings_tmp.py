from pathlib import Path

TOCK_DATA_PATH = Path("/full/path/to/data/folder").expanduser().resolve()

if not TOCK_DATA_PATH.exists():
    raise RuntimeError(f"TOCK_DATA_PATH does not exist: {TOCK_DATA_PATH}")
if not TOCK_DATA_PATH.is_dir():
    raise RuntimeError(f"TOCK_DATA_PATH is not a directory: {TOCK_DATA_PATH}")
