from __future__ import annotations

import importlib.abc
import importlib.machinery
import importlib.util
from pathlib import Path
from typing import Optional

from .mjd_context import get_current_mjd
from .import_trace import register_import

_HOOK_INSTALLED = False


def _parse_mjd_token(token: str) -> float:
    # "60001_234" -> 60001.234
    parts = token.split("_")
    if len(parts) == 1:
        return float(parts[0])
    return float(parts[0] + "." + "".join(parts[1:]))


def _select_version_file(folder: Path, leaf: str, mjd: float) -> Optional[Path]:
    """
    folder: .../<leaf>/
    leaf:   nazwa skryptu (ostatni człon importu)
    """
    best_file = None
    best_ver = None

    prefix = leaf + "_"
    for p in folder.iterdir():
        if not p.is_file() or p.suffix != ".py":
            continue
        stem = p.stem  # bez .py
        if not stem.startswith(prefix):
            continue
        ver_str = stem[len(prefix):]
        try:
            ver = _parse_mjd_token(ver_str)
        except ValueError:
            continue
        if ver <= mjd and (best_ver is None or ver > best_ver):
            best_ver = ver
            best_file = p

    if best_file is not None:
        return best_file

    base_file = folder / f"{leaf}.py"
    if base_file.exists():
        return base_file

    return None


class CmpmakerScriptsFinder(importlib.abc.MetaPathFinder):
    """
    Obsługuje importy:
      import scripts.shift.x
    mapując je na:
      <pkg>/scripts/shift/x/(x_<mjd>.py lub x.py)
    """
    def __init__(self, scripts_root: Path):
        self.scripts_root = scripts_root.resolve()

    def find_spec(self, fullname: str, path, target=None):
        # interesują nas tylko importy "scripts...."
        if fullname == "scripts":
            # namespace package: scripts
            spec = importlib.machinery.ModuleSpec(fullname, loader=None, is_package=True)
            spec.submodule_search_locations = [str(self.scripts_root)]
            return spec

        if not fullname.startswith("scripts."):
            return None

        rel = fullname.split(".")[1:]  # ucinamy "scripts"
        d = self.scripts_root.joinpath(*rel)

        if not d.exists() or not d.is_dir():
            return None

        leaf = rel[-1]
        mjd = get_current_mjd()
        candidate = _select_version_file(d, leaf, mjd=mjd)

        if candidate is None:
            # folder jest pakietem/namespace (nie liściem skryptu)
            spec = importlib.machinery.ModuleSpec(fullname, loader=None, is_package=True)
            spec.submodule_search_locations = [str(d)]
            return spec

        register_import(fullname, candidate)

        loader = importlib.machinery.SourceFileLoader(fullname, str(candidate))
        return importlib.util.spec_from_loader(fullname, loader, origin=str(candidate))


def install_import_hook() -> None:
    """
    Instaluj raz na proces.
    """
    global _HOOK_INSTALLED
    if _HOOK_INSTALLED:
        return

    scripts_root = Path(__file__).resolve().parent / "scripts"
    finder = CmpmakerScriptsFinder(scripts_root=scripts_root)

    import sys
    sys.meta_path.insert(0, finder)

    _HOOK_INSTALLED = True
