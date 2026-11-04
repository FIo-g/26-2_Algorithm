"""Figures for the video and README (matplotlib; not a core module).

Uses matplotlib.figure.Figure directly (no pyplot), so no GUI backend is needed.
CLI: python scripts/make_figures.py NAME [NAME ...] [--graph PATH] [--out-dir DIR]   (NAME: f, ..., all)
"""
from __future__ import annotations

import argparse
import math
from pathlib import Path

import csv
import json
import re
import statistics
from collections import defaultdict

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
    from matplotlib.collections import LineCollection
    from matplotlib.figure import Figure

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
    p.add_argument("--out-dir", "--output-dir", dest="out_dir", default="figures")
    p.add_argument("--results-dir", default="results")
    p.add_argument("--e3-graph", default="gss", choices=("gangnam", "gss", "seoul"))
    p.add_argument("--graphs-dir", default="data/graphs", help="figure g: {name}_graph_v1.pkl and .meta.json")
    args = p.parse_args(argv)
    for name in (list(FIGURES) if "all" in args.which else args.which):
        print(FIGURES[name](args))


def _paths(paths):
    return [Path(paths)] if isinstance(paths, (str, Path)) else [Path(p) for p in paths]


def _read_rows(paths, required):
    rows = []
    for path in _paths(paths):
        with path.open(newline="", encoding="utf-8-sig") as stream:
            reader = csv.DictReader(stream)
            missing = set(required) - set(reader.fieldnames or ())
            if missing:
                raise ValueError(f"{path}: missing CSV columns {sorted(missing)}")
            for row in reader:
                if not row.get("graph"):
                    match = re.fullmatch(r"e3_(.+)_(?:accuracy|timing)\.csv", path.name)
                    if not match:
                        raise ValueError(f"{path}: a graph column is required")
                    row["graph"] = match.group(1)
                rows.append(row)
    if not rows:
        raise ValueError("No measured CSV rows were supplied")
    return rows


def _number(row, key, *, positive=False):
    try:
        value = float(row[key])
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError(f"invalid {key}: {row.get(key)!r}") from exc
    if not math.isfinite(value) or value < 0 or (positive and value == 0):
        raise ValueError(f"{key} must be finite and {'positive' if positive else 'nonnegative'}")
    return value


def _accuracy_summary(paths):
    """Return per-graph/scenario/algorithm accuracy without assuming failures."""
    totals = defaultdict(lambda: [0, 0])
    for row in _read_rows(paths, {"scenario", "algo", "n", "n_wrong"}):
        n, wrong = _number(row, "n", positive=True), _number(row, "n_wrong")
        if n != int(n) or wrong != int(wrong) or wrong > n:
            raise ValueError("n and n_wrong must be integer counts with 0 <= n_wrong <= n")
        key = (row["graph"], row["scenario"], row["algo"])
        totals[key][0] += int(n)
        totals[key][1] += int(wrong)
    return [{"graph": g, "scenario": s, "algo": a, "n": n, "n_wrong": wrong,
             "accuracy_pct": 100 * (n - wrong) / n}
            for (g, s, a), (n, wrong) in sorted(totals.items())]


def _timing_summary(paths):
    """Aggregate raw full-query rows; speedup is a ratio of pooled medians.

    Negative-control rows are excluded even if a caller supplies them. Each
    graph/scenario must contain Dijkstra; graph sizes are never pooled.
    """
    groups = defaultdict(lambda: ([], []))
    for row in _read_rows(paths, {"scenario", "algo", "time_s", "settled"}):
        if row["scenario"] == "control" or row.get("kind", "full") != "full":
            continue
        key = (row["graph"], row["scenario"], row["algo"])
        groups[key][0].append(_number(row, "time_s", positive=True))
        groups[key][1].append(_number(row, "settled"))
    if not groups:
        raise ValueError("No safe full-query timing rows were supplied")
    medians = {key: (statistics.median(ts), statistics.median(ns))
               for key, (ts, ns) in groups.items()}
    out = []
    for (graph, scenario, algo), (time_s, settled) in sorted(medians.items()):
        base = medians.get((graph, scenario, "dijkstra"))
        if base is None:
            raise ValueError(f"Missing Dijkstra baseline for {graph}/{scenario}")
        out.append({"graph": graph, "scenario": scenario, "algo": algo,
                    "median_s": time_s, "median_settled": settled,
                    "speedup": base[0] / time_s,
                    "settled_ratio": (1.0 if algo == "dijkstra" else
                                      settled / base[1] if base[1] else math.nan)})
    return out


