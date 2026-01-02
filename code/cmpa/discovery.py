from __future__ import annotations

from pathlib import Path
from typing import List, Optional, Tuple

from .model import ComparatorId, ComparatorMeta


def _split_comparator_name(name: str) -> Optional[Tuple[str, str]]:
    if "-" not in name:
        return None
    a, b = name.split("-", 1)
    a, b = a.strip(), b.strip()
    if not a or not b:
        return None
    return a, b


def discover_comparators(root: Path) -> List[ComparatorMeta]:
    """
    Zakłada:
    root/
      A-B/
        A-B.yml
        A-B.dat  (i/lub wiele plików .dat)
    """
    metas: List[ComparatorMeta] = []
    for d in sorted([p for p in root.iterdir() if p.is_dir()]):
        if _split_comparator_name(d.name) is None:
            continue

        cid = ComparatorId(d.name)
        yml = d / f"{d.name}.yml"
        if not yml.exists():
            # fallback: jakby był .yaml
            yml2 = d / f"{d.name}.yaml"
            yml = yml2 if yml2.exists() else None

        dats = sorted(d.glob("*.dat"))

        metas.append(
            ComparatorMeta(
                cid=cid,
                folder=d,
                yml_path=yml if yml and yml.exists() else None,
                dat_paths=list(dats),
            )
        )
    return metas
