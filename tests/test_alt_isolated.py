"""Standard-library ALT checks, separate from the Task 3 integration gate.

Missing Task 3 modules alone receive temporary test-only protocol adapters.
Production routing has no fallback. Run from the repository root:
python -m unittest discover -s tests -p 'test_alt*.py' -v
"""
from contextlib import ExitStack
import importlib
import importlib.util
import math
from pathlib import Path
import random
import sys
import tracemalloc
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from routing.synthetic import from_edge_list, grid_graph
from _alt_test_support import assert_path, dependency_modules, floyd_warshall


class ALTIsolatedTests(unittest.TestCase):
    """Independent oracle checks do not certify Task 3 integration."""

    def setUp(self):
        stack = ExitStack()
        self.addCleanup(stack.close)
        for name, module in dependency_modules().items():
            try:
                importlib.import_module(name)
            except ModuleNotFoundError as exc:
                if exc.name != name:
                    raise
                stack.enter_context(patch.dict(sys.modules, {name: module}))
        name = "routing._alt_isolated"
        path = Path(__file__).parents[1] / "src" / "routing" / "alt.py"
        spec = importlib.util.spec_from_file_location(name, path)
        module = importlib.util.module_from_spec(spec)
        stack.enter_context(patch.dict(sys.modules, {name: module}))
        spec.loader.exec_module(module)
        self.alt = module

    def test_distance_table_direction_and_memory(self):
        g = from_edge_list(3, [(0, 1, 2), (1, 2, 3), (2, 0, 7)])
        lm = self.alt.build_landmarks(g, [0])
        self.assertEqual(list(lm.d_from[0]), [0, 2, 5])
        self.assertEqual(list(lm.d_to[0]), [0, 10, 7])
        self.assertEqual((lm.k, lm.k_requested, lm.nbytes), (1, 1, 48))
        self.assertGreaterEqual(lm.prep_s, 0)

    def test_disconnected_inf_and_landmark_reaches_neither_endpoint(self):
        g = from_edge_list(7, [(0, 1, 1), (1, 2, 1), (2, 0, 1),
                               (3, 4, 1), (4, 6, 1), (3, 5, 1),
                               (5, 6, 3), (6, 3, 1)])
        lm, truth = self.alt.build_landmarks(g, [0]), floyd_warshall(g)
        for s in range(g.n):
            for t in range(g.n):
                h = self.alt.alt_heuristic(lm, s, t)
                self.assertTrue(math.isfinite(h) and h >= 0)
                assert_path(g, s, t, truth[s][t], self.alt.alt(g, s, t, lm))
        self.assertEqual(self.alt.alt(g, 3, 6, lm)[:2], (2., [3, 4, 6]))

    def test_farthest_selection_is_deterministic_unique_and_finite(self):
        g = grid_graph(4, 4)
        a = self.alt.preprocess_landmarks(g, 6, seed=13)
        b = self.alt.preprocess_landmarks(g, 6, seed=13)
        self.assertEqual(a.ids, b.ids)
        self.assertEqual((len(set(a.ids)), a.k), (6, 6))
        nearest = [math.inf] * g.n
        for i, chosen in enumerate(a.ids):
            if i:
                candidates = [v for v in range(g.n)
                              if v not in a.ids[:i] and math.isfinite(nearest[v])]
                self.assertEqual(chosen, max(candidates, key=lambda v: (nearest[v], -v)))
            nearest = [min(old, f + b) for old, f, b in
                       zip(nearest, a.d_from[i], a.d_to[i])]

    def test_12800_paths_match_independent_floyd_warshall(self):
        checked = 0
        for seed in range(50):
            with self.subTest(seed=seed):
                rng = random.Random(seed)
                edges = [(u, v, rng.choice([0., .25, 1., 7.]))
                         for u in range(8) for v in range(8)
                         if u != v and rng.random() < .22]
                base = from_edge_list(8, edges)
                tables = [self.alt.build_landmarks(base, [0, 3, 7]),
                          self.alt.preprocess_landmarks(base, 10, seed=seed)]
                for lm in tables:
                    slowed = base.reweighted([w * rng.uniform(1., 4.) for w in base.time])
                    for g in (base, slowed):
                        truth = floyd_warshall(g)
                        for s in range(g.n):
                            for t in range(g.n):
                                h = self.alt.alt_heuristic(lm, s, t)
                                self.assertTrue(math.isfinite(h))
                                self.assertLessEqual(h, truth[s][t] + 1e-9)
                                assert_path(g, s, t, truth[s][t],
                                            self.alt.alt(g, s, t, lm))
                                checked += 1
        self.assertEqual(checked, 12800)

    def test_speedup_negative_control(self):
        base = from_edge_list(3, [(0, 1, 100), (0, 2, 510), (2, 1, 520)])
        faster = base.reweighted([100, 10, 10])
        old = self.alt.build_landmarks(base, [1])
        self.assertEqual(floyd_warshall(faster)[0][1], 20)
        self.assertEqual(self.alt.alt(faster, 0, 1, old)[0], 100)
        fresh = self.alt.build_landmarks(faster, [1])
        self.assertEqual(self.alt.alt(faster, 0, 1, fresh)[0], 20)

    def test_zero_costs_empty_landmarks_and_same_vertex(self):
        g = from_edge_list(3, [(0, 1, 0), (1, 2, 0), (0, 2, 5)])
        lm = self.alt.build_landmarks(g, [])
        self.assertEqual((lm.k, lm.nbytes), (0, 0))
        self.assertEqual(self.alt.alt(g, 0, 2, lm)[:2], (0., [0, 1, 2]))
        self.assertEqual(self.alt.alt(g, 1, 1, lm), (0., [1], 0))
        self.assertEqual(self.alt.preprocess_landmarks(g, 0).k, 0)
        self.assertEqual(self.alt.preprocess_landmarks(from_edge_list(0, []), 4).k, 0)
        limited = self.alt.preprocess_landmarks(g, 4)
        self.assertTrue(len(set(limited.ids)) == limited.k <= 3)
        self.assertEqual(limited.k_requested, 4)

    def test_stats_and_trace_follow_shared_protocol(self):
        g = from_edge_list(4, [(0, 1, 5), (0, 2, 1), (2, 1, 1), (1, 3, 10)])
        stats = self.alt.Stats(trace=[])
        result = self.alt.alt(g, 0, 3, self.alt.build_landmarks(g, []), stats=stats)
        self.assertEqual(result, (12., [0, 2, 1, 3], 4))
        self.assertEqual((stats.settled, stats.relaxed, stats.pushes, stats.pops), (4, 4, 5, 5))
        self.assertEqual(stats.trace, [0, 2, 1, 3])

    def test_short_query_has_no_per_vertex_allocations(self):
        # One n-sized pointer list alone is about 180 KB at this graph size.
        # The shared benchmark's budget is 50 KB for a nearby-point query.
        g = grid_graph(150, 150)
        lm = self.alt.preprocess_landmarks(g, 4)
        tracemalloc.start()
        try:
            result = self.alt.alt(g, 0, 1, lm)
            peak = tracemalloc.get_traced_memory()[1]
        finally:
            tracemalloc.stop()
        self.assertEqual(result[:2], (g.weight(0, 1), [0, 1]))
        self.assertLess(peak, 50_000)

    def test_reopens_for_an_admissible_inconsistent_bound(self):
        g = from_edge_list(4, [(0, 1, 3), (0, 2, 1), (2, 1, 1), (1, 3, 3)])
        lm = self.alt.build_landmarks(g, [])
        heuristic = lambda _lm, v, _t: [0, 0, 4, 0][v]
        stats = self.alt.Stats(trace=[])
        with patch.object(self.alt, "alt_heuristic", heuristic):
            result = self.alt.alt(g, 0, 3, lm, stats=stats)
        self.assertEqual(result[:2], (5., [0, 2, 1, 3]))
        self.assertEqual(stats.trace.count(1), 2)

    def test_invalid_inputs_are_rejected(self):
        for ids in ([-1], [3], [0, 0], [0.5]):
            with self.subTest(ids=ids), self.assertRaises(ValueError):
                self.alt.build_landmarks(from_edge_list(3, []), ids)
        for k in (-1, 1.5):
            with self.subTest(k=k), self.assertRaises(ValueError):
                self.alt.preprocess_landmarks(from_edge_list(3, []), k)
        g = from_edge_list(3, [(0, 1, 2)])
        lm = self.alt.build_landmarks(from_edge_list(2, []), [0])
        with self.assertRaisesRegex(ValueError, "size"):
            self.alt.alt(g, 0, 1, lm)
        with self.assertRaisesRegex(ValueError, "vertex"):
            self.alt.alt(g, -1, 1, lm)


if __name__ == "__main__":
    unittest.main()
