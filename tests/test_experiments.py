"""Task 14: E2 run (speedup, ALT preprocessing, bound tightness) and figure (b)."""
import csv
import importlib.util
import json
import os
import subprocess
import shutil
from pathlib import Path

import pytest

from routing.bench import ExactnessError, summarize, write_csv
from routing.dijkstra import dijkstra
from routing.experiments import e2
from routing.experiments.e2 import run_e2
from routing.graph import save_graph
from routing.queries import make_queries, save_queries
from routing.synthetic import grid_graph

REPO = Path(__file__).resolve().parents[1]
PNG = b"\x89PNG\r\n\x1a\n"


def test_run_e2_smoke():
    g = grid_graph(12, 12); qs = make_queries(g, per_bin=10, bins=[(0, 500, "a"), (500, 2000, "b")])
    rows, prep, tight = run_e2(g, qs, graph="grid", ks=(4,))
    assert {r.algo for r in rows} == {"dijkstra", "astar", "bidir", "alt4"}
    assert prep[0]["k"] == 4 and prep[0]["breakeven"] > 0
    assert all(0 <= r["ratio"] <= 1 for r in tight) and {r["algo"] for r in tight} == {"astar", "alt4"}


def test_run_e2_refuses_to_time_wrong_algo():
    g = grid_graph(6, 6); qs = make_queries(g, per_bin=5, bins=[(0, 1000, "a")])
    bad = {"dijkstra": dijkstra, "bad": lambda g, s, t, stats=None: (0.5, [s, t], 0)}
    with pytest.raises(ExactnessError):
        run_e2(g, qs, graph="grid", algos=bad)


def test_run_e2_gate_runs_before_any_timer(monkeypatch):
    g = grid_graph(6, 6); qs = make_queries(g, per_bin=5, bins=[(0, 1000, "a")])
    bad = {"dijkstra": dijkstra, "bad": lambda g, s, t, stats=None: (0.5, [s, t], 0)}
    monkeypatch.setattr(e2, "time_all", lambda *a, **k: pytest.fail("timed before the gate passed"))
    with pytest.raises(ExactnessError, match="bad q"):
        run_e2(g, qs, graph="grid", algos=bad)


def test_run_e2_prep_and_tightness_rows():
    g = grid_graph(12, 12); qs = make_queries(g, per_bin=10, bins=[(0, 500, "a"), (500, 2000, "b")])
    rows, prep, tight = run_e2(g, qs, graph="grid", ks=(4, 8))
    assert [p["k"] for p in prep] == [4, 8]
    assert all(p["graph"] == "grid" and p["k_actual"] <= p["k"] and p["prep_s"] > 0 and p["nbytes"] > 0 for p in prep)
    assert all(t["dist"] > 0 and t["ratio"] == t["h0"] / t["dist"] for t in tight)
    assert len(tight) == len(qs) * 3  # astar, alt4, alt8 for every reachable query
    assert {t["bin"] for t in tight} == {"a", "b"}


def _fig_b_inputs(root):
    # hand-made CSVs: one empty speedup cell (summarize writes None as ""), Gangnam has the >10km bin
    summary = [dict(graph=gr, scenario="free", kind="full", bin=b, algo=a, n=10, median_s=0.1, p95_s=0.2,
                    median_settled=100, speedup=("" if (gr, b, a) == ("gss", "3-10km", "alt4") else sp), settled_ratio=sr)
               for gr, bins in (("gangnam", ["<3km", "3-10km", ">10km"]), ("gss", ["<3km", "3-10km"]))
               for b in bins
               for a, sp, sr in (("dijkstra", 1.0, 1.0), ("astar", 1.5, 0.5), ("alt4", 4.0, 0.1))]
    tight = [dict(graph=gr, qid=i, bin=b, algo=a, h0=r * 100, dist=100.0, ratio=r)
             for gr, bins in (("gangnam", ["<3km", "3-10km", ">10km"]), ("gss", ["<3km", "3-10km"]))
             for i, b in enumerate(bins) for a, r in (("astar", 0.6), ("alt4", 0.9))]
    write_csv(root / "summary.csv", summary)
    write_csv(root / "tight.csv", tight)
    return root / "summary.csv", root / "tight.csv"


def test_fig_b_renders_png_and_marks_corner_pairs(tmp_path):
    pytest.importorskip("matplotlib")
    from routing.figures import fig_b
    summary, tight = _fig_b_inputs(tmp_path)
    fig = fig_b(summary, tight, tmp_path / "b.png")
    assert (tmp_path / "b.png").read_bytes()[:8] == PNG and (tmp_path / "b.png").stat().st_size > 1000
    labels = [t.get_text() for ax in fig.axes for t in ax.get_xticklabels()]
    assert sum("corner pairs only" in s for s in labels) == 3  # gangnam column only, one per panel row


