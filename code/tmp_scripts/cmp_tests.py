from cmpa import (
    build_adjacency,
    build_connection_graph,
    discover_comparators,
    find_path_nodes,
    path_to_edges,
    report_graph,
)
from pathlib import Path

data_path = Path(__file__).parent.parent / "tock_data"

print("*** Discover comparators in the data path ***********************")
cmps = discover_comparators(data_path)
for cmp in cmps:
    print(f"{cmp.cid.name}")

print("\n*** Graph *******************************")
graph_report = build_connection_graph(cmps)
print(report_graph(graph_report))

print("\n*** Find path between two nodes ***********************")
start_node = "UMK_Sr1"
goal_node = "PTB_Sr3_CombKnoten"
path_nodes = find_path_nodes(graph_report, start_node, goal_node)
if path_nodes is None:
    print(f"No path between {start_node} and {goal_node}")
else:
    print(" -> ".join(path_nodes))

edges = path_to_edges(graph_report, path_nodes)
print("\nPath edges:")
for u, v, cids in edges:
    print(f"{u} <--> {v}   ({len(cids)}): " + ", ".join(cid.name for cid in cids))  

print("\n*** Graph adjacency *******************************")
adjacency = build_adjacency(graph_report)
for node in sorted(adjacency.keys()):
    neighbors = adjacency[node]
    neighbor_strs = [f"{nbr} ({len(cids)})" for nbr, cids in neighbors]
    print(f"\n{node}:\n\t" + "\n\t".join(neighbor_strs))  