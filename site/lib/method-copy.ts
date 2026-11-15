// One-line description of each method. Read by the step demo and the map cards.
export const METHOD_COPY = {
  dijkstra: "Always settles the closest unsettled intersection. Never looks at a settled one again.",
  astar:
    "Adds a lower bound on the remaining time (straight-line distance divided by the top speed), so it leans toward the destination.",
  bidir:
    "Searches from both ends and stops when the two frontiers together cannot beat the best route found.",
  alt: "A* with a tighter bound built from precomputed distances to a few landmarks and the triangle inequality.",
} as const;

export type MethodCopyId = keyof typeof METHOD_COPY;
