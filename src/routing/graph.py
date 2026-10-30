"""Shared road-graph format for every algorithm (standard library only).

Vertices are 0..n-1. Edge e goes tail[e] -> head[e] with length[e] meters and
time[e] seconds. fwd[u] = [(v, w), ...] and bwd[v] = [(u, w), ...] are built once.
"""
from __future__ import annotations

import math
import pickle
from dataclasses import dataclass, field
from pathlib import Path
from typing import Sequence

EARTH_RADIUS_M = 6_371_009.0  # same as osmnx.distance.EARTH_RADIUS_M


def haversine_m(a: tuple[float, float], b: tuple[float, float]) -> float:
    """Great-circle distance in meters between two (lat, lon) points."""
    lat1, lon1 = math.radians(a[0]), math.radians(a[1])
    lat2, lon2 = math.radians(b[0]), math.radians(b[1])
    h = (math.sin((lat2 - lat1) / 2) ** 2
         + math.cos(lat1) * math.cos(lat2) * math.sin((lon2 - lon1) / 2) ** 2)
    return 2 * EARTH_RADIUS_M * math.asin(math.sqrt(min(1.0, h)))


def _max_speed(length: Sequence[float], time: Sequence[float]) -> float:
    """max(length / time) over edges with positive length; inf if such an edge takes 0 s."""
    best, seen = 0.0, False
    for ln, t in zip(length, time):
        if ln == 0:
            continue  # zero-length edges say nothing about speed
        seen = True
        if t == 0:
            return math.inf
        best = max(best, ln / t)
    return best if seen else 1.0


# eq=False: graphs compare and hash by identity (they are large; compare fields explicitly).
@dataclass(eq=False)
class Graph:
    coords: list[tuple[float, float]]  # (lat, lon)
    osm_ids: list[int]
    tail: list[int]
    head: list[int]
    length: list[float]  # meters
    time: list[float]  # seconds
    hwy: list[str]
    name: str = ""
    fwd: list[list[tuple[int, float]]] = field(init=False, repr=False)
    bwd: list[list[tuple[int, float]]] = field(init=False, repr=False)
    vmax: float = field(init=False)  # m/s, computed once
    _index: dict[int, int] = field(init=False, repr=False)

    def __post_init__(self) -> None:
        # Normalize to built-in types: numpy scalars from OSMnx would make pickles need numpy
        # (the SUMO PC has none) and slow down the pure-Python search loops.
        self.coords = [(float(lat), float(lon)) for lat, lon in self.coords]
        self.osm_ids = [int(x) for x in self.osm_ids]
        self.tail = [int(x) for x in self.tail]
        self.head = [int(x) for x in self.head]
        self.length = [float(x) for x in self.length]
        self.time = [float(x) for x in self.time]
        self.hwy = [str(x) for x in self.hwy]
        self.name = str(self.name)
        n, m = len(self.coords), len(self.tail)
        if len(self.osm_ids) != n:
            raise ValueError("coords and osm_ids must have the same length")
        if not (len(self.head) == len(self.length) == len(self.time) == len(self.hwy) == m):
            raise ValueError("edge lists must all have the same length")
        self._index = {osm: i for i, osm in enumerate(self.osm_ids)}
        if len(self._index) != n:
            raise ValueError("osm_ids must be unique")
        fwd: list[list[tuple[int, float]]] = [[] for _ in range(n)]
        bwd: list[list[tuple[int, float]]] = [[] for _ in range(n)]
        seen: set[tuple[int, int]] = set()
        for u, v, t in zip(self.tail, self.head, self.time):
            if not (0 <= u < n and 0 <= v < n):
                raise ValueError(f"edge ({u}, {v}) has an endpoint outside 0..{n - 1}")
            if math.isnan(t) or t < 0:
                raise ValueError(f"edge ({u}, {v}) has invalid time {t}")
            if (u, v) in seen:
                raise ValueError(f"duplicate edge ({u}, {v}); keep only the fastest")
            seen.add((u, v))
            fwd[u].append((v, t))
            bwd[v].append((u, t))
        self.fwd, self.bwd = fwd, bwd
        self.vmax = _max_speed(self.length, self.time)

    def __getstate__(self) -> dict:
        # Pickle only the input fields; derived structures are rebuilt on load.
        return {k: getattr(self, k) for k in
                ("coords", "osm_ids", "tail", "head", "length", "time", "hwy", "name")}

    def __setstate__(self, state: dict) -> None:
        self.__dict__.update(state)
        self.__post_init__()

    @property
    def n(self) -> int:
        return len(self.coords)

    @property
    def m(self) -> int:
        return len(self.tail)

    def index_of(self, osm_id: int) -> int:
        return self._index[osm_id]

    def weight(self, u: int, v: int) -> float | None:
        for w, t in self.fwd[u]:
            if w == v:
                return t
        return None

    def nearest(self, lat: float, lon: float) -> int:
        return min(range(self.n), key=lambda i: haversine_m(self.coords[i], (lat, lon)))

    def reweighted(self, times: Sequence[float]) -> Graph:
        """Same topology with new edge times (lists are copied while normalizing types)."""
        if len(times) != self.m:
            raise ValueError(f"expected {self.m} times, got {len(times)}")
        return Graph(self.coords, self.osm_ids, self.tail, self.head, self.length,
                     list(times), self.hwy, self.name)

    def subgraph(self, vertices: Sequence[int]) -> Graph:
        """Induced subgraph on `vertices`, renumbered in the given order."""
        new = {v: i for i, v in enumerate(vertices)}
        keep = [e for e in range(self.m) if self.tail[e] in new and self.head[e] in new]
        return Graph(
            coords=[self.coords[v] for v in vertices],
            osm_ids=[self.osm_ids[v] for v in vertices],
            tail=[new[self.tail[e]] for e in keep],
            head=[new[self.head[e]] for e in keep],
            length=[self.length[e] for e in keep],
            time=[self.time[e] for e in keep],
            hwy=[self.hwy[e] for e in keep],
            name=self.name,
        )


def largest_scc(g: Graph) -> list[int]:
    """Vertices of the largest strongly connected component (iterative Kosaraju), sorted."""
    order: list[int] = []
    visited = [False] * g.n
    for root in range(g.n):
        if visited[root]:
            continue
        visited[root] = True
        stack = [(root, iter(g.fwd[root]))]
        while stack:
            u, it = stack[-1]
            for v, _ in it:
                if not visited[v]:
                    visited[v] = True
                    stack.append((v, iter(g.fwd[v])))
                    break
            else:
                stack.pop()
                order.append(u)
    comp = [-1] * g.n
    best: list[int] = []
    for root in reversed(order):
        if comp[root] != -1:
            continue
        members, stack = [root], [root]
        comp[root] = root
        while stack:
            u = stack.pop()
            for v, _ in g.bwd[u]:
                if comp[v] == -1:
                    comp[v] = root
                    members.append(v)
                    stack.append(v)
        if len(members) > len(best):
            best = members
    return sorted(best)


def save_graph(g: Graph, path: str | Path) -> None:
    with open(path, "wb") as f:
        pickle.dump(g, f, protocol=pickle.HIGHEST_PROTOCOL)


def load_graph(path: str | Path) -> Graph:
    with open(path, "rb") as f:
        g = pickle.load(f)
    if not isinstance(g, Graph):
        raise TypeError(f"{path} does not contain a Graph")
    return g
