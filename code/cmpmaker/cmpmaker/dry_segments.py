from pathlib import Path
from typing import List, Tuple, Set
import importlib

from .import_trace import clear_import_trace, get_imported_modules
from .import_hook import install_import_hook
from .mjd_context import set_current_mjd
from .version_utils import list_version_thresholds


def detect_mjd_segments(
    *,
    entry: str,
    from_mjd: float,
    to_mjd: float,
) -> List[Tuple[float, float]]:
    """
    entry: np. "scripts.comparators.A"
    """

    # --- dry-run ---
    clear_import_trace()
    install_import_hook()
    set_current_mjd(from_mjd)

    importlib.import_module(entry)

    used = get_imported_modules()  # fullname -> file path

    # --- zbieramy progi ---
    cuts: Set[float] = {from_mjd, to_mjd}

    for fullname, path in used.items():
        # np. scripts.shift.x -> folder .../shift/x/
        folder = path.parent
        name = folder.name          # <-- TO JEST NAZWA SKRYPTU
        print(name)



        thresholds = list_version_thresholds(folder, name)
        for t in thresholds:
            if from_mjd < t < to_mjd:
                cuts.add(t)

    cuts_sorted = sorted(cuts)

    segments = list(zip(cuts_sorted[:-1], cuts_sorted[1:]))
    return segments
