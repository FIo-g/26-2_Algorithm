import { isMethodId, type MethodId } from "@/lib/methods";

export type GraphKey = "gangnam" | "seoul";
type Label = { ko: string; en: string };
export type HeroAlgo = { id: MethodId; settled: number; time_s: number; path: number[] };
export type HeroGraph = {
  n: number;
  e: number;
  aspect: number;
  net: string;
  trace: string;
  query: { s: number; t: number; sLabel: Label; tLabel: Label };
  algos: HeroAlgo[];
};

export type HeroData = {
  key: GraphKey;
  graph: HeroGraph;
  order: MethodId[]; // trace order in the file, also the order of the method plates
  positions: Float32Array; // x, y per vertex, both 0..1
  edges: Uint32Array; // vertex index pairs, two entries per segment
  traces: Record<string, Uint32Array>; // vertex indices in settle order, by method id
  algos: Record<string, HeroAlgo>;
};

// Rank of a segment with an end that was never settled. Larger than any clock value.
export const NEVER = 1e9;

async function getJson(url: string, signal: AbortSignal): Promise<unknown> {
  const res = await fetch(url, { signal });
  if (!res.ok) throw new Error(`${url}: ${res.status}`);
  return res.json();
}

async function getBytes(url: string, signal: AbortSignal): Promise<ArrayBuffer> {
  const res = await fetch(url, { signal });
  if (!res.ok) throw new Error(`${url}: ${res.status}`);
  return res.arrayBuffer();
}

// shortcut: typed-array views assume a little-endian host, as every current browser is. Upgrade if a big-endian target ever matters.
function parseNet(buf: ArrayBuffer) {
  const head = new DataView(buf);
  const n = head.getUint32(0, true);
  const e = head.getUint32(4, true);
  return {
    n,
    e,
    positions: new Float32Array(buf, 8, 2 * n),
    edges: new Uint32Array(buf, 8 + 8 * n, 2 * e),
  };
}

function parseTraces(buf: ArrayBuffer, order: MethodId[]): Record<string, Uint32Array> {
  const head = new DataView(buf);
  const out: Record<string, Uint32Array> = {};
  let offset = 0;
  for (const id of order) {
    const count = head.getUint32(offset, true);
    out[id] = new Uint32Array(buf, offset + 4, count);
    offset += 4 + 4 * count;
  }
  return out;
}

export async function loadHero(key: GraphKey, signal: AbortSignal): Promise<HeroData> {
  const file = (await getJson("/data/hero.json", signal)) as { graphs: Record<string, HeroGraph>; order: string[] };
  const graph = file.graphs[key];
  const order = file.order.filter(isMethodId);
  const [netBuf, traceBuf] = await Promise.all([
    getBytes(`/data/${graph.net}`, signal),
    getBytes(`/data/${graph.trace}`, signal),
  ]);
  const net = parseNet(netBuf);
  const traces = parseTraces(traceBuf, order);
  if (net.n !== graph.n || net.e !== graph.e) throw new Error("net file does not match hero.json");
  const algos: Record<string, HeroAlgo> = {};
  for (const a of graph.algos) {
    algos[a.id] = a;
    if (traces[a.id]?.length !== a.settled) throw new Error(`trace of ${a.id} does not match hero.json`);
  }
  if (!algos.dijkstra || !order.includes("dijkstra")) throw new Error("hero.json has no dijkstra run");
  return { key, graph, order, positions: net.positions, edges: net.edges, traces, algos };
}

// One rank per line vertex, so a segment's two ends carry the same value. A segment is lit once the clock has
// passed the later of its two settle indices. A segment with an unsettled end gets NEVER.
export function segmentRanks(edges: Uint32Array, n: number, trace: Uint32Array): Float32Array {
  const settleIndex = new Float32Array(n).fill(NEVER);
  for (let i = 0; i < trace.length; i++) settleIndex[trace[i]] = i;
  const ranks = new Float32Array(edges.length);
  for (let i = 0; i < edges.length; i += 2) {
    ranks[i] = ranks[i + 1] = Math.max(settleIndex[edges[i]], settleIndex[edges[i + 1]]);
  }
  return ranks;
}
