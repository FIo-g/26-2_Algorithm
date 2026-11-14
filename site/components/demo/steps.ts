import type { DemoEvent, LoopEvent, PopEvent, Run } from "./types";

export const ALGO_LABEL: Record<string, string> = {
  dijkstra: "Dijkstra",
  astar: "A*",
  bidir: "Bidirectional",
  alt: "ALT",
};

// Numbers in narration: whole numbers as they are, otherwise one decimal.
export function num(x: number): string {
  const r = Math.round(x * 10) / 10;
  return Number.isInteger(r) ? String(r) : r.toFixed(1);
}

export type Step = {
  events: DemoEvent[]; // one pop and the pushes and loop tests that follow it
  pop: PopEvent | null;
  narration: string;
  settled: number[]; // non-stale pops so far, in settle order
  loop: LoopEvent | null; // latest stop test so far
};

function sentence(ev: DemoEvent, bidir: boolean): string {
  if (ev.type === "loop") {
    const { top_f: f, top_b: b, mu } = ev;
    if (mu === null || f === null || b === null) return "Stop test: no meeting yet, keep going.";
    const sum = f + b;
    return `Stop test: top_f + top_b = ${num(sum)}, μ = ${num(mu)}. ${sum >= mu ? "So stop." : "Keep going."}`;
  }
  const side = bidir ? (ev.heap === 0 ? "forward" : "backward") : "";
  if (ev.type === "push") return `Push ${ev.v} with key ${num(ev.key)}${side ? ` (${side})` : ""}.`;
  const what = `Pop ${ev.v} (key ${num(ev.key)}${side ? `, ${side}` : ""})`;
  if (ev.stale) return `${what}: already settled, skip.`;
  return `${what}. Settle it.`;
}

// Groups the recorded events into steps. A step starts at each pop; events before the first pop join step 1.
export function buildSteps(run: Run, bidir: boolean): Step[] {
  const groups: DemoEvent[][] = [];
  let current: DemoEvent[] = [];
  for (const ev of run.events) {
    if (ev.type === "pop" && current.some((e) => e.type === "pop")) {
      groups.push(current);
      current = [];
    }
    current.push(ev);
  }
  if (current.length > 0) groups.push(current);

  const steps: Step[] = [];
  const settled: number[] = [];
  let loop: LoopEvent | null = null;
  for (const events of groups) {
    let pop: PopEvent | null = null;
    for (const ev of events) {
      if (ev.type === "pop") {
        pop = pop ?? ev;
        if (!ev.stale) settled.push(ev.v);
      }
      if (ev.type === "loop") loop = ev;
    }
    steps.push({
      events,
      pop,
      narration: events.map((ev) => sentence(ev, bidir)).join(" "),
      settled: [...settled],
      loop,
    });
  }
  return steps;
}

// The stop rule holds when the frontiers together reach the best meeting distance.
export function isStopPoint(loop: LoopEvent | null): boolean {
  return !!loop && loop.mu !== null && loop.top_f !== null && loop.top_b !== null && loop.top_f + loop.top_b >= loop.mu;
}
