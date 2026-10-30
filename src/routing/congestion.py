"""Reproducible synthetic traffic snapshots (standard library only).

The multipliers below are experimental assumptions, not observed Seoul traffic.
Every function returns a new Graph; the baseline graph is never edited.
"""
from __future__ import annotations

import math
import random
from collections.abc import Iterable

from routing.graph import Graph


SYNTH_PROFILES = {
    "03": {"motorway": 1.0, "trunk": 1.0, "primary": 1.0,
           "secondary": 1.0, "tertiary": 1.0, "other": 1.0},
    "08": {"motorway": 1.6, "trunk": 1.8, "primary": 2.0,
           "secondary": 1.8, "tertiary": 1.5, "other": 1.2},
    "18": {"motorway": 1.8, "trunk": 2.0, "primary": 2.2,
           "secondary": 1.9, "tertiary": 1.6, "other": 1.3},
}


def hwy_class(h: str) -> str:
    """Group OSM road types and their *_link counterparts into six classes."""
    h = h.removesuffix("_link")
    return h if h in {"motorway", "trunk", "primary", "secondary", "tertiary"} else "other"


def _fraction(value: float, name: str) -> float:
    value = float(value)
    if not math.isfinite(value) or not 0 <= value <= 1:
        raise ValueError(f"{name} must be finite and between 0 and 1")
    return value


def synthetic(g0: Graph, hour: str) -> Graph:
    """Apply the declared 03/08/18 road-class multipliers to baseline times."""
    if hour not in SYNTH_PROFILES:
        raise ValueError(f"unknown hour {hour!r}; choose one of {tuple(SYNTH_PROFILES)}")
    profile = SYNTH_PROFILES[hour]
    return g0.reweighted([t * profile[hwy_class(h)] for t, h in zip(g0.time, g0.hwy)])


def random_slowdown(g0: Graph, *, frac: float = 0.3,
                    factor: float = 2.0, seed: int = 0) -> Graph:
    """Sample exactly round(frac*m) edges without replacement and slow them.

    A selected zero-time edge remains zero, so selected and numerically changed
    counts need not coincide. Edge ordering and the seed define the selection.
    """
    frac = _fraction(frac, "frac")
    factor = float(factor)
    if not math.isfinite(factor) or factor < 1:
        raise ValueError("slowdown factor must be finite and at least 1")
    chosen = set(random.Random(seed).sample(range(g0.m), round(frac * g0.m)))
    return g0.reweighted([t * factor if e in chosen else t for e, t in enumerate(g0.time)])


def control_speedup(g0: Graph, *, factor: float = 0.5,
                    frac_other: float = 0.1, seed: int = 0) -> Graph:
    """Deliberately violate the old lower bound; this is a negative control.

    All motorway/trunk edges (including links) and a sampled fraction of the
    remaining edges receive the speedup. A stale heuristic may then fail; a
    failure is not guaranteed for every graph and query set.
    """
    factor = float(factor)
    if not math.isfinite(factor) or not 0 < factor <= 1:
        raise ValueError("speedup factor must be finite and in (0, 1]")
    frac_other = _fraction(frac_other, "frac_other")
    major = {e for e, h in enumerate(g0.hwy) if hwy_class(h) in {"motorway", "trunk"}}
    rest = [e for e in range(g0.m) if e not in major]
    chosen = major | set(random.Random(seed).sample(rest, round(frac_other * len(rest))))
    return g0.reweighted([t * factor if e in chosen else t for e, t in enumerate(g0.time)])


def standard_scenarios(g0: Graph, *, seed: int = 0) -> dict[str, Graph]:
    """Four safe snapshots and one deliberately unsafe lower-bound control."""
    return {
        "synth03": synthetic(g0, "03"),
        "synth08": synthetic(g0, "08"),
        "synth18": synthetic(g0, "18"),
        "random30": random_slowdown(g0, seed=seed),
        "control": control_speedup(g0, seed=seed),
    }


def lower_bound(g0: Graph, scenarios: Iterable[Graph]) -> Graph:
    """Take edge-wise minimum times with g0, checking edge/index alignment.

    Pass only the scenarios that must be exact. E3 deliberately excludes its
    negative control. Adding a faster real snapshot requires rebuilding this
    baseline and its landmark preprocessing once, before measuring queries.
    """
    times = list(g0.time)
    for g in scenarios:
        if (g.osm_ids != g0.osm_ids or g.tail != g0.tail or g.head != g0.head
                or g.coords != g0.coords or g.length != g0.length):
            raise ValueError("scenario topology/edge ordering does not match the baseline")
        times = [min(a, b) for a, b in zip(times, g.time)]
    return g0.reweighted(times)


def midpoint(g0: Graph, s: int, t: int) -> int:
    """First baseline-path vertex at or beyond half its travel time.

    Return s for an unreachable target, s == t, or a path of at most two
    vertices. Only this function requires the shared Task 3 Dijkstra module.
    """
    if not 0 <= s < g0.n or not 0 <= t < g0.n:
        raise ValueError("source and target must be graph vertex indices")
    if s == t:
        return s
    from routing.dijkstra import dijkstra

    distance, path, _ = dijkstra(g0, s, t)
    if not math.isfinite(distance) or len(path) <= 2:
        return s
    elapsed = 0.0
    for u, v in zip(path, path[1:]):
        weight = g0.weight(u, v)
        if weight is None:
            raise RuntimeError("Dijkstra returned a path containing a missing edge")
        elapsed += weight
        if elapsed >= distance / 2:
            return v
    return t
