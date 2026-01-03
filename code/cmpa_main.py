from settings import TOCK_DATA_PATH
import cmpa
from cmpa.pipeline import compare_and_plot


def main():
    # 1) discovery + YAML
    metas = cmpa.discover_comparators(TOCK_DATA_PATH)
    metas = [cmpa.load_yaml_into_meta(m) for m in metas]

    # 2) graf połączeń
    g = cmpa.build_connection_graph(metas)

    # 3) PARAMETRY ANALIZY (jak podałeś)
    start = "PTB_Sr3_CombKnoten"
    goal  = "UMK_Sr1"

    t0 = 60760.6
    t1 = 60760.7

    # 4) nominalna częstotliwość referencyjna
    # Na tym etapie MUSI być podana jawnie.
    # Jeśli ścieżka obejmuje Sr/Yb, sensowny wybór to CIPM Sr albo Yb.
    # (To później zautomatyzujemy.)
    nu0_ref = 4.2922800422987299e14  # Sr (CIPM)

    # 5) END-TO-END: wczytaj → narysuj Δ → policz → narysuj rho
    result = compare_and_plot(
        g=g,
        metas=metas,
        start=start,
        goal=goal,
        t_start_mjd=t0,
        t_stop_mjd=t1,
        nu0_ref=nu0_ref,
        tol_s=0.2,
        plot_raw=True,     # multiwykres Δ dla każdego komparatora
        plot_tilde=True,   # dodatkowo wykres zredukowanego stosunku
    )

    # 6) krótka diagnostyka w konsoli
    print("Path:")
    print("  " + " -> ".join(result.path_nodes))
    print("Comparators:")
    for c in result.step_comparators:
        print(" -", c)
    print(f"rho0_prod = {result.rho0_prod:.16e}")
    print(f"N points  = {len(result.mjd)}")


if __name__ == "__main__":
    main()
