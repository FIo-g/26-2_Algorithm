"""Production Task 3 integration checks with no test adapters.

Missing prerequisites cause an explicit skip, never an integration pass.
"""
import importlib.util
import math
from pathlib import Path
import random
import sys
import unittest

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

MISSING_TASK3 = [name for name in ("routing.heap", "routing.dijkstra")
                 if importlib.util.find_spec(name) is None]


@unittest.skipIf(MISSING_TASK3, "Task 3 not merged: " + ", ".join(MISSING_TASK3))
class ALTTask3IntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from routing.alt import alt, alt_heuristic, build_landmarks, preprocess_landmarks
        from routing.dijkstra import dijkstra
        from routing.synthetic import from_edge_list, grid_graph, random_geo_graph
        cls.alt = staticmethod(alt)
        cls.alt_heuristic = staticmethod(alt_heuristic)
        cls.build_landmarks = staticmethod(build_landmarks)
        cls.preprocess_landmarks = staticmethod(preprocess_landmarks)
        cls.dijkstra = staticmethod(dijkstra)
        cls.from_edge_list = staticmethod(from_edge_list)
        cls.grid_graph = staticmethod(grid_graph)
        cls.random_geo_graph = staticmethod(random_geo_graph)

    def test_alt_matches_dijkstra_after_slowdown(self):
        base = self.random_geo_graph(80, 200, seed=11)
        lm = self.preprocess_landmarks(base, 4)
        rng = random.Random(0)
        g = base.reweighted([w * rng.uniform(1., 3.) for w in base.time])
        for _ in range(40):
            s, t = rng.randrange(g.n), rng.randrange(g.n)
            ref = self.dijkstra(g, s, t)[0]
            dist, path, _ = self.alt(g, s, t, lm)
            if math.isinf(ref):
                self.assertEqual((dist, path), (math.inf, []))
            else:
                self.assertTrue(math.isclose(dist, ref, rel_tol=1e-9, abs_tol=1e-9))
                self.assertEqual((path[0], path[-1]), (s, t))
                self.assertTrue(math.isclose(sum(g.weight(u, v) for u, v in zip(path, path[1:])),
                                             dist, rel_tol=1e-9, abs_tol=1e-9))

    def test_alt_settles_fewer_on_grid(self):
        g = self.grid_graph(15, 15)
        lm = self.preprocess_landmarks(g, 8)
        rng = random.Random(0)
        pairs = [(rng.randrange(g.n), rng.randrange(g.n)) for _ in range(50)]
        self.assertLess(sum(self.alt(g, s, t, lm)[2] for s, t in pairs),
                        sum(self.dijkstra(g, s, t)[2] for s, t in pairs))

    def test_empty_component_and_zero_weight_edges(self):
        g = self.from_edge_list(4, [(0, 1, 0), (1, 2, 0)])
        lm = self.build_landmarks(g, [3])
        self.assertEqual(self.alt(g, 0, 2, lm)[:2], (0., [0, 1, 2]))
        self.assertEqual(self.alt(g, 0, 3, lm)[:2], (math.inf, []))
        self.assertEqual(self.alt(g, 2, 2, lm), (0., [2], 0))
        self.assertTrue(all(math.isfinite(self.alt_heuristic(lm, v, t))
                            for v in range(g.n) for t in range(g.n)))


if __name__ == "__main__":
    unittest.main()
