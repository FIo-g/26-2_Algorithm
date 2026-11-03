"""Task 23: static re-routing benefit (stand-in for E4 while SUMO is deferred)."""
import math

import pytest

from routing.congestion import random_slowdown
from routing.graph import Graph
from routing.queries import Query, make_queries
from routing.synthetic import grid_graph


def _hand_graph():
    """s=0, a=1, b=2, t=3. Free flow: s-a-t 20 s, s-a-b-t 23 s, s-b-t 24 s.

    The snapshot doubles s->a and a->t, so the kept free-flow path costs 40 s.
    """
    tail = [0, 1, 1, 0, 2]
    head = [1, 3, 2, 2, 3]
    time = [10.0, 10.0, 1.0, 12.0, 12.0]
    coords = [(37.5, 127.0), (37.5, 127.001), (37.501, 127.001), (37.5, 127.002)]
    g0 = Graph(coords=coords, osm_ids=[10, 11, 12, 13], tail=tail, head=head,
               length=[200.0] * 5, time=time, hwy=["primary"] * 5)
    snap = g0.reweighted([20.0, 20.0, 1.0, 12.0, 12.0])
    return g0, snap


def _rows(mode, rows):
    return [r for r in rows if r["mode"] == mode]


def test_depart_keeps_free_flow_path_vs_replans_on_snapshot():
    from routing.experiments.reroute_gain import reroute_gain
    g0, snap = _hand_graph()
    (row,) = _rows("depart", reroute_gain(g0, [Query(0, "a", 0, 3, 0.0)], graph="hand", scenarios={"x": snap}))
    # kept path s-a-t on the snapshot: 20 + 20; replanned: s-b-t 12 + 12
    assert (row["graph"], row["scenario"], row["qid"], row["bin"]) == ("hand", "x", 0, "a")
    assert (row["fixed_s"], row["reroute_s"], row["improved"]) == (40.0, 24.0, 1)
    assert row["saving"] == pytest.approx(0.4)


def test_midway_replans_from_the_e3_midpoint():
    from routing.experiments.reroute_gain import reroute_gain
    g0, snap = _hand_graph()
    (row,) = _rows("midway", reroute_gain(g0, [Query(0, "a", 0, 3, 0.0)], graph="hand", scenarios={"x": snap}))
    # E3's midpoint of s-a-t is a. First half s->a at free flow (10 s), then the snapshot applies:
    # kept a->t 20 s vs replanned a-b-t 1 + 12 s
    assert (row["fixed_s"], row["reroute_s"], row["improved"]) == (30.0, 23.0, 1)
    assert row["saving"] == pytest.approx(7 / 30)


def test_unchanged_snapshot_saves_nothing():
    from routing.experiments.reroute_gain import reroute_gain
    g = grid_graph(8, 8)
    qs = make_queries(g, per_bin=8, bins=[(0, 2000, "a")])
    rows = reroute_gain(g, qs, graph="grid", scenarios={"same": g.reweighted(g.time)})
    assert len(rows) == 2 * len(qs)  # one depart and one midway row per query
    assert all(r["saving"] == 0.0 and r["improved"] == 0 and r["fixed_s"] == r["reroute_s"] for r in rows)


def test_replanning_never_costs_more_than_keeping_the_path():
    from routing.experiments.reroute_gain import reroute_gain
    g = grid_graph(10, 10)
    qs = make_queries(g, per_bin=10, bins=[(0, 3000, "a")])
    rows = reroute_gain(g, qs, graph="grid", scenarios={"r": random_slowdown(g, frac=0.5, factor=3.0, seed=1)})
    assert all(r["reroute_s"] <= r["fixed_s"] * (1 + 1e-9) and 0.0 <= r["saving"] < 1.0 for r in rows)
    assert any(r["improved"] for r in rows)  # 50% of edges 3x slower: some trips must find a better path


def test_same_source_and_target_has_zero_saving():
    from routing.experiments.reroute_gain import reroute_gain
    g0, snap = _hand_graph()
    rows = reroute_gain(g0, [Query(0, "a", 2, 2, 0.0)], graph="hand", scenarios={"x": snap})
    assert all((r["fixed_s"], r["reroute_s"], r["saving"], r["improved"]) == (0.0, 0.0, 0.0, 0) for r in rows)


def test_unreachable_query_is_rejected():
    from routing.experiments.reroute_gain import reroute_gain
    g0, snap = _hand_graph()
    with pytest.raises(ValueError, match="unreachable"):
        reroute_gain(g0, [Query(0, "a", 3, 0, 0.0)], graph="hand", scenarios={"x": snap})  # t has no out-edges


