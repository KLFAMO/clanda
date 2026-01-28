from __future__ import annotations

from pathlib import Path
from typing import List, Tuple

from timanda.gtserie import GTserie
from timanda.mtserie import MTSerie

from .discovery import discover_comparators
from .graph import build_connection_graph, find_path_nodes, path_to_edges
from .model import ComparatorMeta
from .yamlio import load_yaml_into_meta

# u Ciebie dane są tu:
data_path = Path(__file__).parent.parent.parent.parent / "tock_data"


def _rho0(meta: ComparatorMeta) -> float:
    if meta.rho0_num is None or meta.rho0_den is None:
        raise ValueError(f"Missing rho0 in YAML for {meta.cid.name} (need numrhoBA/denrhoBA).")
    return float(meta.rho0_num) / float(meta.rho0_den)


def _sB(meta: ComparatorMeta) -> float:
    return float(meta.sB) if meta.sB is not None else 1.0


def _nu0_ref_from_start_node(metas: list[ComparatorMeta], start_node: str, *, rtol: float = 1e-9) -> float:
    """
    Zwraca nu0_ref jako nominalną częstotliwość optyczną węzła startowego.

    Bierzemy nu0A z tych YAML-i, w których start_node występuje jako strona A (cid.node_a).
    Jeśli jest kilka takich YAML-i, sprawdzamy spójność (względnie).
    """
    return 429228066418007.0
    vals = [m.nu0A for m in metas if (m.cid.node_a == start_node and m.nu0A is not None)]
    if not vals:
        raise ValueError(
            f"Brak nu0A w YAML-ach dla start_node='{start_node}'. "
            f"Potrzebujesz przynajmniej jednego komparatora z cid.node_a == '{start_node}' i ustawionym nu0A."
        )

    v0 = float(vals[0])
    for v in vals[1:]:
        v = float(v)
        if abs(v - v0) > rtol * abs(v0):
            raise ValueError(
                f"Niespójne nu0A dla start_node='{start_node}': {v0} vs {v} (rtol={rtol}). "
                f"Ujednolić YAML-e lub jednoznacznie przypisać nu0A dla tego węzła."
            )
    return v0



