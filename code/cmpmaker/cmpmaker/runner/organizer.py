from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

from timanda.gtserie import GTserie

from .resolver import collect_change_points, normalize_logical_name


def build_segments(*, from_mjd: float, to_mjd: float, change_points: list[float]) -> list[tuple[float, float]]:
    if to_mjd <= from_mjd:
        raise ValueError("to_mjd must be greater than from_mjd")

    points = [from_mjd, *change_points, to_mjd]
    points = sorted(set(points))

    segments: list[tuple[float, float]] = []
    for start, stop in zip(points[:-1], points[1:]):
        if stop > start:
            segments.append((start, stop))
    return segments


def run_segment(
    *,
    script_name: str,
    from_mjd: float,
    to_mjd: float,
    kwargs: dict[str, Any],
    result_file: str,
) -> dict[str, Any]:
    payload = {
        "script_name": script_name,
        "from_mjd": from_mjd,
        "to_mjd": to_mjd,
        "kwargs": kwargs,
        "result_file": result_file,
    }

    proc = subprocess.run(
        [sys.executable, "-m", "cmpmaker.runner.worker"],
        input=json.dumps(payload),
        text=True,
        capture_output=True,
    )

    if proc.returncode != 0:
        raise RuntimeError(
            "Segment execution failed.\n"
            f"script_name={script_name}\n"
            f"from_mjd={from_mjd}\n"
            f"to_mjd={to_mjd}\n"
            f"STDOUT:\n{proc.stdout}\n"
            f"STDERR:\n{proc.stderr}"
        )

    return json.loads(proc.stdout)


def merge_gts_list(gts_list: list[GTserie]) -> GTserie | None:
    if not gts_list:
        return None

    out = gts_list[0].copy()
    for gts in gts_list[1:]:
        out.extend_from(gts)

    return out


def calc(
    script_name: str,
    *,
    from_mjd: float,
    to_mjd: float,
    output_file: str | None = None,
    keep_temp_dir: bool = False,
    temp_dir: str | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """
    Main API.

    Przykład:
        calc(
            "comparators.UMK_LO_UMK_Sr1",
            from_mjd=60761.3,
            to_mjd=60762.8,
            plot=False,
        )
    """
    logical_name = normalize_logical_name(script_name)

    print(f"Calculating '{logical_name}' from MJD {from_mjd} to {to_mjd}", file=sys.stderr)
    print(f"logical_name={logical_name}", file=sys.stderr)

    change_points = collect_change_points(logical_name, from_mjd, to_mjd)
    print(f"Found change points: {change_points}", file=sys.stderr)

    segments = build_segments(
        from_mjd=from_mjd,
        to_mjd=to_mjd,
        change_points=change_points,
    )
    print(f"Built segments: {segments}", file=sys.stderr)

    segment_results: list[dict[str, Any]] = []
    segment_objects: list[GTserie] = []

    if temp_dir is not None:
        base_tmp = Path(temp_dir)
        base_tmp.mkdir(parents=True, exist_ok=True)
        tmp_context = None
        run_dir = base_tmp
    else:
        tmp_context = tempfile.TemporaryDirectory(prefix="cmpmaker_run_")
        run_dir = Path(tmp_context.name)

    try:
        print(f"Temporary run dir: {run_dir}", file=sys.stderr)

        for i, (seg_from, seg_to) in enumerate(segments):
            safe_from = str(seg_from).replace(".", "p")
            safe_to = str(seg_to).replace(".", "p")
            result_file = run_dir / f"segment_{i:03d}_{safe_from}_{safe_to}.npz"

            meta = run_segment(
                script_name=logical_name,
                from_mjd=seg_from,
                to_mjd=seg_to,
                kwargs=kwargs,
                result_file=str(result_file),
            )
            segment_results.append(meta)

            gts = GTserie.load_npz(result_file)
            segment_objects.append(gts)

            print(f"Loaded segment file: {result_file}", file=sys.stderr)
            print(f"Segment result meta: {meta}", file=sys.stderr)

        merged_result = merge_gts_list(segment_objects)

        if merged_result is not None:
            if output_file is not None:
                merged_file = Path(output_file)
                merged_file.parent.mkdir(parents=True, exist_ok=True)
            else:
                merged_file = run_dir / "result.npz"

            merged_result.dump_npz(merged_file, compress=True)

            merged_meta = {
                "result_file": str(merged_file),
                "result_format": "gts_npz",
            }
        else:
            merged_meta = None

        out = {
            "script_name": logical_name,
            "from_mjd": from_mjd,
            "to_mjd": to_mjd,
            "change_points": change_points,
            "segments": segment_results,
            "merged_result": merged_result,
            "merged_meta": merged_meta,
            "temp_dir": str(run_dir),
        }

        if not keep_temp_dir and temp_dir is None:
            # zwracasz obiekt w pamięci, ale pliki tymczasowe znikną po wyjściu z contextu
            pass

        return out

    finally:
        if tmp_context is not None and not keep_temp_dir:
            tmp_context.cleanup()