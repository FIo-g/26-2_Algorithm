"""Exactness checks against Dijkstra (standard library only).

A result is correct when its distance matches the reference within rel_tol and its
path is a real s-t path in the graph whose cost equals the reported distance.
Paths are not compared with the reference path: ties can give different optimal paths.
No timing happens here; timing comes only after these checks pass (bench.py).
"""
from __future__ import annotations

import math
from collections.abc import Callable, Iterable, Sequence

from routing.dijkstra import dijkstra
from routing.graph import Graph

ABS_TOL = 1e-9


def path_cost(g: Graph, path: Sequence[int]) -> float | None:
    """Sum of edge times along path, or None if some consecutive pair is not an edge."""
    if any(not 0 <= v < g.n for v in path):
        return None
    total = 0.0
    for u, v in zip(path, path[1:]):
        w = g.weight(u, v)
        if w is None:
            return None
        total += w
    return total


def check_result(g: Graph, s: int, t: int, ref_dist: float, result, *,
                 rel_tol: float = 1e-9) -> list[str]:
    """Error messages for result = (dist, path, settled); an empty list means it passed."""
    dist, path = result[0], list(result[1])
    if math.isinf(ref_dist):
        if dist != math.inf or path:
            return [f"unreachable target needs (inf, []), got ({dist}, {path[:5]}...)"]
        return []
    errors = []
    if not math.isclose(dist, ref_dist, rel_tol=rel_tol, abs_tol=ABS_TOL):
        errors.append(f"distance {dist!r} != reference {ref_dist!r}")
    if not path:
        return errors + ["empty path for a reachable target"]
    if path[0] != s:
        errors.append(f"path starts at {path[0]}, not {s}")
    if path[-1] != t:
        errors.append(f"path ends at {path[-1]}, not {t}")
    cost = path_cost(g, path)
    if cost is None:
        errors.append("path uses an edge that is not in the graph")
    elif not math.isclose(cost, dist, rel_tol=rel_tol, abs_tol=ABS_TOL):
        errors.append(f"path cost {cost!r} != reported distance {dist!r}")
    return errors


def verify_all(g: Graph, queries: Iterable, algos: dict[str, Callable], *,
               ref: str = "dijkstra") -> list[str]:
    """Check every algorithm on every query (objects with .qid, .s, .t) against the reference.

    The reference is algos[ref] when present, otherwise routing.dijkstra. Returns
    "{algo} q{qid}: ..." messages; an empty list means everything is exact.
    """
    reference = algos.get(ref, dijkstra)
    messages = []
    for q in queries:
        ref_result = reference(g, q.s, q.t)
        ref_dist = ref_result[0]
        for name, algo in algos.items():
            try:
                # The reference ran once above; reuse it so its path is still checked.
                result = ref_result if name == ref else algo(g, q.s, q.t)
                issues = check_result(g, q.s, q.t, ref_dist, result)
            except Exception as e:  # a crash is a failed check, not a reason to stop the gate
                issues = [f"raised {type(e).__name__}: {e}"]
            messages.extend(f"{name} q{q.qid}: {issue}" for issue in issues)
    return messages
