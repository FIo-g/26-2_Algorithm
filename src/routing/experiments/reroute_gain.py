"""Static re-routing benefit: keep the free-flow path, or re-plan it on a traffic snapshot.

Stand-in for E4 (SUMO) while E4 is deferred. One vehicle, one snapshot that stays
fixed for the rest of the trip, and no other vehicle reacts. The result is a per-trip
benefit under the snapshot assumptions, not a traffic simulation: crowding onto the
same detour and the share of re-routing vehicles stay out of scope.
"""
from __future__ import annotations

import math
import statistics
from collections import defaultdict

from routing.bench import _p95
from routing.congestion import lower_bound, midpoint
from routing.dijkstra import dijkstra
from routing.verify import path_cost


def _gain(fixed: float, rerouted: float) -> tuple[float, int]:
    """(saving fraction, improved flag); differences within 1e-9 count as no change."""
    if math.isclose(rerouted, fixed, rel_tol=1e-9, abs_tol=1e-9):
        return 0.0, 0
    return (fixed - rerouted) / fixed, 1


def reroute_gain(g0, queries, *, graph, scenarios):
    """Two rows per query and snapshot.

    - depart: the snapshot is known at departure. Kept = the free-flow path timed on
      the snapshot; re-planned = the snapshot's shortest path.
    - midway: the snapshot starts when the vehicle reaches E3's reroute source
      (congestion.midpoint). Both cases drive the first half at free-flow times.

    saving = (kept - re-planned) / kept over the whole trip.
    """
    for g in scenarios.values():
        lower_bound(g0, [g])  # ValueError unless topology and edge order match g0
    rows = []
    for q in queries:
        free, path, _ = dijkstra(g0, q.s, q.t)
        if math.isinf(free):
            raise ValueError(f"query {q.qid} is unreachable on the baseline graph")
        k = path.index(midpoint(g0, q.s, q.t))  # same deterministic Dijkstra path
        first_half = path_cost(g0, path[:k + 1])
        for name, g in scenarios.items():
            for mode, before, rest in (("depart", 0.0, path), ("midway", first_half, path[k:])):
                fixed = before + path_cost(g, rest)
                rerouted = before + dijkstra(g, rest[0], q.t)[0]
                saving, improved = _gain(fixed, rerouted)
                rows.append({"graph": graph, "scenario": name, "mode": mode, "qid": q.qid,
                             "bin": q.bin, "fixed_s": fixed, "reroute_s": rerouted,
                             "saving": saving, "improved": improved})
    return rows


def summarize_gain(rows):
    """Per (graph, scenario, mode) and distance bin, plus bin "all":
    n, n_improved, median/mean/p95 (nearest-rank, as in E2)/max saving."""
    groups = defaultdict(list)
    for r in rows:
        for b in (r["bin"], "all"):
            groups[(r["graph"], r["scenario"], r["mode"], b)].append(r)
    first_seen = {}
    for key in groups:
        first_seen.setdefault(key[:3], len(first_seen))
    out = []
    # Stable sort: bins keep their input order, "all" comes last in each group
    for key in sorted(groups, key=lambda k: (first_seen[k[:3]], k[3] == "all")):
        savings = [r["saving"] for r in groups[key]]
        out.append({"graph": key[0], "scenario": key[1], "mode": key[2], "bin": key[3],
                    "n": len(savings), "n_improved": sum(r["improved"] for r in groups[key]),
                    "median_saving": statistics.median(savings), "mean_saving": statistics.mean(savings),
                    "p95_saving": _p95(savings), "max_saving": max(savings)})
    return out
