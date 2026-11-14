// Shape of public/data/demos.json, written by scripts/export_site_data.py.
// Infinite values were written as null (no meeting yet, empty heap).

export type Vertex = { id: number; x: number; y: number };
export type Edge = { u: number; v: number; w: number };

export type PushEvent = { type: "push"; heap: number; key: number; v: number };
export type PopEvent = { type: "pop"; heap: number; key: number; v: number; stale: boolean };
export type LoopEvent = { type: "loop"; top_f: number | null; top_b: number | null; mu: number | null };
export type DemoEvent = PushEvent | PopEvent | LoopEvent;

export type Run = {
  algo: string;
  dist: number;
  path: number[];
  settled: number;
  h: number[] | null;
  events: DemoEvent[];
};

export type Demo = {
  id: string;
  title: string;
  source_test: string;
  vertices: Vertex[];
  edges: Edge[];
  s: number;
  t: number;
  runs: Run[]; // runs[0] is the method itself; grids add a Dijkstra run for comparison
  landmarks?: number[]; // ALT demo only
};
