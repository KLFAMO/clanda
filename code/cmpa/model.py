from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Tuple, Set


@dataclass(frozen=True)
class ComparatorId:
    """Id of comparator, ex. 'INRIM_DoPTBSr4-INRIM_LoYb'."""
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
    yml_path: Path | None = None
    dat_paths: List[Path] = field(default_factory=list)

    # parsed YAML (after normalization)
    raw: Dict[str, Any] = field(default_factory=dict)

    # fields from YAML
    rho0_num: float | None = None
    rho0_den: float | None = None
    sB: float | None = None

    ref_osc: str | None = None
    interval: float | None = None
    lag: float | None = None
    weighting: str | None = None
    grsA: float | None = None
    nu0A: float | None = None


@dataclass
class Graph:
    """
    Undirected graph of comparator connections.
    Nodes are strings (oscillator names).
    Edges are pairs of nodes mapped to lists of ComparatorId.
    """
    
    nodes: Set[str] = field(default_factory=set)
    edges: Dict[Tuple[str, str], List[ComparatorId]] = field(default_factory=dict)

    def add(self, a: str, b: str, cid: ComparatorId) -> None:
        if not a or not b or a == b:
            return
        u, v = sorted((a, b))
        self.nodes.add(u)
        self.nodes.add(v)
        self.edges.setdefault((u, v), []).append(cid)
