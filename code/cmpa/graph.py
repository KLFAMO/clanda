from __future__ import annotations

from typing import List, Tuple

from .model import ComparatorMeta, Graph


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