def _tradeoff_summary(alt_prep_csv, e3_timing_csv):
    """Pair E2 preprocessing costs with E3 synth08 medians for each graph/k.

    The caller must ensure the E2 index was built on the same lower-bound graph
    used in E3. E2's saved breakeven value is deliberately not reused: the
    denominator below is recomputed from the E3 synth08 measurements.
    """
    timing = [r for r in _timing_summary(e3_timing_csv) if r["scenario"] == "synth08"]
    by_key = {(r["graph"], r["algo"]): r for r in timing}
    if not by_key:
        raise ValueError("No synth08 timing rows were supplied")
    graphs = {r["graph"] for r in timing}
    out = []
    seen = set()
    for row in _read_rows(alt_prep_csv, {"graph", "k", "prep_s", "nbytes"}):
        if row["graph"] not in graphs:
            continue
        k = _number(row, "k", positive=True)
        if k != int(k):
            raise ValueError("landmark k must be an integer")
        k = int(k)
        key = (row["graph"], k)
        if key in seen:
            raise ValueError(f"Duplicate preprocessing row for {key}")
        seen.add(key)
        alt = by_key.get((row["graph"], f"alt{k}"))
        if alt is None:
            raise ValueError(f"Missing synth08 alt{k} timing for {row['graph']}")
        base = by_key[(row["graph"], "dijkstra")]
        prep_s, nbytes = _number(row, "prep_s"), _number(row, "nbytes")
        saving = base["median_s"] - alt["median_s"]
        actual = int(_number(row, "k_actual")) if row.get("k_actual") else k
        out.append({"graph": row["graph"], "k": k, "k_actual": actual,
                    "prep_s": prep_s, "index_mb": nbytes / 1_000_000,
                    "speedup": alt["speedup"],
                    "breakeven": prep_s / saving if saving > 0 else math.inf})
    if not out:
        raise ValueError("No matching preprocessing and E3 synth08 measurements")
    return sorted(out, key=lambda r: (r["graph"], r["k"]))


def _pyplot():
    try:
        import matplotlib.pyplot as plt
    except ImportError as exc:
        raise RuntimeError("Plotting requires matplotlib; install the project's plotting dependencies") from exc
    return plt


def _scenario_order(names):
    preferred = ["synth03", "synth08", "synth18", "random30", "real03", "real08", "real18", "control"]
    return [s for s in preferred if s in names] + sorted(set(names) - set(preferred))


def _save(plt, fig, out_png):
    out = Path(out_png)
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=180, bbox_inches="tight")
    plt.close(fig)


