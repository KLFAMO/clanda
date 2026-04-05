from __future__ import annotations

import ast
import importlib
import math
import re
from dataclasses import dataclass
from pathlib import Path

from .mjd_context import get_current_mjd


CMPMAKER_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_ROOT = CMPMAKER_ROOT / "scripts"

IMPORT_PREFIXES = (
    "cmpmaker.scripts.",
    "scripts.",   # opcjonalnie tolerowane przy analizie AST
)

VERSION_RE = re.compile(r"^(?P<stem>.+)__mjd_(?P<mjd>\d+(?:p\d+)?)\.py$")


@dataclass(frozen=True)
class VersionedFile:
    logical_name: str
    module_path: str
    file_path: Path
    valid_from: float


@dataclass(frozen=True)
class ResolvedTarget:
    kind: str  # "family" albo "module"
    logical_name: str
    module_path: str
    file_path: Path
    valid_from: float


def normalize_logical_name(name: str) -> str:
    """
    Przyjmuje np.:
      - "comparators.UMK_LO_UMK_Sr1"
      - "comparators/UMK_LO_UMK_Sr1.py"
      - "cmpmaker.scripts.sr1_budget"
      - "scripts.sr1_budget"
    i zwraca nazwę logiczną względną do cmpmaker/scripts.
    """
    name = name.strip().replace("\\", "/")

    if name.endswith(".py"):
        name = name[:-3]

    if name.startswith("cmpmaker.scripts."):
        name = name[len("cmpmaker.scripts."):]
    elif name.startswith("scripts."):
        name = name[len("scripts."):]

    name = name.replace("/", ".").strip(".")
    return name


def mjd_token_to_float(token: str) -> float:
    """
    "60761p9" -> 60761.9
    "60761"   -> 60761.0
    """
    return float(token.replace("p", "."))


def logical_name_to_module_path(logical_name: str) -> str:
    return f"cmpmaker.scripts.{logical_name}"


def module_file_for_logical_name(logical_name: str) -> Path:
    parts = logical_name.split(".")
    if not parts:
        raise ValueError("Empty logical name.")
    return SCRIPTS_ROOT.joinpath(*parts[:-1], f"{parts[-1]}.py")


def family_dir_for_logical_name(logical_name: str) -> Path:
    return SCRIPTS_ROOT.joinpath(*logical_name.split("."))


def is_family(logical_name: str) -> bool:
    family_dir = family_dir_for_logical_name(logical_name)
    return family_dir.is_dir() and (family_dir / "__init__.py").exists()


def is_plain_module(logical_name: str) -> bool:
    return module_file_for_logical_name(logical_name).is_file()


def discover_family_versions(logical_name: str) -> list[VersionedFile]:
    family_dir = family_dir_for_logical_name(logical_name)
    if not family_dir.is_dir():
        raise FileNotFoundError(f"Family directory does not exist: {family_dir}")

    base_stem = family_dir.name
    versions: list[VersionedFile] = []

    base_file = family_dir / f"{base_stem}.py"
    if base_file.is_file():
        versions.append(
            VersionedFile(
                logical_name=logical_name,
                module_path=f"{logical_name_to_module_path(logical_name)}.{base_stem}",
                file_path=base_file,
                valid_from=float("-inf"),
            )
        )

    for path in family_dir.glob(f"{base_stem}__mjd_*.py"):
        match = VERSION_RE.match(path.name)
        if not match:
            continue

        valid_from = mjd_token_to_float(match.group("mjd"))
        versions.append(
            VersionedFile(
                logical_name=logical_name,
                module_path=f"{logical_name_to_module_path(logical_name)}.{path.stem}",
                file_path=path,
                valid_from=valid_from,
            )
        )

    if not versions:
        raise FileNotFoundError(
            f"No version files found for family '{logical_name}' in {family_dir}"
        )

    versions.sort(key=lambda x: x.valid_from)
    return versions


