"""CSV arithmetic checks run without matplotlib; rendering is an optional check."""
from __future__ import annotations

import csv
import importlib.util
import math
from pathlib import Path
import tempfile
import unittest

from routing.figures import _accuracy_summary, _timing_summary, _tradeoff_summary, fig_c, fig_d


class E3FigureTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def write(self, name, rows, fields=None):
        path = self.root / name
        with path.open("w", newline="", encoding="utf-8") as stream:
            writer = csv.DictWriter(stream, fieldnames=fields or list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)
        return path

    def timing(self, graph="gss", scenario="synth08"):
        # Deliberately unequal per-bin ratios: use pooled medians, not their mean.
        return [dict(graph=graph, scenario=scenario, kind="full", qid=i, bin="a" if i < 2 else "b",
                     algo=algo, time_s=t, settled=n)
                for algo, times, counts in [("dijkstra", [2, 4, 10], [10, 20, 40]),
                                            ("alt4", [1, 1, 5], [2, 5, 10]),
                                            ("alt8", [3, 6, 10], [6, 7, 8])]
                for i, (t, n) in enumerate(zip(times, counts))]

    def prep(self):
        return [dict(graph="gss", k=4, k_actual=4, prep_s=6, nbytes=2_000_000, breakeven=999),
                dict(graph="gss", k=8, k_actual=7, prep_s=10, nbytes=3_500_000, breakeven=999)]

    def test_accuracy_records_zero_error_control_honestly(self):
        path = self.write("e3_gss_accuracy.csv", [
            dict(scenario="control", algo="astar", n=10, n_wrong=0),
            dict(scenario="control", algo="alt4", n=10, n_wrong=2)])
        rows = {r["algo"]: r for r in _accuracy_summary([path])}
        self.assertEqual(rows["astar"]["accuracy_pct"], 100)
        self.assertEqual(rows["alt4"]["accuracy_pct"], 80)
        self.assertEqual(rows["astar"]["graph"], "gss")

    def test_accuracy_rejects_bad_counts_empty_and_missing_columns(self):
        path = self.write("acc.csv", [dict(graph="gss", scenario="control", algo="alt4", n=3, n_wrong=4)])
        with self.assertRaises(ValueError):
            _accuracy_summary(path)
        empty = self.write("empty.csv", [], ["graph", "scenario", "algo", "n", "n_wrong"])
        with self.assertRaisesRegex(ValueError, "No measured"):
            _accuracy_summary(empty)
        missing = self.write("missing.csv", [dict(x=1)])
        with self.assertRaisesRegex(ValueError, "missing CSV"):
            _accuracy_summary(missing)

    def test_pooled_medians_and_graphs_are_separate(self):
        first = self.write("timing1.csv", self.timing())
        other = self.timing(graph="seoul")
        for row in other:
            if row["algo"] == "dijkstra":
                row["time_s"] *= 10
        second = self.write("timing2.csv", other)
        rows = {(r["graph"], r["algo"]): r for r in _timing_summary([first, second])}
        self.assertEqual(rows[("gss", "dijkstra")]["speedup"], 1)
        self.assertEqual(rows[("gss", "alt4")]["speedup"], 4)
        self.assertEqual(rows[("seoul", "alt4")]["speedup"], 40)
        self.assertEqual(rows[("gss", "alt4")]["settled_ratio"], 0.25)

    def test_control_and_reroute_are_not_full_query_timings(self):
        rows = self.timing()
        rows.extend(self.timing(scenario="control"))
        extra = self.timing(scenario="reroute_snapshot")
        for row in extra:
            row["kind"] = "reroute"
        rows.extend(extra)
        result = _timing_summary(self.write("timing.csv", rows))
        self.assertEqual({r["scenario"] for r in result}, {"synth08"})

    def test_missing_dijkstra_and_zero_timings_are_errors(self):
        rows = [r for r in self.timing() if r["algo"] != "dijkstra"]
        with self.assertRaisesRegex(ValueError, "Dijkstra"):
            _timing_summary(self.write("missing_base.csv", rows))
        rows = self.timing()
        rows[0]["time_s"] = 0
        with self.assertRaisesRegex(ValueError, "positive"):
            _timing_summary(self.write("zero.csv", rows))

    def test_tradeoff_recomputes_synth08_break_even(self):
        prep = self.write("prep.csv", self.prep())
        timing = self.write("timing.csv", self.timing())
        rows = _tradeoff_summary(prep, timing)
        self.assertEqual(rows[0]["k"], 4)
        self.assertEqual(rows[0]["index_mb"], 2)
        self.assertEqual(rows[0]["breakeven"], 6 / (4 - 1))
        self.assertTrue(math.isinf(rows[1]["breakeven"]))
        self.assertEqual(rows[1]["k_actual"], 7)

    def test_tradeoff_rejects_nonmatching_algorithm(self):
        prep = self.prep()
        prep[0]["k"] = 16
        with self.assertRaisesRegex(ValueError, "alt16"):
            _tradeoff_summary(self.write("prep.csv", prep), self.write("timing.csv", self.timing()))

    @unittest.skipUnless(importlib.util.find_spec("matplotlib"), "matplotlib is not installed")
    def test_render_pngs(self):
        import matplotlib
        matplotlib.use("Agg")
        accuracy = self.write("acc.csv", [dict(graph="gss", scenario=scenario, algo=algo, n=3, n_wrong=0)
                                            for scenario in ("synth08", "control")
                                            for algo in ("dijkstra", "alt4", "alt8")])
        timing = self.write("timing.csv", self.timing())
        prep = self.write("prep.csv", self.prep())
        c, d = self.root / "c.png", self.root / "d.png"
        fig_c([accuracy], [timing], c)
        fig_d(prep, timing, d)
        for path in (c, d):
            self.assertTrue(path.read_bytes().startswith(b"\x89PNG\r\n\x1a\n"))
            self.assertGreater(path.stat().st_size, 1000)


if __name__ == "__main__":
    unittest.main()
