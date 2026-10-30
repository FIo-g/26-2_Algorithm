"""Benchmark harness: the standard algorithm set, timing, and summaries (standard library only).

Only time queries that already passed the exactness check (verify_all in Task 4).
"""
from __future__ import annotations

import csv
import gc
import math
import statistics
from collections import defaultdict
from functools import partial
from pathlib import Path
from time import perf_counter
from typing import Callable, Iterable, NamedTuple

from routing.astar import astar
from routing.bidirectional import bidirectional_dijkstra
from routing.dijkstra import dijkstra
from routing.graph import Graph
from routing.heap import Stats

Algo = Callable[..., tuple[float, list[int], int]]  # algo(g, s, t, stats=Stats())


class ExactnessError(Exception):
    """An exact algorithm disagreed with Dijkstra; nothing may be timed until it is fixed."""


class Row(NamedTuple):
    graph: str
    scenario: str
    kind: str  # "full" query or "reroute" (current position -> target)
    qid: int
    bin: str
    algo: str
    time_s: float  # median of `repeats` runs
    dist: float
    settled: int
    relaxed: int
    pushes: int
    pops: int


def standard_algos(g_bound: Graph, *, ks=(4, 8, 16), seed: int = 0) -> tuple[dict[str, Algo], dict]:
    """dijkstra, astar, bidir, alt{k}. Bounds (vmax, landmarks) come from g_bound, which may
    differ from the graph being queried (e.g. free-flow bound, congested query graph)."""
    algos: dict[str, Algo] = {
        "dijkstra": dijkstra,
        "astar": partial(astar, vmax=g_bound.vmax),  # bound once, not recomputed per query
        "bidir": bidirectional_dijkstra,
    }
    landmarks: dict = {}
    if ks:
        from routing.alt import alt, preprocess_landmarks  # Task 8

        for k in ks:
            landmarks[k] = preprocess_landmarks(g_bound, k, seed=seed)
            algos[f"alt{k}"] = partial(alt, lm=landmarks[k])
    return algos, landmarks


def _timed(algo: Algo, g: Graph, s: int, t: int) -> tuple[float, tuple, Stats]:
    st = Stats()
    was_enabled = gc.isenabled()
    gc.disable()
    try:
        t0 = perf_counter()
        res = algo(g, s, t, stats=st)
        t1 = perf_counter()
    finally:
        if was_enabled:
            gc.enable()
    return t1 - t0, res, st


def time_all(g: Graph, queries, algos: dict[str, Algo], *, graph: str, scenario: str = "free",
             kind: str = "full", warmup: int = 5, repeats: int = 3) -> list[Row]:
    """Time every query x algorithm. Warm-up runs (first `warmup` queries) are extra and discarded."""
    queries = list(queries)  # may be a generator; it is iterated twice
    for q in queries[:warmup]:
        for algo in algos.values():
            algo(g, q.s, q.t)
    rows: list[Row] = []
    for q in queries:
        for name, algo in algos.items():
            runs = [_timed(algo, g, q.s, q.t) for _ in range(repeats)]
            _, (dist, _, _), st = runs[0]  # counters are deterministic; take the first run's
            rows.append(Row(graph, scenario, kind, q.qid, q.bin, name,
                            statistics.median(r[0] for r in runs), dist,
                            st.settled, st.relaxed, st.pushes, st.pops))
    return rows


def _p95(xs: list[float]) -> float:
    s = sorted(xs)
    return s[max(0, math.ceil(0.95 * len(s)) - 1)]  # nearest-rank


def summarize(rows: Iterable[Row]) -> list[dict]:
    """Per (graph, scenario, kind, bin, algo): n, median_s, p95_s, median_settled, and
    speedup / settled_ratio against dijkstra in the same group (None if dijkstra is absent)."""
    groups: dict[tuple, list[Row]] = defaultdict(list)
    for r in rows:
        groups[(r.graph, r.scenario, r.kind, r.bin, r.algo)].append(r)
    base = {}
    for key, rs in groups.items():
        base[key] = (statistics.median(r.time_s for r in rs), statistics.median(r.settled for r in rs))
    out = []
    for key, rs in groups.items():
        med_s, med_settled = base[key]
        ref = base.get(key[:4] + ("dijkstra",))
        out.append({
            "graph": key[0], "scenario": key[1], "kind": key[2], "bin": key[3], "algo": key[4],
            "n": len(rs), "median_s": med_s, "p95_s": _p95([r.time_s for r in rs]),
            "median_settled": med_settled,
            "speedup": ref[0] / med_s if ref and med_s > 0 else None,
            "settled_ratio": med_settled / ref[1] if ref and ref[1] > 0 else None,
        })
    return out


def write_csv(path: str | Path, rows: Iterable) -> None:
    """Rows may be dicts or NamedTuples; the header comes from the first row."""
    dicts = [r._asdict() if hasattr(r, "_asdict") else dict(r) for r in rows]
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="") as f:
        if dicts:
            w = csv.DictWriter(f, fieldnames=list(dicts[0]))
            w.writeheader()
            w.writerows(dicts)
