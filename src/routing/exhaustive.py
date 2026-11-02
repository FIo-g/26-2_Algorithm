"""Exhaustive s-t search over all simple paths, path counting, and BFS subgraphs (standard library only).

This is the baseline for E1: it enumerates every simple path with no pruning, so
its cost grows with the number of paths, which is exponential in the graph size
(a k x k grid has 12, 184, 8512, ... corner-to-corner paths, OEIS A007764).
"""
from __future__ import annotations

import math
from collections import deque
from time import perf_counter
from typing import NamedTuple

from routing.graph import Graph, largest_scc

CHECK_EVERY = 4096  # expansions between clock checks


class ExhaustiveResult(NamedTuple):
    dist: float
    path: list[int]
    paths: int  # simple s-t paths seen (all of them unless timed_out)
    timed_out: bool


def _enumerate(g: Graph, s: int, t: int, deadline: float | None) -> ExhaustiveResult:
    """Iterative DFS over simple paths from s; every path that reaches t is a candidate."""
    if s == t:
        return ExhaustiveResult(0.0, [s], 1, False)
    best, best_path, paths, expansions = math.inf, [], 0, 0
    path, cost = [s], [0.0]           # cost[i] = time from s to path[i]
    on_path = {s}
    stack = [iter(g.fwd[s])]          # stack[i] iterates the out-edges of path[i]
    while stack:
        for v, w in stack[-1]:
            if v in on_path:
                continue              # simple paths only
            expansions += 1
            if deadline is not None and expansions % CHECK_EVERY == 0 and perf_counter() > deadline:
                return ExhaustiveResult(best, best_path, paths, True)
            d = cost[-1] + w
            if v == t:                # a complete path; a simple path cannot pass t and return
                paths += 1
                if d < best:
                    best, best_path = d, path + [t]
                continue
            path.append(v); cost.append(d); on_path.add(v)
            stack.append(iter(g.fwd[v]))
            break
        else:                         # every out-edge of path[-1] tried: backtrack
            stack.pop()
            on_path.discard(path.pop())
            cost.pop()
    return ExhaustiveResult(best, best_path, paths, False)


def exhaustive_shortest(g: Graph, s: int, t: int, *, time_limit_s: float | None = 10.0) -> ExhaustiveResult:
    """Shortest s-t path by trying every simple path. On timeout returns the best so far."""
    deadline = None if time_limit_s is None else perf_counter() + time_limit_s
    return _enumerate(g, s, t, deadline)


def count_simple_paths(g: Graph, s: int, t: int) -> int:
    return _enumerate(g, s, t, None).paths


def bfs_subgraph(g: Graph, root: int, n: int) -> Graph:
    """Strongly connected subgraph of at least n vertices grown around root.

    Take the first m vertices in undirected BFS order (fwd and bwd edges), keep the
    largest SCC of the induced subgraph, and grow m from n until that SCC has n
    vertices. If m reaches the size of root's component, return what is there.
    """
    if n > g.n:
        raise ValueError(f"n={n} is larger than the graph (n={g.n})")
    order, seen, queue = [], {root}, deque([root])
    while queue:
        u = queue.popleft()
        order.append(u)
        for v, _ in g.fwd[u] + g.bwd[u]:
            if v not in seen:
                seen.add(v)
                queue.append(v)
    for m in range(min(n, len(order)), len(order) + 1):
        sub = g.subgraph(order[:m])
        scc = largest_scc(sub)
        if len(scc) >= n or m == len(order):
            return sub.subgraph(scc)
    raise AssertionError("unreachable")  # the loop always returns at m == len(order)
