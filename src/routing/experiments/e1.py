"""E1: how large a road graph exhaustive search can handle before it hits the time limit.

Standard library only. Subgraphs grow around Gangnam Station (bfs_subgraph); every
finished exhaustive answer is checked against Dijkstra before it is recorded.
"""
from __future__ import annotations

import gc
import random
from statistics import median
from time import perf_counter

from routing.bench import ExactnessError
from routing.dijkstra import dijkstra
from routing.exhaustive import bfs_subgraph, count_simple_paths, exhaustive_shortest
from routing.graph import Graph
from routing.synthetic import grid_graph
from routing.verify import check_result

GANGNAM_STATION = (37.4979, 127.0276)  # BFS root = nearest vertex (planner's choice)
DIJKSTRA_REPEATS = 3                   # Dijkstra on tiny graphs takes microseconds: take a median
# Corner-to-corner simple paths in a k x k grid, OEIS A007764 (https://oeis.org/A007764).
# k = 6, 7 are too slow to count here (7 x 7 would take over an hour), so the OEIS values are used.
OEIS_GRID_PATHS = {6: 1_262_816, 7: 575_780_564}


def _timed(fn):
    was_enabled = gc.isenabled()
    gc.disable()
    try:
        start = perf_counter()
        result = fn()
        return perf_counter() - start, result
    finally:
        if was_enabled:
            gc.enable()


def run_e1(g: Graph, root: int, *, start_n: int = 10, step: int = 2, per_size: int = 20,
           time_limit_s: float = 10.0, max_n: int = 200) -> list[dict]:
    """One row per query: target_n, actual_n, actual_m, qid, ex_time_s, ex_paths, timed_out, dij_time_s.

    Sizes grow from start_n by step. A size whose actual subgraph has the same number of
    vertices as the previous one is skipped. The run stops after the first size where any
    query timed out (that size is recorded), or once target_n exceeds min(max_n, g.n).
    """
    rows: list[dict] = []
    prev_n = None
    target_n = start_n
    while target_n <= min(max_n, g.n):
        sub = bfs_subgraph(g, root, target_n)
        if sub.n == prev_n or sub.n < 2:
            target_n += step
            continue
        prev_n = sub.n
        rng = random.Random(target_n)
        any_timeout = False
        for qid in range(per_size):
            s = rng.randrange(sub.n)
            t = rng.randrange(sub.n - 1)
            t += t >= s                                   # uniform over t != s
            ex_time, ex = _timed(lambda: exhaustive_shortest(sub, s, t, time_limit_s=time_limit_s))
            dij_times, ref = [], None
            for _ in range(DIJKSTRA_REPEATS):
                dt, ref = _timed(lambda: dijkstra(sub, s, t))
                dij_times.append(dt)
            if not ex.timed_out:
                issues = check_result(sub, s, t, ref[0], (ex.dist, ex.path, 0))
                if issues:
                    raise ExactnessError(f"E1 n={sub.n} q{qid} ({s}->{t}): {'; '.join(issues)}")
            any_timeout |= ex.timed_out
            rows.append({"target_n": target_n, "actual_n": sub.n, "actual_m": sub.m, "qid": qid,
                         "ex_time_s": ex_time, "ex_paths": ex.paths, "timed_out": ex.timed_out,
                         "dij_time_s": median(dij_times)})
        if any_timeout:
            break
        target_n += step
    return rows


def grid_counts() -> list[dict]:
    """Corner-to-corner simple path counts for k x k grids, k = 3..7 (counted, or from OEIS)."""
    out = []
    for k in range(3, 8):
        if k in OEIS_GRID_PATHS:
            out.append({"k": k, "n": k * k, "paths": OEIS_GRID_PATHS[k], "source": "OEIS A007764",
                        "count_s": ""})
        else:
            elapsed, paths = _timed(lambda: count_simple_paths(grid_graph(k, k), 0, k * k - 1))
            out.append({"k": k, "n": k * k, "paths": paths, "source": "counted", "count_s": elapsed})
    return out


def give_up_n(rows: list[dict]) -> int | None:
    """actual_n of the first size where some query timed out, or None."""
    return next((r["actual_n"] for r in rows if r["timed_out"]), None)
