"""Test-only Task 3 protocol doubles and independent distance oracles.

These helpers never enter production routing code or a measured experiment.
They make isolated ALT tests possible before the team's Task 3 is merged.
"""
from dataclasses import dataclass, field
import heapq
import math
import types


@dataclass
class TestStats:
    __test__ = False
    settled: int = 0
    relaxed: int = 0
    pushes: int = 0
    pops: int = 0
    trace: list[int] | None = field(default=None, compare=False)


class TestCountingHeap:
    __test__ = False

    def __init__(self, stats):
        self.items = []
        self.stats = stats

    def push(self, key, vertex):
        self.stats.pushes += 1
        heapq.heappush(self.items, (key, vertex))

    def pop(self):
        self.stats.pops += 1
        return heapq.heappop(self.items)

    def __len__(self):
        return len(self.items)


def bellman_ford(adj, source):
    """Independent O(VE) preprocessing oracle; not Dijkstra or a benchmark."""
    distances = [math.inf] * len(adj)
    distances[source] = 0.0
    for _ in range(len(adj) - 1):
        changed = False
        for u, edges in enumerate(adj):
            for v, weight in edges:
                candidate = distances[u] + weight
                if candidate < distances[v]:
                    distances[v] = candidate
                    changed = True
        if not changed:
            break
    return distances


def floyd_warshall(g):
    """Independent all-pairs oracle, including unreachable and zero costs."""
    distances = [[math.inf] * g.n for _ in range(g.n)]
    for v in range(g.n):
        distances[v][v] = 0.0
    for u, v, weight in zip(g.tail, g.head, g.time):
        distances[u][v] = min(distances[u][v], weight)
    for k in range(g.n):
        for i in range(g.n):
            for j in range(g.n):
                distances[i][j] = min(distances[i][j],
                                      distances[i][k] + distances[k][j])
    return distances


def dependency_modules():
    heap = types.ModuleType("routing.heap")
    heap.Stats, heap.CountingHeap = TestStats, TestCountingHeap
    dijkstra = types.ModuleType("routing.dijkstra")
    dijkstra.sssp = bellman_ford
    return {"routing.heap": heap, "routing.dijkstra": dijkstra}


def assert_path(g, source, target, expected, result):
    distance, path, settled = result
    assert settled >= 0
    if math.isinf(expected):
        assert distance == math.inf and path == []
        return
    assert math.isclose(distance, expected, rel_tol=1e-9, abs_tol=1e-9)
    assert path[0] == source and path[-1] == target
    weights = [g.weight(u, v) for u, v in zip(path, path[1:])]
    assert all(weight is not None for weight in weights)
    assert math.isclose(sum(weights), distance, rel_tol=1e-9, abs_tol=1e-9)
