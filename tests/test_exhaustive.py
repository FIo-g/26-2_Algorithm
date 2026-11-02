"""Exhaustive search and BFS subgraph tests on synthetic graphs."""
import math
import random

import pytest

from routing.dijkstra import dijkstra
from routing.exhaustive import bfs_subgraph, count_simple_paths, exhaustive_shortest
from routing.graph import largest_scc
from routing.synthetic import from_edge_list, grid_graph, random_geo_graph
from routing.verify import check_result


@pytest.mark.parametrize("k,count", [(3, 12), (4, 184), (5, 8512)])      # OEIS A007764
def test_grid_path_counts(k, count):
    assert count_simple_paths(grid_graph(k, k), 0, k * k - 1) == count


@pytest.mark.parametrize("seed", range(10))
def test_exhaustive_matches_dijkstra(seed):
    g = random_geo_graph(10, 15, seed=seed); rng = random.Random(seed)
    for _ in range(10):
        s, t = rng.randrange(g.n), rng.randrange(g.n); r = exhaustive_shortest(g, s, t)
        assert not r.timed_out and check_result(g, s, t, dijkstra(g, s, t)[0], (r.dist, r.path, 0)) == []


def test_exhaustive_timeout():
    assert exhaustive_shortest(grid_graph(7, 7), 0, 48, time_limit_s=0.05).timed_out


def test_bfs_subgraph_strongly_connected():
    g = grid_graph(10, 10); sub = bfs_subgraph(g, 0, 12)
    assert sub.n >= 12 and len(largest_scc(sub)) == sub.n and set(sub.osm_ids) <= set(g.osm_ids)


def test_bfs_subgraph_too_large():
    with pytest.raises(ValueError):
        bfs_subgraph(grid_graph(3, 3), 0, 10)


def test_exhaustive_same_source_and_unreachable():
    assert exhaustive_shortest(grid_graph(3, 3), 4, 4) == (0.0, [4], 1, False)
    g = from_edge_list(4, [(0, 1, 1.0), (2, 3, 1.0)])
    assert exhaustive_shortest(g, 0, 3) == (math.inf, [], 0, False)
    assert count_simple_paths(g, 0, 3) == 0 and count_simple_paths(g, 2, 2) == 1


def test_exhaustive_counts_all_paths_and_keeps_best():
    # 0->3 directly (10 s) or via 1 (1+1) or via 2 (2+2): three simple paths, best is 0-1-3
    g = from_edge_list(4, [(0, 3, 10.0), (0, 1, 1.0), (1, 3, 1.0), (0, 2, 2.0), (2, 3, 2.0)])
    assert exhaustive_shortest(g, 0, 3) == (2.0, [0, 1, 3], 3, False)


def test_bfs_subgraph_stops_at_component_edge():
    # root's component has 3 vertices; asking for 4 (<= g.n = 6) must return, not loop
    g = from_edge_list(6, [(0, 1, 1.0), (1, 0, 1.0), (1, 2, 1.0), (2, 1, 1.0),
                           (3, 4, 1.0), (4, 5, 1.0), (5, 3, 1.0)])
    assert sorted(bfs_subgraph(g, 0, 4).osm_ids) == sorted(g.osm_ids[:3])
