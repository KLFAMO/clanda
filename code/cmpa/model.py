from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Set


@dataclass(frozen=True)
class ComparatorId:
    """Id komparatora, np. 'INRIM_DoPTBSr4-INRIM_LoYb'."""
    name: str

    @property
    def node_a(self) -> str:
        return self.name.split("-", 1)[0]

    @property
    def node_b(self) -> str:
        return self.name.split("-", 1)[1]


@dataclass
class ComparatorMeta:
    cid: ComparatorId
    folder: Path
    yml_path: Optional[Path] = None
    dat_paths: List[Path] = field(default_factory=list)

    # parsed YAML (po normalizacji)
    raw: Dict[str, Any] = field(default_factory=dict)

    # pola typowe
    rho0_num: Optional[float] = None
    rho0_den: Optional[float] = None
    sB: Optional[float] = None

    ref_osc: Optional[str] = None
    interval: Optional[float] = None
    lag: Optional[float] = None
    weighting: Optional[str] = None
    grsA: Optional[float] = None
    nu0A: Optional[float] = None


@dataclass
class Graph:
    """Na start: graf nieskierowany struktury połączeń."""
    nodes: Set[str] = field(default_factory=set)
    edges: Dict[Tuple[str, str], List[ComparatorId]] = field(default_factory=dict)

    def add(self, a: str, b: str, cid: ComparatorId) -> None:
        if not a or not b or a == b:
            return
        u, v = sorted((a, b))
        self.nodes.add(u)
        self.nodes.add(v)
        self.edges.setdefault((u, v), []).append(cid)