def fig_c(accuracy_csvs, timing_csvs, out_png):
    """Plot observed exactness, speedup, and settled ratio per graph/scenario."""
    accuracy = _accuracy_summary(accuracy_csvs)
    timing = _timing_summary(timing_csvs)
    graphs = sorted({r["graph"] for r in accuracy})
    if {r["graph"] for r in timing} - set(graphs):
        raise ValueError("Timing CSVs contain a graph with no accuracy measurements")
    plt = _pyplot()
    fig, axes = plt.subplots(3, len(graphs), figsize=(6 * len(graphs), 10), squeeze=False)
    for col, graph in enumerate(graphs):
        acc = [r for r in accuracy if r["graph"] == graph]
        ts = [r for r in timing if r["graph"] == graph]
        scenarios = _scenario_order({r["scenario"] for r in acc})
        pos = {s: i for i, s in enumerate(scenarios)}
        algos = sorted({r["algo"] for r in acc})
        for algo in algos:
            aa = {r["scenario"]: r["accuracy_pct"] for r in acc if r["algo"] == algo}
            tt = {r["scenario"]: r for r in ts if r["algo"] == algo}
            axes[0, col].plot([pos[s] for s in scenarios], [aa.get(s, math.nan) for s in scenarios],
                              marker="o", label=algo)
            for row_index, key in ((1, "speedup"), (2, "settled_ratio")):
                axes[row_index, col].plot([pos[s] for s in scenarios],
                                         [tt[s][key] if s in tt else math.nan for s in scenarios],
                                         marker="o", label=algo)
        axes[0, col].set_title(graph)
        axes[0, col].set_ylim(-2, 102)
        axes[0, col].set_ylabel("Exact queries (%)")
        axes[1, col].set_ylabel("Speedup vs Dijkstra")
        axes[2, col].set_ylabel("Settled nodes / Dijkstra")
        for row_index in range(3):
            ax = axes[row_index, col]
            ax.set_xticks(range(len(scenarios)), scenarios, rotation=30, ha="right")
            ax.grid(alpha=0.25)
        for row_index in (1, 2):
            axes[row_index, col].axhline(1, color="grey", linewidth=0.8, linestyle="--")
        axes[0, col].legend(fontsize="small")
    fig.suptitle("E3: measured congestion snapshots; preprocessing reused")
    fig.text(0.01, 0.005, "Control is excluded from timing. Missing or zero-denominator metrics are N/A; errors are not assumed.", fontsize=8)
    fig.tight_layout(rect=(0, 0.025, 1, 0.97))
    _save(plt, fig, out_png)


def fig_d(alt_prep_csv, e3_timing_csv, out_png):
    """Plot ALT cost/performance using E2 prep and E3 synth08 measurements."""
    rows = _tradeoff_summary(alt_prep_csv, e3_timing_csv)
    plt = _pyplot()
    fig, axes = plt.subplots(2, 2, figsize=(10, 7))
    metrics = [("prep_s", "Preprocessing (s)"), ("index_mb", "Distance-array payload (MB)"),
               ("speedup", "synth08 speedup vs Dijkstra"), ("breakeven", "synth08 break-even queries")]
    for graph in sorted({r["graph"] for r in rows}):
        selected = [r for r in rows if r["graph"] == graph]
        xs = [r["k"] for r in selected]
        for ax, (key, label) in zip(axes.flat, metrics):
            ys = [r[key] if math.isfinite(r[key]) else math.nan for r in selected]
            ax.plot(xs, ys, marker="o", label=graph)
            ax.set_xlabel("Requested landmarks k")
            ax.set_ylabel(label)
            ax.set_xticks(sorted({r["k"] for r in rows}))
            ax.grid(alpha=0.25)
        for r in selected:
            if not math.isfinite(r["breakeven"]):
                axes[1, 1].annotate(f"{graph}: no break-even at k={r['k']}",
                                    xy=(r["k"], 0), xytext=(0, 10), textcoords="offset points", fontsize=8)
            if r["k_actual"] != r["k"]:
                axes[0, 0].annotate(f"actual={r['k_actual']}", (r["k"], r["prep_s"]), fontsize=8)
    axes[0, 0].legend(fontsize="small")
    fig.suptitle("ALT trade-off: E2 preprocessing + E3 synth08 queries")
    fig.text(0.01, 0.005, "Use matching lower-bound graphs. Break-even is recomputed from synth08 medians; payload excludes Python overhead.", fontsize=8)
    fig.tight_layout(rect=(0, 0.025, 1, 0.95))
    _save(plt, fig, out_png)


FIG_B_GRAPHS = ("gangnam", "gss", "seoul")  # panel order: small to large
FIG_B_CORNER = ("gangnam", ">10km")  # Gangnam's >10 km bin only holds pairs from opposite corners