def test_snapshot_with_other_topology_is_rejected():
    from routing.experiments.reroute_gain import reroute_gain
    g0, _ = _hand_graph()
    with pytest.raises(ValueError, match="topology"):
        reroute_gain(g0, [Query(0, "a", 0, 3, 0.0)], graph="hand", scenarios={"x": grid_graph(2, 2)})


def test_summarize_gain_per_bin_and_overall():
    from routing.experiments.reroute_gain import summarize_gain
    rows = [{"graph": "g", "scenario": "x", "mode": "depart", "qid": i, "bin": b,
             "fixed_s": 1.0, "reroute_s": 1.0 - s, "saving": s, "improved": int(s > 0)}
            for i, (b, s) in enumerate([("a", 0.0), ("a", 0.2), ("b", 0.4)])]
    by_bin = {r["bin"]: r for r in summarize_gain(rows)}
    assert set(by_bin) == {"a", "b", "all"}
    a, overall = by_bin["a"], by_bin["all"]
    assert (a["n"], a["n_improved"], a["p95_saving"], a["max_saving"]) == (2, 1, 0.2, 0.2)
    assert a["median_saving"] == pytest.approx(0.1) and a["mean_saving"] == pytest.approx(0.1)
    assert (overall["n"], overall["n_improved"], overall["p95_saving"]) == (3, 2, 0.4)  # nearest-rank p95
    assert overall["median_saving"] == pytest.approx(0.2) and overall["mean_saving"] == pytest.approx(0.2)
    assert (overall["graph"], overall["scenario"], overall["mode"]) == ("g", "x", "depart")


# ---- CLI: scripts/run_reroute_gain.py ----
import csv
import importlib.util
import json
from pathlib import Path

from routing.graph import save_graph
from routing.queries import save_queries

REPO = Path(__file__).resolve().parents[1]


def _load_script():
    spec = importlib.util.spec_from_file_location("run_reroute_gain_cli_test", REPO / "scripts" / "run_reroute_gain.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _inputs(root, names=("gss",)):
    """Tiny graph + query files named like the real ones (the CLI only accepts the three real names)."""
    g = grid_graph(8, 8)
    qs = make_queries(g, per_bin=6, bins=[(0, 400, "near"), (400, 1500, "far")])
    (root / "graphs").mkdir()
    for name in names:
        save_graph(g, root / "graphs" / f"{name}_graph_v1.pkl")
        save_queries(root / "queries" / f"{name}_q_seed42.csv", g, qs)
    return ["--graphs-dir", str(root / "graphs"), "--queries-dir", str(root / "queries"),
            "--results-dir", str(root / "results")]


def _csv(path):
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def test_run_reroute_gain_cli_writes_outputs_and_guards_overwrite(tmp_path, capsys):
    cli = _load_script()
    common = _inputs(tmp_path)
    assert cli.main(["gss", *common]) == 0
    results = tmp_path / "results"
    rows = _csv(results / "reroute_gain_gss.csv")
    assert {r["scenario"] for r in rows} == {"synth08", "synth18", "random30"}  # congestion snapshots only
    assert len(rows) == 3 * 2 * 12  # scenarios x modes x queries
    summary = _csv(results / "reroute_gain_gss_summary.csv")
    assert {(r["mode"], r["bin"]) for r in summary} >= {("depart", "all"), ("midway", "far")}
    manifest = json.loads((results / "reroute_gain_gss_manifest.json").read_text())
    assert manifest["nodes"] == 64 and manifest["query_count"] == 12 and len(manifest["graph_sha256"]) == 64
    assert manifest["scenarios"] == ["synth08", "synth18", "random30"] and manifest["scenario_seed"] == 0
    before = (results / "reroute_gain_gss.csv").read_text()
    with pytest.raises(SystemExit):
        cli.main(["gss", *common])
    assert "--overwrite" in capsys.readouterr().err
    assert (results / "reroute_gain_gss.csv").read_text() == before  # refused run left the files alone
    assert cli.main(["gss", *common, "--overwrite"]) == 0


def test_run_reroute_gain_cli_missing_inputs_stop_before_loading(tmp_path, capsys):
    cli = _load_script()
    with pytest.raises(SystemExit):
        cli.main(["seoul", "--graphs-dir", str(tmp_path), "--results-dir", str(tmp_path / "results")])
    assert "blocked" in capsys.readouterr().err and not (tmp_path / "results").exists()
