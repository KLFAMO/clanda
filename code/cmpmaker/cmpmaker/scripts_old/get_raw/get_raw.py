from scripts.datamap import DATAMAP
from timanda.mtserie import MTSerie
from timanda.utils import get_test_mtserie
import sys, os
sys.path.insert(1, '/home/stront/svnSr/progs/mytools/')
import sqldata as sqd

def import_raw(*, from_mjd: float, to_mjd: float, names: list[str] | tuple[str] | set[str] | None = None):
    """
    Import raw data from database or files as specified in DATAMAP.

    Args:
        from_mjd (float): Start MJD for data import.
        to_mjd (float): End MJD for data import.
        names (list/tuple/set, optional): Specific DATAMAP keys to import. If None, import all.
    """
    if names is None:
        selected_keys = set(DATAMAP.keys())
    else:
        selected_keys = set(names)

    for key, val in DATAMAP.items():
        if key not in selected_keys:
            continue
        if val["source"]["type"] == "famo_database":
            table = val["source"]["table"]
            mts = sqd.getdata(name=table, from_mjd=from_mjd, to_mjd=to_mjd)
            path = f"../npdata/{key}/{int(from_mjd)}"
            if not os.path.exists(path):
                os.makedirs(path)
            mts.dump_npz(f"{path}/{key}_{from_mjd}_raw.npz")


def import_first_day_raw(from_mjd, to_mjd, names: list[str] | tuple[str] | set[str] | None = None):
    fmjd = int(from_mjd)
    tmjd = fmjd + 1 - 1e-8
    import_raw(from_mjd=fmjd, to_mjd=tmjd, names=['intensity_698_PD'])

def calc(*, from_mjd, to_mjd, **kwargs):
    import_first_day_raw(from_mjd=from_mjd, to_mjd=to_mjd)