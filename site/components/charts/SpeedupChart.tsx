// Chart B: speed relative to Dijkstra. Source: results/e2_summary.csv (speedup).
// Axis ticks round to whole multiples; values read aloud and in tooltips keep two digits, so 0.69× is not "1×".
import type { E2Row, GraphId } from "@/lib/results";
import { formatMultiplier } from "@/lib/format";
import { MethodPanels, PANEL_METHODS } from "./MethodPanels";

export function SpeedupChart({ rows, graph }: { rows: E2Row[]; graph: GraphId }) {
  return (
    <MethodPanels
      rows={rows.filter((r) => PANEL_METHODS.includes(r.algo))}
      graph={graph}
      value={(r) => r.speedup}
      tickFormat={(v) => formatMultiplier(v, 0)}
      valueFormat={(v) => formatMultiplier(v, 2)}
      yTitle="Speed, × Dijkstra"
      reference={1}
      referenceLabel="Dijkstra"
    />
  );
}
