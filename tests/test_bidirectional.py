import pytest
from helpers import assert_matches_dijkstra

from routing.bidirectional import bidirectional_dijkstra
from routing.dijkstra import dijkstra
from routing.heap import Stats
from routing.synthetic import from_edge_list, grid_graph, random_geo_graph


def test_bidirectional_not_first_meeting():
    # s=0 a=1 t=2 u=3 v=4 ; a is settled by both sides first (6.0), but 0-3-4-2 is 5.5
    g = from_edge_list(5, [(0, 1, 3), (1, 2, 3), (0, 3, 2), (3, 4, 1.5), (4, 2, 2)])
    assert bidirectional_dijkstra(g, 0, 2)[:2] == (5.5, [0, 3, 4, 2])


def test_bidirectional_one_way_uses_bwd():
    g = from_edge_list(3, [(0, 1, 1), (1, 2, 1), (2, 0, 1)])  # one-way cycle
    assert bidirectional_dijkstra(g, 0, 2)[:2] == (2.0, [0, 1, 2])
    assert bidirectional_dijkstra(g, 2, 1)[:2] == (2.0, [2, 0, 1])


# Exactness until Task 4's registry exists (then register "bidir" in tests/test_correctness.py).
@pytest.mark.parametrize("seed", range(10))
def test_bidirectional_matches_dijkstra(seed):
    assert_matches_dijkstra(random_geo_graph(80, 200, seed=100 + seed), bidirectional_dijkstra, seed=seed)
    assert_matches_dijkstra(random_geo_graph(60, 20, seed=seed), bidirectional_dijkstra, seed=seed)


def test_bidirectional_edge_cases():
    assert bidirectional_dijkstra(grid_graph(3, 3), 4, 4) == (0.0, [4], 0)
    assert bidirectional_dijkstra(from_edge_list(4, [(0, 1, 1.0), (2, 3, 1.0)]), 0, 3)[:2] == (float("inf"), [])
    g = from_edge_list(3, [(0, 1, 0.0), (1, 2, 0.0), (0, 2, 5.0)])
    assert bidirectional_dijkstra(g, 0, 2)[:2] == (0.0, [0, 1, 2])


def test_bidirectional_counts_both_sides():
    g = grid_graph(15, 15)
    st, tr = Stats(), Stats(trace=[])
    d, _, settled = bidirectional_dijkstra(g, 0, 224, stats=st)
    bidirectional_dijkstra(g, 0, 224, stats=tr)
    assert settled == st.settled == len(tr.trace) and settled < dijkstra(g, 0, 224)[2]
