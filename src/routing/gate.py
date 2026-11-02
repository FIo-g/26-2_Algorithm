"""Exactness gate: every exact algorithm must match Dijkstra before anything is timed (standard library only).

The query CSV is created on first use (seed 42) and reused afterwards, so every
experiment on a graph version sees the same queries.
"""
from __future__ import annotations

from pathlib import Path

from routing.bench import standard_algos
from routing.graph import Graph, load_graph
from routing.queries import Query, load_queries, make_queries, save_queries
from routing.verify import verify_all


def load_or_make_queries(g: Graph, queries_path: str | Path) -> list[Query]:
    path = Path(queries_path)
    if path.exists():
        return load_queries(path, g)
    qs = make_queries(g)
    save_queries(path, g, qs)
    return qs


def run_gate(graph_path: str | Path, queries_path: str | Path, *, algos=None) -> tuple[int, list[str]]:
    """(0, []) when every algorithm is exact on every query, else (1, mismatch messages)."""
    g = load_graph(graph_path)
    qs = load_or_make_queries(g, queries_path)
    if algos is None:
        algos, _ = standard_algos(g)
    msgs = verify_all(g, qs, algos)
    return (1 if msgs else 0), msgs
