from __future__ import annotations

import re
import importlib.util
from pathlib import Path
from typing import Any

_VERSION_RE = re.compile(r"^(?P<base>[A-Za-z]\w*)_(?P<mjd>\d+(?:_\d+)*)\.py$")

def _parse_mjd(token: str) -> float:
    parts = token.split("_")
    return float(parts[0]) if len(parts) == 1 else float(parts[0] + "." + "".join(parts[1:]))

def run(script_path: str, *, from_mjd: float, to_mjd: float, **kwargs: Any) -> Any:
    scripts_root = Path(__file__).resolve().parent / "scripts"
    folder = scripts_root / script_path
    base = Path(script_path).name

    best_file = None
    best_mjd = None

    for p in folder.glob(f"{base}_*.py"):
        m = _VERSION_RE.match(p.name)
        if not m:
            continue
        mjd0 = _parse_mjd(m.group("mjd"))
        if mjd0 <= from_mjd and (best_mjd is None or mjd0 > best_mjd):
            best_mjd, best_file = mjd0, p

    if best_file is None:
        best_file = folder / f"{base}.py"  # fallback “od -inf”
        if not best_file.exists():
            raise FileNotFoundError(f"Missing {base}.py or {base}_<mjd>.py in {folder}")

    spec = importlib.util.spec_from_file_location(best_file.stem, best_file)
    mod = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(mod)

    if not hasattr(mod, "calc"):
        raise AttributeError(f"{best_file} must define calc(from_mjd, to_mjd, **kwargs)")

    return mod.calc(from_mjd=from_mjd, to_mjd=to_mjd, **kwargs)
