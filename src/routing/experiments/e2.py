"""E2: speedup over Dijkstra, ALT preprocessing cost, and how tight the A*/ALT lower bounds are.

Standard library only. Every algorithm is checked against Dijkstra on every query first;
nothing is timed until all of them are exact (Global Constraints, measurement rules).
"""
from __future__ import annotations

import math
from functools import partial
from statistics import median

from routing.alt import alt_heuristic
from routing.astar import astar_heuristic
from routing.bench import ExactnessError, standard_algos, time_all
from routing.verify import verify_all


def run_e2(g, queries, *, graph, ks=(4, 8, 16), algos=None):
    """Return (rows, prep, tight).

    rows:  one Row per query x algorithm (bench.time_all), the input of summarize().
    prep:  one dict per ALT landmark set: graph, k, k_actual, prep_s, nbytes, breakeven.
    tight: one dict per query x (astar, alt{k}): graph, qid, bin, algo, h0, dist, ratio.

    algos=None builds the standard set on g itself, landmarks included. A caller-supplied
    algos dict has no landmark tables, so prep is empty and tight covers only "astar".
    """
    queries = list(queries)  # may be a generator; it is iterated several times
    if not queries:
        raise ValueError("E2 requires at least one query")
    landmarks = {}
    if algos is None:
        algos, landmarks = standard_algos(g, ks=ks)
    if "dijkstra" not in algos:
        raise ValueError("E2 needs 'dijkstra' in algos (reference and baseline)")

    # Gate: no timer runs until every algorithm matched Dijkstra on every query.
    issues = verify_all(g, queries, algos)
    if issues:
        raise ExactnessError(f"E2 exactness gate failed before timing ({len(issues)} problems):\n"
                             + "\n".join(issues[:10]))

    rows = time_all(g, queries, algos, graph=graph)
    return rows, _prep_rows(rows, landmarks, graph), _tightness_rows(g, queries, rows, algos, landmarks, graph)


def _prep_rows(rows, landmarks, graph):
    """Preprocessing cost per k. prep_s, nbytes and k come from the Landmarks that standard_algos
    already built, so nothing is preprocessed twice.

    breakeven = prep_s / (median Dijkstra time - median ALT time), both medians over ALL queries
    (bins pooled). It is the number of queries after which ALT has paid back its preprocessing;
    inf when ALT is not faster.
    """
    base = median(r.time_s for r in rows if r.algo == "dijkstra")
    out = []
    for k, lm in landmarks.items():
        saving = base - median(r.time_s for r in rows if r.algo == f"alt{k}")
        out.append({"graph": graph, "k": k, "k_actual": lm.k, "prep_s": lm.prep_s, "nbytes": lm.nbytes,
                    "breakeven": lm.prep_s / saving if saving > 0 else math.inf})
    return out


def _tightness_rows(g, queries, rows, algos, landmarks, graph):
    """ratio = h0 / dist, where h0 is the lower bound at the start vertex and dist the true distance.

    Close to 1 means a tight bound (few extra vertices get settled). A* with straight-line
    distance over vmax is far below 1 on roads, which is why it speeds up less than ALT.
    Unreachable pairs (dist = inf) and s == t (dist = 0) have no ratio and are skipped.
    """
    bounds = {}  # algo name -> h0(s, t)
    if "astar" in algos:
        bounds["astar"] = partial(astar_heuristic, g, vmax=g.vmax)
    for k, lm in landmarks.items():
        bounds[f"alt{k}"] = partial(alt_heuristic, lm)
    dist = {r.qid: r.dist for r in rows if r.algo == "dijkstra"}  # true distances, no extra Dijkstra
    out = []
    for q in queries:
        if not 0 < dist[q.qid] < math.inf:
            continue
        for name, h in bounds.items():
            h0 = h(q.s, q.t)
            out.append({"graph": graph, "qid": q.qid, "bin": q.bin, "algo": name,
                        "h0": h0, "dist": dist[q.qid], "ratio": h0 / dist[q.qid]})
    return out
