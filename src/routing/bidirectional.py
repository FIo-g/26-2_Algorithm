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
    n, trace = g.n, st.trace
    df, db = [math.inf] * n, [math.inf] * n
    pf, pb = [-1] * n, [-1] * n
    done_f, done_b = [False] * n, [False] * n
    df[s] = db[t] = 0.0
    hf, hb = CountingHeap(st), CountingHeap(st)
    hf.push(0.0, s)
    hb.push(0.0, t)
    mu, meet, settled = math.inf, None, 0  # meet = (u, v): u reached forward, v backward, edge u->v

    while True:
        hf.drop_stale(done_f)
        hb.drop_stale(done_b)
        if hf.top_key() + hb.top_key() >= mu:  # also ends when either side runs dry (inf)
            break
        forward = hf.top_key() <= hb.top_key()
        heap, dist, par, done, other, adj = (
            (hf, df, pf, done_f, db, g.fwd) if forward else (hb, db, pb, done_b, df, g.bwd))
        d, u = heap.pop()
        done[u] = True
        settled += 1
        st.settled += 1
        if trace is not None:
            trace.append(u)
        for v, w in adj[u]:
            st.relaxed += 1
            nd = d + w
            if nd < dist[v]:
                dist[v] = nd
                par[v] = u
                heap.push(nd, v)
            if nd + other[v] < mu:
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
