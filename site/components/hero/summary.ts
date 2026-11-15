import { readFileSync } from "node:fs";
import path from "node:path";
import { formatInt, formatMinutesSeconds } from "@/lib/format";
import { isMethodId, type MethodId } from "@/lib/methods";
import { samePath, share, type GraphKey, type HeroGraph } from "./data";

export const HERO_GRAPHS: GraphKey[] = ["seoul", "gangnam"];

type HeroFile = { graphs: Record<GraphKey, HeroGraph>; order: string[] };

// Read at build time (static page). Server-only: never import this from a client component.
export function loadHeroFile(): { graphs: HeroFile["graphs"]; order: MethodId[] } {
  const text = readFileSync(path.join(process.cwd(), "public", "data", "hero.json"), "utf8");
  const file = JSON.parse(text) as HeroFile;
  const order = file.order.filter(isMethodId);
  if (order.length === 0 || !order.includes("dijkstra")) throw new Error("hero.json has no dijkstra run");
  return { graphs: file.graphs, order };
}

// The numbers sentence of one method's card, for one graph.
export function cardFacts(graph: HeroGraph, id: MethodId): string {
  const algo = graph.algos.find((a) => a.id === id);
  const base = graph.algos.find((a) => a.id === "dijkstra");
  if (!algo || !base) throw new Error(`hero.json has no ${id} run`);
  if (id === "dijkstra") {
    return `Here it settled ${formatInt(algo.settled)} of ${formatInt(graph.n)} intersections before it reached ${graph.query.tLabel.en}.`;
  }
  const same = samePath(algo, base)
    ? ` Same route, same estimated travel time (${formatMinutesSeconds(algo.time_s)}).`
    : "";
  return `Here it settled ${formatInt(algo.settled)} intersections: ${share(algo.settled, base.settled)} of what Dijkstra settled.${same}`;
}
