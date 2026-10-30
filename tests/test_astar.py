import math
import random

import pytest
from helpers import assert_matches_dijkstra, control_pair

from routing.astar import H_SCALE, astar, astar_heuristic
from routing.dijkstra import dijkstra, sssp
from routing.synthetic import from_edge_list, grid_graph, random_geo_graph


def test_astar_breaks_when_edge_faster_than_vmax():
    g0, g1 = control_pair()
    assert dijkstra(g1, 0, 1)[0] == 20.0
    assert astar(g1, 0, 1, vmax=g0.vmax)[0] == 100.0  # bound from g0 is violated -> wrong
    assert astar(g1, 0, 1)[0] == 20.0  # bound from g1 itself is valid


def test_astar_heuristic_admissible_on_grid():
    g = grid_graph(10, 10)
    d = sssp(g.bwd, 99)
    assert all(astar_heuristic(g, v, 99, g.vmax) <= d[v] for v in range(g.n))


def test_astar_settles_fewer_on_grid():
    g = grid_graph(15, 15)
    rng = random.Random(0)
    pairs = [(rng.randrange(g.n), rng.randrange(g.n)) for _ in range(50)]
    assert sum(astar(g, s, t)[2] for s, t in pairs) < sum(dijkstra(g, s, t)[2] for s, t in pairs)


@pytest.mark.parametrize("eps", [1.2, 1.5])
def test_weighted_astar_within_eps(eps):
    g = random_geo_graph(80, 200, seed=7)
    rng = random.Random(1)
    for _ in range(40):
        s, t = rng.randrange(g.n), rng.randrange(g.n)
        opt = dijkstra(g, s, t)[0]
        if opt < math.inf:
            assert astar(g, s, t, eps=eps)[0] <= eps * opt + 1e-9


# Exactness until Task 4's registry exists (then register "astar" in tests/test_correctness.py).
@pytest.mark.parametrize("seed", range(10))
def test_astar_matches_dijkstra(seed):
    assert_matches_dijkstra(random_geo_graph(80, 200, seed=100 + seed), astar, seed=seed)
    assert_matches_dijkstra(random_geo_graph(60, 20, seed=seed), astar, seed=seed)  # many unreachable pairs


def test_astar_edge_cases():
    assert astar(grid_graph(3, 3), 4, 4) == (0.0, [4], 0)
    assert astar(from_edge_list(3, [(0, 1, 0.0), (1, 2, 0.0), (0, 2, 5.0)]), 0, 2)[:2] == (0.0, [0, 1, 2])
    assert H_SCALE == 1 - 1e-9
