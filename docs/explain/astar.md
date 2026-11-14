A* is Dijkstra guided by a heuristic h(v), which estimates the remaining travel time from v to the target.
It expands the vertex with the smallest f(v) = g(v) + h(v), where g(v) is the best known time from the source.
Suppose h(0) = 6, h(1) = 4, h(2) = 5, and h(3) = 0.
Then f(2) = 1 + 5 = 6 seconds, so vertex 2 is expanded before vertex 1, whose f(1) = 4 + 4 = 8 seconds.
A* is optimal when the heuristic is admissible, meaning h(v) never exceeds the actual shortest remaining time.
The estimate h(2) = 5 is safe because the actual shortest time from vertex 2 to vertex 3 is 7 seconds, but it would be unsafe if a road change made that time 4 seconds.
A stronger property, consistency, requires h(u) ≤ w(u, v) + h(v) for every edge, so each vertex only needs to be settled once.
All five edges satisfy it: 6 ≤ 4 + 4 for 0→1, 6 ≤ 1 + 5 for 0→2, 5 ≤ 2 + 4 for 2→1, 4 ≤ 5 + 0 for 1→3, and 5 ≤ 8 + 0 for 2→3.
Our code never reopens a settled vertex (astar.py:50), which is exact only because our heuristic is consistent, not merely admissible.
With h(0) = 0, h(1) = 0, h(2) = 7, and h(3) = 0, every estimate is admissible, but h(2) = 7 > w(2, 1) + h(1) = 2.
Vertex 1 is then settled with g = 4 before vertex 2, and the later 3-second path through vertex 2 is ignored, so A* returns 9 seconds instead of 8.
Our heuristic is straight-line distance divided by the maximum speed vmax.
It is consistent, because an edge is never shorter than the straight line between its endpoints and never faster than vmax: h(u) − h(v) ≤ straight(u, v) / vmax ≤ length(u, v) / vmax ≤ w(u, v).
Our code multiplies h by 1 − 1e-9 to absorb tiny differences between haversine distances and OSMnx edge lengths, and scaling by a factor below 1 keeps the heuristic consistent.
Our vmax is the largest length / time over all edges, so the single fastest edge, usually an urban expressway, sets it for the whole graph.
On side streets, real speeds are far below vmax, so h covers only a fraction of the true remaining time.
Across our graphs, the median ratio of h to the true travel time was only 0.37 to 0.49.
A loose bound barely separates vertices by f, so the search spreads out much as Dijkstra does and settles many more vertices than a tight bound would, while also paying for a haversine computation at every push.
Congestion that only increases travel times keeps this heuristic consistent, so it stays admissible.
If actual speeds can exceed the assumed maximum, the heuristic may overestimate, and optimality is no longer guaranteed.
