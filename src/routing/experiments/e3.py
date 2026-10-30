"""E3: exactness under changed weights and the cost of a new route query.

This module orchestrates the shared team algorithms; it does not substitute
another implementation when a prerequisite task has not been merged.
"""
from __future__ import annotations

import math
from collections import defaultdict
from statistics import mean, median
from types import SimpleNamespace

from routing.congestion import lower_bound, midpoint


def _dependencies():
    """Resolve the public interfaces only when an experiment is requested."""
    try:
        from routing.astar import astar
        from routing.bench import ExactnessError, standard_algos, time_all
        from routing.dijkstra import dijkstra
        from routing.verify import check_result, verify_all
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            f"E3 prerequisite {exc.name!r} is unavailable. Merge Tasks 3, 4, "
            "6, 7, 10 and 11, then run the correctness gate before benchmarking."
        ) from exc
    return SimpleNamespace(astar=astar, ExactnessError=ExactnessError,
                           standard_algos=standard_algos, time_all=time_all,
                           dijkstra=dijkstra, check_result=check_result,
                           verify_all=verify_all)


def _relative_error(distance, optimum):
    if distance == optimum:
        return 0.0
    if not math.isfinite(distance) or not math.isfinite(optimum) or optimum == 0:
        return math.inf
    return abs(distance - optimum) / abs(optimum)


def _cost_ratio(distance, optimum):
    """Unreachable pairs have no finite approximation ratio; 0/0 is exact."""
    if math.isinf(optimum):
        return None
    if optimum == 0:
        return 1.0 if distance == 0 else math.inf
    return distance / optimum


def _row_value(row, key):
    return row[key] if isinstance(row, dict) else getattr(row, key)


def _median_time(rows, algorithm):
    times = [float(_row_value(r, "time_s")) for r in rows
             if _row_value(r, "algo") == algorithm]
    if not times or any(not math.isfinite(t) or t < 0 for t in times):
        raise ValueError(f"missing or invalid timing samples for {algorithm}")
    return median(times)


