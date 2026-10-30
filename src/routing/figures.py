"""Figures for the video and README (matplotlib; not a core module).

Uses matplotlib.figure.Figure directly (no pyplot), so no GUI backend is needed.
CLI: python scripts/make_figures.py NAME [NAME ...] [--graph PATH] [--out-dir DIR]   (NAME: f, ..., all)
"""
from __future__ import annotations

import argparse
import math
from pathlib import Path

from matplotlib.collections import LineCollection
from matplotlib.figure import Figure

from routing.graph import Graph, load_graph
from routing.heap import Stats

FIG_F_QUERY = ((37.4979, 127.0276), (37.5088, 127.0631))  # Gangnam Stn -> Samseong Stn (planner's choice)
FIG_F_ALGOS = ("dijkstra", "astar", "bidir", "alt16")


def collect_trace(algo, g: Graph, s: int, t: int) -> tuple[list[int], list[int]]:
    """(settled vertices in order, path) for one query."""
    st = Stats(trace=[])
    _, path, _ = algo(g, s, t, stats=st)
    return st.trace, path


def fig_f(g: Graph, s: int, t: int, algos: dict, out_png: str | Path) -> None:
    """Figure (f): one panel per algorithm showing what it settled for the same query."""
    names = list(algos)
    cols = min(2, len(names))
    rows = math.ceil(len(names) / cols)
    fig = Figure(figsize=(6 * cols, 5 * rows), layout="constrained")
    xy = [(lon, lat) for lat, lon in g.coords]
    roads = [(xy[u], xy[v]) for u, v in zip(g.tail, g.head)]
    aspect = 1 / math.cos(math.radians(sum(lat for lat, _ in g.coords) / g.n))
    for i, name in enumerate(names):
        trace, path = collect_trace(algos[name], g, s, t)
        ax = fig.add_subplot(rows, cols, i + 1)
        ax.add_collection(LineCollection(roads, colors="#d9d9d9", linewidths=0.4, zorder=1))
        ax.scatter([xy[v][0] for v in trace], [xy[v][1] for v in trace],
                   s=4, color="#4c78a8", alpha=0.6, linewidths=0, zorder=2, label="settled")
        ax.plot([xy[v][0] for v in path], [xy[v][1] for v in path],
                color="#e45756", linewidth=2.2, zorder=3, label="shortest path")
        ax.scatter([xy[s][0], xy[t][0]], [xy[s][1], xy[t][1]], s=40, color="black", zorder=4)
        ax.set_title(f"{name}: {len(trace):,} settled")
        ax.set_aspect(aspect)
        ax.autoscale_view()
        ax.set_xticks([])
        ax.set_yticks([])
        if i == 0:
            ax.legend(loc="lower right", fontsize=8)
    Path(out_png).parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_png, dpi=200)


def _make_f(args) -> Path:
    from routing.bench import standard_algos

    g = load_graph(args.graph)
    s, t = (g.nearest(*p) for p in FIG_F_QUERY)
    algos, _ = standard_algos(g, ks=(16,))
    out = Path(args.out_dir) / "fig_f_search_space.png"
    fig_f(g, s, t, {k: algos[k] for k in FIG_F_ALGOS}, out)
    return out


FIGURES = {"f": _make_f}  # Task 13/14/16/18 add "a", "b", "c", "d", "g"


def main(argv: list[str] | None = None) -> None:
    p = argparse.ArgumentParser(description="Make project figures.")
    p.add_argument("which", nargs="+", choices=[*FIGURES, "all"])
    p.add_argument("--graph", default="data/graphs/gangnam_graph_v1.pkl")
    p.add_argument("--out-dir", default="figures")
    args = p.parse_args(argv)
    for name in (list(FIGURES) if "all" in args.which else args.which):
        print(FIGURES[name](args))
