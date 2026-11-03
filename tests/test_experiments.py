"""Task 14: E2 run (speedup, ALT preprocessing, bound tightness) and figure (b)."""
import csv
import importlib.util
import json
import os
import subprocess
import shutil
from pathlib import Path

import pytest

from routing.bench import ExactnessError, write_csv
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
               for a, sp, sr in (("dijkstra", 1.0, 1.0), ("astar", 1.5, 0.5), ("bidir", 2.0, 0.4), ("alt4", 4.0, 0.1))]
    # like the real data: bidir has speedup rows only, no tightness rows
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


def test_fig_b_same_algorithm_same_color_in_every_row(tmp_path):
    pytest.importorskip("matplotlib")
    from routing.figures import fig_b
    summary, tight = _fig_b_inputs(tmp_path)
    fig = fig_b(summary, tight, tmp_path / "b.png")
    def algo_lines(ax):  # drop the dashed Dijkstra reference (axhline has a "_"-prefixed label)
        return [line for line in ax.get_lines() if not line.get_label().startswith("_")]

    ncols = len(fig.axes) // 3  # subplots are row-major: row r, column c is fig.axes[r * ncols + c]
    for col in range(ncols):
        top, bottom = fig.axes[col], fig.axes[2 * ncols + col]
        top_colors = {line.get_label(): line.get_color() for line in algo_lines(top)}
        bottom_lines = algo_lines(bottom)
        assert {line.get_label() for line in bottom_lines} <= set(top_colors) and "alt4" in top_colors
        for line in bottom_lines:
            assert line.get_color() == top_colors[line.get_label()], line.get_label()
    # the top row of the first column has astar, bidir and alt4, each with its own color
    first = {line.get_label(): line.get_color() for line in algo_lines(fig.axes[0])}
    assert set(first) == {"astar", "bidir", "alt4"} and len(set(first.values())) == 3


def test_make_figures_b(tmp_path):
    pytest.importorskip("matplotlib")
    from routing.figures import FIGURES, main
    assert "b" in FIGURES
    results = tmp_path / "results"; results.mkdir()
    summary, tight = _fig_b_inputs(tmp_path)
    shutil.copy(summary, results / "e2_summary.csv"); shutil.copy(tight, results / "e2_tightness.csv")
    main(["b", "--results-dir", str(results), "--out-dir", str(tmp_path / "figures")])
    assert (tmp_path / "figures" / "fig_b_speedup.png").read_bytes()[:8] == PNG


SLIDES = ("fig_b1_settled.png", "fig_b2_speedup.png", "fig_b3_tightness.png")


def _lines(ax):
    """(label, color, y values) of the algorithm lines, without the dashed Dijkstra reference.
    A missing bin is drawn as nan, and nan != nan, so it is compared as None."""
    import math
    return [(l.get_label(), l.get_color(), [None if math.isnan(y) else round(float(y), 9) for y in l.get_ydata()])
            for l in ax.get_lines() if not l.get_label().startswith("_")]


def test_fig_b_slides_one_png_per_row(tmp_path):
    pytest.importorskip("matplotlib")
    from routing.figures import fig_b_slides
    summary, tight = _fig_b_inputs(tmp_path)
    figs = fig_b_slides(summary, tight, tmp_path / "slides")
    assert len(figs) == 3
    for name, fig in zip(SLIDES, figs):
        assert (tmp_path / "slides" / name).read_bytes()[:8] == PNG, name
        assert len(fig.axes) == 2  # one panel per graph (gangnam, gss), side by side


def test_fig_b_slides_show_the_same_lines_as_fig_b(tmp_path):
    pytest.importorskip("matplotlib")
    from routing.figures import fig_b, fig_b_slides
    summary, tight = _fig_b_inputs(tmp_path)
    full = fig_b(summary, tight, tmp_path / "b.png")
    slides = fig_b_slides(summary, tight, tmp_path / "slides")
    ncols = len(full.axes) // 3
    for row, slide in enumerate(slides):
        for col in range(ncols):
            assert _lines(slide.axes[col]) == _lines(full.axes[row * ncols + col]), (row, col)


