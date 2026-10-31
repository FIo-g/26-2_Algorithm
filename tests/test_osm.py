"""OSMnx conversion tests on a hand-made MultiDiGraph; no network access is required."""
import networkx as nx

from routing.osm import from_osmnx, meta


def tiny_osm():
    G = nx.MultiDiGraph(crs="epsg:4326")
    for osmid, (y, x) in {30: (37.50, 127.00), 10: (37.50, 127.01), 20: (37.51, 127.01)}.items():
        G.add_node(osmid, y=y, x=x)
    G.add_edge(30, 10, 0, length=900.0, travel_time=90.0, highway=["primary", "secondary"], maxspeed="50")
    G.add_edge(30, 10, 1, length=950.0, travel_time=70.0, highway="trunk")
    G.add_edge(10, 20, 0, length=1100.0, travel_time=110.0, highway="residential")
    G.add_edge(20, 20, 0, length=5.0, travel_time=1.0, highway="residential")       # self loop
    return G


def test_from_osmnx_conventions():
    g = from_osmnx(tiny_osm(), "tiny")
    assert g.osm_ids == [10, 20, 30] and g.coords[0] == (37.50, 127.01)
    e = [i for i in range(g.m) if (g.osm_ids[g.tail[i]], g.osm_ids[g.head[i]]) == (30, 10)]
    assert len(e) == 1 and (g.time[e[0]], g.length[e[0]], g.hwy[e[0]]) == (70.0, 950.0, "trunk")
    assert g.m == 2                                     # self loop dropped


def test_from_osmnx_list_highway():
    G = tiny_osm(); G.remove_edge(30, 10, 1)
    assert "primary" in from_osmnx(G, "tiny").hwy


def test_meta_maxspeed_ratio():
    G = tiny_osm(); assert meta(G, from_osmnx(G, "tiny"))["maxspeed_missing_ratio"] == 0.75


def test_meta_counts_haversine_violations():
    G = tiny_osm()
    m = meta(G, from_osmnx(G, "tiny"))
    assert m["haversine_violations"] == 1               # 10->20: 1100 m < straight line ~1112 m
    G[10][20][0]["length"] = 1200.0                     # 30->10 kept 950 m >= ~882 m
    assert meta(G, from_osmnx(G, "tiny"))["haversine_violations"] == 0
    assert (m["name"], m["n"], m["m"]) == ("tiny", 3, 2)
