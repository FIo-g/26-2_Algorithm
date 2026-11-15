import { AccuracyGrid } from "@/components/charts/AccuracyGrid";
import { RerouteGain } from "@/components/charts/RerouteGain";
import { SumoTable, findE4, formatTravelS } from "@/components/charts/SumoTable";
import { GraphPicker } from "@/components/ui/GraphPicker";
import { formatInt, formatMultiplier } from "@/lib/format";
import {
  GRAPH_LABELS,
  loadAccuracy,
  loadE4Manifest,
  loadE4Summary,
  loadReroute,
  timingSpeed,
  type E4Manifest,
  type E4Row,
  type ExperimentGraph,
} from "@/lib/results";

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
      <p>
        {`Exact is not the same as fast: under 08 h congestion, on trips over 10 km in ${GRAPH_LABELS[graph]}, ALT (16) ran at ${formatMultiplier(timingSpeed(graph, "synth08", ">10km", "alt16"), 3)} Dijkstra's speed, because its bounds were built on free-flow times.`}
      </p>
      <p className="small muted">Source: results/e3_{graph}_timing.csv, median time per method.</p>

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

function SumoBlock({ rows, manifest }: { rows: E4Row[]; manifest: E4Manifest }) {
  const seeds = findE4(rows, "W", "medium", "fixed").seeds;
  const wFixed = findE4(rows, "W", "medium", "fixed");
  const w30 = findE4(rows, "W", "medium", "reroute30");
  const w100 = findE4(rows, "W", "medium", "reroute100");
  const hFixed = findE4(rows, "W", "high", "fixed");
  const h30 = findE4(rows, "W", "high", "reroute30");
  const h100 = findE4(rows, "W", "high", "reroute100");
  const equipped = findE4(rows, "W", "medium", "reroute30", "equipped");
  const unequipped = findE4(rows, "W", "medium", "reroute30", "unequipped");

  return (
    <>
      <h3>When many vehicles re-route, it helps only if the fixed routes jam</h3>
      <p>
        {`Simulated in SUMO on a 3 × 3 intersection network in Anyang: SUMO's built-in re-routing (Dijkstra, every ${manifest.periodS} s) on 30% or 100% of vehicles, against fixed routes. Mean of ${seeds} seeds. Signal times and demand are assumed values.`}
      </p>
      <SumoTable rows={rows} plans={manifest.plans} />
      <p>
        {`Normal demand (Webster timing): re-routing only made trips longer, and more re-routing made it worse: ${formatTravelS(wFixed.meanTtS)} s, then ${formatTravelS(w30.meanTtS)} s, then ${formatTravelS(w100.meanTtS)} s.`}
      </p>
      <p>
        {`Heavy demand (Webster timing): with fixed routes only ${formatInt(hFixed.arrivedPct)}% of vehicles arrived, so ${formatTravelS(hFixed.meanTtS)} s is a lower bound; with re-routing every vehicle arrived: ${formatTravelS(h30.meanTtS)} s at 30%, ${formatTravelS(h100.meanTtS)} s at 100%.`}
      </p>
      <p>
        {`In the 30% run under normal demand, re-routing vehicles (${formatTravelS(equipped.meanTtS)} s) were slower than the rest (${formatTravelS(unequipped.meanTtS)} s): we read this as vehicles crowding onto the same fast road.`}
      </p>
      <p>
        Webster timing is computed from the original routes, which may favour fixed routes. The queue-responsive plan is in
        the file but left out here, because it miscounts re-routed vehicles.
      </p>
      <p className="small muted">Source: results/e4_summary.csv, results/e4_manifest.json.</p>
    </>
  );
}

export function CongestionSection() {
  const sumo = loadE4Summary();
  const manifest = loadE4Manifest();
  if (sumo && !manifest) throw new Error("e4_summary.csv exists but e4_manifest.json does not");
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

      {sumo && manifest && <SumoBlock rows={sumo} manifest={manifest} />}
    </section>
  );
}
