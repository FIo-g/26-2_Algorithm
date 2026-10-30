"""A* with a straight-line lower bound: h(v) = haversine(v, t) / vmax (standard library only).

vmax comes from the graph (max length/time), never from an agreed constant. Under
congestion, pass the bound graph's vmax: edges only slow down, so the bound stays valid.
"""
from __future__ import annotations

import math

from routing.dijkstra import walk_back
from routing.graph import Graph, haversine_m
from routing.heap import CountingHeap, Stats

H_SCALE = 1 - 1e-9  # absorbs tiny haversine vs OSMnx length differences so h never overshoots


def astar_heuristic(g: Graph, v: int, t: int, vmax: float) -> float:
    return haversine_m(g.coords[v], g.coords[t]) / vmax * H_SCALE


def astar(g: Graph, s: int, t: int, *, vmax: float | None = None, eps: float = 1.0,
          stats: Stats | None = None) -> tuple[float, list[int], int]:
    """(distance, path, settled count). eps > 1 is Weighted A*: faster, at most eps times longer."""
    if s == t:
        return 0.0, [s], 0
    st = stats if stats is not None else Stats()
    scale = H_SCALE * eps / (g.vmax if vmax is None else vmax)  # vmax = inf -> plain Dijkstra
    coords, ct = g.coords, g.coords[t]
    gs = [math.inf] * g.n
    parent = [-1] * g.n
    done = [False] * g.n
    gs[s] = 0.0
    heap = CountingHeap(st)
    heap.push(haversine_m(coords[s], ct) * scale, s)
    fwd, trace, settled = g.fwd, st.trace, 0
    while heap:
        _, u = heap.pop()
        if done[u]:
            continue  # stale entry
        done[u] = True
        settled += 1
        st.settled += 1
        if trace is not None:
            trace.append(u)
        if u == t:
            return gs[t], walk_back(parent, s, t), settled
        gu = gs[u]
        for v, w in fwd[u]:
            st.relaxed += 1
            nv = gu + w
            if nv < gs[v] and not done[v]:  # no reopening (matters only for eps > 1)
                gs[v] = nv
                parent[v] = u
                heap.push(nv + haversine_m(coords[v], ct) * scale, v)
    return math.inf, [], settled
