from __future__ import annotations

_current_mjd: float | None = None


def set_current_mjd(mjd: float) -> None:
    global _current_mjd
    _current_mjd = float(mjd)


def get_current_mjd() -> float:
    if _current_mjd is None:
        raise RuntimeError("Current MJD is not set.")
    return _current_mjd