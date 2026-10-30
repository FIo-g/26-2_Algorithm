"""Shared test fixtures. Import as `from helpers import ...` (pytest puts tests/ on sys.path)."""
import math
import random

from routing.dijkstra import dijkstra
from routing.graph import Graph


def control_pair():
    """g0: s->t 1.0 km, detour s->m 5.1 km, m->t 5.2 km, all at 10 m/s (lengths >= haversine).
    g1: detour edges take 10 s each (>500 m/s), i.e. faster than g0.vmax."""
    coords = [(37.5, 127.0), (37.5, 127.0113), (37.545, 127.0)]  # s, t (~997 m east), m (~5004 m north)
    g0 = Graph(coords=coords, osm_ids=[1, 2, 3], tail=[0, 0, 2], head=[1, 2, 1],
               length=[1000.0, 5100.0, 5200.0], time=[100.0, 510.0, 520.0], hwy=["primary"] * 3)
    return g0, g0.reweighted([100.0, 10.0, 10.0])


def assert_matches_dijkstra(g, algo, *, queries=40, seed=0):
    """Distance equals Dijkstra's and the path is a real s-t path of that cost.

    Stand-in until 세현's Task 4 (tests/test_correctness.py registry) lands.
    """
    rng = random.Random(seed)
    for _ in range(queries):
        s, t = rng.randrange(g.n), rng.randrange(g.n)
        ref = dijkstra(g, s, t)[0]
        d, path, _ = algo(g, s, t)
        if ref == math.inf:
            assert (d, path) == (math.inf, []), (s, t)
            continue
        assert math.isclose(d, ref, rel_tol=1e-9, abs_tol=1e-9), (s, t, d, ref)
        assert path[0] == s and path[-1] == t, (s, t, path)
        cost = sum(g.weight(u, v) for u, v in zip(path, path[1:]))  # weight() is None for non-edges -> TypeError
        assert math.isclose(cost, d, rel_tol=1e-9, abs_tol=1e-9), (s, t, cost, d)
