import pytest

from routing.bench import ExactnessError, Row, standard_algos, summarize, time_all, write_csv
from routing.dijkstra import dijkstra
from routing.queries import make_queries
from routing.synthetic import grid_graph

BIN = [(0, 2000, "a")]


def test_standard_algos_without_alt():
    algos, lms = standard_algos(grid_graph(8, 8), ks=())
    assert set(algos) == {"dijkstra", "astar", "bidir"} and lms == {}


def test_standard_algos_with_alt():
    pytest.importorskip("routing.alt")  # runs once 의종's Task 8 is merged
    algos, lms = standard_algos(grid_graph(8, 8), ks=(4,))
    assert "alt4" in algos and lms[4].k <= 4


def test_time_all_times_every_query():
    g = grid_graph(8, 8)
    qs = make_queries(g, per_bin=10, bins=BIN)
    algos, _ = standard_algos(g, ks=())
    rows = time_all(g, qs, algos, graph="grid", warmup=5)
    assert len(rows) == len(qs) * len(algos)  # warm-up runs are extra, not subtracted
    assert all(r.time_s > 0 and (r.graph, r.scenario, r.kind) == ("grid", "free", "full") for r in rows)


def test_rows_carry_distance_and_counters():
    g = grid_graph(8, 8)
    qs = make_queries(g, per_bin=5, bins=BIN)
    rows = time_all(g, qs, {"dijkstra": dijkstra}, graph="grid")
    for q, r in zip(qs, rows):
        d, _, settled = dijkstra(g, q.s, q.t)
        assert (r.dist, r.settled) == (d, settled) and r.pops >= r.settled and r.pushes >= r.settled


def test_summarize_ratios():
    g = grid_graph(8, 8)
    qs = make_queries(g, per_bin=10, bins=BIN)
    algos, _ = standard_algos(g, ks=())
    s = {r["algo"]: r for r in summarize(time_all(g, qs, algos, graph="grid"))}
    assert s["dijkstra"]["speedup"] == 1.0 and s["dijkstra"]["settled_ratio"] == 1.0
    assert s["astar"]["median_settled"] <= s["dijkstra"]["median_settled"]


def test_summarize_p95_nearest_rank():
    rows = [Row("g", "free", "full", i, "a", "dijkstra", float(i), 0.0, i, 0, 0, 0) for i in range(1, 21)]
    (r,) = summarize(rows)
    assert (r["n"], r["median_s"], r["p95_s"]) == (20, 10.5, 19.0)


def test_write_csv_accepts_dicts_and_rows(tmp_path):
    write_csv(tmp_path / "a.csv", [{"x": 1}])
    write_csv(tmp_path / "b.csv", [Row(*range(12))])
    assert (tmp_path / "a.csv").read_text().splitlines() == ["x", "1"]
    assert (tmp_path / "b.csv").read_text().splitlines()[0].startswith("graph,scenario,kind")


def test_exactness_error_is_an_exception():
    assert issubclass(ExactnessError, Exception)
