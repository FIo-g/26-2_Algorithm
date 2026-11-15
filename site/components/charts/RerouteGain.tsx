import { scenarioLabel } from "@/components/charts/AccuracyGrid";
import styles from "@/components/charts/congestion.module.css";
import { formatInt, formatPercent } from "@/lib/format";
import { GRAPH_LABELS, type ExperimentGraph, type RerouteBin, type RerouteRow } from "@/lib/results";

const BINS: { bin: RerouteBin; label: string }[] = [
  { bin: "<3km", label: "Under 3 km" },
  { bin: "3-10km", label: "3 to 10 km" },
  { bin: ">10km", label: "Over 10 km" },
  { bin: "all", label: "All trips" },
];

const MODE_LABEL: Record<RerouteRow["mode"], string> = {
  depart: "known at departure",
  midway: "starts halfway",
};

// Median saving from one re-route for one graph. Rows: congestion scenario and timing mode; columns: distance band.
export function RerouteGain({ graph, rows, source }: { graph: ExperimentGraph; rows: RerouteRow[]; source: string }) {
  return (
    <>
      <div className="table-scroll" role="region" aria-label={`Median saving from one re-route, ${GRAPH_LABELS[graph]}`} tabIndex={0}>
        <table className={styles.table}>
          <caption style={{ textAlign: "left", fontWeight: 800, paddingBottom: "0.5rem" }}>{GRAPH_LABELS[graph]}</caption>
          <thead>
            <tr>
              <th scope="col">Congestion and timing</th>
              {BINS.map((b) => (
                <th scope="col" key={b.bin} className="num">
                  {b.label}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {distinctPairs(rows).map(([scenario, mode]) => (
              <tr key={`${scenario}-${mode}`}>
                <th scope="row">
                  {scenarioLabel(scenario)}, {MODE_LABEL[mode]}
                </th>
                {BINS.map((b) => {
                  const row = rows.find((r) => r.scenario === scenario && r.mode === mode && r.bin === b.bin);
                  if (!row) throw new Error(`No reroute row for ${graph} ${scenario} ${mode} ${b.bin}`);
                  return (
                    <td key={b.bin} className="num" data-label={b.label}>
                      <span className={styles.cell}>
                        <strong className={styles.median}>{formatPercent(row.medianSaving, 1)}</strong>
                        <span className={styles.count}>
                          {formatInt(row.nImproved)} of {formatInt(row.n)} improved
                        </span>
                      </span>
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <p className="source">Source: {source}</p>
    </>
  );
}

function distinctPairs(rows: RerouteRow[]): [string, RerouteRow["mode"]][] {
  const seen = new Map<string, [string, RerouteRow["mode"]]>();
  for (const r of rows) seen.set(`${r.scenario}|${r.mode}`, [r.scenario, r.mode]);
  return [...seen.values()];
}
