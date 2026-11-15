// Chart A: share of intersections settled, relative to Dijkstra. Source: results/e2_summary.csv (settled_ratio).
import type { E2Row, GraphId } from "@/lib/results";
import { formatPercent } from "@/lib/format";
import { MethodPanels, PANEL_METHODS } from "./MethodPanels";

export function SettledChart({ rows, graph }: { rows: E2Row[]; graph: GraphId }) {
  return (
    <MethodPanels
      rows={rows.filter((r) => PANEL_METHODS.includes(r.algo))}
      graph={graph}
      value={(r) => r.settledRatio}
      tickFormat={(v) => formatPercent(v, 0)}
      valueFormat={(v) => formatPercent(v, 0)}
      yTitle="Settled, % of Dijkstra"
      reference={1}
      referenceLabel="Dijkstra"
    />
  );
}