def test_fig_b_slides_use_larger_text(tmp_path):
    pytest.importorskip("matplotlib")
    from routing.figures import fig_b, fig_b_slides
    summary, tight = _fig_b_inputs(tmp_path)
    full = fig_b(summary, tight, tmp_path / "b.png")
    slide = fig_b_slides(summary, tight, tmp_path / "slides")[0]
    size = lambda fig: fig.axes[0].get_xticklabels()[0].get_fontsize()
    assert size(slide) >= 1.4 * size(full)  # readable on a recorded slide


def test_make_figures_b_also_writes_slides(tmp_path):
    pytest.importorskip("matplotlib")
    from routing.figures import main
    results = tmp_path / "results"; results.mkdir()
    summary, tight = _fig_b_inputs(tmp_path)
    shutil.copy(summary, results / "e2_summary.csv"); shutil.copy(tight, results / "e2_tightness.csv")
    main(["b", "--results-dir", str(results), "--out-dir", str(tmp_path / "figures")])
    for name in SLIDES:
        assert (tmp_path / "figures" / name).read_bytes()[:8] == PNG, name


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


# ---- Task 13: E1 (exhaustive search limit) and figure (a) ----

from routing.experiments import e1 as e1_module
from routing.experiments.e1 import grid_counts, run_e1
from routing.exhaustive import ExhaustiveResult


def test_run_e1_stops_at_first_timeout():
    rows = run_e1(grid_graph(8, 8), 0, start_n=6, per_size=3, time_limit_s=0.02, max_n=64)
    last = max(r["target_n"] for r in rows)
    assert any(r["timed_out"] for r in rows if r["target_n"] == last)
    assert not any(r["timed_out"] for r in rows if r["target_n"] < last)


def test_run_e1_actual_sizes_strictly_increase():
    rows = run_e1(grid_graph(8, 8), 0, start_n=6, per_size=2, time_limit_s=0.02, max_n=64)
    sizes = sorted({(r["target_n"], r["actual_n"]) for r in rows})
    assert all(a[1] < b[1] for a, b in zip(sizes, sizes[1:]))


def test_grid_counts_values():
    assert [r["paths"] for r in grid_counts()] == [12, 184, 8512, 1262816, 575780564]


def test_run_e1_rows_and_max_n_stop():
    rows = run_e1(grid_graph(4, 4), 0, start_n=4, step=4, per_size=2, time_limit_s=5.0, max_n=12)
    assert {r["target_n"] for r in rows} == {4, 8, 12} and not any(r["timed_out"] for r in rows)
    assert set(rows[0]) == {"target_n", "actual_n", "actual_m", "qid", "ex_time_s", "ex_paths",
                            "timed_out", "dij_time_s"}
    assert all(r["ex_paths"] >= 1 and r["actual_n"] >= r["target_n"] for r in rows)


def test_run_e1_refuses_wrong_exhaustive(monkeypatch):
    monkeypatch.setattr(e1_module, "exhaustive_shortest",
                        lambda g, s, t, time_limit_s: ExhaustiveResult(0.0, [s], 1, False))
    with pytest.raises(ExactnessError):
        run_e1(grid_graph(4, 4), 0, start_n=4, per_size=2, max_n=8)


def test_fig_a_renders_png(tmp_path):
    from routing.figures import fig_a
    rows = run_e1(grid_graph(8, 8), 0, start_n=6, per_size=2, time_limit_s=0.02, max_n=64)
    write_csv(tmp_path / "e1.csv", rows)
    fig_a(tmp_path / "e1.csv", tmp_path / "a.png")
    assert (tmp_path / "a.png").read_bytes().startswith(PNG)