def _float_or_nan(text):
    """CSV cell -> float; summarize() writes None (no Dijkstra in the group) as an empty cell."""
    return float(text) if text not in (None, "") else math.nan


def fig_b(summary_csv, tightness_csv, out_png):
    """Figure (b): per graph size, settled ratio and speedup per distance bin, and bound tightness.

    Rows: settled nodes / Dijkstra (main metric, machine independent), speedup vs Dijkstra,
    median h0 / true distance of the A* and ALT lower bounds. Returns the Figure (for tests).
    """
    from matplotlib.figure import Figure
    from matplotlib.ticker import FuncFormatter, LogLocator, NullFormatter

    summary = _read_rows(summary_csv, {"bin", "algo", "speedup", "settled_ratio"})
    tight = _read_rows(tightness_csv, {"bin", "algo", "ratio"})
    graphs = sorted({r["graph"] for r in summary},
                    key=lambda n: (FIG_B_GRAPHS.index(n) if n in FIG_B_GRAPHS else len(FIG_B_GRAPHS), n))
    bins = list(dict.fromkeys(r["bin"] for r in summary))  # first appearance = query order = short to long
    ratios = defaultdict(list)  # (graph, bin, algo) -> per-query h0 / dist
    for r in tight:
        ratios[(r["graph"], r["bin"], r["algo"])].append(float(r["ratio"]))
    # One fixed color per algorithm for all rows: each Axes has its own color cycle, and row 2 skips bidir
    algo_list = [a for a in dict.fromkeys(r["algo"] for r in summary) if a != "dijkstra"]
    colors = {algo: f"C{i}" for i, algo in enumerate(algo_list)}

    fig = Figure(figsize=(5 * len(graphs), 10), layout="constrained")
    axes = fig.subplots(3, len(graphs), sharey="row", squeeze=False)
    xs = list(range(len(bins)))
    for col, graph in enumerate(graphs):
        rows = [r for r in summary if r["graph"] == graph]
        for algo in [a for a in dict.fromkeys(r["algo"] for r in rows) if a != "dijkstra"]:
            by_bin = {r["bin"]: r for r in rows if r["algo"] == algo}
            for row_index, key in ((0, "settled_ratio"), (1, "speedup")):
                axes[row_index, col].plot(xs, [_float_or_nan(by_bin[b][key]) if b in by_bin else math.nan for b in bins],
                                          marker="o", label=algo, color=colors[algo])
            if any((graph, b, algo) in ratios for b in bins):  # only astar and alt{k} have tightness rows
                axes[2, col].plot(xs, [statistics.median(ratios[(graph, b, algo)]) if (graph, b, algo) in ratios
                                       else math.nan for b in bins], marker="o", label=algo, color=colors[algo])
        # the Gangnam >10 km bin holds only diagonal-corner pairs: say so under the tick
        labels = [f"{b}\n(corner pairs only)" if (graph, b) == FIG_B_CORNER else b for b in bins]
        for row_index in range(3):
            ax = axes[row_index, col]
            ax.set_xticks(xs, labels)
            ax.grid(alpha=0.25)
        for row_index in (0, 1):
            ax = axes[row_index, col]
            ax.set_yscale("log")
            ax.yaxis.set_major_locator(LogLocator(subs=(1, 2, 5)))  # ticks at 0.1, 0.2, 0.5, 1, 2, 5, ...
            ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:g}"))  # plain numbers, not 1e-01
            ax.yaxis.set_minor_formatter(NullFormatter())
            ax.axhline(1, color="grey", linewidth=0.8, linestyle="--")  # = Dijkstra
        axes[2, col].set_ylim(0, 1.02)
        axes[0, col].set_title(graph)
        axes[2, col].set_xlabel("Straight-line distance of the query")
    axes[0, 0].set_ylabel("Settled nodes / Dijkstra (median)")
    axes[1, 0].set_ylabel("Speedup vs Dijkstra (median time)")
    axes[2, 0].set_ylabel("Lower bound tightness (median h0 / distance)")
    axes[0, 0].legend(fontsize="small")
    fig.suptitle("E2: A*, bidirectional and ALT vs Dijkstra by query distance")
    Path(out_png).parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_png, dpi=200)
    return fig


