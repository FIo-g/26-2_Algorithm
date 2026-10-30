"""E3 orchestration tests with explicit, test-only prerequisite doubles.

These deterministic sample times are not routing benchmark measurements.
"""
from __future__ import annotations

import math
import contextlib
import importlib.util
import io
from pathlib import Path
import tempfile
from collections import namedtuple
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from routing.experiments import e3
from routing.synthetic import from_edge_list

Query = namedtuple("Query", "qid bin s t crow_m")
Row = namedtuple("Row", "graph scenario kind qid bin algo time_s dist settled relaxed pushes pops")


def oracle(g, source, target, *, stats=None):
    """Independent Bellman-Ford oracle used only by isolated tests."""
    distances, previous = [math.inf] * g.n, [None] * g.n
    distances[source] = 0.0
    for _ in range(g.n - 1):
        changed = False
        for u, v, weight in zip(g.tail, g.head, g.time):
            if distances[u] + weight < distances[v]:
                distances[v], previous[v], changed = distances[u] + weight, u, True
        if not changed:
            break
    if not math.isfinite(distances[target]):
        return math.inf, [], 0
    path = [target]
    while path[-1] != source:
        path.append(previous[path[-1]])
    return distances[target], list(reversed(path)), 0


def check(g, source, target, optimum, result):
    distance, path, _ = result
    if optimum == math.inf:
        return [] if distance == math.inf and path == [] else ["unreachable mismatch"]
    issues = []
    if not math.isclose(distance, optimum, rel_tol=1e-9, abs_tol=1e-9):
        issues.append("cost differs")
    if not path or path[0] != source or path[-1] != target:
        issues.append("endpoints differ")
    else:
        weights = [g.weight(u, v) for u, v in zip(path, path[1:])]
        if None in weights or not math.isclose(sum(weights), distance):
            issues.append("invalid path cost")
    return issues


class DependencyDouble:
    class ExactnessError(Exception):
        pass

    def __init__(self):
        self.standard_calls, self.timer_calls = [], []
        self.bad_graph = None
        self.bad_source = None
        self.bad_weighted = False

    def standard_algos(self, graph, *, ks):
        self.standard_calls.append((graph, ks))
        def tested(g, source, target, *, stats=None):
            result = oracle(g, source, target)
            if g is self.bad_graph and (self.bad_source is None or source == self.bad_source):
                return result[0] + 1, result[1], result[2]
            return result
        return {"dijkstra": oracle, "astar": tested, "bidir": oracle,
                **{f"alt{k}": oracle for k in ks}}, {}

    dijkstra = staticmethod(oracle)
    check_result = staticmethod(check)

    def verify_all(self, g, queries, algos):
        return [f"{name} q{q.qid}: {issue}"
                for name, search in algos.items() for q in queries
                for issue in check(g, q.s, q.t, oracle(g, q.s, q.t)[0], search(g, q.s, q.t))]

    def astar(self, g, source, target, *, vmax, eps, stats=None):
        result = oracle(g, source, target)
        if self.bad_weighted:
            return result[0] + 100, result[1], 0
        return result

    def time_all(self, g, queries, algos, *, graph, scenario, kind):
        self.timer_calls.append((scenario, kind, tuple(algos)))
        return [Row(graph, scenario, kind, q.qid, q.bin, name,
                    2.0 if name == "dijkstra" else 1.0,
                    search(g, q.s, q.t)[0], 0, 0, 0, 0)
                for name, search in algos.items() for q in queries]


