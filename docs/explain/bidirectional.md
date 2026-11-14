Bidirectional search runs one Dijkstra forward from the source and another backward from the target on the reversed graph.
It keeps μ, the best complete path found so far, updated whenever an edge connects a vertex reached by the forward search to one reached by the backward search.
Our code expands the side with the smaller top key (bidirectional.py:40), which gives the order forward, backward, forward in our example.
In our example, the forward search settles vertex 0, giving d_f(1) = 4 and d_f(2) = 1.
The backward search settles vertex 3, giving d_b(1) = 5 and d_b(2) = 8, so μ = min(4 + 5, 1 + 8) = 9 seconds.
Stopping as soon as the two searches touch a common vertex would wrongly report 9 seconds.
The forward search then settles vertex 2 and improves d_f(1) to 3, so μ = 3 + 5 = 8 seconds.
The correct stopping rule is to stop when the smallest forward key plus the smallest backward key is at least μ.
Here, 3 + 5 = 8 ≥ 8, so the search stops with the correct answer of 8 seconds.
Our example shows why stopping at the first reached vertex is wrong, but it cannot show a second pitfall.
If we kept searching, the first vertex settled by both sides would be vertex 1, and d_f(1) + d_b(1) = 3 + 5 = 8 happens to be correct.
The test graph (tests/test_bidirectional.py:10-13) shows why stopping at the first vertex settled by both sides is also wrong.
Its edges are 0→1: 3, 1→2: 3, 0→3: 2, 3→4: 1.5, and 4→2: 2, with source 0 and target 2.
The forward search settles vertex 0, giving d_f(1) = 3 and d_f(3) = 2.
The backward search settles vertex 2, giving d_b(1) = 3 and d_b(4) = 2, so μ = 3 + 3 = 6.0 seconds through vertex 1.
The forward search settles vertex 3 and relaxes edge 3→4, giving d_f(4) = 3.5, so μ drops to 3.5 + 2 = 5.5 seconds.
The backward search settles vertex 4, giving d_b(3) = 3.5, but 2 + 3.5 = 5.5 does not improve μ.
Now top_f = 3 and top_b = 3, both for vertex 1, and 3 + 3 = 6 ≥ 5.5, so the search stops with 5.5 seconds along 0→3→4→2.
If we waited for the first vertex settled by both sides, both searches would next settle vertex 1, and we would report 3 + 3 = 6.0 seconds.
The correct rule stops before either side settles vertex 1.
Each search only needs to cover about half the distance, which usually means far fewer vertices are explored than in a single Dijkstra search.
Like Dijkstra, it needs nonnegative edge times and no preprocessing, so it adapts to traffic changes by simply running again.
Adding a heuristic gives bidirectional A*, but the stopping rule must then be adjusted, because the naive rule can stop too early.
