from cmpa import discover_comparators, build_connection_graph, report_graph, find_path_nodes
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