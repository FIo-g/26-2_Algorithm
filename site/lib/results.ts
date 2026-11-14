// Typed loaders for results/*.csv. Every number shown on the site comes through here.
import fs from "node:fs";
import { readResults, resultsExists, resultsPath } from "./csv";
import { isMethodId, type MethodId } from "./methods";

export const GRAPH_IDS = ["gangnam", "gss", "seoul"] as const;
export type GraphId = (typeof GRAPH_IDS)[number];
export const GRAPH_LABELS: Record<GraphId, string> = {
  gangnam: "Gangnam-gu",
  gss: "Gangnam + Seocho + Songpa",
  seoul: "All of Seoul",
};

// Experiments E3 and re-routing use only these two graphs.
export type ExperimentGraph = "gss" | "seoul";

export const BANDS = ["<3km", "3-10km", ">10km"] as const;
export type Band = (typeof BANDS)[number];
export type RerouteBin = Band | "all";

function num(value: string | undefined, column: string): number {
  const n = Number(value);
  if (value === undefined || value === "" || Number.isNaN(n)) {
    throw new Error(`Expected a number in column ${column}, got "${value ?? ""}"`);
  }
  return n;
}

function optNum(value: string | undefined): number | null {
  return value === undefined || value === "" ? null : Number(value);
}

function bool(value: string | undefined, column: string): boolean {
  if (value === "True") return true;
  if (value === "False") return false;
  throw new Error(`Expected True or False in column ${column}, got "${value ?? ""}"`);
}

function method(value: string | undefined): MethodId {
  if (value === undefined || !isMethodId(value)) throw new Error(`Unknown method id "${value ?? ""}"`);
  return value;
}

function median(values: number[]): number {
  if (values.length === 0) throw new Error("median of an empty list");
  const sorted = [...values].sort((a, b) => a - b);
  const mid = Math.floor(sorted.length / 2);
  return sorted.length % 2 ? sorted[mid] : (sorted[mid - 1] + sorted[mid]) / 2;
}

// graph_table.csv

export type GraphRow = {
  name: GraphId;
  n: number; // intersections
  m: number; // road segments
  vmaxKph: number; // top speed, drawn as a Roundel
  maxspeedMissingFraction: number; // share of roads with no posted limit, as a fraction
};

export function loadGraphTable(): GraphRow[] {
  return readResults("graph_table.csv").map((r) => ({
    name: r.name as GraphId,
    n: num(r.n, "n"),
    m: num(r.m, "m"),
    vmaxKph: num(r.vmax_kph, "vmax_kph"),
    maxspeedMissingFraction: num(r.maxspeed_missing_ratio, "maxspeed_missing_ratio"),
  }));
}

export function graphRow(graph: GraphId): GraphRow {
  const row = loadGraphTable().find((r) => r.name === graph);
  if (!row) throw new Error(`No graph_table.csv row for ${graph}`);
  return row;
}

// Range of the missing-maxspeed share over the three graphs, in percent (for the caveat line).
export function maxspeedMissingRangePercent(): { min: number; max: number } {
  const pct = loadGraphTable().map((r) => r.maxspeedMissingFraction * 100);
  return { min: Math.min(...pct), max: Math.max(...pct) };
}

// e2_summary.csv (one row per graph, band and method; scenario "free", kind "full" for the main results)

export type E2Row = {
  graph: GraphId;
  scenario: string;
  kind: string;
  bin: Band;
  algo: MethodId;
  n: number; // queries in this band
  medianS: number;
  p95S: number;
  medianSettled: number;
  speedup: number; // Dijkstra median time / method median time
  settledRatio: number; // method settled count / Dijkstra settled count
};

export function loadE2Summary(): E2Row[] {
  return readResults("e2_summary.csv").map((r) => ({
    graph: r.graph as GraphId,
    scenario: r.scenario,
    kind: r.kind,
    bin: r.bin as Band,
    algo: method(r.algo),
    n: num(r.n, "n"),
    medianS: num(r.median_s, "median_s"),
    p95S: num(r.p95_s, "p95_s"),
    medianSettled: num(r.median_settled, "median_settled"),
    speedup: num(r.speedup, "speedup"),
    settledRatio: num(r.settled_ratio, "settled_ratio"),
  }));
}

function isMainE2(r: E2Row): boolean {
  return r.scenario === "free" && r.kind === "full";
}

export function getE2(graph: GraphId, bin: Band, algo: MethodId): E2Row {
  const row = loadE2Summary().find((r) => isMainE2(r) && r.graph === graph && r.bin === bin && r.algo === algo);
  if (!row) throw new Error(`No e2_summary.csv row for ${graph} ${bin} ${algo}`);
  return row;
}

// Non-Dijkstra rows that were slower than Dijkstra (speedup below 1), for the caveat line.
export function e2Slowdowns(): E2Row[] {
  return loadE2Summary().filter((r) => isMainE2(r) && r.algo !== "dijkstra" && r.speedup < 1);
}

