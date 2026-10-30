"""Dijkstra's algorithm: the reference every other search is checked against (standard library only).

Point-to-point searches keep their state in dicts/sets, never in arrays of size n:
allocating n-sized arrays per query would make short queries cost O(n) and skew timings.
"""
from __future__ import annotations

import heapq
import math
from typing import Mapping

from routing.graph import Graph
from routing.heap import CountingHeap, Stats


def walk_back(parent: Mapping[int, int], s: int, t: int) -> list[int]:
    """Path s..t from a parent array filled by a forward search."""
    path = [t]
    while path[-1] != s:
        path.append(parent[path[-1]])
    path.reverse()
    return path


def dijkstra(g: Graph, s: int, t: int, *, stats: Stats | None = None) -> tuple[float, list[int], int]:
    """(distance, path, settled count). Stops as soon as t is settled."""
    if s == t:
        return 0.0, [s], 0
    st = stats if stats is not None else Stats()
    inf = math.inf
    dist: dict[int, float] = {s: 0.0}
    parent: dict[int, int] = {}
    done: set[int] = set()
    heap = CountingHeap(st)
    heap.push(0.0, s)
    fwd, trace, settled = g.fwd, st.trace, 0
    while heap:
        d, u = heap.pop()
        if u in done:
            continue  # stale entry
        done.add(u)
        settled += 1
        st.settled += 1
        if trace is not None:
            trace.append(u)
        if u == t:
            return d, walk_back(parent, s, t), settled
        for v, w in fwd[u]:
            st.relaxed += 1
            nd = d + w
            if nd < dist.get(v, inf):
                dist[v] = nd
                parent[v] = u
                heap.push(nd, v)
    return math.inf, [], settled


shortest_path = dijkstra  # name used in the spec (4-1)


def sssp(adj: list[list[tuple[int, float]]], s: int) -> list[float]:
    """One-to-all distances over `adj` (g.fwd: from s, g.bwd: to s). No counters."""
    dist = [math.inf] * len(adj)
    dist[s] = 0.0
    heap = [(0.0, s)]
    while heap:
        d, u = heapq.heappop(heap)
        if d > dist[u]:
            continue
        for v, w in adj[u]:
            nd = d + w
            if nd < dist[v]:
                dist[v] = nd
                heapq.heappush(heap, (nd, v))
    return dist
