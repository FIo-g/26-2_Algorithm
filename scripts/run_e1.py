"""Run E1 (exhaustive search limit): python scripts/run_e1.py GRAPH_PKL [--time-limit S]

Writes results/e1.csv (one row per query) and results/e1_grid.csv (grid path counts),
then prints the give-up size n. Draw figure (a) with: python scripts/make_figures.py a
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from routing.bench import write_csv  # noqa: E402
from routing.experiments.e1 import GANGNAM_STATION, give_up_n, grid_counts, run_e1  # noqa: E402
from routing.graph import load_graph  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="E1: exhaustive search vs subgraph size.")
    ap.add_argument("graph", type=Path)
    ap.add_argument("--time-limit", type=float, default=10.0, help="seconds per exhaustive query")
    ap.add_argument("--per-size", type=int, default=20)
    ap.add_argument("--max-n", type=int, default=200)
    ap.add_argument("--results-dir", type=Path, default=Path("results"))
    args = ap.parse_args(argv)

    start = time.monotonic()
    g = load_graph(args.graph)
    root = g.nearest(*GANGNAM_STATION)
    print(f"{g!r}, root = vertex {root} (osm {g.osm_ids[root]}) nearest to Gangnam Station", flush=True)
    rows = run_e1(g, root, per_size=args.per_size, time_limit_s=args.time_limit, max_n=args.max_n)
    write_csv(args.results_dir / "e1.csv", rows)
    write_csv(args.results_dir / "e1_grid.csv", grid_counts())
    n = give_up_n(rows)
    sizes = sorted({r["actual_n"] for r in rows})
    print(f"sizes run: {sizes[0]}..{sizes[-1]} ({len(sizes)} sizes, {len(rows)} queries)")
    print(f"give-up n = {n} (first size with a query over {args.time_limit:g} s)" if n is not None
          else f"no timeout up to n = {sizes[-1]} (max_n = {args.max_n})")
    print(f"wrote {args.results_dir / 'e1.csv'}, {args.results_dir / 'e1_grid.csv'} "
          f"({time.monotonic() - start:.0f} s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
