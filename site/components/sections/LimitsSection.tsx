import { Plate } from "@/components/sign/Plate";
import { resultsExists } from "@/lib/csv";
import { formatPercentPoints } from "@/lib/format";
import { loadMachine, maxspeedMissingRangePercent } from "@/lib/results";

// Server component. Numbers and machine details come from results/ at build time.
export function LimitsSection() {
  const missing = maxspeedMissingRangePercent();
  const machine = loadMachine();
  const hasE4 = resultsExists("e4_summary.csv");

  return (
    <Plate tone="yellow" id="limits" labelledBy="limits-title">
      <h2 id="limits-title">What this does not show</h2>
      <ul className="sign-list">
        <li>
          Travel times are estimates from road class, not measured speeds. Between{" "}
          {formatPercentPoints(missing.min)} and {formatPercentPoints(missing.max)} of roads have no posted
          speed in OpenStreetMap.
        </li>
        <li>
          Real speeds were collected from the national ITS API and rejected. Its monthly call limit ended
          collection on 2026-11-03, before any morning-peak snapshot existed. Congestion in these results is
          synthetic.
        </li>
        <li>No turn restrictions, traffic signals, or time-dependent travel times.</li>
        <li>
          Stronger preprocessing methods, such as contraction hierarchies and customizable route planning, were
          not implemented.
        </li>
        {!hasE4 && <li>Multi-vehicle re-routing in the SUMO simulator is not part of the frozen results.</li>}
        <li>
          Timings are from one machine ({machine.cpu}, {machine.python}), in pure Python. Settled counts do not
          depend on the machine.
        </li>
      </ul>
      <p className="source">
        Sources: results/graph_table.csv, results/match_decision.md, results/machine.txt
        {hasE4 ? "" : ", results/e4_summary.csv (absent)"}.
      </p>
    </Plate>
  );
}