// e2_tightness.csv: ratio = lower bound / true distance per query (1.0 is perfect).

export type TightnessRow = {
  graph: GraphId;
  qid: number;
  bin: Band;
  algo: MethodId;
  h0: number; // bound at the source
  dist: number; // true distance
  ratio: number;
};

export function loadTightness(): TightnessRow[] {
  return readResults("e2_tightness.csv").map((r) => ({
    graph: r.graph as GraphId,
    qid: num(r.qid, "qid"),
    bin: r.bin as Band,
    algo: method(r.algo),
    h0: num(r.h0, "h0"),
    dist: num(r.dist, "dist"),
    ratio: num(r.ratio, "ratio"),
  }));
}

// Median ratio per graph and method, pooled over all distance bands.
export type MedianTightness = { graph: GraphId; algo: MethodId; medianRatio: number; count: number };

export function medianTightness(): MedianTightness[] {
  const groups = new Map<string, { graph: GraphId; algo: MethodId; values: number[] }>();
  for (const r of loadTightness()) {
    const key = `${r.graph}|${r.algo}`;
    const g = groups.get(key) ?? { graph: r.graph, algo: r.algo, values: [] };
    g.values.push(r.ratio);
    groups.set(key, g);
  }
  return [...groups.values()].map((g) => ({
    graph: g.graph,
    algo: g.algo,
    medianRatio: median(g.values),
    count: g.values.length,
  }));
}

// e2_alt_prep.csv

export type AltPrepRow = {
  graph: GraphId;
  k: number; // landmarks requested
  kActual: number;
  prepS: number; // preprocessing seconds
  nbytes: number;
  memoryMb: number; // nbytes in decimal MB (10^6 bytes)
  breakeven: number; // queries until ALT's preprocessing pays off
  breakevenQueries: number; // breakeven rounded up
};

export function loadAltPrep(): AltPrepRow[] {
  return readResults("e2_alt_prep.csv").map((r) => {
    const breakeven = num(r.breakeven, "breakeven");
    const nbytes = num(r.nbytes, "nbytes");
    return {
      graph: r.graph as GraphId,
      k: num(r.k, "k"),
      kActual: num(r.k_actual, "k_actual"),
      prepS: num(r.prep_s, "prep_s"),
      nbytes,
      memoryMb: nbytes / 1e6,
      breakeven,
      breakevenQueries: Math.ceil(breakeven),
    };
  });
}

// e1.csv: exhaustive search on growing subgraphs. Timed-out queries have timedOut = true.

export type E1Row = {
  targetN: number;
  actualN: number; // intersections in the subgraph
  actualM: number;
  qid: number;
  exTimeS: number; // exhaustive search time (capped at the limit when timed out)
  exPaths: number; // number of simple paths counted
  timedOut: boolean;
  dijTimeS: number;
};

export function loadE1(): E1Row[] {
  return readResults("e1.csv").map((r) => ({
    targetN: num(r.target_n, "target_n"),
    actualN: num(r.actual_n, "actual_n"),
    actualM: num(r.actual_m, "actual_m"),
    qid: num(r.qid, "qid"),
    exTimeS: num(r.ex_time_s, "ex_time_s"),
    exPaths: num(r.ex_paths, "ex_paths"),
    timedOut: bool(r.timed_out, "timed_out"),
    dijTimeS: num(r.dij_time_s, "dij_time_s"),
  }));
}

// The time limit is not a column. It is read from the timed-out rows, which stop at the limit.
export function e1TimeLimitS(): number | null {
  const times = loadE1().filter((r) => r.timedOut).map((r) => r.exTimeS);
  return times.length ? Math.min(...times) : null;
}

// Smallest subgraph size where at least one query timed out, with its counts.
export function e1FirstTimeout(): { n: number; timedOut: number; total: number } | null {
  const rows = loadE1();
  const timeoutSizes = rows.filter((r) => r.timedOut).map((r) => r.actualN);
  if (timeoutSizes.length === 0) return null;
  const n = Math.min(...timeoutSizes);
  const atN = rows.filter((r) => r.actualN === n);
  return { n, timedOut: atN.filter((r) => r.timedOut).length, total: atN.length };
}

// e1_grid.csv: simple corner-to-corner paths in a k by k grid. Larger k rows have no count time.

export type E1GridRow = {
  k: number;
  n: number;
  paths: number;
  source: string; // "counted" (by us) or "OEIS A007764"
  countS: number | null;
};

export function loadE1Grid(): E1GridRow[] {
  return readResults("e1_grid.csv").map((r) => ({
    k: num(r.k, "k"),
    n: num(r.n, "n"),
    paths: num(r.paths, "paths"),
    source: r.source,
    countS: optNum(r.count_s),
  }));
}

// e3_{gss,seoul}_accuracy.csv: wrong answers per scenario and method (E3, synthetic congestion)

export type AccuracyRow = {
  graph: ExperimentGraph;
  scenario: string; // control, random30, synth03, synth08, synth18
  algo: MethodId;
  n: number;
  nWrong: number;
  maxRelErr: number;
};