def _make_c(args) -> Path:
    root = Path(args.results_dir)
    accuracy = sorted(root.glob("e3_*_accuracy.csv"))
    timing = sorted(root.glob("e3_*_timing.csv"))
    if not accuracy or not timing:
        raise ValueError("Figure c needs measured E3 accuracy and timing CSVs")
    out = Path(args.out_dir) / "fig_c_congestion.png"
    fig_c(accuracy, timing, out)
    return out


def _make_d(args) -> Path:
    root = Path(args.results_dir)
    out = Path(args.out_dir) / "fig_d_alt_tradeoff.png"
    fig_d(root / "e2_alt_prep.csv", root / f"e3_{args.e3_graph}_timing.csv", out)
    return out


FIGURES.update({"c": _make_c, "d": _make_d})


def _make_b(args) -> Path:
    root = Path(args.results_dir)
    out = Path(args.out_dir) / "fig_b_speedup.png"
    fig_b(root / "e2_summary.csv", root / "e2_tightness.csv", out)
    return out


FIGURES["b"] = _make_b



def fig_a(e1_csv, out_png):
    """Figure (a): exhaustive search time vs subgraph size (log y), with Dijkstra for contrast.

    Median per size with each query as a faint dot; sizes where any query hit the time
    limit are marked. Returns the Figure (for tests).
    """
    from matplotlib.figure import Figure

    with Path(e1_csv).open(newline="", encoding="utf-8-sig") as stream:
        rows = list(csv.DictReader(stream))  # one graph only, so no graph column (_read_rows needs one)
    missing = {"actual_n", "ex_time_s", "timed_out", "dij_time_s"} - set(rows[0] if rows else ())
    if missing:
        raise ValueError(f"{e1_csv}: missing CSV columns {sorted(missing)}")
    by_n = defaultdict(list)
    for r in rows:
        by_n[int(r["actual_n"])].append(r)
    ns = sorted(by_n)
    ex_med = [statistics.median(float(r["ex_time_s"]) for r in by_n[n]) for n in ns]
    dij_med = [statistics.median(float(r["dij_time_s"]) for r in by_n[n]) for n in ns]
    timeout_ns = [n for n in ns if any(r["timed_out"] == "True" for r in by_n[n])]

    fig = Figure(figsize=(8, 5), layout="constrained")
    ax = fig.subplots()
    ax.scatter([int(r["actual_n"]) for r in rows], [float(r["ex_time_s"]) for r in rows],
               s=6, alpha=0.25, color="C0")
    ax.plot(ns, ex_med, marker="o", color="C0", label="Exhaustive search (median)")
    ax.plot(ns, dij_med, marker="s", color="C1", label="Dijkstra (median)")
    if timeout_ns:
        # mark the slowest query of the size (the one that hit the limit), not the median
        ax.scatter(timeout_ns, [max(float(r["ex_time_s"]) for r in by_n[n]) for n in timeout_ns],
                   marker="X", s=120, color="C3", zorder=3,
                   label=f"Time limit hit (give up at n = {timeout_ns[0]})")
    ax.set_yscale("log")
    ax.set_xlabel("Vertices in the Gangnam subgraph (n)")
    ax.set_ylabel("Time per query (s, log scale)")
    ax.set_title("E1: exhaustive search time explodes with graph size")
    ax.grid(alpha=0.25, which="both")
    ax.legend()
    Path(out_png).parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_png, dpi=200)
    return fig


def _make_a(args) -> Path:
    out = Path(args.out_dir) / "fig_a_exhaustive.png"
    fig_a(Path(args.results_dir) / "e1.csv", out)
    return out


FIGURES["a"] = _make_a


