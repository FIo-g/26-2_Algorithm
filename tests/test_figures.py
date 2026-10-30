import pytest

from routing import figures
from routing.bench import standard_algos
from routing.figures import collect_trace, fig_f, main
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
