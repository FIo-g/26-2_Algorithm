import { AccuracyGrid } from "@/components/charts/AccuracyGrid";
import { RerouteGain, type RerouteGroup } from "@/components/charts/RerouteGain";
import { SumoTable } from "@/components/charts/SumoTable";
import { CautionTriangle } from "@/components/sign/CautionTriangle";
import { Plate } from "@/components/sign/Plate";
import { formatInt } from "@/lib/format";
import { GRAPH_LABELS, loadAccuracy, loadE4Summary, loadReroute, type ExperimentGraph } from "@/lib/results";

const GRAPHS: ExperimentGraph[] = ["seoul", "gss"];

export function CongestionSection() {
  const accuracy = GRAPHS.map((graph) => ({ graph, rows: loadAccuracy(graph) }));
  const queries = accuracy[0].rows[0]?.n;
  if (queries === undefined) throw new Error("e3 accuracy file has no rows");

  const reroute: RerouteGroup[] = GRAPHS.map((graph) => ({ title: GRAPH_LABELS[graph], rows: loadReroute(graph) }));
  const rerouteSources = GRAPHS.map((graph) => `results/reroute_gain_${graph}_summary.csv`);

  const sumo = loadE4Summary();

  return (
    <>
      <Plate tone="white" id="congestion" labelledBy="congestion-title">
        <h2 id="congestion-title">Slower roads never break the answer. Faster roads do.</h2>
        <p>
          The bounds were built on free-flow travel times. When congestion only makes edges slower, a lower bound stays a
          lower bound, so no preprocessing is redone.
        </p>
        <p className="caveat">
          <CautionTriangle />
          <span>
            Caveat: congestion here is synthetic. Multipliers by road class for 03, 08 and 18 h, and a random 30% of edges
            slowed.
          </span>
        </p>

        <h3>Wrong answers out of {formatInt(queries)} queries</h3>
        <p>
          Control: we made some roads faster than the bound assumes. The bound is no longer a lower bound, and A* and ALT
          return wrong routes.
        </p>
        {accuracy.map(({ graph, rows }) => (
          <AccuracyGrid
            key={graph}
            title={GRAPH_LABELS[graph]}
            rows={rows}
            source={`results/e3_${graph}_accuracy.csv`}
          />
        ))}
      </Plate>

      <Plate tone="blue" labelledBy="reroute-title">
        <h2 id="reroute-title">Does re-routing help one driver?</h2>
        <p className="small muted">One vehicle, synthetic congestion snapshot.</p>
        <p>
          Saving is the share of the trip&apos;s travel time cut by re-planning, compared with keeping the original route
          under the same congestion.
        </p>
        <RerouteGain groups={reroute} sources={rerouteSources} />
      </Plate>

      {sumo && (
        <Plate tone="white" labelledBy="sumo-title">
          <h2 id="sumo-title">What happens when many drivers re-route (SUMO)</h2>
          <p>
            Simulated in SUMO, not measured traffic. Where Arrived is below 100%, the mean still counts every departed
            vehicle, so it is a lower bound.
          </p>
          <SumoTable rows={sumo} />
        </Plate>
      )}
    </>
  );
}
