import math
import pickle

import pytest

from routing.graph import Graph, haversine_m, largest_scc, load_graph, save_graph
from routing.synthetic import from_edge_list, grid_graph, random_geo_graph


def test_fwd_bwd_mirror():
    g = random_geo_graph(30, 60, seed=1)
    for e in range(g.m):
        assert (g.head[e], g.time[e]) in g.fwd[g.tail[e]]
        assert (g.tail[e], g.time[e]) in g.bwd[g.head[e]]


def test_haversine_one_degree_lat():
    assert haversine_m((0.0, 0.0), (1.0, 0.0)) == pytest.approx(111195.0837, abs=1e-3)


def test_vmax_is_max_speed():
    assert grid_graph(3, 3, speed_mps=12.5).vmax == pytest.approx(12.5)


def test_vmax_ignores_zero_length_edge():  # Review Focus 3
    g = Graph(coords=[(37.5, 127.0)] * 3, osm_ids=[1, 2, 3], tail=[0, 1], head=[1, 2],
              length=[0.0, 100.0], time=[0.0, 10.0], hwy=["residential"] * 2)
    assert g.vmax == 10.0


def test_negative_time_rejected():
    with pytest.raises(ValueError):
        from_edge_list(2, [(0, 1, -1.0)])


def test_duplicate_edges_keep_min():
    g = from_edge_list(2, [(0, 1, 5.0), (0, 1, 3.0)])
    assert g.m == 1 and g.weight(0, 1) == 3.0


def test_graph_rejects_duplicate_pairs():
    with pytest.raises(ValueError):
        Graph(coords=[(37.5, 127.0)] * 2, osm_ids=[1, 2], tail=[0, 0], head=[1, 1],
              length=[1.0, 1.0], time=[1.0, 2.0], hwy=["residential"] * 2)


def test_random_geo_graph_has_no_duplicates():
    g = random_geo_graph(60, 150, seed=0)
    assert len(set(zip(g.tail, g.head))) == g.m and all(u != v for u, v in zip(g.tail, g.head))


def test_reweighted_keeps_topology():
    g = grid_graph(3, 3)
    h = g.reweighted([t * 2 for t in g.time])
    assert (h.tail, h.head, h.osm_ids) == (g.tail, g.head, g.osm_ids)
    assert h.weight(0, 1) == 2 * g.weight(0, 1)


def test_largest_scc_drops_tail_vertex():
    g = from_edge_list(4, [(0, 1, 1), (1, 2, 1), (2, 0, 1), (2, 3, 1)])
    assert sorted(largest_scc(g)) == [0, 1, 2]


def test_subgraph_preserves_osm_ids():
    g = grid_graph(3, 3)
    sub = g.subgraph([4, 5, 7, 8])
    assert sub.n == 4 and sub.osm_ids == [g.osm_ids[i] for i in (4, 5, 7, 8)]


class _F(float):  # stands in for numpy.float64 coming from OSMnx
    pass


class _I(int):  # stands in for numpy.int64
    pass


def test_graph_stores_only_builtin_types():
    g = Graph(coords=[(_F(37.5), _F(127.0)), (_F(37.5), _F(127.001))], osm_ids=[_I(1), _I(2)],
              tail=[_I(0)], head=[_I(1)], length=[_F(88.0)], time=[_F(8.8)], hwy=["primary"])
    assert type(g.time[0]) is float and type(g.coords[0][0]) is float and type(g.osm_ids[0]) is int
    assert __name__.encode() not in pickle.dumps(g)  # loading must not need the source types' module


def test_save_load_roundtrip(tmp_path):
    g = random_geo_graph(20, 30, seed=3)
    g.name = "rand"
    save_graph(g, tmp_path / "g.pkl")
    h = load_graph(tmp_path / "g.pkl")
    assert (h.tail, h.time, h.coords, h.name) == (g.tail, g.time, g.coords, g.name)
    assert (h.fwd, h.bwd, h.vmax) == (g.fwd, g.bwd, g.vmax)  # derived fields rebuilt on load
    assert h.index_of(g.osm_ids[7]) == 7


def _two_vertex(**over):
    kw = dict(coords=[(37.5, 127.0)] * 2, osm_ids=[1, 2], tail=[0], head=[1],
              length=[1.0], time=[1.0], hwy=["residential"])
    kw.update(over)
    return Graph(**kw)


def test_vmax_special_cases():
    assert _two_vertex(length=[5.0], time=[0.0]).vmax == math.inf  # positive length in 0 s
    assert from_edge_list(2, [(0, 1, 0.0)]).vmax == 1.0  # no positive-length edge


def test_rejects_non_finite_time():
    with pytest.raises(ValueError):
        from_edge_list(2, [(0, 1, math.inf)])


@pytest.mark.parametrize("bad", [math.nan, -1.0, math.inf])
def test_rejects_invalid_length(bad):
    with pytest.raises(ValueError):
        _two_vertex(length=[bad])


def test_rejects_swapped_coords():  # (lon, lat) by mistake: Seoul's lon ~127 is not a latitude
    with pytest.raises(ValueError):
        _two_vertex(coords=[(127.0, 37.5)] * 2)


def test_repr_is_compact():
    r = repr(grid_graph(30, 30))
    assert len(r) < 200 and "n=900" in r


def test_subgraph_rejects_bad_vertices():
    g = grid_graph(3, 3)
    with pytest.raises(ValueError):
        g.subgraph([-1])
    with pytest.raises(ValueError):
        g.subgraph([0, 0])


def test_from_edge_list_checks_coords_and_uses_haversine():
    coords = [(37.5, 127.0), (37.5, 127.0113)]
    g = from_edge_list(2, [(0, 1, 10.0)], coords=coords)
    assert g.length[0] == pytest.approx(haversine_m(*coords))  # keeps A* admissible
    with pytest.raises(ValueError):
        from_edge_list(3, [(0, 1, 1.0)], coords=coords)
