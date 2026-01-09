from timanda.mtserie import MTSerie
from timanda.gtserie import GTserie

from .discovery import discover_comparators
from .graph import build_connection_graph, find_path_nodes, path_to_edges
from pathlib import Path

data_path = Path(__file__).parent.parent.parent / "tock_data"

d = discover_comparators(data_path)
g = build_connection_graph(d)
pn = find_path_nodes(g, "UMK_Sr1", "PTB_Sr3_CombKnoten")
# pn = find_path_nodes(g, "UMK_Sr1", "NPL_Sr1")
pe = path_to_edges(g, pn)

for u, v, cids in pe:
    print(f"{u} <--> {v}   ({len(cids)}): " + ", ".join(cid.name for cid in cids))

# create list of comparators from pe
comparators = []
for u, v, cids in pe:
    for cid in cids:
        for cmp in d:
            if cmp.cid == cid:
                comparators.append(cmp)
                break  

fmjd = 60760
tmjd = 60761

mjds = list(range(fmjd, tmjd + 1))

# fmjd and tmjd convert to date yyyy-mm-dd

def mjd_to_yyyy_mm_dd(mjd: int) -> str:
    from astropy.time import Time
    t = Time(mjd, format='mjd')
    return t.iso[:10]
fmjd_d = mjd_to_yyyy_mm_dd(fmjd)
tmjd_d = mjd_to_yyyy_mm_dd(tmjd)
print(f"fmjd: {fmjd} -> {fmjd_d}")
print(f"tmjd: {tmjd} -> {tmjd_d}")

mjds_d = [mjd_to_yyyy_mm_dd(mjd) for mjd in mjds]
print("mjds:")
for mjd, mjd_d in zip(mjds, mjds_d):
    print(f"  {mjd} -> {mjd_d}")

gts = GTserie(name="UMK_Sr1->PTB_Sr3_CombKnoten")

for cmp in comparators:
    # each cid.dat_paths has date yyy-mm-dd in filename
    # get only paths with substring date from mjds_d
    print(f"Comparator: {cmp.cid.name}")
    d = MTSerie()
    for mjd_d in mjds_d:
        dat_paths = [p for p in cmp.dat_paths if mjd_d in p.name]
        for dat_path in dat_paths:
            print(f"  {dat_path}")
            d.add_mjdf_from_datfile(
                dat_path,
                delimiter='\t',
                skiprows=0,
            )
            gts.append_mtserie(mts_name=cmp.cid.name, mts=d)
    print("MTS: ", d)
# gts.get_range(60760.6, 60760.7)
gts.align_all_to_grid_zoh_and_drop_missing(
    period_s = 1,
    sh_s = 0.0,
    snap_s = 0.1,
    tol_s = 0.001,
    start_mjd = fmjd,
    stop_mjd = tmjd+1,
    new_gts = False,
    out_name = "aligned_common",
    hold_last = False,
)
# gts.math_mts_and_number("multiply", "UMK_LO-UMK_Sr1", -1, "minus" )
# gts.math_mts_and_mts("add", "UMK_LO-UMK_RLS", "minus", "out")
# gts.math_mts_and_mts("add", "PTB_Si-PTB_Sr3_CombKnoten", "out", "final")
gts.plot()
