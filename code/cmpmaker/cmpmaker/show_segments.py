from .dry_segments import detect_mjd_segments

def show_segments(entry: str, from_mjd: float, to_mjd: float) -> None:
    segments = detect_mjd_segments(
        entry=entry,
        from_mjd=from_mjd,
        to_mjd=to_mjd,
    )

    print("Detected MJD segments:")
    for a, b in segments:
        print(f"  [{a}, {b})")