GRAPH_TABLE_FIELDS = ("name", "n", "m", "vmax_mps", "maxspeed_missing_ratio")


def graph_table(meta_paths) -> list[dict]:
    """One row per graph from its .meta.json: name, n, m, vmax_kph, maxspeed_missing_ratio."""
    rows = []
    for path in _paths(meta_paths):
        meta = json.loads(path.read_text(encoding="utf-8"))
        missing = [k for k in GRAPH_TABLE_FIELDS if k not in meta]
        if missing:
            raise ValueError(f"{path}: missing fields {missing}")
        rows.append({"name": meta["name"], "n": meta["n"], "m": meta["m"],
                     "vmax_kph": round(meta["vmax_mps"] * 3.6, 1),
                     "maxspeed_missing_ratio": round(meta["maxspeed_missing_ratio"], 4)})
    return rows


FIG_G_GRAPHS = ("gangnam", "gss", "seoul")  # the size ladder: 1 district, 3 districts, all of Seoul
# hwy_class classes, major roads first; minor roads are drawn first (underneath) in light grey
HWY_STYLE = {"motorway": ("#d62728", 1.6), "trunk": ("#ff7f0e", 1.4), "primary": ("#1f77b4", 1.1),
             "secondary": ("#2ca02c", 0.9), "tertiary": ("#9467bd", 0.7), "other": ("#c7c7c7", 0.3)}


def fig_g(graph_paths, out_png):
    """Figure (g): one map panel per graph, edges colored by hwy_class, one shared legend.

    Reads the .pkl graphs the experiments use (largest SCC, same edges). Returns the Figure.
    """
    from matplotlib.collections import LineCollection
    from matplotlib.figure import Figure
    from matplotlib.lines import Line2D

    from routing.congestion import hwy_class

    paths = _paths(graph_paths)
    fig = Figure(figsize=(5 * len(paths), 5.6), layout="constrained")
    axes = fig.subplots(1, len(paths), squeeze=False)[0]
    seen = set()
    for ax, path in zip(axes, paths):
        g = load_graph(path)
        segments = defaultdict(list)
        for u, v, h in zip(g.tail, g.head, g.hwy):
            (la1, lo1), (la2, lo2) = g.coords[u], g.coords[v]
            segments[hwy_class(h)].append(((lo1, la1), (lo2, la2)))
        for cls in reversed(HWY_STYLE):  # minor roads underneath
            if segments[cls]:
                color, width = HWY_STYLE[cls]
                ax.add_collection(LineCollection(segments[cls], colors=color, linewidths=width))
                seen.add(cls)
        ax.autoscale()
        lat0 = statistics.fmean(lat for lat, _ in g.coords)
        ax.set_aspect(1 / math.cos(math.radians(lat0)))  # degrees of lon are shorter than of lat
        ax.set_title(f"{g.name or path.stem}: n = {g.n:,}, m = {g.m:,}")
        ax.set_xticks([])
        ax.set_yticks([])
    labels = {"other": "other (residential, living_street, ...)"}
    handles = [Line2D([], [], color=HWY_STYLE[c][0], linewidth=2.5, label=labels.get(c, c))
               for c in HWY_STYLE if c in seen]
    fig.suptitle("Graph size ladder (each panel at its own scale; *_link roads joined to their class)")
    fig.legend(handles=handles, loc="outside lower center", ncol=len(handles), title="Road class (OSM highway)")
    Path(out_png).parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_png, dpi=200)
    return fig


def _make_g(args) -> Path:
    from routing.bench import write_csv

    graphs = Path(args.graphs_dir)
    table = Path(args.results_dir) / "graph_table.csv"
    write_csv(table, graph_table([graphs / f"{n}_graph_v1.meta.json" for n in FIG_G_GRAPHS]))
    print(table)
    out = Path(args.out_dir) / "fig_g_graphs.png"
    fig_g([graphs / f"{n}_graph_v1.pkl" for n in FIG_G_GRAPHS], out)
    return out


FIGURES["g"] = _make_g
