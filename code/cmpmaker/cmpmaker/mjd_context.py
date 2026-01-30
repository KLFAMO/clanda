from contextvars import ContextVar

_current_mjd: ContextVar[float | None] = ContextVar("cmpmaker_current_mjd", default=None)

def set_current_mjd(mjd: float) -> None:
    _current_mjd.set(float(mjd))

def get_current_mjd() -> float:
    mjd = _current_mjd.get()
    if mjd is None:
        raise RuntimeError("cmpmaker current_mjd is not set.")
    return float(mjd)
