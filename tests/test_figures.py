import json

import pytest

from routing import figures
from routing.bench import standard_algos
from routing.figures import collect_trace, fig_f, fig_g, graph_table, main
from routing.graph import save_graph
from routing.synthetic import grid_graph

PNG = b"\x89PNG\r\n\x1a\n"


def test_collect_trace_matches_settled():
    g = grid_graph(10, 10)
    algos, _ = standard_algos(g, ks=())
    for name, algo in algos.items():
        trace, path = collect_trace(algo, g, 0, 99)
        assert len(trace) == algo(g, 0, 99)[2] and path[0] == 0 and path[-1] == 99, name


def test_fig_f_writes_png(tmp_path):
    g = grid_graph(10, 10)
    algos, _ = standard_algos(g, ks=())
    fig_f(g, 0, 99, algos, tmp_path / "f.png")
    assert (tmp_path / "f.png").read_bytes()[:8] == PNG


def test_make_figures_accepts_several_names(monkeypatch):  # plan Task 16 runs `make_figures.py c d`
    calls = []
    monkeypatch.setitem(figures.FIGURES, "x", lambda args: calls.append("x") or "x.png")
    monkeypatch.setitem(figures.FIGURES, "y", lambda args: calls.append("y") or "y.png")
    main(["x", "y"])
    assert calls == ["x", "y"]


def test_make_figures_f(tmp_path):
    pytest.importorskip("routing.alt")  # alt16 panel needs 의종's Task 8
    save_graph(grid_graph(10, 10), tmp_path / "g.pkl")
    main(["f", "--graph", str(tmp_path / "g.pkl"), "--out-dir", str(tmp_path)])
    assert (tmp_path / "fig_f_search_space.png").read_bytes()[:8] == PNG


def test_graph_table_from_meta(tmp_path):
    p = tmp_path / "x_graph_v1.meta.json"
    p.write_text(json.dumps({"name": "x", "n": 10, "m": 20, "vmax_mps": 20.0, "maxspeed_missing_ratio": 0.9}))
    assert graph_table([p]) == [{"name": "x", "n": 10, "m": 20, "vmax_kph": 72.0, "maxspeed_missing_ratio": 0.9}]


def test_graph_table_rejects_missing_field(tmp_path):
    p = tmp_path / "x_graph_v1.meta.json"
    p.write_text(json.dumps({"name": "x", "n": 10, "m": 20, "vmax_mps": 20.0}))
    with pytest.raises(ValueError, match="maxspeed_missing_ratio"):
        graph_table([p])


def test_fig_g_one_panel_per_graph_with_shared_legend(tmp_path):
    paths = []
    for name, hwy in (("a", "primary"), ("b", "trunk_link")):
        paths.append(tmp_path / f"{name}.pkl")
        save_graph(grid_graph(4, 4, hwy=hwy), paths[-1])
    fig = fig_g(paths, tmp_path / "g.png")
    assert (tmp_path / "g.png").read_bytes()[:8] == PNG
    assert len(fig.axes) == 2
    labels = [t.get_text() for t in fig.legends[0].get_texts()]
    assert labels == ["trunk", "primary"]  # hwy_class groups trunk_link with trunk; major roads first


def test_make_figures_g(tmp_path):
    graphs = tmp_path / "graphs"
    graphs.mkdir()
    for name in figures.FIG_G_GRAPHS:
        g = grid_graph(3, 3)
        save_graph(g, graphs / f"{name}_graph_v1.pkl")
        (graphs / f"{name}_graph_v1.meta.json").write_text(json.dumps(
            {"name": name, "n": g.n, "m": g.m, "vmax_mps": g.vmax, "maxspeed_missing_ratio": 1.0}))
    main(["g", "--graphs-dir", str(graphs), "--results-dir", str(tmp_path / "results"),
          "--out-dir", str(tmp_path / "figures")])
    assert (tmp_path / "figures" / "fig_g_graphs.png").read_bytes()[:8] == PNG
    table = (tmp_path / "results" / "graph_table.csv").read_text().splitlines()
    assert table[0] == "name,n,m,vmax_kph,maxspeed_missing_ratio" and len(table) == 4
