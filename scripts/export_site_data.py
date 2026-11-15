"""Export the data the showcase site reads into site/public/data/.

Run from the repo root with the project venv:
    python scripts/export_site_data.py

Writes hero.json, net-{graph}.bin, trace-{graph}.bin and demos.json. Every method is
checked against Dijkstra (routing.verify.check_result) before anything is written;
any failure exits non-zero and leaves site/public/data/ untouched.
"""
from __future__ import annotations

import inspect
import json
import math
import struct
import sys
from collections import Counter
from contextlib import contextmanager
from functools import partial
from pathlib import Path

from routing.alt import alt, alt_heuristic, preprocess_landmarks
from routing.astar import astar, astar_heuristic
from routing.bench import standard_algos
from routing.bidirectional import bidirectional_dijkstra
from routing.dijkstra import dijkstra
from routing.figures import FIG_F_QUERY
from routing.graph import load_graph
from routing.heap import CountingHeap, Stats
from routing.synthetic import from_edge_list, grid_graph
from routing.verify import check_result

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "site" / "public" / "data"
ORDER = ("dijkstra", "astar", "bidir", "alt16")  # hero methods, in display order


# ---------------------------------------------------------------- shared helpers

def run_query(algo, g, s, t):
    """One query with a settle-order trace: (distance, path, settled, trace)."""
    st = Stats(trace=[])
    dist, path, settled = algo(g, s, t, stats=st)
    return dist, path, settled, st.trace


def verified_runs(g, s, t, algos: dict) -> dict:
    """Run every algorithm; exit if any disagrees with algos['dijkstra'] or its trace is off."""
    runs = {name: run_query(algo, g, s, t) for name, algo in algos.items()}
    ref_dist = runs["dijkstra"][0]
    for name, (dist, path, settled, trace) in runs.items():
        errors = check_result(g, s, t, ref_dist, (dist, path, settled))
        if len(trace) != settled:
            errors.append(f"trace has {len(trace)} entries, settled count is {settled}")
        if errors:
            raise SystemExit(f"exactness check failed for {name}: {errors}")
    return runs


def run_dist(demo_run_dict):
    """The raw distance of a demo run (None in the export means infinity)."""
    return math.inf if demo_run_dict["dist"] is None else demo_run_dict["dist"]


def finite_or_none(x):
    """JSON has no Infinity: an empty heap or an unset mu becomes null."""
    return float(x) if math.isfinite(x) else None


# ---------------------------------------------------------------- hero map

# Gangnam uses the figure-f query; Seoul is Gimpo Airport to Jamsil Station.
HERO_QUERIES = {
    "gangnam": (FIG_F_QUERY[0], FIG_F_QUERY[1],
                ("강남역", "Gangnam Station"), ("삼성역", "Samseong Station")),
    "seoul": ((37.5586, 126.8028), (37.5133, 127.1001),
              ("김포공항", "Gimpo Airport"), ("잠실역", "Jamsil Station")),
}


def project(g):
    """Map (lat, lon) to x, y in 0..1 (x east, y south, longitude scaled by cos(mean lat)).

    Returns (xy list, aspect) where aspect is the true width over height.
    """
    kx = math.cos(math.radians(sum(lat for lat, _ in g.coords) / g.n))
    min_lon = min(lon for _, lon in g.coords)
    max_lat = max(lat for lat, _ in g.coords)
    xs = [(lon - min_lon) * kx for _, lon in g.coords]
    ys = [max_lat - lat for lat, _ in g.coords]
    width, height = max(xs), max(ys)
    return [(x / width, y / height) for x, y in zip(xs, ys)], width / height


def encode_net(n: int, xy, segments) -> bytes:
    """net-*.bin: Uint32 n, Uint32 e, Float32 x,y per vertex, Uint32 u,v per undirected segment."""
    flat_xy = [c for pair in xy for c in pair]
    flat_seg = [v for pair in segments for v in pair]
    return (struct.pack("<II", n, len(segments))
            + struct.pack(f"<{len(flat_xy)}f", *flat_xy)
            + struct.pack(f"<{len(flat_seg)}I", *flat_seg))


def encode_trace(traces) -> bytes:
    """trace-*.bin: for each method in ORDER, Uint32 count then Uint32 vertex indices."""
    out = bytearray()
    for trace in traces:
        out += struct.pack(f"<I{len(trace)}I", len(trace), *trace)
    return bytes(out)


def build_hero_graph(name: str):
    g = load_graph(ROOT / "data" / "graphs" / f"{name}_graph_v1.pkl")
    (s_lat, s_lon), (t_lat, t_lon), s_label, t_label = HERO_QUERIES[name]
    s, t = g.nearest(s_lat, s_lon), g.nearest(t_lat, t_lon)
    algos, _ = standard_algos(g, ks=(16,))
    runs = verified_runs(g, s, t, {m: algos[m] for m in ORDER})

    xy, aspect = project(g)
    segments = sorted({(min(u, v), max(u, v)) for u, v in zip(g.tail, g.head) if u != v})
    entry = {
        "n": g.n, "e": len(segments), "aspect": aspect,
        "net": f"net-{name}.bin", "trace": f"trace-{name}.bin",
        "query": {"s": s, "t": t,
                  "sLabel": {"ko": s_label[0], "en": s_label[1]},
                  "tLabel": {"ko": t_label[0], "en": t_label[1]}},
        "algos": [{"id": m, "settled": runs[m][2], "time_s": runs[m][0], "path": runs[m][1]}
                  for m in ORDER],
    }
    blobs = {
        f"net-{name}.bin": encode_net(g.n, xy, segments),
        f"trace-{name}.bin": encode_trace([runs[m][3] for m in ORDER]),
    }
    return entry, blobs


