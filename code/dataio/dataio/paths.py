from pathlib import Path
CLANDA_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_DATA_ROOT = CLANDA_ROOT / "npdata"

DATA_ROOT = DEFAULT_DATA_ROOT

def print_paths():
    print(f"CLANDA_ROOT is set to: {CLANDA_ROOT}")
    print(f"DEFAULT_DATA_ROOT is set to: {DEFAULT_DATA_ROOT}")