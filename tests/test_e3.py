"""Production integration gates: never substitute missing team modules here."""
import importlib.util
import unittest


DEPENDENCIES = ("routing.dijkstra", "routing.heap", "routing.astar",
                "routing.bidirectional", "routing.verify", "routing.queries", "routing.bench",
                "routing.alt", "routing.congestion")
AVAILABLE = all(importlib.util.find_spec(name) is not None for name in DEPENDENCIES)


@unittest.skipUnless(AVAILABLE, "E3 prerequisite modules are missing (currently Task 4 verify)")
class E3IntegrationTests(unittest.TestCase):
    def test_e3_with_team_algorithms(self):
        from routing.synthetic import grid_graph
        from routing.queries import make_queries
        from routing.congestion import standard_scenarios
        from routing.experiments.e3 import run_e3, server_ratio
        g = grid_graph(10, 10, hwy="primary")
        queries = make_queries(g, per_bin=8, bins=[(0, 1500, "a")])
        out = run_e3(g, queries, graph="grid", scenarios=standard_scenarios(g), ks=(4,))
        self.assertTrue(all(row["n_wrong"] == 0 for row in out["accuracy"] if row["scenario"] != "control"))
        self.assertTrue(all(row["max_ratio"] <= row["eps"] + 1e-9 for row in out["wastar"] if row["max_ratio"] is not None))
        self.assertTrue(all(row["ratio"] == 1 for row in server_ratio(out["reroute"]) if row["algo"] == "dijkstra"))


if __name__ == "__main__":
    unittest.main()
