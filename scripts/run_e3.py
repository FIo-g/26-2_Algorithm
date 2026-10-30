"""Run E3 on supplied graph/query files after the shared tasks are merged."""
from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import sys
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

MODULES = ("routing.dijkstra", "routing.heap", "routing.astar", "routing.bidirectional",
           "routing.verify", "routing.queries", "routing.bench", "routing.alt",
           "routing.congestion", "routing.experiments.e3")
HEADERS = {
    "accuracy": ("graph", "scenario", "algo", "n", "n_wrong", "max_rel_err"),
    "timing": ("graph", "scenario", "kind", "qid", "bin", "algo", "time_s", "dist",
               "settled", "relaxed", "pushes", "pops"),
    "reroute": ("graph", "scenario", "kind", "qid", "bin", "algo", "time_s", "dist",
                "settled", "relaxed", "pushes", "pops"),
    "wastar": ("graph", "scenario", "eps", "median_s", "speedup_vs_astar", "mean_ratio",
               "max_ratio", "n", "n_ratio", "n_unreachable"),
}


def resolve_graph(directory, name, version=None):
    """Choose the numerically highest version, never lexicographic v9 > v10."""
    pattern = re.compile(re.escape(name) + r"_graph_v(\d+)\.pkl$")
    candidates = []
    for path in Path(directory).glob(f"{name}_graph_v*.pkl"):
        match = pattern.fullmatch(path.name)
        if match and (version is None or int(match.group(1)) == version):
            candidates.append((int(match.group(1)), path))
    if not candidates:
        suffix = "" if version is None else f" at version {version}"
        raise FileNotFoundError(f"No {name}_graph_vN.pkl{suffix} in {directory}")
    newest = max(v for v, _ in candidates)
    paths = [p for v, p in candidates if v == newest]
    if len(paths) != 1:
        raise ValueError(f"Ambiguous graph version {newest}: {paths}")
    return paths[0]


def _sha256(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _write_csv(path, rows, fieldnames):
    with Path(path).open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(row if isinstance(row, dict) else row._asdict() for row in rows)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("graphs", choices=("gangnam", "gss", "seoul"), nargs="+")
    parser.add_argument("--graphs-dir", type=Path, default=ROOT / "data" / "graphs")
    parser.add_argument("--queries-dir", type=Path, default=ROOT / "data" / "queries")
    parser.add_argument("--results-dir", type=Path, default=ROOT / "results")
    parser.add_argument("--graph-version", type=int, help="pin a graph version instead of choosing the latest")
    parser.add_argument("--ks", type=int, nargs="+", default=(4, 8, 16))
    parser.add_argument("--eps", type=float, nargs="*", default=(1.2, 1.5))
    parser.add_argument("--check-only", action="store_true", help="report missing inputs/dependencies without loading or timing graphs")
    parser.add_argument("--overwrite", action="store_true", help="replace existing E3 output files before the team's result freeze")
    args = parser.parse_args(argv)
    if len(set(args.graphs)) != len(args.graphs):
        parser.error("graph names must be distinct")
    missing = [name for name in MODULES if importlib.util.find_spec(name) is None]
    inputs, input_errors = {}, []
    for name in args.graphs:
        try:
            graph_path = resolve_graph(args.graphs_dir, name, args.graph_version)
            query_path = args.queries_dir / f"{name}_q_seed42.csv"
            if not query_path.is_file():
                raise FileNotFoundError(f"Missing query file: {query_path}")
            inputs[name] = (graph_path, query_path)
        except (OSError, ValueError) as exc:
            input_errors.append(str(exc))
    if args.check_only:
        print(json.dumps({"ready": not missing and not input_errors,
                          "missing_modules": missing, "input_errors": input_errors,
                          "inputs": {n: {"graph": str(g), "queries": str(q)}
                                     for n, (g, q) in inputs.items()}}, indent=2))
        return 0 if not missing and not input_errors else 2
    if missing or input_errors:
        parser.error("E3 is blocked: " + "; ".join([*(f"missing {x}" for x in missing), *input_errors]))
    try:
        from routing.graph import load_graph
        from routing.queries import load_queries
        from routing.congestion import standard_scenarios
        from routing.experiments.e3 import run_e3, server_ratio

        destinations = [args.results_dir / f"e3_{name}_{kind}.csv"
                        for name in args.graphs for kind in HEADERS]
        destinations += [args.results_dir / f"e3_{name}_manifest.json" for name in args.graphs]
        destinations.append(args.results_dir / "server_ratio.csv")
        existing = [str(path) for path in destinations if path.exists()]
        if existing and not args.overwrite:
            raise ValueError("Outputs already exist; preserve the frozen results or explicitly use --overwrite: " + ", ".join(existing))
        outputs, manifests, ratios = {}, {}, []
        for name, (graph_path, query_path) in inputs.items():
            graph_hash, query_hash = _sha256(graph_path), _sha256(query_path)
            g = load_graph(graph_path)
            queries = load_queries(query_path, g)
            out = run_e3(g, queries, graph=name, scenarios=standard_scenarios(g),
                         ks=tuple(args.ks), eps=tuple(args.eps))
            if _sha256(graph_path) != graph_hash or _sha256(query_path) != query_hash:
                raise RuntimeError("An input changed while E3 was running; no outputs were written")
            outputs[name] = out
            ratios.extend(server_ratio(out["reroute"]))
            manifests[name] = {"graph": name, "graph_path": str(graph_path.resolve()),
                               "graph_sha256": graph_hash, "queries_path": str(query_path.resolve()),
                               "queries_sha256": query_hash, "nodes": g.n, "edges": g.m,
                               "query_count": len(queries), "ks": args.ks, "eps": args.eps,
                               "scenario_seed": 0, "scenarios": "synthetic assumptions + negative control",
                               "control_included_in_baseline": False,
                               "timing": "shared Task 11 time_all (warmup + 3 repeats, median)",
                               "completed_utc": datetime.now(timezone.utc).isoformat()}
        # All requested graph experiments pass their gates before any result
        # files are written. No sample or fallback measurements are generated.
        args.results_dir.mkdir(parents=True, exist_ok=True)
        for name, out in outputs.items():
            for kind, rows in out.items():
                _write_csv(args.results_dir / f"e3_{name}_{kind}.csv", rows, HEADERS[kind])
            (args.results_dir / f"e3_{name}_manifest.json").write_text(
                json.dumps(manifests[name], indent=2), encoding="utf-8")
        _write_csv(args.results_dir / "server_ratio.csv", ratios,
                   ("graph", "scenario", "algo", "median_reroute_s", "ratio"))
        for path in destinations:
            print(path)
        return 0
    except (OSError, ValueError, RuntimeError) as exc:
        parser.error(str(exc))


if __name__ == "__main__":
    raise SystemExit(main())
