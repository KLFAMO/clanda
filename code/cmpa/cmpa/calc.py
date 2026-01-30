from __future__ import annotations

from pathlib import Path
from typing import List, Tuple, Dict

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


from typing import List, Optional

def _nu0_ref_from_start_node(metas: List["ComparatorMeta"], start_node: str) -> float:
    """
    """
    candidates: List[float] = []

    for m in metas:
        if not getattr(m, "cid", None) or not getattr(m.cid, "name", None):
            continue

        try:
            B, A = m.cid.name.split("-", 1)
        except ValueError:
            continue

        # pull what we can
        nu0A = getattr(m, "nu0A", None)
        nu0B = getattr(m, "nu0B", None)  # może nie istnieć w Twojej klasie
        rho0 = None
        try:
            rho0 = _rho0(m)  # nominal ratio from YAML, usually rho0_{B,A} for comparator A-B
        except Exception:
            rho0 = None

        if start_node == A:
            if nu0A is not None:
                candidates.append(float(nu0A))
            elif nu0B is not None and rho0 is not None:
                # nu0A = nu0B / rho0_{B,A}
                candidates.append(float(nu0B) / float(rho0))

        elif start_node == B:
            if nu0B is not None:
                candidates.append(float(nu0B))
            elif nu0A is not None and rho0 is not None:
                # nu0B = nu0A * rho0_{B,A}
                candidates.append(float(nu0A) * float(rho0))

    if not candidates:
        raise ValueError(
            f"Cannot determine nu0_ref for start_node='{start_node}'. "
            "No YAML provided nu0 for that node, and no consistent fallback using rho0 was possible."
        )

    # sanity: require consistency (within relative tolerance)
    ref = candidates[0]
    for x in candidates[1:]:
        if abs(x - ref) > 1e-9 * abs(ref):
            raise ValueError(
                f"Inconsistent nominal nu0 for node '{start_node}'. "
                f"Got multiple candidates: {candidates[:5]}{'...' if len(candidates)>5 else ''}"
            )

    return float(ref)


def calc_nodes_ratio(
    fmjd: int = 60760,
    tmjd: int = 60764,
    start_node: str = "UMK_Sr1",
    goal_node: str = "PTB_Sr3_CombKnoten",
    impl: str = "my",
) -> MTSerie:
    if impl == "my":
        return _calc_nodes_ratio(fmjd, tmjd, start_node, goal_node)
    else:
        raise ValueError(f"Unknown impl='{impl}' in calc_nodes_ratio.")

def _calc_nodes_ratio(
    fmjd: int = 60760,
    tmjd: int = 60764,
    start_node: str = "UMK_Sr1",
    goal_node: str = "PTB_Sr3_CombKnoten",
) -> MTSerie:
    gts, edge_info, pn = build_gts_for_path(
        fmjd=fmjd,
        tmjd=tmjd,
        start_node=start_node,
        goal_node=goal_node,
        data_path=data_path,
    )
    ratio = calc_ratio_from_gts(
        gts=gts,
        edge_info=edge_info,
        start_node=start_node,
    )
    return ratio


def calc_ratio_from_gts(
    gts: "GTserie",
    edge_info: List[Tuple[str, str, ComparatorMeta, bool, str]],
    start_node: str,
) -> "MTSerie":

    """
    Liczy remote frequency ratio rho_{n,0}(t) na bazie już wyrównanego GTserie.

    ratio(t) = rho0_prod * (1 + sum_i R_{i-1->i}(t))
    gdzie:
    - rho0_prod = Π rho^0_{i,i-1} wzdłuż ścieżki
    - R_{i-1->i}(t) liczone wg MD z poprawnym mianownikiem i znakiem (forward/reverse).
    """

    available = set(gts.mts_dict.keys())
    if not available:
        raise ValueError("GTserie is empty (no comparator series).")

    # nu0_ref = nominal frequency of the START NODE
    metas_used = [meta for (_a, _b, meta, _forward, _series_name) in edge_info]
    nu0_ref = _nu0_ref_from_start_node(metas_used, start_node)

    print(f"[MODEL] nu0_ref = nu0({start_node}) = {nu0_ref:.6e} Hz")

    # prod_prev = Π rho0 for previous steps (path direction)
    prod_prev = 1.0
    rho0_prod = 1.0

    r_terms: List[str] = []
    tmp_idx = 0

    for (a, b, meta, forward, series_name) in edge_info:

        rho0_yaml = _rho0(meta)
        sB_yaml = _sB(meta)

        if forward:
            # We assume comparator 'a-b' YAML corresponds to Δ_{a->b} and rho0_yaml = rho0_{b,a}
            rho0_step = rho0_yaml
            denom = prod_prev * rho0_step
            scale = (sB_yaml / nu0_ref) / denom

            prod_prev *= rho0_step
            rho0_prod *= rho0_step
            direction = "forward"
        else:
            # We have Δ_{b->a}, but need R_{a->b}:
            # R_{a->b} = - Δ_{b->a} * (s_a/nu0_ref) / prod_prev
            # In comparator 'b-a', its YAML sB is for node 'a' (B=a), so sB_yaml = s_a.
            scale = -(sB_yaml / nu0_ref) / prod_prev

            # Nominal step in path direction is rho0_{b,a}. If YAML is for 'b-a', then rho0_yaml = rho0_{a,b},
            # hence invert for path step:
            rho0_step = 1.0 / rho0_yaml

            prod_prev *= rho0_step
            rho0_prod *= rho0_step
            direction = "reverse"

        tmp_name = f"__tmp_R_{tmp_idx}__"
        tmp_idx += 1

        gts.math_mts_and_number("multiply", series_name, scale, tmp_name)
        r_terms.append(tmp_name)

        print(
            f"[STEP] \n\t{a}->{b}: '{series_name}' ({direction}), "
            f"\n\trho0_yaml={rho0_yaml:.16e}, rho0_step(path)={rho0_step:.16e}, "
            f"\n\tprod_prev(after)={prod_prev:.16e}, scale={scale:.6e}"
        )

    print(f"[MODEL] rho0_prod along path = {rho0_prod:.16e}")

    if not r_terms:
        raise ValueError("No edges/terms in path; cannot compute ratio.")

    # Sum R terms: R_sum
    if len(r_terms) == 1:
        rsum_name = r_terms[0]
    else:
        out_name = "__tmp_sum_0__"
        gts.math_mts_and_mts("add", r_terms[0], r_terms[1], out_name)
        for k in range(2, len(r_terms)):
            next_out = f"__tmp_sum_{k-1}__"
            gts.math_mts_and_mts("add", r_terms[k], out_name, next_out)
            out_name = next_out
        rsum_name = out_name

    # Build constant-1 series on the same grid
    template = next(iter(available))
    gts.math_mts_and_number("multiply", template, 0.0, "__tmp_zero__")
    gts.math_mts_and_number("add", "__tmp_zero__", 1.0, "__tmp_one__")

    # one_plus_R = 1 + R_sum
    gts.math_mts_and_mts("add", "__tmp_one__", rsum_name, "__tmp_one_plus_R__")

    # ratio = rho0_prod * (1 + R_sum)
    gts.math_mts_and_number("multiply", "__tmp_one_plus_R__", rho0_prod, "ratio")

    # return gts.mts_dict["ratio"]
    gts.math_mts_and_number("multiply", rsum_name, 1.0, "ratio_rel")
    return gts.mts_dict["ratio_rel"]


