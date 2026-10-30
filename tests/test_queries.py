import pytest

from routing.queries import BINS_M, Query, load_queries, make_queries, save_queries
from routing.synthetic import grid_graph

SMALL = [(0, 300, "a"), (300, 700, "b")]


def test_deterministic_and_binned():
    g = grid_graph(10, 10)
    q1 = make_queries(g, per_bin=20, bins=SMALL, seed=1)
    q2 = make_queries(g, per_bin=20, bins=SMALL, seed=1)
    assert q1 == q2 and len(q1) == 40
    assert all((q.crow_m < 300) == (q.bin == "a") for q in q1)
    assert [q.qid for q in q1] == list(range(40)) and all(q.s != q.t for q in q1)


def test_unfillable_bin_warns():  # Review Focus 5
    with pytest.warns(UserWarning) as rec:  # both 3-10km and >10km are unfillable on a 400 m grid
        qs = make_queries(grid_graph(5, 5), per_bin=5, max_tries=5_000)
    assert any(">10km" in str(w.message) for w in rec)
    assert not any(q.bin == ">10km" for q in qs) and sum(q.bin == "<3km" for q in qs) == 5


def test_save_load_roundtrip(tmp_path):
    g = grid_graph(6, 6)
    qs = make_queries(g, per_bin=5, bins=SMALL)
    save_queries(tmp_path / "q.csv", g, qs)
    assert [(q.s, q.t) for q in load_queries(tmp_path / "q.csv", g)] == [(q.s, q.t) for q in qs]


def test_load_rejects_other_graph(tmp_path):
    g = grid_graph(6, 6)
    save_queries(tmp_path / "q.csv", g, make_queries(g, per_bin=5, bins=SMALL))
    with pytest.raises(KeyError, match="graph version mismatch"):
        load_queries(tmp_path / "q.csv", grid_graph(2, 2))


def test_default_bins():
    assert [b[2] for b in BINS_M] == ["<3km", "3-10km", ">10km"]
    assert Query._fields == ("qid", "bin", "s", "t", "crow_m")
