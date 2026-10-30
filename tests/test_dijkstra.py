import math
import random

import networkx as nx
import pytest

from routing.dijkstra import dijkstra, shortest_path, sssp
from routing.heap import Stats
from routing.synthetic import from_edge_list, grid_graph, random_geo_graph


def to_nx(g):
    G = nx.DiGraph()
    G.add_nodes_from(range(g.n))
    for e in range(g.m):
        G.add_edge(g.tail[e], g.head[e], weight=g.time[e])  # (u, v) unique by Graph invariant
    return G


@pytest.mark.parametrize("seed", range(20))
def test_dijkstra_distance_matches_networkx(seed):
    g = random_geo_graph(60, 150, seed=seed)
    G = to_nx(g)
    rng = random.Random(seed)
    for _ in range(30):
        s, t = rng.randrange(g.n), rng.randrange(g.n)
        try:
            ref = nx.dijkstra_path_length(G, s, t)
        except nx.NetworkXNoPath:
            ref = math.inf
        d = dijkstra(g, s, t)[0]
        assert (d == ref == math.inf) or math.isclose(d, ref, rel_tol=1e-9, abs_tol=1e-9)


def test_sssp_matches_networkx():
    g = random_geo_graph(60, 150, seed=5)
    ref = nx.single_source_dijkstra_path_length(to_nx(g), 0)
    d = sssp(g.fwd, 0)
    assert all(math.isclose(d[v], ref[v]) if v in ref else d[v] == math.inf for v in range(g.n))


def test_dijkstra_stats_counting():
    g = from_edge_list(4, [(0, 1, 5), (0, 2, 1), (2, 1, 1), (1, 3, 10)])
    st = Stats()
    assert dijkstra(g, 0, 3, stats=st) == (12.0, [0, 2, 1, 3], 4)
    assert st == Stats(settled=4, relaxed=4, pushes=5, pops=5)  # stale (5, 1) is popped but not settled


def test_trace_records_settled_order():
    st = Stats(trace=[])
    dijkstra(from_edge_list(4, [(0, 1, 5), (0, 2, 1), (2, 1, 1), (1, 3, 10)]), 0, 3, stats=st)
    assert st.trace == [0, 2, 1, 3]


def test_same_source_and_unreachable():
    assert dijkstra(grid_graph(3, 3), 4, 4) == (0.0, [4], 0)
    assert dijkstra(from_edge_list(4, [(0, 1, 1.0), (2, 3, 1.0)]), 0, 3)[:2] == (math.inf, [])


def test_shortest_path_alias():
    assert shortest_path is dijkstra
