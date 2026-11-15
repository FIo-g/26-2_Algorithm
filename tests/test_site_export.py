"""Tests for scripts/export_site_data.py: recorded heap events and the binary layouts."""
import struct
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import export_site_data as exp  # noqa: E402

from routing.bidirectional import bidirectional_dijkstra  # noqa: E402
from routing.dijkstra import dijkstra  # noqa: E402
from routing.synthetic import from_edge_list, grid_graph  # noqa: E402


@pytest.mark.parametrize("algo, g, t", [
    (dijkstra, grid_graph(4, 4), 15),
    (bidirectional_dijkstra, grid_graph(6, 6), 35),
])
def test_recorded_events_match_stats_and_trace(algo, g, t):
    run = exp.traced_run(algo, g, 0, t)  # traced_run exits if its events disagree with Stats
    pushes = [e for e in run["events"] if e["type"] == "push"]
    pops = [e for e in run["events"] if e["type"] == "pop"]
    assert len(pushes) == run["stats"].pushes
    assert len(pops) == run["stats"].pops
    assert [e["v"] for e in pops if not e["stale"]] == run["stats"].trace


def test_bidirectional_run_records_stop_tests():
    g = from_edge_list(5, [(0, 1, 3), (1, 2, 3), (0, 3, 2), (3, 4, 1.5), (4, 2, 2)])
    run = exp.traced_run(bidirectional_dijkstra, g, 0, 2, loops=True)
    loops = [e for e in run["events"] if e["type"] == "loop"]
    assert run["dist"] == 5.5 and loops[0]["mu"] is None  # mu is inf before the first meeting
    assert loops[-1]["top_f"] + loops[-1]["top_b"] >= loops[-1]["mu"]  # the stop rule held at the end


def test_binary_layouts_round_trip(tmp_path):
    xy = [(0.0, 0.5), (1.0, 0.25), (0.5, 1.0)]
    segments = [(0, 1), (1, 2)]
    net = tmp_path / "net-test.bin"
    net.write_bytes(exp.encode_net(3, xy, segments))
    data = net.read_bytes()
    assert struct.unpack_from("<II", data, 0) == (3, 2)
    assert struct.unpack_from("<6f", data, 8) == (0.0, 0.5, 1.0, 0.25, 0.5, 1.0)
    assert struct.unpack_from("<4I", data, 8 + 24) == (0, 1, 1, 2)

    trace = tmp_path / "trace-test.bin"
    trace.write_bytes(exp.encode_trace([[0, 2, 1], [0]]))
    data = trace.read_bytes()
    assert struct.unpack_from("<I3I", data, 0) == (3, 0, 2, 1)
    assert struct.unpack_from("<2I", data, 16) == (1, 0)
