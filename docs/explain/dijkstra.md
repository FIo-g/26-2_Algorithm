Dijkstra finds shortest travel times from a source by always expanding the unsettled vertex with the smallest tentative time.
When a vertex is removed from the priority queue, its time is final, because every remaining path to it cannot get shorter.
In our example, after settling vertex 0, we have d(1) = 4 and d(2) = 1.
Settling vertex 2 relaxes edge 2→1, which improves d(1) = min(4, 1 + 2) = 3 seconds.
Settling vertex 1 then gives d(3) = min(1 + 8, 3 + 5) = 8 seconds.
This correctness argument holds only when every edge time is nonnegative.
In this example, no single negative edge breaks Dijkstra, because every edge points to a vertex that is settled later.
A failure needs a negative edge into a vertex that is already settled.
If 0→2 were 5 and 2→1 were −3, vertex 1 would be settled at 4 before vertex 2 is settled at 5.
Edge 2→1 would then offer 5 − 3 = 2 seconds, but vertex 1 is already final, so Dijkstra reports d(3) = 9 although 0→2→1→3 takes 7 seconds.
Our Graph rejects negative edge times, so this case cannot occur in our code.
Our heap uses lazy deletion: when a vertex improves, we push a new entry instead of updating the old one.
In our example, vertex 1 is pushed with key 4 when vertex 0 is settled and again with key 3 when vertex 2 is settled.
The entry (3, 1) settles vertex 1, so the entry (4, 1) becomes stale.
It is popped after vertex 1 is settled and before vertex 3 is settled.
The check at dijkstra.py:40 skips it, so vertex 1 is not settled or relaxed a second time.
Without this check, the distance would still be 8 seconds, because 4 + 5 = 9 does not beat 8, but vertex 1 would appear twice in the settled count and the trace.
The settled count measures how many vertices a search finalizes, and we compare it across algorithms, so a stale pop counts in pops but not in settled.
This query ends with 6 pushes, 5 pops, and 4 settled vertices, and the entry (9, 3) is never popped because the search returns as soon as vertex 3 is settled.
Dijkstra does no preprocessing, so it always uses the current edge times.
However, a computed shortest-path tree becomes stale whenever any edge time changes, and the search must be rerun.