def test_make_figures_b(tmp_path):
    pytest.importorskip("matplotlib")
    from routing.figures import FIGURES, main
    assert "b" in FIGURES
    results = tmp_path / "results"; results.mkdir()
    summary, tight = _fig_b_inputs(tmp_path)
    shutil.copy(summary, results / "e2_summary.csv"); shutil.copy(tight, results / "e2_tightness.csv")
    main(["b", "--results-dir", str(results), "--out-dir", str(tmp_path / "figures")])
    assert (tmp_path / "figures" / "fig_b_speedup.png").read_bytes()[:8] == PNG


def _load_script():
    spec = importlib.util.spec_from_file_location("run_e2_cli_test", REPO / "scripts" / "run_e2.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _inputs(root, names=("gangnam",)):
    """Tiny graph + query files named like the real ones (the CLI only accepts the three real names)."""
    g = grid_graph(8, 8)
    qs = make_queries(g, per_bin=6, bins=[(0, 400, "near"), (400, 1500, "far")])
    (root / "graphs").mkdir()  # save_graph does not create folders
    for name in names:
        save_graph(g, root / "graphs" / f"{name}_graph_v1.pkl")
        save_queries(root / "queries" / f"{name}_q_seed42.csv", g, qs)
    return ["--graphs-dir", str(root / "graphs"), "--queries-dir", str(root / "queries"),
            "--results-dir", str(root / "results"), "--ks", "4"]


def _graphs_in(path):
    with open(path, newline="") as f:
        return [row["graph"] for row in csv.DictReader(f)]


def test_run_e2_cli_writes_outputs_and_guards_overwrite(tmp_path, capsys):
    cli = _load_script()
    common = _inputs(tmp_path)
    assert cli.main(["gangnam", *common]) == 0
    results = tmp_path / "results"
    for name in ("e2_gangnam.csv", "e2_alt_prep.csv", "e2_tightness.csv", "e2_summary.csv", "e2_gangnam_manifest.json"):
        assert (results / name).is_file(), name
    manifest = json.loads((results / "e2_gangnam_manifest.json").read_text())
    assert manifest["nodes"] == 64 and manifest["query_count"] == 12 and len(manifest["graph_sha256"]) == 64
    assert set(_graphs_in(results / "e2_summary.csv")) == {"gangnam"}
    assert _graphs_in(results / "e2_alt_prep.csv") == ["gangnam"]
    before = (results / "e2_summary.csv").read_text()
    with pytest.raises(SystemExit):
        cli.main(["gangnam", *common])
    assert "--overwrite" in capsys.readouterr().err
    assert (results / "e2_summary.csv").read_text() == before  # refused run left the files alone
    assert cli.main(["gangnam", *common, "--overwrite"]) == 0


def test_run_e2_cli_keeps_other_graphs_in_shared_csvs(tmp_path):
    cli = _load_script()
    common = _inputs(tmp_path, names=("gangnam", "gss"))
    assert cli.main(["gangnam", *common]) == 0
    assert cli.main(["gss", *common]) == 0  # different graph: no --overwrite needed
    assert cli.main(["gangnam", *common, "--overwrite"]) == 0
    results = tmp_path / "results"
    assert sorted(_graphs_in(results / "e2_alt_prep.csv")) == ["gangnam", "gss"]  # one row each, not doubled
    assert set(_graphs_in(results / "e2_tightness.csv")) == {"gangnam", "gss"}
    assert set(_graphs_in(results / "e2_summary.csv")) == {"gangnam", "gss"}


def test_run_e2_cli_missing_inputs_stop_before_loading(tmp_path, capsys):
    cli = _load_script()
    with pytest.raises(SystemExit):
        cli.main(["seoul", "--graphs-dir", str(tmp_path), "--results-dir", str(tmp_path / "results")])
    assert "blocked" in capsys.readouterr().err and not (tmp_path / "results").exists()


def test_run_all_passes_overwrite_to_e2(tmp_path):
    r = subprocess.run(["bash", "scripts/run_all.sh", "--dry-run", "--allow-collector"], cwd=REPO, capture_output=True,
                       text=True, env={**os.environ, "RESULTS_DIR": str(tmp_path)})
    assert r.returncode == 0 and "run_e2.py gangnam gss seoul --overwrite" in r.stdout