# ---------------------------------------------------------------- step demos

@contextmanager
def _recording(events: list, loop_test_line: int | None):
    """Append every CountingHeap push/pop to events while active; restore the class afterwards.

    Heaps are numbered in construction order (0 = forward or only heap). A pop is stale
    when its heap already popped that vertex fresh, which is lazy deletion's definition.
    With loop_test_line set, the stop test of bidirectional_dijkstra is traced as well.
    """
    orig_init, orig_push = CountingHeap.__init__, CountingHeap.push
    orig_pop, orig_drop = CountingHeap.pop, CountingHeap.drop_stale
    heap_no: dict[int, int] = {}
    seen: dict[int, set[int]] = {}

    def init(self, stats):
        orig_init(self, stats)
        heap_no[id(self)] = len(heap_no)
        seen[id(self)] = set()

    def note_pop(self, key, v):
        seen_here = seen[id(self)]
        events.append({"type": "pop", "heap": heap_no[id(self)], "key": key, "v": v,
                       "stale": v in seen_here})
        seen_here.add(v)

    def push(self, key, v):
        orig_push(self, key, v)
        events.append({"type": "push", "heap": heap_no[id(self)], "key": key, "v": v})

    def pop(self):
        key, v = orig_pop(self)
        note_pop(self, key, v)
        return key, v

    def drop_stale(self, done):
        before = Counter(self._h)
        orig_drop(self, done)
        # drop_stale pops the top entries in ascending (key, v) order; recover them from the diff
        for key, v in sorted((before - Counter(self._h)).elements()):
            note_pop(self, key, v)

    def tracer(frame, event, arg):
        if event == "call" and frame.f_code is bidirectional_dijkstra.__code__:
            return local
        return None

    def local(frame, event, arg):
        if event == "line" and frame.f_lineno == loop_test_line:
            loc = frame.f_locals
            events.append({"type": "loop", "top_f": finite_or_none(loc["top_f"]),
                           "top_b": finite_or_none(loc["top_b"]),
                           "mu": finite_or_none(loc["mu"])})
        return local

    CountingHeap.__init__, CountingHeap.push = init, push
    CountingHeap.pop, CountingHeap.drop_stale = pop, drop_stale
    if loop_test_line is not None:
        sys.settrace(tracer)
    try:
        yield
    finally:
        sys.settrace(None)
        CountingHeap.__init__, CountingHeap.push = orig_init, orig_push
        CountingHeap.pop, CountingHeap.drop_stale = orig_pop, orig_drop


def _stop_test_line() -> int:
    lines, start = inspect.getsourcelines(bidirectional_dijkstra)
    return start + next(i for i, line in enumerate(lines) if "top_f + top_b >= mu" in line)


def traced_run(algo, g, s, t, *, loops: bool = False) -> dict:
    """One query with its exact heap events (and bidirectional stop tests when loops=True)."""
    events: list[dict] = []
    stats = Stats(trace=[])
    with _recording(events, _stop_test_line() if loops else None):
        dist, path, settled = algo(g, s, t, stats=stats)
    # Exit if the recorded events disagree with the algorithm's own counters: the demo would show another run.
    pushes = sum(e["type"] == "push" for e in events)
    pops = [e for e in events if e["type"] == "pop"]
    fresh = [e["v"] for e in pops if not e["stale"]]
    if pushes != stats.pushes or len(pops) != stats.pops or fresh != stats.trace:
        raise SystemExit(f"recorded events disagree with Stats: pushes {pushes} vs {stats.pushes}, "
                         f"pops {len(pops)} vs {stats.pops}, fresh pops match trace: {fresh == stats.trace}")
    return {"dist": dist, "path": path, "settled": settled, "events": events, "stats": stats}


def demo_run(name, algo, g, s, t, *, loops=False, heuristic=None) -> dict:
    run = traced_run(algo, g, s, t, loops=loops)
    h = None if heuristic is None else [finite_or_none(heuristic(v)) for v in range(g.n)]
    return {"algo": name, "dist": finite_or_none(run["dist"]), "path": run["path"],
            "settled": run["settled"], "h": h, "events": run["events"]}


def _grid_vertices(rows: int, cols: int):
    return [{"id": r * cols + c, "x": c / (cols - 1), "y": r / (rows - 1)}
            for r in range(rows) for c in range(cols)]


