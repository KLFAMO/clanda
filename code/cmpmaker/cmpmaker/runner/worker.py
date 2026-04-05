from __future__ import annotations

import importlib
import json
import sys

from .mjd_context import set_current_mjd
from .resolver import normalize_logical_name, resolve_logical_target


def main() -> None:
    payload = json.loads(sys.stdin.read())

    script_name = normalize_logical_name(payload["script_name"])
    from_mjd = float(payload["from_mjd"])
    to_mjd = float(payload["to_mjd"])
    kwargs = payload.get("kwargs", {})
    result_file = payload["result_file"]

    set_current_mjd(from_mjd)

    resolved = resolve_logical_target(script_name, from_mjd)
    mod = importlib.import_module(resolved.module_path)

    calc = getattr(mod, "calc", None)
    if not callable(calc):
        raise AttributeError(
            f"Resolved entry module '{resolved.module_path}' must define callable calc(...)"
        )

    result = calc(
        from_mjd=from_mjd,
        to_mjd=to_mjd,
        result_file=result_file,
        **kwargs,
    )

    output = {
        "script_name": script_name,
        "resolved_entry_module": resolved.module_path,
        "resolved_entry_file": str(resolved.file_path),
        "resolved_entry_valid_from": resolved.valid_from,
        "from_mjd": from_mjd,
        "to_mjd": to_mjd,
        "result_file": result_file,
        "result_format": "gts_npz",
        "result_repr": str(result),
    }

    sys.__stdout__.write(json.dumps(output))


if __name__ == "__main__":
    main()