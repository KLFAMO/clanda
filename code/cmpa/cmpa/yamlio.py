from __future__ import annotations

from typing import Any, Dict, Optional

import yaml

from .model import ComparatorMeta


def _normalize_yaml_root(obj: Any) -> Dict[str, Any]:
    """
    Convert list to dict if necessary

    Args:
        obj (Any): _description_

    Returns:
        Dict[str, Any]: _description_
    """
    if isinstance(obj, dict):
        return obj
    if isinstance(obj, list):
        for el in obj:
            if isinstance(el, dict):
                return el
        return {"_yaml_root": obj}
    return {"_yaml_root": obj}


def _as_float(x: Any) -> Optional[float]:
    try:
        if x is None:
            return None
        return float(x)
    except Exception:
        return None


def _as_str(x: Any) -> Optional[str]:
    if x is None:
        return None
    return str(x)


def load_yaml_into_meta(meta: ComparatorMeta) -> ComparatorMeta:
    """
    Reads YAML and fills meta fields.
    If YAML is missing – leaves meta unchanged.
    Returns updated meta.
    """
    if meta.yml_path is None:
        return meta

    loaded = yaml.safe_load(meta.yml_path.read_text(encoding="utf-8"))
    raw = _normalize_yaml_root(loaded)
    meta.raw = raw

    # typical keys according to optical-link-data-format
    meta.rho0_num = _as_float(raw.get("numrhoBA"))
    meta.rho0_den = _as_float(raw.get("denrhoBA"))
    meta.sB = _as_float(raw.get("sB"))

    meta.ref_osc = _as_str(raw.get("ref_osc"))
    meta.interval = _as_float(raw.get("interval"))
    meta.lag = _as_float(raw.get("lag"))
    meta.weighting = _as_str(raw.get("weighting"))
    meta.grsA = _as_float(raw.get("grsA"))
    meta.nu0A = _as_float(raw.get("nu0A"))
    meta.nu0B = _as_float(raw.get("nu0B"))

    return meta
