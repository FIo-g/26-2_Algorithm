"""Counting binary heap shared by every search, so the counters mean the same thing everywhere.

Lazy deletion: a vertex can sit in the heap several times; when an entry for an
already-settled vertex is popped it counts in `pops` but not in `settled`.
"""
from __future__ import annotations

import heapq
import math
from dataclasses import dataclass, field


@dataclass
class Stats:
    settled: int = 0  # fresh pops = vertices finalized
    relaxed: int = 0  # edges scanned out of settled vertices
    pushes: int = 0  # every push
    pops: int = 0  # every pop, stale entries included
    trace: list[int] | None = field(default=None, compare=False)  # settled order, for figure (f)


class CountingHeap:
    __slots__ = ("_h", "_stats")

    def __init__(self, stats: Stats) -> None:
        self._h: list[tuple[float, int]] = []
        self._stats = stats

    def push(self, key: float, v: int) -> None:
        heapq.heappush(self._h, (key, v))
        self._stats.pushes += 1

    def pop(self) -> tuple[float, int]:
        self._stats.pops += 1
        return heapq.heappop(self._h)

    def drop_stale(self, done: list[bool]) -> None:
        """Pop entries of settled vertices off the top, so top_key() is a fresh key."""
        h = self._h
        while h and done[h[0][1]]:
            heapq.heappop(h)
            self._stats.pops += 1

    def top_key(self) -> float:
        return self._h[0][0] if self._h else math.inf

    def __len__(self) -> int:
        return len(self._h)