def _small_graph_demo(demo_id, title, source_test, g, layout, s, t, runs_spec) -> dict:
    """Demos 1 and 2: hand-placed vertices; runs_spec is [(name, algo, loops), ...]."""
    dijkstra_run = run_query(dijkstra, g, s, t)
    runs = []
    for name, algo, loops in runs_spec:
        run = demo_run(name, algo, g, s, t, loops=loops)
        errors = check_result(g, s, t, dijkstra_run[0], (run_dist(run), run["path"], run["settled"]))
        if errors:
            raise SystemExit(f"demo {demo_id}: {name} failed exactness: {errors}")
        runs.append(run)
    return {"id": demo_id, "title": title, "source_test": source_test,
            "vertices": [{"id": v, "x": x, "y": y} for v, (x, y) in enumerate(layout)],
            "edges": [{"u": u, "v": v, "w": w} for u, v, w in zip(g.tail, g.head, g.time)],
            "s": s, "t": t, "runs": runs}


def _grid_demo(demo_id, title, source_test, algo_name, algo, g, rows, cols, landmarks=None) -> dict:
    s, t = 0, rows * cols - 1  # opposite corners
    heuristic = None
    if algo_name == "astar":
        heuristic = lambda v: astar_heuristic(g, v, t, g.vmax)  # noqa: E731
    elif algo_name == "alt":
        heuristic = lambda v: alt_heuristic(landmarks, v, t)  # noqa: E731
    dijkstra_run = run_query(dijkstra, g, s, t)
    runs = []
    for name, fn, h in ((algo_name, algo, heuristic), ("dijkstra", dijkstra, None)):
        run = demo_run(name, fn, g, s, t, heuristic=h)
        errors = check_result(g, s, t, dijkstra_run[0], (run_dist(run), run["path"], run["settled"]))
        if errors:
            raise SystemExit(f"demo {demo_id}: {name} failed exactness: {errors}")
        runs.append(run)
    demo = {"id": demo_id, "title": title, "source_test": source_test,
            "vertices": _grid_vertices(rows, cols),
            "edges": [{"u": u, "v": v, "w": w} for u, v, w in zip(g.tail, g.head, g.time)],
            "s": s, "t": t, "runs": runs}
    if landmarks is not None:
        demo["landmarks"] = landmarks.ids
    return demo


def build_demos() -> dict:
    demo1 = _small_graph_demo(
        "dijkstra", "Dijkstra on four intersections",
        "tests/test_dijkstra.py::test_dijkstra_stats_counting",
        from_edge_list(4, [(0, 1, 5), (0, 2, 1), (2, 1, 1), (1, 3, 10)]),
        [(0.08, 0.5), (0.5, 0.15), (0.45, 0.85), (0.92, 0.5)], 0, 3,
        [("dijkstra", dijkstra, False)])
    demo2 = _small_graph_demo(
        "bidir", "Bidirectional Dijkstra on five intersections",
        "tests/test_bidirectional.py::test_bidirectional_not_first_meeting",
        from_edge_list(5, [(0, 1, 3), (1, 2, 3), (0, 3, 2), (3, 4, 1.5), (4, 2, 2)]),
        [(0.08, 0.5), (0.5, 0.12), (0.3, 0.85), (0.65, 0.85), (0.92, 0.5)], 0, 2,
        [("bidir", bidirectional_dijkstra, True)])

    rows = cols = 8
    grid = grid_graph(rows, cols)
    demo3 = _grid_demo(
        "astar", "A* on an eight by eight grid",
        "routing.synthetic.grid_graph(8, 8), corner to corner (property tested in "
        "tests/test_astar.py::test_astar_settles_fewer_on_grid on a 15 by 15 grid)",
        "astar", partial(astar, vmax=grid.vmax), grid, rows, cols)
    landmarks = preprocess_landmarks(grid, 4, seed=0)
    demo4 = _grid_demo(
        "alt", "ALT with four landmarks on an eight by eight grid",
        "routing.synthetic.grid_graph(8, 8), corner to corner, preprocess_landmarks(g, 4, seed=0) "
        "(property tested in tests/test_alt.py::ALTTask3IntegrationTests::test_alt_settles_fewer_on_grid "
        "on a 15 by 15 grid)",
        "alt", partial(alt, lm=landmarks), grid, rows, cols, landmarks=landmarks)
    return {"demos": [demo1, demo2, demo3, demo4]}


# ---------------------------------------------------------------- main

def dumps(obj) -> bytes:
    return json.dumps(obj, allow_nan=False, separators=(",", ":")).encode("utf-8")


def main() -> None:
    hero = {"graphs": {}, "order": list(ORDER)}
    blobs: dict[str, bytes] = {}
    for name in HERO_QUERIES:
        entry, files = build_hero_graph(name)
        hero["graphs"][name] = entry
        blobs.update(files)
    blobs["hero.json"] = dumps(hero)
    blobs["demos.json"] = dumps(build_demos())

    OUT.mkdir(parents=True, exist_ok=True)
    for filename, data in blobs.items():
        (OUT / filename).write_bytes(data)
        print(f"{OUT / filename}  {len(data)} bytes")


if __name__ == "__main__":
    main()
