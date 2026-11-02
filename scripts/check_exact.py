"""Exactness gate on one graph: python scripts/check_exact.py GRAPH_PKL QUERIES_CSV

Prints "ALL EXACT: {n} queries x {k} algos" and exits 0, or prints the mismatches and exits 1.
If QUERIES_CSV does not exist it is created (seed 42) and should be committed.
Any failure means: stop all timing and fix the bug first.
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from routing.bench import standard_algos  # noqa: E402
from routing.gate import load_or_make_queries  # noqa: E402
from routing.graph import load_graph  # noqa: E402
from routing.verify import verify_all  # noqa: E402

MAX_SHOWN = 50


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Check every exact algorithm against Dijkstra.")
    ap.add_argument("graph", type=Path)
    ap.add_argument("queries", type=Path)
    args = ap.parse_args(argv)

    start = time.monotonic()
    g = load_graph(args.graph)
    created = not args.queries.exists()
    qs = load_or_make_queries(g, args.queries)
    print(f"{g!r}: {len(qs)} queries ({'created' if created else 'loaded'} {args.queries})", flush=True)
    algos, _ = standard_algos(g)
    print(f"algos: {', '.join(algos)} (landmarks ready after {time.monotonic() - start:.1f} s)", flush=True)
    msgs = verify_all(g, qs, algos)
    elapsed = time.monotonic() - start
    if msgs:
        for m in msgs[:MAX_SHOWN]:
            print(m)
        if len(msgs) > MAX_SHOWN:
            print(f"... {len(msgs) - MAX_SHOWN} more")
        print(f"NOT EXACT: {len(msgs)} problems ({elapsed:.1f} s). Stop timing and fix the bug first.")
        return 1
    print(f"ALL EXACT: {len(qs)} queries x {len(algos)} algos ({elapsed:.1f} s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