def resolve_logical_target(logical_name: str, mjd: float) -> ResolvedTarget:
    logical_name = normalize_logical_name(logical_name)

    if is_family(logical_name):
        versions = discover_family_versions(logical_name)
        candidates = [v for v in versions if v.valid_from <= mjd]
        if not candidates:
            raise LookupError(
                f"No version of family '{logical_name}' is valid for MJD={mjd}"
            )
        chosen = candidates[-1]
        return ResolvedTarget(
            kind="family",
            logical_name=logical_name,
            module_path=chosen.module_path,
            file_path=chosen.file_path,
            valid_from=chosen.valid_from,
        )

    if is_plain_module(logical_name):
        file_path = module_file_for_logical_name(logical_name)
        return ResolvedTarget(
            kind="module",
            logical_name=logical_name,
            module_path=logical_name_to_module_path(logical_name),
            file_path=file_path,
            valid_from=float("-inf"),
        )

    raise FileNotFoundError(
        f"Cannot resolve logical target '{logical_name}'. "
        f"Expected either family dir or module file under {SCRIPTS_ROOT}"
    )


def resolve_family_export(package_name: str, package_file: str, attr_name: str):
    """
    Używane przez scripts/<family>/__init__.py.
    package_name np. "cmpmaker.scripts.sr1_budget"
    """
    logical_name = normalize_logical_name(package_name)
    current_mjd = get_current_mjd()
    target = resolve_logical_target(logical_name, current_mjd)
    mod = importlib.import_module(target.module_path)

    try:
        return getattr(mod, attr_name)
    except AttributeError as exc:
        raise AttributeError(
            f"Resolved module '{mod.__name__}' for family '{logical_name}' "
            f"has no attribute '{attr_name}'."
        ) from exc


def parse_script_imports(file_path: Path) -> set[str]:
    """
    Zwraca nazwy logiczne importów spod cmpmaker.scripts.* albo scripts.*.
    """
    src = file_path.read_text(encoding="utf-8")
    tree = ast.parse(src, filename=str(file_path))

    found: set[str] = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            if not node.module:
                continue

            for prefix in IMPORT_PREFIXES:
                if node.module.startswith(prefix):
                    logical_name = normalize_logical_name(node.module)
                    if logical_name:
                        found.add(logical_name)
                    break

        elif isinstance(node, ast.Import):
            for alias in node.names:
                for prefix in IMPORT_PREFIXES:
                    if alias.name.startswith(prefix):
                        logical_name = normalize_logical_name(alias.name)
                        if logical_name:
                            found.add(logical_name)
                        break

    return found


def discover_reachable_families(entry_logical_name: str) -> set[str]:
    """
    Rekurencyjnie znajduje wszystkie rodziny wersjonowanych skryptów,
    do których może dojść analiza startująca od entry_logical_name.

    Dla rodziny analizuje wszystkie jej wersje, żeby nie przegapić zależności
    pojawiających się dopiero w nowszym pliku.
    """
    entry_logical_name = normalize_logical_name(entry_logical_name)
    seen: set[str] = set()
    families: set[str] = set()

    def visit(logical_name: str) -> None:
        logical_name = normalize_logical_name(logical_name)
        if logical_name in seen:
            return
        seen.add(logical_name)

        if is_family(logical_name):
            families.add(logical_name)
            files_to_scan = [v.file_path for v in discover_family_versions(logical_name)]
        elif is_plain_module(logical_name):
            files_to_scan = [module_file_for_logical_name(logical_name)]
        else:
            raise FileNotFoundError(f"Unknown script target: {logical_name}")

        for file_path in files_to_scan:
            for dep in parse_script_imports(file_path):
                visit(dep)

    visit(entry_logical_name)
    return families


def collect_change_points(entry_logical_name: str, from_mjd: float, to_mjd: float) -> list[float]:
    """
    Zwraca wszystkie punkty zmian wersji w otwartym przedziale (from_mjd, to_mjd),
    dla rodzin osiągalnych z danego skryptu wejściowego.
    """
    families = discover_reachable_families(entry_logical_name)
    points: set[float] = set()

    for family in families:
        for version in discover_family_versions(family):
            if math.isfinite(version.valid_from) and from_mjd < version.valid_from < to_mjd:
                points.add(version.valid_from)

    return sorted(points)