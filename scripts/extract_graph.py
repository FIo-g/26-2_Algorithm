"""Download one OSM drive network and save it as versioned Graph files.

Usage: python scripts/extract_graph.py {gangnam|gss|seoul} --version N

Writes data/graphs/{name}_graph_vN.pkl, {name}_vN.graphml and {name}_graph_vN.meta.json.
Existing files are never overwritten (exit code 1): re-extract with a new version.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from routing.graph import save_graph  # noqa: E402
from routing.osm import PLACES, download, from_osmnx, meta  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("name", choices=sorted(PLACES))
    ap.add_argument("--version", type=int, required=True)
    ap.add_argument("--out", type=Path, default=Path("data/graphs"))
    args = ap.parse_args(argv)

    stem = f"{args.name}_graph_v{args.version}"
    pkl, graphml = args.out / f"{stem}.pkl", args.out / f"{args.name}_v{args.version}.graphml"
    meta_path = args.out / f"{stem}.meta.json"
    existing = [p for p in (pkl, graphml, meta_path) if p.exists()]
    if existing:
        print(f"refusing to overwrite {', '.join(map(str, existing))}; use a new --version",
              file=sys.stderr)
        return 1

    start = time.monotonic()
    print(f"downloading {args.name}: {PLACES[args.name]}", flush=True)
    G = download(args.name)
    g = from_osmnx(G, args.name)
    info = meta(G, g)
    info["version"] = args.version
    info["seconds"] = round(time.monotonic() - start, 1)

    import osmnx as ox
    args.out.mkdir(parents=True, exist_ok=True)
    save_graph(g, pkl)
    ox.save_graphml(G, graphml)
    meta_path.write_text(json.dumps(info, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"n={info['n']} m={info['m']} vmax={info['vmax_kph']:.1f} km/h "
          f"maxspeed missing={info['maxspeed_missing_ratio']:.1%} "
          f"haversine violations={info['haversine_violations']} ({info['seconds']} s)")
    print(f"wrote {pkl}, {graphml}, {meta_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
