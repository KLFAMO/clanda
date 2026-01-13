from __future__ import annotations

from collections import deque
from typing import List, Tuple, Optional, Dict

from .model import ComparatorMeta, Graph, ComparatorId


def build_connection_graph(metas: List[ComparatorMeta]) -> Graph:
    g = Graph()
    for m in metas:
        g.add(m.cid.node_a, m.cid.node_b, m.cid)
    return g


def report_graph(g: Graph) -> str:
    lines = []
    lines.append(f"Nodes: {len(g.nodes)}")
    lines.append(f"Edges: {len(g.edges)}")
    lines.append("")
    for (u, v), cids in sorted(g.edges.items()):
        lines.append(f"{u} <--> {v}   ({len(cids)}): " + ", ".join(cid.name for cid in cids))
    return "\n".join(lines)


def build_adjacency(g: Graph) -> Dict[str, List[Tuple[str, List[ComparatorId]]]]:
    """
    Based on edges in Graph. Builds undirected adjacency list.
    adj[u] = [(v, [comparators_u_v]), ...]
    """
    adj: Dict[str, List[Tuple[str, List[ComparatorId]]]] = {n: [] for n in g.nodes}
    for (u, v), cids in g.edges.items():
        adj[u].append((v, cids))
        adj[v].append((u, cids))
    return adj


def find_path_nodes(g: Graph, start: str, goal: str) -> Optional[List[str]]:
    """
    Receives the shortest path in number of edges as a list of nodes:
      [start, ..., goal]
    If no connection → None.
    """
    if start not in g.nodes:
        raise ValueError(f"Unknown start node: {start}")
    if goal not in g.nodes:
        raise ValueError(f"Unknown goal node: {goal}")
    if start == goal:
        return [start]

    adj = build_adjacency(g)

    q = deque([start])
    prev: Dict[str, Optional[str]] = {start: None}

    while q:
        u = q.popleft()
        for v, _cids in adj.get(u, []):
            if v in prev:
                continue
            prev[v] = u
            if v == goal:
                q.clear()
                break
            q.append(v)

    if goal not in prev:
        return None

    # reconstruct path
    path = []
    cur: Optional[str] = goal
    while cur is not None:
        path.append(cur)
        cur = prev[cur]
    path.reverse()
    return path


def path_to_edges(g: Graph, node_path: List[str]) -> List[Tuple[str, str, List[ComparatorId]]]:
    """
    Converts a node path [n0, n1, n2, ...] to a list of steps:
      (n_i, n_{i+1}, [comparators between them])
    """
    steps: List[Tuple[str, str, List[ComparatorId]]] = []
    for a, b in zip(node_path, node_path[1:]):
        u, v = sorted((a, b))
        cids = g.edges.get((u, v), [])
        steps.append((a, b, cids))
    return steps


def format_path(g: Graph, start: str, goal: str) -> str:
    node_path = find_path_nodes(g, start, goal)
    if node_path is None:
        return f"No path between '{start}' and '{goal}'."

    steps = path_to_edges(g, node_path)
    lines = []
    lines.append(f"Path ({len(node_path)-1} edge(s)):")
    lines.append("  " + " -> ".join(node_path))
    lines.append("")
    lines.append("Edges / comparators:")
    for a, b, cids in steps:
        if cids:
            lines.append(f"- {a} <-> {b}: " + ", ".join(cid.name for cid in cids))
        else:
            lines.append(f"- {a} <-> {b}: (no comparator ids found?)")
    return "\n".join(lines)