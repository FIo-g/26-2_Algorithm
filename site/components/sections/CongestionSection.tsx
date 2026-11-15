import { AccuracyGrid } from "@/components/charts/AccuracyGrid";
import { RerouteGain } from "@/components/charts/RerouteGain";
import { SumoTable } from "@/components/charts/SumoTable";
import { GraphPicker } from "@/components/ui/GraphPicker";
import { formatInt } from "@/lib/format";
import { GRAPH_LABELS, loadAccuracy, loadE4Summary, loadReroute, type ExperimentGraph } from "@/lib/results";

const GRAPHS: ExperimentGraph[] = ["seoul", "gss"];

function CongestionPanel({ graph }: { graph: ExperimentGraph }) {
  const accuracy = loadAccuracy(graph);
  const queries = accuracy[0]?.n;
  if (queries === undefined) throw new Error(`e3 accuracy file for ${graph} has no rows`);

  return (
    <>
      <h3>Wrong answers out of {formatInt(queries)} queries</h3>
      <p>
        Control: we made some roads faster than the bound assumes. The bound is no longer a lower bound, and A* and ALT
        return wrong routes.
      </p>
      <AccuracyGrid
        title={GRAPH_LABELS[graph]}
        rows={accuracy}
        source={`results/e3_${graph}_accuracy.csv`}
      />

      <h3>Does re-routing help one driver?</h3>
      <p className="small muted">One vehicle, synthetic congestion snapshot.</p>
      <p>
        Saving is the share of the trip&apos;s travel time cut by re-planning, compared with keeping the original route
        under the same congestion.
      </p>
      <RerouteGain graph={graph} rows={loadReroute(graph)} source={`results/reroute_gain_${graph}_summary.csv`} />
    </>
  );
}

export function CongestionSection() {
  const sumo = loadE4Summary();
  const panels = Object.fromEntries(GRAPHS.map((graph) => [graph, <CongestionPanel key={graph} graph={graph} />]));

  return (
    <section id="congestion" className="flow-section" aria-labelledby="congestion-title">
      <h2 id="congestion-title">Slower roads never break the answer. Faster roads do.</h2>
      <p>
        The bounds were built on free-flow travel times. When congestion only makes edges slower, a lower bound stays a
        lower bound, so no preprocessing is redone.
      </p>
      <p>
        The congestion scenarios are synthetic: multipliers by road class for 03, 08 and 18 h, and a random 30% of edges
        slowed.
      </p>

      <GraphPicker
        name="congestion-graph"
        label="Road graph for congestion results"
        options={GRAPHS.map((id) => ({ id, label: GRAPH_LABELS[id] }))}
        initial="seoul"
        panels={panels}
      />

      {sumo && (
        <>
          <h3>What happens when many drivers re-route (SUMO)</h3>
          <p>
            Simulated in SUMO, not measured traffic.
          </p>
          <SumoTable rows={sumo} />
        </>
      )}
    </section>
  );
}
