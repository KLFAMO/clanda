from cmpmaker.runner import run
from cmpa.calc import (
    # discover_comparators,
    # build_connection_graph,
    # find_path_nodes,
    # path_to_edges,
    calc_nodes_ratio,
)

mjd = 60763

run(
    # script_path="comparators/UMK_LO-UMK_RLS",
    script_path="comparators/UMK_LO-UMK_Sr1",
    from_mjd=mjd,
    to_mjd=mjd + 0.1,
    plot=True,
    create_cmp_file=True,
)

mts = calc_nodes_ratio(
        fmjd=mjd,
        tmjd=mjd+1,
        start_node='PTB_Sr3_CombKnoten',
        goal_node='UMK_Sr1',
    )
# mts.split()
mts.plot()