class E3IsolatedTests(unittest.TestCase):
    def setUp(self):
        self.g = from_edge_list(4, [(0, 1, 1), (1, 2, 1), (2, 3, 1)])
        self.queries = [Query(7, "original-bin", 0, 3, 0)]
        self.dep = DependencyDouble()

    def run_case(self, scenarios, queries=None, **kwargs):
        with patch.object(e3, "_dependencies", return_value=self.dep), \
                patch.object(e3, "midpoint", return_value=1):
            return e3.run_e3(self.g, self.queries if queries is None else queries,
                             graph="unit-only", scenarios=scenarios, ks=(4,), **kwargs)

    def test_bundle_is_built_once_and_control_excluded_from_lower_bound(self):
        normal = self.g.reweighted([2, 3, 4])
        faster_observed = self.g.reweighted([0.5, 2, 3])
        control = self.g.reweighted([0.1, 0.1, 0.1])
        out = self.run_case({"synth08": normal, "real08": faster_observed, "control": control})
        self.assertEqual(len(self.dep.standard_calls), 1)
        self.assertEqual(self.dep.standard_calls[0][0].time, [0.5, 1, 1])
        self.assertEqual(self.dep.standard_calls[0][1], (4,))
        self.assertEqual(len(out["accuracy"]), 3 * 4)
        self.assertFalse(any(scenario == "control" for scenario, _, _ in self.dep.timer_calls))
        self.assertTrue(all(row.qid == 7 and row.bin == "original-bin" for row in out["reroute"]))
        self.assertTrue(all(row.kind == "reroute" for row in out["reroute"]))

    def test_bad_last_scenario_stops_all_timing(self):
        bad = self.g.reweighted([2, 2, 2])
        self.dep.bad_graph = bad
        with self.assertRaisesRegex(self.dep.ExactnessError, "full-query gate"):
            self.run_case({"good": self.g, "bad": bad})
        self.assertEqual(self.dep.timer_calls, [])

    def test_bad_reroute_stops_all_timing(self):
        self.dep.bad_graph, self.dep.bad_source = self.g, 1
        with self.assertRaisesRegex(self.dep.ExactnessError, "reroute gate"):
            self.run_case({"synth08": self.g})
        self.assertEqual(self.dep.timer_calls, [])

    def test_bad_weighted_path_stops_all_timing(self):
        self.dep.bad_weighted = True
        with self.assertRaisesRegex(self.dep.ExactnessError, "weighted gate"):
            self.run_case({"synth08": self.g})
        self.assertEqual(self.dep.timer_calls, [])

    def test_control_wrong_answer_is_recorded_and_not_timed(self):
        control = self.g.reweighted([0.5, 0.5, 0.5])
        self.dep.bad_graph = control
        out = self.run_case({"synth08": self.g, "control": control})
        control_row = next(r for r in out["accuracy"] if r["scenario"] == "control" and r["algo"] == "astar")
        self.assertEqual(control_row["n_wrong"], 1)
        self.assertFalse(any(row.scenario == "control" for row in out["timing"]))

    def test_unreachable_and_zero_optimum_ratios_are_explicit(self):
        self.g = from_edge_list(4, [(0, 1, 0), (1, 2, 0)])
        queries = [Query(1, "zero", 0, 2, 0), Query(2, "unreachable", 3, 0, 0)]
        out = self.run_case({"synth08": self.g}, queries=queries)
        for row in out["wastar"]:
            self.assertEqual(row["max_ratio"], 1)
            self.assertEqual(row["mean_ratio"], 1)
            self.assertEqual(row["n_ratio"], 1)
            self.assertEqual(row["n_unreachable"], 1)

    def test_all_unreachable_has_no_fabricated_cost_ratio(self):
        queries = [Query(1, "unreachable", 3, 0, 0)]
        out = self.run_case({"synth08": self.g}, queries=queries)
        self.assertTrue(all(row["max_ratio"] is None and row["mean_ratio"] is None for row in out["wastar"]))

    def test_empty_and_invalid_parameters(self):
        for eps in ((0.9,), (math.inf,), (math.nan,), (1.2, 1.2)):
            with self.assertRaises(ValueError):
                self.run_case({"safe": self.g}, eps=eps)
        with self.assertRaises(ValueError):
            self.run_case({}, eps=())
        with self.assertRaises(ValueError):
            self.run_case({"safe": self.g}, queries=[])

    def test_server_ratio_is_relative_and_graphs_are_not_mixed(self):
        rows = [Row(graph, "synth08", "reroute", q, "bin", algo, seconds, 3, 0, 0, 0, 0)
                for graph, base in (("gss", 2), ("seoul", 10)) for q in range(2)
                for algo, seconds in (("dijkstra", base), ("alt4", base / 2))]
        out = e3.server_ratio(rows)
        self.assertEqual(len(out), 4)
        self.assertTrue(all(row["ratio"] == (1 if row["algo"] == "dijkstra" else 0.5) for row in out))

    def test_server_ratio_rejects_zero_or_missing_baseline(self):
        row = Row("grid", "safe", "reroute", 0, "bin", "dijkstra", 0, 0, 0, 0, 0, 0)
        with self.assertRaises(ValueError):
            e3.server_ratio([row])
        with self.assertRaises(ValueError):
            e3.server_ratio([row._replace(algo="alt4", time_s=1)])
        with self.assertRaises(ValueError):
            e3.server_ratio([row._replace(kind="full", time_s=1)])

    def test_cli_selects_graph_versions_numerically_and_honors_pinning(self):
        script = Path(__file__).resolve().parents[1] / "scripts" / "run_e3.py"
        spec = importlib.util.spec_from_file_location("e3_cli_test", script)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)
            for version in (1, 9, 10):
                (folder / f"gss_graph_v{version}.pkl").write_bytes(b"test-only")
            self.assertEqual(module.resolve_graph(folder, "gss").name, "gss_graph_v10.pkl")
            self.assertEqual(module.resolve_graph(folder, "gss", 9).name, "gss_graph_v9.pkl")
            with self.assertRaises(FileNotFoundError):
                module.resolve_graph(folder, "seoul")
            (folder / "gss_graph_v010.pkl").write_bytes(b"test-only")
            with self.assertRaisesRegex(ValueError, "Ambiguous"):
                module.resolve_graph(folder, "gss")

    def test_cli_check_only_reports_missing_inputs_without_creating_results(self):
        script = Path(__file__).resolve().parents[1] / "scripts" / "run_e3.py"
        spec = importlib.util.spec_from_file_location("e3_cli_test", script)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                result = module.main(["gss", "--graphs-dir", str(folder),
                                      "--results-dir", str(folder / "results"), "--check-only"])
            self.assertEqual(result, 2)
            self.assertIn('"ready": false', output.getvalue())
            self.assertFalse((folder / "results").exists())


if __name__ == "__main__":
    unittest.main()
