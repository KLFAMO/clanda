from __future__ import annotations

from timanda.mtserie import MTSerie

from pathlib import Path
from typing import Iterable, List, Union, Tuple, Optional
import re, shutil

from .paths import DATA_ROOT
import astropy.time as ast

PathLike = Union[str, Path]


def mjd2utc(mjd, strfmt='%Y-%m-%d %H:%M:%S'):
    t = ast.Time(mjd, format='mjd')
    return t.strftime(strfmt)

def get_data_names(
    roots: Union[PathLike, Iterable[PathLike], None] = None,
    *,
    include_hidden: bool = False,
) -> List[str]:
    """
    Return sorted dataset names.

    Assumption: under each root directory, each dataset is a subdirectory:
        DATA_ROOT/<dataset_name>/

    Args:
        roots: one directory or iterable of directories; if None, uses DATA_ROOT
        include_hidden: if False, skip directories starting with '.'

    Returns:
        Sorted list of dataset directory names.
    """
    if roots is None:
        root_list = [Path(DATA_ROOT)]
    elif isinstance(roots, (str, Path)):
        root_list = [Path(roots)]
    else:
        root_list = [Path(r) for r in roots]

    names = set()

    for root in root_list:
        if not root.exists() or not root.is_dir():
            continue

        for p in root.iterdir():
            if not p.is_dir():
                continue
            name = p.name
            if not include_hidden and name.startswith("."):
                continue
            names.add(name)

    return sorted(names)


def list_available_mjds(dataset: str) -> List[float]:
    """
    List available MJD values for a dataset based on subfolder names.

    Assumption:
        DATA_ROOT/<dataset>/<mjd_folder>/
    where <mjd_folder> is a string convertible to float (e.g. "59000" or "59000.123456").

    Returns:
        Sorted list of MJD floats.
    """
    folder = Path(DATA_ROOT) / dataset
    if not folder.is_dir():
        return []

    mjds = set()

    for p in folder.iterdir():
        if not p.is_dir():
            continue
        name = p.name.strip()
        try:
            mjd = float(name)
        except ValueError:
            continue
        mjds.add(mjd)

    return sorted(mjds)


def get_data_single_mjd(
    dataset: str, mjd: int
) -> MTSerie:
    """
    Load MTSerie for a given dataset and MJD.

    Args:
        dataset: dataset name
        mjd: MJD value
    Returns:
        MTSerie object
    """
    file = Path(DATA_ROOT) / dataset / f"{int(mjd):d}" / f"{dataset}_{int(mjd):d}_raw.npz"
    print(f"Loading data from: {file}")
    print(file)
    if not file.is_file():
        raise FileNotFoundError(f"Data file not found: {file}")

    mts = MTSerie()
    mts.append_npz(file)
    return mts


def mk_clean_single_mjd(
    dataset: str, mjd: int, force = False
):
    folder = Path(DATA_ROOT) / dataset / f"{mjd:d}"
    src = folder / f"{dataset}_{mjd:d}_raw.npz"
    dst = folder / f"{dataset}_{mjd:d}_cln.npz"

    if not src.exists():
        raise FileNotFoundError(src)

    if dst.exists() and not force:
        print("clean file already exists")
    else:
        shutil.copy2(src, dst)