"""Small synthetic graphs for tests and for starting before the OSM files arrive (standard library only).

Every synthetic graph uses osm_ids = 1000 + index, so code that mixes up
indices and OSM ids fails loudly.
"""
from __future__ import annotations

import math
import random

from routing.graph import EARTH_RADIUS_M, Graph, haversine_m

OSM_ID_OFFSET = 1000
ORIGIN = (37.5, 127.0)


def _osm_ids(n: int) -> list[int]:
    return [OSM_ID_OFFSET + i for i in range(n)]


def _build(coords, edges: dict[tuple[int, int], tuple[float, float]], hwy: str) -> Graph:
    """edges maps (u, v) -> (length, time); one entry per pair by construction."""
    pairs = list(edges)
    return Graph(
        coords=coords,
        osm_ids=_osm_ids(len(coords)),
        tail=[u for u, _ in pairs],
        head=[v for _, v in pairs],
        length=[edges[p][0] for p in pairs],
        time=[edges[p][1] for p in pairs],
        hwy=[hwy] * len(pairs),
    )


def from_edge_list(n: int, edges: list[tuple[int, int, float]], coords=None) -> Graph:
    """Hand-made graph from (u, v, time). Duplicate pairs keep the smallest time; length = time (1 m/s)."""
    best: dict[tuple[int, int], float] = {}
    for u, v, t in edges:
        if (u, v) not in best or t < best[(u, v)]:
            best[(u, v)] = float(t)
    coords = list(coords) if coords is not None else [ORIGIN] * n
    return _build(coords, {p: (t, t) for p, t in best.items()}, "residential")


def _offset(lat0: float, north_m: float, east_m: float) -> tuple[float, float]:
    dlat = math.degrees(north_m / EARTH_RADIUS_M)
    dlon = math.degrees(east_m / (EARTH_RADIUS_M * math.cos(math.radians(lat0))))
    return dlat, dlon


def grid_graph(rows: int, cols: int, *, spacing_m: float = 100.0, speed_mps: float = 10.0,
               hwy: str = "residential") -> Graph:
    """rows x cols grid, row-major ids, two-way edges between 4-neighbors."""
    dlat, dlon = _offset(ORIGIN[0], spacing_m, spacing_m)
    coords = [(ORIGIN[0] + r * dlat, ORIGIN[1] + c * dlon) for r in range(rows) for c in range(cols)]
    edges: dict[tuple[int, int], tuple[float, float]] = {}
    for r in range(rows):
        for c in range(cols):
            u = r * cols + c
            for v in ([u + 1] if c + 1 < cols else []) + ([u + cols] if r + 1 < rows else []):
                ln = haversine_m(coords[u], coords[v])
                edges[(u, v)] = edges[(v, u)] = (ln, ln / speed_mps)
    return _build(coords, edges, hwy)


def random_geo_graph(n: int, extra_edges: int, *, seed: int, one_way_ratio: float = 0.3) -> Graph:
    """Random points in a ~2 km box, each linked to its 2 nearest neighbors, plus random extra edges.

    Not guaranteed to be strongly connected: with few extra edges (e.g. n=60, extra_edges=20)
    many pairs are unreachable; with many (e.g. n=80, extra_edges=200) it usually is.
    """
    rng = random.Random(seed)
    span_lat, span_lon = _offset(ORIGIN[0], 2000.0, 2000.0)
    coords = [(ORIGIN[0] + rng.random() * span_lat, ORIGIN[1] + rng.random() * span_lon)
              for _ in range(n)]
    edges: dict[tuple[int, int], tuple[float, float]] = {}

    def add(u: int, v: int) -> None:
        ln = haversine_m(coords[u], coords[v]) * rng.uniform(1.0, 1.3)
        edges[(u, v)] = (ln, ln / rng.uniform(5.0, 25.0))

    for u in range(n):
        near = sorted((v for v in range(n) if v != u),
                      key=lambda v: haversine_m(coords[u], coords[v]))[:2]
        for v in near:
            if (u, v) in edges or (v, u) in edges:
                continue
            if rng.random() < one_way_ratio:
                add(*((u, v) if rng.random() < 0.5 else (v, u)))
            else:
                add(u, v)
                add(v, u)
    for _ in range(extra_edges):
        u, v = rng.randrange(n), rng.randrange(n)
        if u != v and (u, v) not in edges:
            add(u, v)
    return _build(coords, edges, "residential")
