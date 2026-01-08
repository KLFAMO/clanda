from timanda.mtserie import MTSerie
from timanda.gtserie import GTserie

from .discovery import discover_comparators
from .graph import build_connection_graph, find_path_nodes, path_to_edges
from pathlib import Path

data_path = Path(__file__).parent.parent.parent / "tock_data"

d = discover_comparators(data_path)
g = build_connection_graph(d)
pn = find_path_nodes(g, "UMK_Sr1", "PTB_Sr3_CombKnoten")
pe = path_to_edges(g, pn)
for u, v, cids in pe:
    print(f"{u} <--> {v}   ({len(cids)}): " + ", ".join(cid.name for cid in cids))