def build_gts_for_path(
    fmjd: int,
    tmjd: int,
    start_node: str,
    goal_node: str,
    data_path: Path,
) -> Tuple["GTserie", List[Tuple[str, str, ComparatorMeta, bool, str]], List[str]]:
    """
    Buduje GTserie zawierające tylko te komparatory, które leżą na ścieżce start->goal,
    wczytuje dane .dat dla zadanego zakresu dni i alignuje je do wspólnej siatki.

    Zwraca: (gts, metas_all, pn)
    - gts: gotowe, wyrównane serie komparatorów na wspólnej siatce
    - metas_all: wszystkie meta (przydaje się dalej do mapowania YAML->meta)
    - pn: lista węzłów na ścieżce (start..goal)
    """
    # 1) discover comparators and load YAMLs into meta
    metas_raw = discover_comparators(data_path)
    metas_all = [load_yaml_into_meta(m) for m in metas_raw]

    # 2) graph and path
    g = build_connection_graph(metas_all)
    pn = find_path_nodes(g, start_node, goal_node)
    pe = path_to_edges(g, pn)

    print("\n[PATH] edges:")
    for u, v, cids in pe:
        print(f"{u} <--> {v}   ({len(cids)}): " + ", ".join(cid.name for cid in cids))

    # 3) list of comparators used on the path (in order of edges)
    used: List[ComparatorMeta] = []
    for u, v, cids in pe:
        for cid in cids:
            for m in metas_all:
                if m.cid == cid:
                    used.append(m)
                    break

    # 3b) edge_info in path order: (a, b, meta, forward, series_name)
    metas_map: Dict[str, ComparatorMeta] = {m.cid.name: m for m in used}
    edge_info: List[Tuple[str, str, ComparatorMeta, bool, str]] = []

    steps: List[Tuple[str, str]] = list(zip(pn, pn[1:]))
    for (a, b) in steps:
        n1 = f"{b}-{a}"
        n2 = f"{a}-{b}"
        if n1 in metas_map:
            edge_info.append((a, b, metas_map[n1], True, n1))
        elif n2 in metas_map:
            edge_info.append((a, b, metas_map[n2], False, n2))
        else:
            # w praktyce nie powinno się zdarzyć, skoro 'used' było z pe,
            # ale zostawiamy sanity check
            raise KeyError(f"Missing comparator meta for edge {a}<->{b}. Tried: {n1}, {n2}")


    # 4) range of days and load data into GTserie
    def mjd_to_yyyy_mm_dd(mjd: int) -> str:
        from astropy.time import Time
        t = Time(mjd, format="mjd")
        return t.iso[:10]

    mjds = list(range(fmjd, tmjd + 1))
    mjds_d = [mjd_to_yyyy_mm_dd(m) for m in mjds]

    # print("\n[MJD range]")
    # print(f"fmjd: {fmjd} -> {mjd_to_yyyy_mm_dd(fmjd)}")
    # print(f"tmjd: {tmjd} -> {mjd_to_yyyy_mm_dd(tmjd)}")

    print("\n[LOAD] Creating GTserie and loading MTSeries:")
    gts = GTserie(name=f"{start_node}->{goal_node}")

    for meta in used:
        print(" -", meta.cid.name)
        mts = MTSerie()
        for day in mjds_d:
            dat_paths = [p for p in meta.dat_paths if day in p.name]
            for dat_path in dat_paths:
                mts.add_mjdf_from_datfile(dat_path, delimiter="\t", skiprows=0)
        gts.append_mtserie(mts_name=meta.cid.name, mts=mts)

    # 5) align data to common grid
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

    print("\n")

    return gts, edge_info, pn

