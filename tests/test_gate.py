"""Exactness gate tests on synthetic graphs; no road data is required."""
import pytest

from routing.dijkstra import dijkstra
from routing.gate import run_gate
from routing.graph import save_graph
from routing.queries import load_queries
from routing.synthetic import grid_graph

pytestmark = pytest.mark.filterwarnings("ignore:bin :UserWarning")  # small grids cannot fill the long bins


def test_gate_passes_and_creates_queries(tmp_path):
    save_graph(grid_graph(8, 8), tmp_path / "g.pkl")
    code, msgs = run_gate(tmp_path / "g.pkl", tmp_path / "q.csv")
    assert code == 0 and msgs == [] and (tmp_path / "q.csv").exists()


def test_gate_fails_on_wrong_algo(tmp_path):
    save_graph(grid_graph(6, 6), tmp_path / "g.pkl")
    bad = {"dijkstra": dijkstra, "bad": lambda g, s, t, stats=None: (0.5, [s, t], 0)}
    assert run_gate(tmp_path / "g.pkl", tmp_path / "q.csv", algos=bad)[0] == 1


def test_gate_reuses_existing_queries(tmp_path):
    g = grid_graph(6, 6); save_graph(g, tmp_path / "g.pkl")
    run_gate(tmp_path / "g.pkl", tmp_path / "q.csv", algos={"dijkstra": dijkstra})
    before = (tmp_path / "q.csv").read_bytes()
    run_gate(tmp_path / "g.pkl", tmp_path / "q.csv", algos={"dijkstra": dijkstra})
    assert (tmp_path / "q.csv").read_bytes() == before and load_queries(tmp_path / "q.csv", g)
