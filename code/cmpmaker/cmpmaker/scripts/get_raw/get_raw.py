from scripts.datamap import DATAMAP
from timanda.mtserie import MTSerie
from timanda.utils import get_test_mtserie
import sys, os
sys.path.insert(1, '/home/stront/svnSr/progs/mytools/')
import sqldata as sqd

def import_raw(*, from_mjd: float, to_mjd: float):
    """
    Import raw data from database or files as specified in DATAMAP.

    Args:
        from_mjd (float): Start MJD for data import.
        to_mjd (float): End MJD for data import.
        path (str): Directory path to save imported data.
        file_name (str): Base name for saved files.
    """
    for key, val in DATAMAP.items():
        if val["source"]["type"] == "famo_database":
            table = val["source"]["table"]
            mts = sqd.getdata(name=table, from_mjd=from_mjd, to_mjd=to_mjd)
            path = f"../npdata/{key}/{int(from_mjd)}"
            if not os.path.exists(path):
                os.makedirs(path)
            mts.dump_npz(f"{path}/{key}_{from_mjd}.npz")


def import_first_day_raw(from_mjd, to_mjd):
    fmjd = int(from_mjd)
    tmjd = fmjd + 1 - 1e-8
    import_raw(from_mjd=fmjd, to_mjd=tmjd)

def calc(*, from_mjd, to_mjd, **kwargs):
    import_first_day_raw(from_mjd=from_mjd, to_mjd=to_mjd)