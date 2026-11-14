// Method ids match the `algo` column in results/*.csv and the `id` values in public/data/hero.json.
export const METHOD_IDS = ["dijkstra", "astar", "bidir", "alt4", "alt8", "alt16"] as const;
export type MethodId = (typeof METHOD_IDS)[number];

export type MethodShape = "disc" | "triangle" | "diamond" | "square";
export type SquareSize = "small" | "medium" | "large";

export type MethodInfo = {
  id: MethodId;
  label: string;
  shape: MethodShape;
  fill: string; // CSS colour token, used as a style value
  squareSize?: SquareSize; // ALT variants differ by square size as well as label
};

export const METHODS: Record<MethodId, MethodInfo> = {
  dijkstra: { id: "dijkstra", label: "Dijkstra", shape: "disc", fill: "var(--black)" },
  astar: { id: "astar", label: "A*", shape: "triangle", fill: "var(--blue)" },
  bidir: { id: "bidir", label: "Bidirectional", shape: "diamond", fill: "var(--red)" },
  alt4: { id: "alt4", label: "ALT (4)", shape: "square", fill: "var(--yellow)", squareSize: "small" },
  alt8: { id: "alt8", label: "ALT (8)", shape: "square", fill: "var(--yellow)", squareSize: "medium" },
  alt16: { id: "alt16", label: "ALT (16)", shape: "square", fill: "var(--yellow)", squareSize: "large" },
};

export function isMethodId(value: string): value is MethodId {
  return (METHOD_IDS as readonly string[]).includes(value);
}
