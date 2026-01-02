from settings import TOCK_DATA_PATH
import cmpa
from cmpa.rawplot import load_path_series_1hz, plot_path_series

def main():
    metas = cmpa.discover_comparators(TOCK_DATA_PATH)
    metas = [cmpa.load_yaml_into_meta(m) for m in metas]
    g = cmpa.build_connection_graph(metas)

    start = "PTB_Sr3_CombKnoten"
    goal  = "PTB_Yb_CombKnoten"

    t0 = 60752.7
    t1 = 60753.2

    series_list = load_path_series_1hz(g, metas, start, goal, t0, t1, tol_s=0.2)
    plot_path_series(series_list)

if __name__ == "__main__":
    main()
