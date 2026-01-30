from __future__ import annotations

import importlib
from typing import Any

from .import_hook import install_import_hook
from .mjd_context import set_current_mjd


def run(script_path: str, *, from_mjd: float, to_mjd: float, **kwargs: Any) -> Any:
    install_import_hook()
    set_current_mjd(from_mjd)

    module_name = "scripts." + script_path.replace("/", ".")
    mod = importlib.import_module(module_name)

    deps = getattr(mod, "DEPENDENCIES", None)  # lista stringów albo None

    if not hasattr(mod, "calc"):
        raise AttributeError(f"{module_name} must define calc(*, from_mjd, to_mjd, **kwargs)")

    return mod.calc(from_mjd=from_mjd, to_mjd=to_mjd, **kwargs)
