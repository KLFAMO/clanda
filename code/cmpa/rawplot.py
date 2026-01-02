from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

import numpy as np
import matplotlib.pyplot as plt

from .model import ComparatorMeta, Graph
from .graph import find_path_nodes


# -------------------------
# Struktury danych
# -------------------------

@dataclass
class AlignedSeries:
    """Dane komparatora wyrównane do siatki 1 Hz."""
    t_mjd: np.ndarray          # (N,) siatka czasu
    delta: np.ndarray          # (N,) Δ, NaN tam gdzie brak danych
    flag: np.ndarray           # (N,) flagi (np.int16), -1 gdy brak
    comparator_name: str       # np. "A-B"
    used_files: List[str]      # lista plików .dat użytych do okna


# -------------------------
# IO
# -------------------------

def _read_dat_file(path: str) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Minimalny reader: MJD, Δ, flag.
    Ignoruje dodatkowe kolumny.
    """
    data = np.genfromtxt(path, comments="#", usecols=(0, 1, 2), dtype=float, invalid_raise=False)
    if data.size == 0:
        return np.array([]), np.array([]), np.array([])
    if data.ndim == 1:
        data = data.reshape(1, -1)

    mjd = data[:, 0]
    delta = data[:, 1]
    flag = data[:, 2].astype(np.int16)
    return mjd, delta, flag


def _load_comparator_window(meta: ComparatorMeta, t0: float, t1: float) -> Tuple[np.ndarray, np.ndarray, np.ndarray, List[str]]:
    """
    Ładuje wszystkie .dat w folderze komparatora i filtruje do okna czasu.
    Założenie: w meta.dat_paths masz listę plików .dat w tym folderze.
    """
    mjd_all = []
    delta_all = []
    flag_all = []
    used_files: List[str] = []

    for p in meta.dat_paths:
        mjd, delta, flag = _read_dat_file(str(p))
        if mjd.size == 0:
            continue

        m = (mjd >= t0) & (mjd <= t1)
        if np.any(m):
            mjd_all.append(mjd[m])
            delta_all.append(delta[m])
            flag_all.append(flag[m])
            used_files.append(str(p))

    if not mjd_all:
        return np.array([]), np.array([]), np.array([]), used_files

    mjd_cat = np.concatenate(mjd_all)
    delta_cat = np.concatenate(delta_all)
    flag_cat = np.concatenate(flag_all)

    # sort po czasie
    idx = np.argsort(mjd_cat)
    return mjd_cat[idx], delta_cat[idx], flag_cat[idx], used_files


# -------------------------
# Siatka 1 Hz i dopasowanie
# -------------------------

def _make_1hz_grid(t0: float, t1: float) -> np.ndarray:
    """
    Tworzy siatkę 1 Hz w MJD, inclusive.
    """
    # sekundy w MJD
    s0 = int(np.ceil(t0 * 86400.0))
    s1 = int(np.floor(t1 * 86400.0))
    if s1 < s0:
        return np.array([], dtype=float)
    sec = np.arange(s0, s1 + 1, dtype=np.int64)
    return sec.astype(float) / 86400.0


def _align_to_grid_1hz(
    mjd: np.ndarray,
    delta: np.ndarray,
    flag: np.ndarray,
    grid_mjd: np.ndarray,
    *,
    tol_s: float = 0.2,
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Mapuje próbki na siatkę 1 Hz.
    - jeśli próbka jest dalej niż tol_s od środka sekundy → ignorujemy
    - jeśli w tej samej sekundzie jest kilka próbek → bierzemy tę z najwyższą flagą,
      a jeśli flagi równe → ostatnią czasowo.
    """
    n = grid_mjd.size
    out_delta = np.full(n, np.nan, dtype=float)
    out_flag = np.full(n, -1, dtype=np.int16)

    if mjd.size == 0 or n == 0:
        return out_delta, out_flag

    grid_sec0 = int(round(grid_mjd[0] * 86400.0))
    # dla każdej próbki policz jej "sekundę"
    sec = mjd * 86400.0
    sec_round = np.rint(sec).astype(np.int64)
    dist = np.abs(sec - sec_round)

    # tolerancja
    ok = dist <= tol_s
    sec_round = sec_round[ok]
    delta = delta[ok]
    flag = flag[ok]
    if sec_round.size == 0:
        return out_delta, out_flag

    idx = sec_round - grid_sec0
    m = (idx >= 0) & (idx < n)
    idx = idx[m]
    delta = delta[m]
    flag = flag[m]

    # wybór próbki w tej samej sekundzie: max(flag), potem "ostatnia"
    for i, d, f in zip(idx, delta, flag):
        if f > out_flag[i]:
            out_flag[i] = f
            out_delta[i] = d
        elif f == out_flag[i]:
            # nadpisz (ostatnia wygrywa)
            out_delta[i] = d

    return out_delta, out_flag


