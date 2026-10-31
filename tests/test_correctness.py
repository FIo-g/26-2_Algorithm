"""Exactness gate for every exact algorithm: distance equals Dijkstra's and the path is valid.

Register each exact algorithm in EXACT_ALGOS as name -> algo(g, s, t, *, stats=None).
"""
import math
import random
from collections import namedtuple

import pytest

from routing.alt import alt, preprocess_landmarks
from routing.astar import astar
from routing.bidirectional import bidirectional_dijkstra
from routing.dijkstra import dijkstra
from routing.synthetic import from_edge_list, grid_graph, random_geo_graph
from routing.verify import check_result, path_cost, verify_all


def alt4(g, s, t, *, stats=None):
    # Landmarks are rebuilt per call: test graphs are tiny, and this avoids any graph cache.
    return alt(g, s, t, preprocess_landmarks(g, 4), stats=stats)


EXACT_ALGOS = {
    "dijkstra": dijkstra,
    "astar": astar,                      # Task 6
    "bidir": bidirectional_dijkstra,     # Task 7
    "alt4": alt4,                        # Task 8
}
Q = namedtuple("Q", "qid s t")


@pytest.mark.parametrize("name", EXACT_ALGOS)
@pytest.mark.parametrize("seed", range(10))
def test_algo_matches_dijkstra(name, seed):
    g = random_geo_graph(80, 200, seed=100 + seed); rng = random.Random(seed)
    for _ in range(40):
        s, t = rng.randrange(g.n), rng.randrange(g.n)
        assert check_result(g, s, t, dijkstra(g, s, t)[0], EXACT_ALGOS[name](g, s, t)) == []


@pytest.mark.parametrize("name", EXACT_ALGOS)
def test_same_source_target(name):                      # Review Focus 4
    assert EXACT_ALGOS[name](grid_graph(3, 3), 4, 4) == (0.0, [4], 0)


@pytest.mark.parametrize("name", EXACT_ALGOS)
def test_unreachable(name):
    d, p, _ = EXACT_ALGOS[name](from_edge_list(4, [(0, 1, 1.0), (2, 3, 1.0)]), 0, 3)
    assert (d, p) == (math.inf, [])


@pytest.mark.parametrize("name", EXACT_ALGOS)
def test_zero_weight_edges(name):                        # Review Focus 3
    g = from_edge_list(3, [(0, 1, 0.0), (1, 2, 0.0), (0, 2, 5.0)])
    assert EXACT_ALGOS[name](g, 0, 2)[:2] == (0.0, [0, 1, 2])


def test_check_result_rejects_bad_path():
    g = grid_graph(2, 2)
    assert check_result(g, 0, 3, 20.0, (20.0, [0, 3], 0)) != []   # 0-3 is not an edge


def test_check_result_rejects_cost_mismatch():
    g = grid_graph(2, 2); d, p, _ = dijkstra(g, 0, 3)
    assert check_result(g, 0, 3, d, (d, [0, 1, 0, 1, 3], 0)) != []   # valid edges, wrong cost


def test_verify_all_catches_wrong_algo():
    g = grid_graph(6, 6); qs = [Q(i, i, 35 - i) for i in range(5)]
    bad = {"dijkstra": dijkstra, "bad": lambda g, s, t, stats=None: (dijkstra(g, s, t)[0] + 1, *dijkstra(g, s, t)[1:])}
    assert any(m.startswith("bad") for m in verify_all(g, qs, bad))


def test_path_cost():
    g = from_edge_list(3, [(0, 1, 1.5), (1, 2, 2.5)])
    assert path_cost(g, [0, 1, 2]) == 4.0
    assert path_cost(g, [0]) == 0.0
    assert path_cost(g, [0, 2]) is None                  # not an edge
    assert path_cost(g, [2, 1]) is None                  # edges are directed


def test_check_result_unreachable_rules():
    g = from_edge_list(2, [(0, 1, 1.0)])
    assert check_result(g, 1, 0, math.inf, (math.inf, [], 0)) == []
    assert check_result(g, 1, 0, math.inf, (math.inf, [1, 0], 0)) != []   # inf needs an empty path
    assert check_result(g, 0, 1, 1.0, (math.inf, [], 0)) != []            # missed a reachable target
    assert check_result(g, 0, 1, 1.0, (1.0, [1], 0)) != []                # wrong start vertex


def test_verify_all_message_format():
    g = grid_graph(3, 3)
    wrong = {"bad": lambda g, s, t, stats=None: (0.0, [s], 0)}
    msgs = verify_all(g, [Q(7, 0, 8)], wrong)
    assert msgs and all(m.startswith("bad q7: ") for m in msgs)


def test_verify_all_runs_reference_once_per_query():
    g = grid_graph(4, 4); calls = []
    def counted(g, s, t, stats=None):
        calls.append((s, t))
        return dijkstra(g, s, t)
    assert verify_all(g, [Q(0, 0, 15), Q(1, 3, 12)], {"dijkstra": counted, "astar": astar}) == []
    assert calls == [(0, 15), (3, 12)]
