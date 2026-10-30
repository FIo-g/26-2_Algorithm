"""Synthetic scenario tests; no road data or network access is required."""
from __future__ import annotations

import importlib.util
import math
import unittest
from unittest.mock import patch
import sys
import types

from routing.graph import Graph
from routing.synthetic import from_edge_list, grid_graph, random_geo_graph
from routing.congestion import (
    SYNTH_PROFILES, control_speedup, hwy_class, lower_bound, midpoint,
    random_slowdown, standard_scenarios, synthetic,
)


class CongestionTests(unittest.TestCase):
    def test_profiles_are_declared_assumptions(self):
        self.assertEqual(SYNTH_PROFILES["08"]["primary"], 2.0)
        self.assertEqual(SYNTH_PROFILES["18"]["primary"], 2.2)
        self.assertTrue(all(x >= 1 for p in SYNTH_PROFILES.values() for x in p.values()))

    def test_link_classes(self):
        self.assertEqual(hwy_class("primary_link"), "primary")
        self.assertEqual(hwy_class("motorway_link"), "motorway")
        self.assertEqual(hwy_class("living_street"), "other")
        self.assertEqual(hwy_class("unclassified"), "other")

    def test_slowdowns_never_faster(self):
        g = random_geo_graph(60, 150, seed=2)
        snapshots = standard_scenarios(g)
        self.assertEqual(set(snapshots), {"synth03", "synth08", "synth18", "random30", "control"})
        for name in ("synth03", "synth08", "synth18", "random30"):
            self.assertTrue(all(a >= b for a, b in zip(snapshots[name].time, g.time)), name)

    def test_random30_exact_count_and_determinism(self):
        g = random_geo_graph(60, 150, seed=2)
        h = random_slowdown(g)
        self.assertEqual(sum(a == 2 * b for a, b in zip(h.time, g.time)), round(0.3 * g.m))
        self.assertEqual(h.time, random_slowdown(g).time)
        self.assertNotEqual(h.time, random_slowdown(g, seed=5).time)

    def test_random_selection_extremes(self):
        g = from_edge_list(3, [(0, 1, 0), (1, 2, 5)])
        self.assertEqual(random_slowdown(g, frac=0).time, g.time)
        self.assertEqual(random_slowdown(g, frac=1).time, [0, 10])

    def test_control_exceeds_vmax_and_includes_links(self):
        g = grid_graph(4, 4, hwy="motorway_link")
        h = control_speedup(g)
        self.assertGreater(h.vmax, g.vmax)
        self.assertEqual(h.time, [0.5 * t for t in g.time])

    def test_control_selects_highways_and_exact_fraction_of_rest(self):
        g = from_edge_list(13, [(u, u + 1, 10) for u in range(12)])
        g = Graph(g.coords, g.osm_ids, g.tail, g.head, g.length, g.time,
                  ["motorway", "trunk_link"] + ["residential"] * 10)
        h = control_speedup(g, frac_other=0.3)
        selected = [e for e, (a, b) in enumerate(zip(h.time, g.time)) if a < b]
        self.assertEqual(len(selected), 2 + 3)
        self.assertTrue({0, 1}.issubset(selected))

    def test_input_graph_remains_unchanged(self):
        g = grid_graph(3, 3)
        old_time = list(g.time)
        old_fwd = [list(x) for x in g.fwd]
        for h in standard_scenarios(g).values():
            self.assertIsNot(h, g)
            self.assertEqual(h.tail, g.tail)
            self.assertEqual(h.osm_ids, g.osm_ids)
        self.assertEqual(g.time, old_time)
        self.assertEqual(g.fwd, old_fwd)

    def test_lower_bound(self):
        g = from_edge_list(4, [(0, 1, 1), (1, 2, 1), (2, 3, 2)])
        h = g.reweighted([2, 0.5, 2])
        self.assertEqual(lower_bound(g, [h]).time, [1, 0.5, 2])
        self.assertEqual(lower_bound(g, []).time, g.time)
        snapshots = standard_scenarios(g)
        safe = [h for name, h in snapshots.items() if name != "control"]
        self.assertEqual(lower_bound(g, safe).time, g.time)

    def test_lower_bound_rejects_reordered_edges(self):
        g = from_edge_list(3, [(0, 1, 2), (1, 2, 3)])
        h = from_edge_list(3, [(1, 2, 3), (0, 1, 2)])
        with self.assertRaisesRegex(ValueError, "topology"):
            lower_bound(g, [h])

    def test_invalid_parameters(self):
        g = grid_graph(2, 2)
        for frac in (-0.1, 1.1, math.nan, math.inf):
            with self.assertRaises(ValueError):
                random_slowdown(g, frac=frac)
        for factor in (-1, 0, 0.5, math.nan, math.inf):
            with self.assertRaises(ValueError):
                random_slowdown(g, factor=factor)
        for factor in (-1, 0, 2, math.nan, math.inf):
            with self.assertRaises(ValueError):
                control_speedup(g, factor=factor)
        with self.assertRaises(ValueError):
            synthetic(g, "09")

    def test_midpoint_path_logic_with_dependency_double(self):
        # Only the Task 3 API is replaced here; this tests midpoint selection,
        # not integration with the unmerged team Dijkstra implementation.
        g = from_edge_list(4, [(0, 1, 1), (1, 2, 1), (2, 3, 2)])
        dependency = types.ModuleType("routing.dijkstra")
        dependency.dijkstra = lambda graph, s, t: (4.0, [0, 1, 2, 3], 4)
        with patch.dict(sys.modules, {"routing.dijkstra": dependency}):
            self.assertEqual(midpoint(g, 0, 3), 2)
            self.assertEqual(midpoint(g, 2, 2), 2)
        dependency.dijkstra = lambda graph, s, t: (2.0, [2, 3], 2)
        with patch.dict(sys.modules, {"routing.dijkstra": dependency}):
            self.assertEqual(midpoint(g, 2, 3), 2)
        dependency.dijkstra = lambda graph, s, t: (math.inf, [], 1)
        with patch.dict(sys.modules, {"routing.dijkstra": dependency}):
            self.assertEqual(midpoint(g, 3, 0), 3)

    @unittest.skipUnless(importlib.util.find_spec("routing.dijkstra"), "Task 3 Dijkstra is not merged")
    def test_midpoint_with_team_dijkstra(self):
        g = from_edge_list(4, [(0, 1, 1), (1, 2, 1), (2, 3, 2)])
        self.assertEqual(midpoint(g, 0, 3), 2)


if __name__ == "__main__":
    unittest.main()