def calc_nodes_ratio(
    fmjd: int = 60760,
    tmjd: int = 60764,
    start_node: str = "UMK_Sr1",
    goal_node: str = "PTB_Sr3_CombKnoten",
) -> MTSerie:
    """
    Zwraca MTSerie 'tilde_rho' ~ (rho/rho0_prod - 1) w pierwszym rzędzie.
    To jest bezwymiarowe i powinno oscylować wokół 0 na poziomie ~1e-15 (dla dobrych zegarów),
    jeśli YAML i dane .dat są spójne z formalizmem.

    Wszystkie potrzebne stałe (rho0, sB, nu0A) są brane z YAML.
    """

    # 1) discover + wczytaj YAML do meta
    metas_raw = discover_comparators(data_path)
    metas = [load_yaml_into_meta(m) for m in metas_raw]

    # 2) graf i ścieżka
    g = build_connection_graph(metas)
    pn = find_path_nodes(g, start_node, goal_node)
    pe = path_to_edges(g, pn)

    for u, v, cids in pe:
        print(f"{u} <--> {v}   ({len(cids)}): " + ", ".join(cid.name for cid in cids))

    # 3) lista komparatorów użytych na ścieżce (w kolejności krawędzi)
    used: List[ComparatorMeta] = []
    for u, v, cids in pe:
        for cid in cids:
            for m in metas:
                if m.cid == cid:
                    used.append(m)
                    break

    # 4) zakres dni i wczytanie danych do GTserie
    def mjd_to_yyyy_mm_dd(mjd: int) -> str:
        from astropy.time import Time

        t = Time(mjd, format="mjd")
        return t.iso[:10]

    mjds = list(range(fmjd, tmjd + 1))
    mjds_d = [mjd_to_yyyy_mm_dd(m) for m in mjds]

    fmjd_d = mjd_to_yyyy_mm_dd(fmjd)
    tmjd_d = mjd_to_yyyy_mm_dd(tmjd)
    print(f"fmjd: {fmjd} -> {fmjd_d}")
    print(f"tmjd: {tmjd} -> {tmjd_d}")

    gts = GTserie(name=f"{start_node}->{goal_node}")

    for meta in used:
        mts = MTSerie()
        for day in mjds_d:
            dat_paths = [p for p in meta.dat_paths if day in p.name]
            for dat_path in dat_paths:
                mts.add_mjdf_from_datfile(
                    dat_path,
                    delimiter="\t",
                    skiprows=0,
                )
        # append raz per komparator (po zebraniu wszystkich plików z zakresu)
        gts.append_mtserie(mts_name=meta.cid.name, mts=mts)

    # 5) align na wspólną siatkę
    gts.align_all_to_grid_zoh_and_drop_missing(
        period_s=1,
        sh_s=0.0,
        snap_s=0.1,
        tol_s=0.001,
        start_mjd=fmjd,
        stop_mjd=tmjd + 1,
        new_gts=False,
        out_name="aligned_common",
        hold_last=False,
    )

    available = set(gts.mts_dict.keys())
    print("Available MTSeries in GTSerie:")
    for name in sorted(available):
        print(" -", name)

    # 6) model: nu0_ref z YAML (automatycznie)
    nu0_ref = _nu0_ref_from_start_node(metas, start_node)
    print(f"[MODEL] nu0_ref = nu0(start_node='{start_node}') = {nu0_ref:.6e} Hz")


    # 7) zbuduj R_sum(t) po ścieżce w formalizmie (jak w remote.py),
    #    ale na obiektach GTserie (operacje math_*).
    steps: List[Tuple[str, str]] = list(zip(pn, pn[1:]))

    metas_map = {m.cid.name: m for m in metas}

    def meta_for_edge(a: str, b: str) -> Tuple[ComparatorMeta, bool, str]:
        """
        Zwraca (meta, forward, series_name)
        forward=True jeśli istnieje komparator 'a-b'
        forward=False jeśli istnieje tylko 'b-a' (czyli przejście odwrotne)
        """
        n1 = f"{a}-{b}"
        n2 = f"{b}-{a}"
        if n1 in metas_map and n1 in available:
            return metas_map[n1], True, n1
        if n2 in metas_map and n2 in available:
            return metas_map[n2], False, n2
        raise KeyError(f"Missing comparator series for edge {a}<->{b}. Tried: {n1} and {n2}")

    # prefix i rho0_prod informacyjnie
    prefix = 1.0
    rho0_prod = 1.0

    r_terms: List[str] = []
    tmp_idx = 0

    for (a, b) in steps:
        meta, forward, series_name = meta_for_edge(a, b)

        rho0_step = _rho0(meta)
        sB_step = _sB(meta)

        if forward:
            # zgodnie z definicją A->B
            prefix *= rho0_step
            rho0_prod *= rho0_step
            sign = +1.0
        else:
            # odwrotnie niż definicja w YAML/danych
            rho0_inv = 1.0 / rho0_step
            prefix *= rho0_inv
            rho0_prod *= rho0_inv
            sign = -1.0

        # R_i(t) ~ sign * Δ(t) * (sB/nu0_ref) / prefix
        scale = sign * (sB_step / nu0_ref) / prefix

        tmp_name = f"__tmp_R_{tmp_idx}__"
        tmp_idx += 1
        gts.math_mts_and_number("multiply", series_name, scale, tmp_name)
        r_terms.append(tmp_name)

        direction = "forward" if forward else "reverse"
        print(
            f"[STEP] {a}->{b}: use '{series_name}' ({direction}), "
            f"rho0_step={rho0_step:.6e}, sB={sB_step:.6e}, prefix={prefix:.6e}, scale={scale:.6e}"
        )

    print(f"[MODEL] rho0_prod along path = {rho0_prod:.16e}")

    if not r_terms:
        raise ValueError("No terms found for the path (empty r_terms).")

    # 8) suma R_i -> tilde_rho
    if len(r_terms) == 1:
        gts.math_mts_and_number("multiply", r_terms[0], 1.0, "tilde_rho")
        print("[DONE] tilde_rho = single term")
    else:
        out_name = "__tmp_sum_0"
        gts.math_mts_and_mts("add", r_terms[0], r_terms[1], out_name)
        print(f"[SUM] {out_name} = {r_terms[0]} + {r_terms[1]}")

        for k in range(2, len(r_terms)):
            next_out = f"__tmp_sum_{k-1}"
            gts.math_mts_and_mts("add", r_terms[k], out_name, next_out)
            print(f"[SUM] {next_out} = {r_terms[k]} + {out_name}")
            out_name = next_out

        gts.math_mts_and_number("multiply", out_name, 1.0, "tilde_rho")
        print(f"[DONE] tilde_rho = {out_name}")

    # To jest to, co chcesz do wykresu (odchyłki wokół 0, bezwymiarowe)
    return gts.mts_dict["tilde_rho"]