export function loadAccuracy(graph: ExperimentGraph): AccuracyRow[] {
  return readResults(`e3_${graph}_accuracy.csv`).map((r) => ({
    graph: r.graph as ExperimentGraph,
    scenario: r.scenario,
    algo: method(r.algo),
    n: num(r.n, "n"),
    nWrong: num(r.n_wrong, "n_wrong"),
    maxRelErr: num(r.max_rel_err, "max_rel_err"),
  }));
}

// e3_{gss,seoul}_wastar.csv: weighted A* with factor eps against plain A*

export type WastarRow = {
  graph: ExperimentGraph;
  scenario: string;
  eps: number;
  medianS: number;
  speedupVsAstar: number;
  meanRatio: number;
  maxRatio: number; // worst route length divided by the optimal one
  n: number;
  nRatio: number;
  nUnreachable: number;
};

export function loadWastar(graph: ExperimentGraph): WastarRow[] {
  return readResults(`e3_${graph}_wastar.csv`).map((r) => ({
    graph: r.graph as ExperimentGraph,
    scenario: r.scenario,
    eps: num(r.eps, "eps"),
    medianS: num(r.median_s, "median_s"),
    speedupVsAstar: num(r.speedup_vs_astar, "speedup_vs_astar"),
    meanRatio: num(r.mean_ratio, "mean_ratio"),
    maxRatio: num(r.max_ratio, "max_ratio"),
    n: num(r.n, "n"),
    nRatio: num(r.n_ratio, "n_ratio"),
    nUnreachable: num(r.n_unreachable, "n_unreachable"),
  }));
}

// reroute_gain_{gss,seoul}_summary.csv: saving from re-routing one vehicle. Savings are fractions.

export type RerouteRow = {
  graph: ExperimentGraph;
  scenario: string;
  mode: "depart" | "midway"; // depart: congestion known at departure; midway: starts halfway
  bin: RerouteBin;
  n: number;
  nImproved: number;
  medianSaving: number;
  meanSaving: number;
  p95Saving: number;
  maxSaving: number;
};

export function loadReroute(graph: ExperimentGraph): RerouteRow[] {
  return readResults(`reroute_gain_${graph}_summary.csv`).map((r) => ({
    graph: r.graph as ExperimentGraph,
    scenario: r.scenario,
    mode: r.mode as "depart" | "midway",
    bin: r.bin as RerouteBin,
    n: num(r.n, "n"),
    nImproved: num(r.n_improved, "n_improved"),
    medianSaving: num(r.median_saving, "median_saving"),
    meanSaving: num(r.mean_saving, "mean_saving"),
    p95Saving: num(r.p95_saving, "p95_saving"),
    maxSaving: num(r.max_saving, "max_saving"),
  }));
}

// e4_summary.csv (SUMO). The file may be absent, in which case the loader returns null.

export type E4Row = {
  plan: string;
  level: string;
  strategy: string; // fixed, reroute30, reroute100
  group: string; // "all" for the whole fleet
  seeds: number;
  arrivedPct: number;
  meanTtS: number;
  p95TtS: number;
  meanTtArrivedS: number;
  meanTtMinS: number;
  meanTtMaxS: number;
  changePct: number | null;
};

export function loadE4Summary(): E4Row[] | null {
  if (!resultsExists("e4_summary.csv")) return null;
  return readResults("e4_summary.csv").map((r) => ({
    plan: r.plan,
    level: r.level,
    strategy: r.strategy,
    group: r.group,
    seeds: num(r.seeds, "seeds"),
    arrivedPct: num(r.arrived_pct, "arrived_pct"),
    meanTtS: num(r.mean_tt_s, "mean_tt_s"),
    p95TtS: num(r.p95_tt_s, "p95_tt_s"),
    meanTtArrivedS: num(r.mean_tt_arrived_s, "mean_tt_arrived_s"),
    meanTtMinS: num(r.mean_tt_min_s, "mean_tt_min_s"),
    meanTtMaxS: num(r.mean_tt_max_s, "mean_tt_max_s"),
    changePct: optNum(r.change_pct),
  }));
}

// results/machine.txt: free-form lines, e.g. "Python 3.14.8 (...)" and the CPU name on its own line.

export type MachineInfo = { cpu: string; python: string; start: string | null };

export function loadMachine(): MachineInfo {
  const lines = fs.readFileSync(resultsPath("machine.txt"), "utf8").split(/\r?\n/).map((l) => l.trim()).filter(Boolean);
  const pyLine = lines.find((l) => l.startsWith("Python ")) ?? "";
  const cpuLine = lines.find((l) => !l.includes(":") && !l.startsWith("Python ")) ?? "";
  const startLine = lines.find((l) => l.startsWith("start:")) ?? null;
  return {
    cpu: cpuLine,
    python: pyLine.split(" (")[0],
    start: startLine ? startLine.slice("start:".length).trim() : null,
  };
}

