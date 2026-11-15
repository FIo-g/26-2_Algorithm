import { formatPercent } from "@/lib/format";
import { maxspeedMissingRange } from "@/lib/results";

// Estimated speeds, synthetic congestion and the one-vehicle re-routing model are disclosed here.
export function LimitsSection() {
  const range = maxspeedMissingRange();
  const low = formatPercent(range.min, 0);
  const high = formatPercent(range.max, 0);

  return (
    <section id="limits" className="flow-section" aria-labelledby="limits-title">
      <h2 id="limits-title">Assumptions and limits</h2>
      <ul className="sign-list">
        <li>
          Travel times are estimates. OpenStreetMap has no posted speed on {low} to {high} of these roads, so each of those roads
          gets a representative speed for its road class.
        </li>
        <li>
          Congestion is synthetic. Real speeds from the national ITS API were collected but not used in these results.
        </li>
        <li>
          Re-routing is modelled for one vehicle on a fixed congestion snapshot, so it does not change the traffic around
          it.
        </li>
      </ul>
      <p className="small muted">Source: results/graph_table.csv, column maxspeed_missing_ratio; results/match_decision.md.</p>
    </section>
  );
}
