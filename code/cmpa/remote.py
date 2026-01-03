from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Tuple

import numpy as np

from .model import ComparatorMeta, Graph
from .graph import find_path_nodes
from .rawplot import AlignedSeries


@dataclass
class RemoteResult:
    mjd: np.ndarray
    rho: np.ndarray          # rho(goal/start)
    tilde_rho: np.ndarray    # rho/rho0_prod - 1  (najczęściej najwygodniejsze)
    rho0_prod: float         # iloczyn nominalny
    path_nodes: List[str]
    step_comparators: List[str]


def _rho0(meta: ComparatorMeta) -> float:
    if meta.rho0_num is None or meta.rho0_den is None:
        raise ValueError(f"Missing rho0 in YAML for {meta.cid.name}")
    return float(meta.rho0_num) / float(meta.rho0_den)


def _sB(meta: ComparatorMeta) -> float:
    return float(meta.sB) if meta.sB is not None else 1.0


def _meta_for_edge(metas_map: Dict[str, ComparatorMeta], a: str, b: str) -> Tuple[ComparatorMeta, bool]:
    """
    Zwraca (meta, forward)
    forward=True  jeśli istnieje komparator 'a-b'
    forward=False jeśli istnieje tylko 'b-a' (użyjemy odwrócenia).
    """
    n1 = f"{a}-{b}"
    n2 = f"{b}-{a}"
    if n1 in metas_map:
        return metas_map[n1], True
    if n2 in metas_map:
        return metas_map[n2], False
    raise KeyError(f"Missing comparator for edge {a}<->{b} (tried {n1} and {n2})")


def compute_remote_ratio_from_path_series(
    g: Graph,
    metas: List[ComparatorMeta],
    path_series: List[AlignedSeries],
    start: str,
    goal: str,
    *,
    nu0_ref: float,
) -> RemoteResult:
    """
    Liczy zdalny stosunek częstotliwości między goal/start dla ścieżki BFS.
    Wymaga:
      - path_series: lista AlignedSeries (po jednym na każdy krok ścieżki),
        w tej samej kolejności co kroki w ścieżce start->goal.
      - nu0_ref: nominalna częstotliwość referencyjna ν0^0 używana do normalizacji (z formalizmu).
        Dla zegarów optycznych sensownie podać np. CIPM value dla jednego z zegarów.
    """
    metas_map = {m.cid.name: m for m in metas}

    path_nodes = find_path_nodes(g, start, goal)
    if path_nodes is None:
        raise ValueError(f"No path between '{start}' and '{goal}'")

    steps = list(zip(path_nodes, path_nodes[1:]))
    if len(steps) != len(path_series):
        raise ValueError("path_series length does not match number of edges in the selected path.")

    # wspólna maska czasu: tylko tam gdzie wszystkie komparatory mają flag>=2
    valid = np.ones_like(path_series[0].flag, dtype=bool)
    for s in path_series:
        valid &= (s.flag >= 1)

    t = path_series[0].t_mjd[valid]
    if t.size == 0:
        raise ValueError("No common valid seconds across all comparators on the path (flags>=2).")

    # policz rho0_prod i sumę R(t)
    rho0_prod = 1.0
    R_sum = np.zeros_like(t, dtype=float)
    step_names: List[str] = []

    # prefiksowy iloczyn nominali (potrzebny w R_i)
    prefix = 1.0

    for (a, b), s in zip(steps, path_series):
        meta, forward = _meta_for_edge(metas_map, a, b)
        step_names.append(meta.cid.name)

        rho0_step = _rho0(meta)
        sB_step = _sB(meta)

        # Δ(t) tylko w ważnych sekundach
        delta = s.delta[valid]

        if forward:
            # traversal zgodny z definicją komparatora A->B
            prefix *= rho0_step
            # R_i(t) ~ Δ * (sB/nu0_ref) / prefix
            R = delta * (sB_step / nu0_ref) / prefix
            rho0_prod *= rho0_step
        else:
            # traversal w stronę przeciwną niż definicja komparatora
            # 1) nominal w drugą stronę: 1/rho0
            rho0_inv = 1.0 / rho0_step
            prefix *= rho0_inv

            # 2) w formalizmie w drugą stronę pojawia się zmiana znaku (pierwszy rząd)
            #    (1/(1+R) ≈ 1 - R), więc przybliżenie: R_rev ≈ -R_fwd
            R = - delta * (sB_step / nu0_ref) / prefix

            rho0_prod *= rho0_inv

        R_sum += R

    tilde_rho = R_sum
    rho = rho0_prod * (1.0 + tilde_rho)

    return RemoteResult(
        mjd=t,
        rho=rho,
        tilde_rho=tilde_rho,
        rho0_prod=float(rho0_prod),
        path_nodes=path_nodes,
        step_comparators=step_names,
    )
