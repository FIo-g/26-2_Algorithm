import os
import subprocess
import sys
import tracemalloc
from pathlib import Path

import pytest

from routing.astar import astar
from routing.bench import ExactnessError, Row, standard_algos, summarize, time_all, write_csv
from routing.bidirectional import bidirectional_dijkstra
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


def test_time_all_accepts_a_generator():
    g = grid_graph(6, 6)
    qs = make_queries(g, per_bin=5, bins=BIN)
    assert len(time_all(g, (q for q in qs), {"dijkstra": dijkstra}, graph="grid")) == len(qs)


@pytest.fixture(scope="module")
def big_grid():
    return grid_graph(150, 150)  # 22,500 vertices: one per-vertex list is ~180 KB


@pytest.mark.parametrize("algo", [dijkstra, astar, bidirectional_dijkstra], ids=["dijkstra", "astar", "bidir"])
def test_short_query_cost_does_not_scale_with_graph(big_grid, algo):
    # Per-query arrays of size n would dominate short (reroute) query times and skew speedups.
    tracemalloc.start()
    try:
        algo(big_grid, 0, 1)
        peak = tracemalloc.get_traced_memory()[1]
    finally:
        tracemalloc.stop()
    assert peak < 50_000


# --- Task 22: scripts/run_all.sh (dry-run and guards only; the real run is on 11/5) ---
REPO = Path(__file__).resolve().parents[1]


def _run_all(tmp_path, *args, decision=None, **env):
    if decision is not None:
        (tmp_path / "match_decision.md").write_text(decision)
    return subprocess.run(["bash", "scripts/run_all.sh", *args], cwd=REPO, capture_output=True, text=True,
                          env={**os.environ, "RESULTS_DIR": str(tmp_path), **env})


def test_run_all_dry_run_real_only_for_gss(tmp_path):
    out = _run_all(tmp_path, "--dry-run", "--allow-collector", decision="ADOPT\ncoverage 78%\n").stdout
    assert "run_e3.py gss --real" in out and "run_e3.py seoul --real" not in out


def test_run_all_dry_run_order_without_adoption(tmp_path):
    r = _run_all(tmp_path, "--dry-run", "--allow-collector", decision="REJECT\n")
    out = r.stdout
    assert r.returncode == 0 and "--real" not in out
    assert (out.index("tests/test_correctness.py") < out.index("check_exact.py") < out.index("run_e1.py")
            < out.index("run_e2.py") < out.index("run_e3.py") < out.index("make_figures.py all"))
    assert not (tmp_path / "machine.txt").exists()  # dry run writes nothing


def test_run_all_stops_when_collector_runs(tmp_path):
    marker = f"fake-collector-{os.getpid()}"
    # stands in for the speed collector; the marker stays in argv (sh -c would exec sleep and drop it)
    fake = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(30)", marker])
    try:
        r = _run_all(tmp_path, "--dry-run", COLLECTOR_PATTERN=marker)
    finally:
        fake.kill()
        fake.wait()
    assert r.returncode == 2 and "collector" in r.stderr
    assert _run_all(tmp_path, "--dry-run", COLLECTOR_PATTERN=marker).returncode == 0  # gone -> runs


@pytest.mark.parametrize("first", ["**ADOPT**", "adopt", "# ADOPT", "maybe", ""])
def test_run_all_rejects_malformed_decision(tmp_path, first):
    r = _run_all(tmp_path, "--dry-run", "--allow-collector", decision=first + "\n")
    assert r.returncode != 0 and "match_decision" in r.stderr  # never silently drop the real-speed run


def test_run_all_rejects_unknown_option(tmp_path):
    assert _run_all(tmp_path, "--nope").returncode == 64
