from pathlib import Path
from typing import List

def parse_mjd_token(token: str) -> float:
    parts = token.split("_")
    if len(parts) == 1:
        return float(parts[0])
    return float(parts[0] + "." + "".join(parts[1:]))

def list_version_thresholds(folder: Path, name: str) -> List[float]:
    """
    Zwraca wszystkie mjd z plików name_<mjd>.py
    """
    out = []
    prefix = name + "_"

    for p in folder.iterdir():
        if not p.is_file() or p.suffix != ".py":
            continue
        if not p.stem.startswith(prefix):
            continue
        token = p.stem[len(prefix):]
        try:
            out.append(parse_mjd_token(token))
        except ValueError:
            pass

    return sorted(out)
