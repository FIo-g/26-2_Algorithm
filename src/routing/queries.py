"""Fixed-seed s-t query sets, binned by straight-line distance and saved by OSM id (standard library only).

Saving osm_ids (not indices) keeps a query set valid when a graph is re-extracted
and renumbered; a missing id means the graph version changed.
"""
from __future__ import annotations

import csv
import math
import random
import warnings
from pathlib import Path
from typing import NamedTuple

from routing.graph import Graph, haversine_m

BINS_M = [(0, 3000, "<3km"), (3000, 10000, "3-10km"), (10000, math.inf, ">10km")]


class Query(NamedTuple):
    qid: int
    bin: str
    s: int
    t: int
    crow_m: float  # straight-line s-t distance


def make_queries(g: Graph, *, per_bin: int = 100, seed: int = 42, bins=BINS_M,
                 max_tries: int = 200_000) -> list[Query]:
    """Draw random s != t pairs until every bin has per_bin of them or max_tries runs out."""
    rng = random.Random(seed)
    filled: dict[str, list[tuple[int, int, float]]] = {label: [] for _, _, label in bins}
    tries = 0
    while tries < max_tries and any(len(v) < per_bin for v in filled.values()):
        tries += 1
        s, t = rng.randrange(g.n), rng.randrange(g.n)
        if s == t:
            continue
        d = haversine_m(g.coords[s], g.coords[t])
        for lo, hi, label in bins:
            if lo <= d < hi:
                if len(filled[label]) < per_bin:
                    filled[label].append((s, t, d))
                break
    for _, _, label in bins:
        if len(filled[label]) < per_bin:
            warnings.warn(f"bin {label}: only {len(filled[label])}/{per_bin} queries "
                          f"after {tries} tries", UserWarning, stacklevel=2)
    qs: list[Query] = []
    for _, _, label in bins:
        for s, t, d in filled[label]:
            qs.append(Query(len(qs), label, s, t, d))
    return qs


def save_queries(path: str | Path, g: Graph, qs: list[Query]) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["qid", "bin", "s_osm", "t_osm", "crow_m"])
        for q in qs:
            w.writerow([q.qid, q.bin, g.osm_ids[q.s], g.osm_ids[q.t], repr(q.crow_m)])


def load_queries(path: str | Path, g: Graph) -> list[Query]:
    qs: list[Query] = []
    with open(path, newline="") as f:
        for row in csv.DictReader(f):
            ids = []
            for key in ("s_osm", "t_osm"):
                osm = int(row[key])
                try:
                    ids.append(g.index_of(osm))
                except KeyError:
                    raise KeyError(f"graph version mismatch: osm_id {osm} not in graph {g.name!r}") from None
            qs.append(Query(int(row["qid"]), row["bin"], ids[0], ids[1], float(row["crow_m"])))
    return qs
