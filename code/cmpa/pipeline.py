from __future__ import annotations

from typing import List, Optional

from .model import ComparatorMeta, Graph
from .rawplot import load_path_series_1hz, plot_path_series
from .remote import compute_remote_ratio_from_path_series, RemoteResult
from .plot_remote import plot_remote


def compare_and_plot(
    *,
    g: Graph,
    metas: List[ComparatorMeta],
    start: str,
    goal: str,
    t_start_mjd: float,
    t_stop_mjd: float,
    nu0_ref: float,
    tol_s: float = 0.2,
    plot_raw: bool = True,
    plot_tilde: bool = True,
) -> RemoteResult:
    """
    End-to-end:
      1) ładuje dane Δ dla wszystkich komparatorów na ścieżce start->goal (1 Hz, flag>=2),
      2) opcjonalnie rysuje surowe Δ (multiwykres),
      3) liczy zdalny stosunek częstotliwości rho(goal/start) oraz tilde_rho,
      4) rysuje wynik.
    Zwraca RemoteResult (możesz go potem zapisać/analizować).
    """

    # 1) wczytaj i wyrównaj dane 1 Hz na ścieżce
    path_series = load_path_series_1hz(
        g=g,
        metas=metas,
        start=start,
        goal=goal,
        t_start_mjd=t_start_mjd,
        t_stop_mjd=t_stop_mjd,
        tol_s=tol_s,
    )

    # 2) wykresy surowych Δ na ścieżce (jeden pod drugim)
    if plot_raw:
        plot_path_series(path_series)

    # 3) policz zdalny stosunek częstotliwości
    result = compute_remote_ratio_from_path_series(
        g=g,
        metas=metas,
        path_series=path_series,
        start=start,
        goal=goal,
        nu0_ref=nu0_ref,
    )

    # 4) wykres wyniku
    plot_remote(result, show_tilde=plot_tilde)

    return result
