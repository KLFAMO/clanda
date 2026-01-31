from pathlib import Path
from typing import Dict, Set

# fullname -> Path do faktycznego pliku wersji
_IMPORTED_MODULES: Dict[str, Path] = {}

def register_import(fullname: str, path: Path) -> None:
    _IMPORTED_MODULES[fullname] = path

def clear_import_trace() -> None:
    _IMPORTED_MODULES.clear()

def get_imported_modules() -> Dict[str, Path]:
    return dict(_IMPORTED_MODULES)
