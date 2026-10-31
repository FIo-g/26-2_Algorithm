"""OSMnx download and conversion to the shared Graph format.

Not a core module: it imports osmnx and networkx. Everything downstream only
needs the pickled Graph, so teammates never download OSM data themselves.
"""
from __future__ import annotations

import re
from collections import Counter
from datetime import datetime, timezone

import networkx as nx
import osmnx as ox

from routing.graph import Graph, haversine_m

PLACES = {
    "gangnam": ["Gangnam-gu, Seoul, South Korea"],
    "gss": ["Gangnam-gu, Seoul, South Korea", "Seocho-gu, Seoul, South Korea",
            "Songpa-gu, Seoul, South Korea"],
    "seoul": ["Seoul, South Korea"],
}
FALLBACK_KPH = 30  # speed for highway types with no maxspeed anywhere in the graph (planner's choice)
# Korea's highest posted limit is 120 km/h; larger tags are mapping errors (e.g. a
# residential street in Songpa tagged 200). Treating them as missing keeps one typo
# from setting vmax, which would loosen the A* bound for the whole graph.
MAXSPEED_CAP_KPH = 120


def _kph_values(value) -> list[float]:
    values = value if isinstance(value, list) else [value]
    out = []
    for v in values:
        m = re.match(r"\s*(\d+(?:\.\d+)?)", str(v))
        if m:
            out.append(float(m.group(1)) * (1.609344 if "mph" in str(v) else 1.0))
    return out


def drop_implausible_maxspeed(G: nx.MultiDiGraph, cap_kph: float = MAXSPEED_CAP_KPH) -> int:
    """Delete maxspeed tags with any value above cap_kph, so they get the class mean instead.

    Must run before add_edge_speeds, which averages maxspeed per highway type.
    The count is stored in G.graph["maxspeed_dropped"] and reported in meta().
    """
    dropped = 0
    for _, _, data in G.edges(data=True):
        if "maxspeed" in data and any(k > cap_kph for k in _kph_values(data["maxspeed"])):
            del data["maxspeed"]
            dropped += 1
    G.graph["maxspeed_dropped"] = dropped
    return dropped


def sort_highway_lists(G: nx.MultiDiGraph) -> None:
    """Sort merged highway lists in place.

    Simplification builds these lists from sets, so their order changes with Python's
    string hash seed. add_edge_speeds and from_osmnx both use the first value, so
    without sorting the same download can give different edge times on each run.
    """
    for _, _, data in G.edges(data=True):
        if isinstance(data.get("highway"), list):
            data["highway"] = sorted(data["highway"])


def download(name: str) -> nx.MultiDiGraph:
    ox.settings.use_cache = True
    ox.settings.cache_folder = "cache"
    G = ox.graph_from_place(PLACES[name], network_type="drive")
    G = ox.truncate.largest_component(G, strongly=True)
    sort_highway_lists(G)
    drop_implausible_maxspeed(G)
    G = ox.routing.add_edge_speeds(G, fallback=FALLBACK_KPH)
    return ox.routing.add_edge_travel_times(G)


def _hwy(value) -> str:
    return str(value[0] if isinstance(value, list) else value)


def from_osmnx(G: nx.MultiDiGraph, name: str) -> Graph:
    """Vertices in ascending osmid order; parallel (u, v) edges keep the fastest one; no self loops."""
    osm_ids = sorted(G.nodes)
    index = {osmid: i for i, osmid in enumerate(osm_ids)}
    best: dict[tuple[int, int], tuple[float, float, str]] = {}  # (u, v) -> (time, length, hwy)
    for u, v, data in G.edges(data=True):
        if u == v:
            continue
        key, t = (index[u], index[v]), float(data["travel_time"])
        if key not in best or t < best[key][0]:
            best[key] = (t, float(data["length"]), _hwy(data.get("highway", "unclassified")))
    pairs = sorted(best)
    return Graph(
        coords=[(float(G.nodes[o]["y"]), float(G.nodes[o]["x"])) for o in osm_ids],
        osm_ids=[int(o) for o in osm_ids],
        tail=[u for u, _ in pairs],
        head=[v for _, v in pairs],
        length=[best[p][1] for p in pairs],
        time=[best[p][0] for p in pairs],
        hwy=[best[p][2] for p in pairs],
        name=name,
    )


def meta(G: nx.MultiDiGraph, g: Graph) -> dict:
    """Summary written next to the graph file. maxspeed_missing_ratio is over all G edges."""
    edges = list(G.edges(data=True))
    missing = sum(1 for _, _, d in edges if d.get("maxspeed") in (None, ""))
    violations = sum(1 for e in range(g.m)
                     if g.length[e] < haversine_m(g.coords[g.tail[e]], g.coords[g.head[e]]) * (1 - 1e-9))
    return {
        "name": g.name,
        "n": g.n,
        "m": g.m,
        "vmax_mps": g.vmax,
        "vmax_kph": g.vmax * 3.6,
        "maxspeed_missing_ratio": missing / len(edges) if edges else 0.0,
        "maxspeed_dropped": G.graph.get("maxspeed_dropped", 0),  # tags above the cap, now missing
        "haversine_violations": violations,  # length < straight line breaks the A* lower bound
        "hwy_counts": dict(Counter(g.hwy).most_common()),
        "osmnx_version": ox.__version__,
        "extracted_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }
