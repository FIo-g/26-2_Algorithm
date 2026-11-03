"""Static re-routing benefit (Task 23, stand-in for the deferred SUMO E4) on supplied graph and query files.

Outputs in --results-dir, per graph: reroute_gain_{graph}.csv (one row per query, snapshot and mode),
reroute_gain_{graph}_summary.csv and reroute_gain_{graph}_manifest.json.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))  # run_e3.py lives next to this script

from run_e3 import _sha256, resolve_graph  # same input rules as E2/E3: newest graph version, file hash

from routing.bench import write_csv
from routing.congestion import standard_scenarios
from routing.experiments.reroute_gain import reroute_gain, summarize_gain
from routing.graph import load_graph
from routing.queries import load_queries

# Congestion snapshots only: synth03 equals free flow, and the control speeds roads up to break heuristics.
SCENARIOS = ("synth08", "synth18", "random30")


def _outputs(results_dir, name):
    return [results_dir / f"reroute_gain_{name}{suffix}"
            for suffix in (".csv", "_summary.csv", "_manifest.json")]


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("graphs", choices=("gangnam", "gss", "seoul"), nargs="+")
    parser.add_argument("--graphs-dir", type=Path, default=ROOT / "data" / "graphs")
    parser.add_argument("--queries-dir", type=Path, default=ROOT / "data" / "queries")
    parser.add_argument("--results-dir", type=Path, default=ROOT / "results")
    parser.add_argument("--graph-version", type=int, help="pin a graph version instead of choosing the latest")
    parser.add_argument("--overwrite", action="store_true", help="replace existing outputs of these graphs")
    args = parser.parse_args(argv)
    if len(set(args.graphs)) != len(args.graphs):
        parser.error("graph names must be distinct")

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
    if input_errors:
        parser.error("Re-routing gain is blocked: " + "; ".join(input_errors))
    existing = [str(p) for name in args.graphs for p in _outputs(args.results_dir, name) if p.exists()]
    if existing and not args.overwrite:
        parser.error("Outputs already exist; keep the frozen results or pass --overwrite: " + ", ".join(existing))

    try:
        for name, (graph_path, query_path) in inputs.items():
            graph_hash, query_hash = _sha256(graph_path), _sha256(query_path)
            g = load_graph(graph_path)
            queries = load_queries(query_path, g)
            print(f"reroute gain {name}: {g.n} nodes, {g.m} edges, {len(queries)} queries", flush=True)
            all_scenarios = standard_scenarios(g, seed=0)
            rows = reroute_gain(g, queries, graph=name, scenarios={s: all_scenarios[s] for s in SCENARIOS})
            if _sha256(graph_path) != graph_hash or _sha256(query_path) != query_hash:
                raise RuntimeError("An input changed during the run; no outputs were written for " + name)
            rows_path, summary_path, manifest_path = _outputs(args.results_dir, name)
            write_csv(rows_path, rows)
            write_csv(summary_path, summarize_gain(rows))
            manifest = {"graph": name, "graph_path": str(graph_path.resolve()), "graph_sha256": graph_hash,
                        "queries_path": str(query_path.resolve()), "queries_sha256": query_hash,
                        "nodes": g.n, "edges": g.m, "query_count": len(queries),
                        "scenarios": list(SCENARIOS), "scenario_seed": 0,
                        "modes": {"depart": "snapshot known at departure",
                                  "midway": "snapshot starts at E3's reroute midpoint; first half at free flow"},
                        "assumptions": "one vehicle, snapshot fixed for the rest of the trip, no other vehicle reacts",
                        "completed_utc": datetime.now(timezone.utc).isoformat()}
            manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
            print(f"reroute gain {name}: done", flush=True)
        for name in inputs:
            for path in _outputs(args.results_dir, name):
                print(path)
        return 0
    except (OSError, ValueError, RuntimeError) as exc:
        parser.error(str(exc))


if __name__ == "__main__":
    raise SystemExit(main())
