"""Run E2 (speedup, ALT preprocessing, bound tightness) on supplied graph and query files.

Outputs in --results-dir: e2_{graph}.csv (raw timing rows) and e2_{graph}_manifest.json per graph,
plus e2_alt_prep.csv, e2_tightness.csv and e2_summary.csv shared by all graphs (one `graph` column).
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))  # run_e3.py lives next to this script

from run_e3 import _sha256, resolve_graph  # same input rules as E3: newest graph version, file hash

from routing.bench import ExactnessError, summarize, write_csv
from routing.experiments.e2 import run_e2
from routing.graph import load_graph
from routing.queries import load_queries

SHARED_FIELDS = {  # shared CSV -> column order
    "e2_alt_prep.csv": ("graph", "k", "k_actual", "prep_s", "nbytes", "breakeven"),
    "e2_tightness.csv": ("graph", "qid", "bin", "algo", "h0", "dist", "ratio"),
    "e2_summary.csv": ("graph", "scenario", "kind", "bin", "algo", "n", "median_s", "p95_s",
                       "median_settled", "speedup", "settled_ratio"),
}


def _graphs_in(path):
    """Graph names that already have rows in a shared CSV."""
    if not path.exists():
        return set()
    with path.open(newline="", encoding="utf-8") as stream:
        return {row["graph"] for row in csv.DictReader(stream)}


def merge_rows(path, new_rows, fields, graph):
    """Replace this graph's rows in a shared CSV and keep the rows of the other graphs."""
    kept = []
    if path.exists():
        with path.open(newline="", encoding="utf-8") as stream:
            kept = [row for row in csv.DictReader(stream) if row["graph"] != graph]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(kept + list(new_rows))


def existing_outputs(results_dir, graphs):
    """Output files or shared-CSV rows that a run for `graphs` would replace."""
    found = []
    for name in graphs:
        found += [str(p) for p in (results_dir / f"e2_{name}.csv", results_dir / f"e2_{name}_manifest.json") if p.exists()]
    for filename in SHARED_FIELDS:
        present = _graphs_in(results_dir / filename) & set(graphs)
        if present:
            found.append(f"{results_dir / filename} (rows for {', '.join(sorted(present))})")
    return found


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("graphs", choices=("gangnam", "gss", "seoul"), nargs="+")
    parser.add_argument("--graphs-dir", type=Path, default=ROOT / "data" / "graphs")
    parser.add_argument("--queries-dir", type=Path, default=ROOT / "data" / "queries")
    parser.add_argument("--results-dir", type=Path, default=ROOT / "results")
    parser.add_argument("--graph-version", type=int, help="pin a graph version instead of choosing the latest")
    parser.add_argument("--ks", type=int, nargs="+", default=(4, 8, 16))
    parser.add_argument("--overwrite", action="store_true", help="replace existing E2 outputs of these graphs")
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
        parser.error("E2 is blocked: " + "; ".join(input_errors))
    existing = existing_outputs(args.results_dir, args.graphs)
    if existing and not args.overwrite:
        parser.error("Outputs already exist; keep the frozen results or pass --overwrite: " + ", ".join(existing))

    try:
        for name, (graph_path, query_path) in inputs.items():
            graph_hash, query_hash = _sha256(graph_path), _sha256(query_path)
            g = load_graph(graph_path)
            queries = load_queries(query_path, g)
            print(f"E2 {name}: {g.n} nodes, {g.m} edges, {len(queries)} queries", flush=True)
            rows, prep, tight = run_e2(g, queries, graph=name, ks=tuple(args.ks))
            if _sha256(graph_path) != graph_hash or _sha256(query_path) != query_hash:
                raise RuntimeError("An input changed while E2 was running; no outputs were written for " + name)
            # Written per graph, so a failure on a later (larger) graph keeps the finished ones.
            write_csv(args.results_dir / f"e2_{name}.csv", rows)
            for filename, new_rows in (("e2_alt_prep.csv", prep), ("e2_tightness.csv", tight),
                                       ("e2_summary.csv", summarize(rows))):
                merge_rows(args.results_dir / filename, new_rows, SHARED_FIELDS[filename], name)
            manifest = {"graph": name, "graph_path": str(graph_path.resolve()), "graph_sha256": graph_hash,
                        "queries_path": str(query_path.resolve()), "queries_sha256": query_hash,
                        "nodes": g.n, "edges": g.m, "query_count": len(queries), "ks": list(args.ks),
                        "landmark_seed": 0,
                        "landmark_graph": "free-flow query graph (same as E3 g_lb unless real speeds are adopted)",
                        "timing": "shared time_all (warmup + 3 repeats, median); ALT preprocessing measured once per k",
                        "completed_utc": datetime.now(timezone.utc).isoformat()}
            (args.results_dir / f"e2_{name}_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
            print(f"E2 {name}: done", flush=True)
        for name in inputs:
            print(args.results_dir / f"e2_{name}.csv")
        for filename in SHARED_FIELDS:
            print(args.results_dir / filename)
        return 0
    except (OSError, ValueError, RuntimeError, ExactnessError) as exc:
        parser.error(str(exc))


if __name__ == "__main__":
    raise SystemExit(main())