# -------------------------
# Ścieżka + ładowanie serii
# -------------------------

def _meta_by_name(metas: List[ComparatorMeta]) -> Dict[str, ComparatorMeta]:
    return {m.cid.name: m for m in metas}


def _find_meta_for_edge(metas_map: Dict[str, ComparatorMeta], a: str, b: str) -> ComparatorMeta:
    """
    Dla krawędzi a<->b szukamy folderu a-b albo b-a.
    Na tym etapie nie obchodzą nas znaki/formalizm, tylko dane.
    """
    n1 = f"{a}-{b}"
    n2 = f"{b}-{a}"
    if n1 in metas_map:
        return metas_map[n1]
    if n2 in metas_map:
        return metas_map[n2]
    raise KeyError(f"Missing comparator folder for edge {a}<->{b} (tried {n1} / {n2})")


def load_path_series_1hz(
    g: Graph,
    metas: List[ComparatorMeta],
    start: str,
    goal: str,
    t_start_mjd: float,
    t_stop_mjd: float,
    *,
    tol_s: float = 0.2,
) -> List[AlignedSeries]:
    """
    Ładuje dane dla wszystkich komparatorów na ścieżce start->goal,
    wyrównuje do siatki 1 Hz i zwraca listę serii (jedna na komparator).
    """
    path = find_path_nodes(g, start, goal)
    if path is None:
        raise ValueError(f"No path between '{start}' and '{goal}'")

    metas_map = _meta_by_name(metas)
    grid = _make_1hz_grid(t_start_mjd, t_stop_mjd)
    if grid.size == 0:
        raise ValueError("Empty time grid (check t_start_mjd/t_stop_mjd).")

    out: List[AlignedSeries] = []
    for a, b in zip(path, path[1:]):
        meta = _find_meta_for_edge(metas_map, a, b)
        mjd, delta, flag, used_files = _load_comparator_window(meta, t_start_mjd, t_stop_mjd)
        aligned_delta, aligned_flag = _align_to_grid_1hz(mjd, delta, flag, grid, tol_s=tol_s)

        out.append(
            AlignedSeries(
                t_mjd=grid,
                delta=aligned_delta,
                flag=aligned_flag,
                comparator_name=meta.cid.name,
                used_files=used_files,
            )
        )
    return out


# -------------------------
# Plot
# -------------------------

def plot_path_series(series_list: List[AlignedSeries], *, show_flags: bool = False) -> None:
    """
    Rysuje wykresy jeden pod drugim (subplots).
    """
    n = len(series_list)
    fig, axes = plt.subplots(n, 1, sharex=True, figsize=(12, max(2.5, 2.5 * n)))
    if n == 1:
        axes = [axes]

    for ax, s in zip(axes, series_list):
        mask = s.flag >= 1
        ax.plot(s.t_mjd[mask], s.delta[mask])
        # ax.plot(s.t_mjd, s.delta)
        ax.set_ylabel("Δ")
        ax.set_title(s.comparator_name)

        # opcjonalnie: zaznaczyć braki (NaN) jako pionowe linie/markery – na razie pomijam
        if show_flags:
            # pokazuje flagę jako drugi przebieg (na osobnej osi)
            ax2 = ax.twinx()
            ax2.plot(s.t_mjd, s.flag)
            ax2.set_ylabel("flag")

    axes[-1].set_xlabel("MJD")
    fig.tight_layout()
    plt.show()
