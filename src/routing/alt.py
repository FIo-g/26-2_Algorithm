"""Directed ALT landmarks and shortest-path queries (standard library only).

Preprocess a lower-bound graph and reuse its landmarks while every query edge
cost stays at least its preprocessing cost. Faster edges can invalidate the
bound; this module intentionally does not silently reprocess that control case.

The shared heap and SSSP implementations belong to Task 3. No production
fallback is provided: missing prerequisites must remain visible to integrators.
"""
from __future__ import annotations

from array import array
from dataclasses import dataclass
import math
import operator
import random
from time import perf_counter
from typing import Sequence

from routing.dijkstra import sssp
from routing.graph import Graph
from routing.heap import CountingHeap, Stats

# Same value specified for A* in Task 6; ALT otherwise depends only on Task 3.
H_SCALE = 1.0 - 1e-9


@dataclass
class Landmarks:
    """Distance tables in vertex-index order, never in OSM-id order.

    ``d_from[i][v]`` is d(landmark_i, v); ``d_to[i][v]`` is d(v, landmark_i).
    ``nbytes`` reports the distance-array payload, not total Python RSS.
    """

    ids: list[int]
    d_from: list[array]
    d_to: list[array]
    prep_s: float
    k_requested: int

    @property
    def k(self) -> int:
        return len(self.ids)

    @property
    def nbytes(self) -> int:
        n = len(self.d_from[0]) if self.d_from else 0
        return 2 * self.k * n * 8


def _vertex(value: int, n: int) -> int:
    try:
        value = operator.index(value)
    except TypeError as exc:
        raise ValueError("vertices must be integer indices") from exc
    if not 0 <= value < n:
        raise ValueError(f"vertex {value} is outside 0..{n - 1}")
    return value


def _append_distances(g: Graph, vertex: int, ids: list[int],
                      d_from: list[array], d_to: list[array]) -> None:
    ids.append(vertex)
    d_from.append(array("d", sssp(g.fwd, vertex)))
    d_to.append(array("d", sssp(g.bwd, vertex)))


def build_landmarks(g: Graph, ids: Sequence[int]) -> Landmarks:
    """Run two SSSPs per explicitly selected landmark, including their timing."""
    start = perf_counter()
    selected = [_vertex(v, g.n) for v in ids]
    if len(set(selected)) != len(selected):
        raise ValueError("landmark indices must be distinct")
    built: list[int] = []
    d_from: list[array] = []
    d_to: list[array] = []
    for vertex in selected:
        _append_distances(g, vertex, built, d_from, d_to)
    return Landmarks(built, d_from, d_to, perf_counter() - start, len(selected))


def preprocess_landmarks(g: Graph, k: int, *, seed: int = 0) -> Landmarks:
    """Select farthest landmarks, stopping when no finite unused candidate exists.

    After the first landmark, maximize the minimum round-trip distance to any
    selected landmark. Ties prefer the smaller vertex index. All selection
    work, the initial SSSP, and the 2*k distance tables are timed in prep_s.
    """
    start = perf_counter()
    try:
        k = operator.index(k)
    except TypeError as exc:
        raise ValueError("k must be a nonnegative integer") from exc
    if k < 0:
        raise ValueError("k must be a nonnegative integer")
    ids: list[int] = []
    d_from: list[array] = []
    d_to: list[array] = []
    if k == 0 or g.n == 0:
        return Landmarks(ids, d_from, d_to, perf_counter() - start, k)

    root = random.Random(seed).randrange(g.n)
    root_dist = sssp(g.fwd, root)
    first = max((v for v in range(g.n) if math.isfinite(root_dist[v])),
                key=lambda v: (root_dist[v], -v))
    selected: set[int] = set()
    nearest = [math.inf] * g.n
    vertex = first
    while len(ids) < k:
        _append_distances(g, vertex, ids, d_from, d_to)
        selected.add(vertex)
        forward, backward = d_from[-1], d_to[-1]
        for v in range(g.n):
            nearest[v] = min(nearest[v], forward[v] + backward[v])
        candidates = (v for v in range(g.n)
                      if v not in selected and math.isfinite(nearest[v]))
        vertex = max(candidates, key=lambda v: (nearest[v], -v), default=None)
        if vertex is None:
            break
    return Landmarks(ids, d_from, d_to, perf_counter() - start, k)


def alt_heuristic(lm: Landmarks, v: int, t: int) -> float:
    """Directed triangle-inequality lower bound; never subtract infinities."""
    bound = 0.0
    for forward, backward in zip(lm.d_from, lm.d_to):
        left, right = forward[t], forward[v]
        if math.isfinite(left) and math.isfinite(right):
            bound = max(bound, left - right)
        left, right = backward[v], backward[t]
        if math.isfinite(left) and math.isfinite(right):
            bound = max(bound, left - right)
    return H_SCALE * bound


def alt(g: Graph, s: int, t: int, lm: Landmarks, *, stats=None
        ) -> tuple[float, list[int], int]:
    """Query with fixed landmark tables and the shared counting heap.

    Finite-term filtering on disconnected directed graphs can make the bound
    inconsistent outside the target's reachable region. Reopen an expanded
    vertex if its distance improves. ``settled`` counts nonstale expansions,
    including a reopening; on a strongly connected graph the usual consistent
    ALT bound settles each vertex at most once.

    Reuse is valid only for the same vertex indexing and a lower-bound graph.
    Verifying that condition edge-by-edge belongs outside the timed query.
    """
    s, t = _vertex(s, g.n), _vertex(t, g.n)
    if s == t:
        return 0.0, [s], 0
    if not (len(lm.ids) == len(lm.d_from) == len(lm.d_to)):
        raise ValueError("landmark ids and distance tables must have equal counts")
    if any(len(row) != g.n for row in (*lm.d_from, *lm.d_to)):
        raise ValueError("landmark tables do not match the query graph size")
    st = Stats() if stats is None else stats
    heap = CountingHeap(st)
    # Query work must scale with the explored region, not the graph's size.
    distance: dict[int, float] = {s: 0.0}
    parent: dict[int, int] = {}
    done: set[int] = set()
    heuristic: dict[int, float] = {}

    def h(v: int) -> float:
        value = heuristic.get(v)
        if value is None:
            value = alt_heuristic(lm, v, t)
            heuristic[v] = value
        return value

    heap.push(h(s), s)
    settled = 0
    while len(heap):
        key, u = heap.pop()
        if u in done or key > distance[u] + h(u):
            continue
        done.add(u)
        settled += 1
        st.settled += 1
        if st.trace is not None:
            st.trace.append(u)
        if u == t:
            path = [t]
            while path[-1] != s:
                path.append(parent[path[-1]])
            path.reverse()
            return distance[t], path, settled
        for v, weight in g.fwd[u]:
            st.relaxed += 1
            candidate = distance[u] + weight
            if candidate < distance.get(v, math.inf):
                distance[v] = candidate
                parent[v] = u
                done.discard(v)
                heap.push(candidate + h(v), v)
    return math.inf, [], settled
