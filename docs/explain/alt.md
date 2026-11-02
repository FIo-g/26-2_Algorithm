ALT uses precomputed landmark distances to guide A* search.
For each landmark, it stores shortest travel times both from and to every vertex.
The triangle inequality provides a lower bound that does not exceed the actual shortest remaining travel time.
With landmark 0, our example gives h(1, 2) = max(0, 5 − 2, 10 − 7) = 3 seconds.
This 3-second bound is safe when the actual shortest travel time becomes 6 seconds, but unsafe when it becomes 1 second.
The preprocessing can be reused when the graph structure and indexing remain unchanged and every edge time stays at or above its preprocessing value.
Congestion that only increases travel times preserves this condition.
If travel times drop below their preprocessing values, the old heuristic may overestimate, and optimality is no longer guaranteed.