"""Bidirectional Dijkstra (standard library only).

Forward search from s on g.fwd, backward search from t on g.bwd. mu is the best
s-t distance seen through any edge joining the two sides. Stop when
top_f + top_b >= mu; stopping at the first vertex settled by both sides is wrong.
"""
from __future__ import annotations

import math

from routing.dijkstra import walk_back
from routing.graph import Graph
from routing.heap import CountingHeap, Stats


def bidirectional_dijkstra(g: Graph, s: int, t: int, *,
                           stats: Stats | None = None) -> tuple[float, list[int], int]:
    """(distance, path, settled count over both sides)."""
    if s == t:
        return 0.0, [s], 0
    st = stats if stats is not None else Stats()
    trace, inf = st.trace, math.inf
    df: dict[int, float] = {s: 0.0}  # dicts/sets, not n-sized arrays (see dijkstra.py)
    db: dict[int, float] = {t: 0.0}
    pf: dict[int, int] = {}
    pb: dict[int, int] = {}
    done_f: set[int] = set()
    done_b: set[int] = set()
    hf, hb = CountingHeap(st), CountingHeap(st)
    hf.push(0.0, s)
    hb.push(0.0, t)
    mu, meet, settled = inf, None, 0  # meet = (u, v): u reached forward, v backward, edge u->v

    while True:
        hf.drop_stale(done_f)
        hb.drop_stale(done_b)
        top_f, top_b = hf.top_key(), hb.top_key()
        if top_f + top_b >= mu:  # also ends when either side runs dry (inf)
            break
        forward = top_f <= top_b
        heap, dist, par, done, other, adj = (
            (hf, df, pf, done_f, db, g.fwd) if forward else (hb, db, pb, done_b, df, g.bwd))
        d, u = heap.pop()
        done.add(u)
        settled += 1
        st.settled += 1
        if trace is not None:
            trace.append(u)
        for v, w in adj[u]:
            st.relaxed += 1
            nd = d + w
            if nd < dist.get(v, inf):
                dist[v] = nd
                par[v] = u
                heap.push(nd, v)
            if nd + other.get(v, inf) < mu:
                mu = nd + other[v]
                meet = (u, v) if forward else (v, u)

    if meet is None:
        return math.inf, [], settled
    u, v = meet
    path = walk_back(pf, s, u)
    while v != t:  # backward parents point one step closer to t
        path.append(v)
        v = pb[v]
    path.append(t)
    return mu, path, settled