def run_e3(g0, queries, *, graph, scenarios, ks=(4, 8, 16), eps=(1.2, 1.5)):
    """Verify all safe snapshots, then measure full/reroute/weighted queries.

    One lower-bound graph and one landmark/algorithm bundle serve every
    snapshot. The scenario named ``control`` deliberately uses stale bounds:
    its errors are recorded but it is never included in performance claims.
    Even the last safe snapshot must pass before any timer is called.
    Reroute rows retain the original qid/bin; only the query source changes.
    """
    queries = list(queries)
    if not queries:
        raise ValueError("E3 requires at least one query")
    if not scenarios:
        raise ValueError("E3 requires at least one scenario")
    eps = tuple(float(x) for x in eps)
    if any(not math.isfinite(x) or x < 1 for x in eps) or len(set(eps)) != len(eps):
        raise ValueError("eps values must be distinct, finite and at least 1")
    ks = tuple(ks)
    if any(isinstance(k, bool) or not isinstance(k, int) or k < 0 for k in ks):
        raise ValueError("landmark counts must be nonnegative integers")
    for q in queries:
        if not 0 <= q.s < g0.n or not 0 <= q.t < g0.n:
            raise ValueError("query endpoints must be graph vertex indices")
    safe = {name: g for name, g in scenarios.items() if name != "control"}
    # Check the control's edge/index alignment as well, without including its
    # times in the preprocessing baseline.
    for g in scenarios.values():
        lower_bound(g0, [g])
    g_lb = lower_bound(g0, safe.values())
    dep = _dependencies()
    algos, _landmarks = dep.standard_algos(g_lb, ks=ks)
    if "dijkstra" not in algos or "astar" not in algos:
        raise ValueError("standard_algos must include dijkstra and astar")
    accuracy, errors, references = [], [], {}
    for name, g in scenarios.items():
        refs = [dep.dijkstra(g, q.s, q.t)[0] for q in queries]
        references[name] = refs
        for algorithm, search in algos.items():
            n_wrong, max_error = 0, 0.0
            for q, optimum in zip(queries, refs):
                result = search(g, q.s, q.t)
                issues = dep.check_result(g, q.s, q.t, optimum, result)
                n_wrong += bool(issues)
                max_error = max(max_error, _relative_error(result[0], optimum))
                if issues and name != "control":
                    errors.append(f"{name}/{algorithm} q{q.qid}: {'; '.join(issues)}")
            accuracy.append({"graph": graph, "scenario": name, "algo": algorithm,
                             "n": len(queries), "n_wrong": n_wrong,
                             "max_rel_err": max_error})
    if errors:
        raise dep.ExactnessError("E3 full-query gate failed before timing:\n" + "\n".join(errors))

    reroute_queries = []
    if safe:
        reroute_queries = [q._replace(s=midpoint(g0, q.s, q.t)) for q in queries]
    for name, g in safe.items():
        issues = dep.verify_all(g, reroute_queries, algos)
        if issues:
            errors.extend(f"{name}/reroute {issue}" for issue in issues)
    if errors:
        raise dep.ExactnessError("E3 reroute gate failed before timing:\n" + "\n".join(errors))

    weighted = {}
    weighted_ratios = {}
    for epsilon in eps:
        def search(g, s, t, *, stats=None, _eps=epsilon):
            return dep.astar(g, s, t, vmax=g_lb.vmax, eps=_eps, stats=stats)
        weighted[f"wastar{epsilon!r}"] = search
    # Validate weighted paths and their approximation guarantee separately
    # from exactness. Unreachable pairs must still return (inf, []).
    for name, g in safe.items():
        for epsilon, (algorithm, search) in zip(eps, weighted.items()):
            ratios = []
            for q, optimum in zip(queries, references[name]):
                result = search(g, q.s, q.t)
                issues = dep.check_result(g, q.s, q.t, result[0], result)
                distance = result[0]
                if math.isinf(optimum):
                    if distance != math.inf or result[1] != []:
                        issues.append("unreachable optimum requires (inf, [])")
                elif (not math.isfinite(distance)
                      or distance < optimum - 1e-9 * max(1.0, abs(optimum))
                      or distance > epsilon * optimum + 1e-9 * max(1.0, abs(optimum))):
                    issues.append("weighted path violates the epsilon cost bound")
                if issues:
                    errors.append(f"{name}/{algorithm} q{q.qid}: {'; '.join(issues)}")
                ratio = _cost_ratio(distance, optimum)
                if ratio is not None:
                    ratios.append(ratio)
            weighted_ratios[(name, algorithm)] = ratios
    if errors:
        raise dep.ExactnessError("E3 weighted gate failed before timing:\n" + "\n".join(errors))

    timing, reroute, wastar = [], [], []
    for name, g in safe.items():
        full_rows = dep.time_all(g, queries, algos, graph=graph, scenario=name, kind="full")
        timing.extend(full_rows)
        reroute.extend(dep.time_all(g, reroute_queries, algos, graph=graph,
                                   scenario=name, kind="reroute"))
        astar_s = _median_time(full_rows, "astar")
        if weighted:
            weighted_rows = dep.time_all(g, queries, weighted, graph=graph,
                                         scenario=name, kind="weighted")
            for epsilon, algorithm in zip(eps, weighted):
                seconds = _median_time(weighted_rows, algorithm)
                ratios = weighted_ratios[(name, algorithm)]
                speedup = (astar_s / seconds if seconds > 0 else
                           (math.inf if astar_s > 0 else 1.0))
                wastar.append({"graph": graph, "scenario": name, "eps": epsilon,
                               "median_s": seconds, "speedup_vs_astar": speedup,
                               "mean_ratio": mean(ratios) if ratios else None,
                               "max_ratio": max(ratios) if ratios else None,
                               "n": len(queries), "n_ratio": len(ratios),
                               "n_unreachable": len(queries) - len(ratios)})
    return {"accuracy": accuracy, "timing": timing, "reroute": reroute, "wastar": wastar}


def server_ratio(reroute_rows):
    """Relative route-query CPU time, not an absolute server-count estimate.

    Group by graph and scenario to avoid mixing different networks. A zero
    Dijkstra median has no meaningful denominator and is rejected explicitly.
    """
    groups = defaultdict(list)
    for row in reroute_rows:
        if _row_value(row, "kind") != "reroute":
            raise ValueError("server_ratio accepts reroute rows only")
        groups[(_row_value(row, "graph"), _row_value(row, "scenario"))].append(row)
    output = []
    for (graph, scenario), rows in sorted(groups.items()):
        baseline = _median_time(rows, "dijkstra")
        if baseline <= 0:
            raise ValueError("Dijkstra median reroute time must be positive")
        for algorithm in sorted({_row_value(row, "algo") for row in rows}):
            seconds = _median_time(rows, algorithm)
            output.append({"graph": graph, "scenario": scenario, "algo": algorithm,
                           "median_reroute_s": seconds, "ratio": seconds / baseline})
    return output
