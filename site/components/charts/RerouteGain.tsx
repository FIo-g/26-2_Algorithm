import { scenarioLabel } from "@/components/charts/AccuracyGrid";
import styles from "@/components/charts/congestion.module.css";
import { formatInt, formatPercent } from "@/lib/format";
import type { RerouteBin, RerouteRow } from "@/lib/results";

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

export type RerouteGroup = { title: string; rows: RerouteRow[] };

// Median saving from one re-route, one table per graph. Rows: congestion scenario and timing mode; columns: distance band.
export function RerouteGain({ groups, sources }: { groups: RerouteGroup[]; sources: string[] }) {
  return (
    <>
      {groups.map((group) => (
        <div key={group.title}>
          <h4>{group.title}</h4>
          <div className="table-scroll" role="region" aria-label={`Median saving from one re-route, ${group.title}`} tabIndex={0}>
            <div className={styles.sheet}>
              <table className={styles.table}>
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
                  {distinctPairs(group.rows).map(([scenario, mode]) => (
                    <tr key={`${scenario}-${mode}`}>
                      <th scope="row">
                        {scenarioLabel(scenario)}, {MODE_LABEL[mode]}
                      </th>
                      {BINS.map((b) => {
                        const row = group.rows.find((r) => r.scenario === scenario && r.mode === mode && r.bin === b.bin);
                        if (!row) throw new Error(`No reroute row for ${group.title} ${scenario} ${mode} ${b.bin}`);
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
          </div>
        </div>
      ))}
      <p className="source">Source: {sources.join("; ")}</p>
    </>
  );
}

function distinctPairs(rows: RerouteRow[]): [string, RerouteRow["mode"]][] {
  const seen = new Map<string, [string, RerouteRow["mode"]]>();
  for (const r of rows) seen.set(`${r.scenario}|${r.mode}`, [r.scenario, r.mode]);
  return [...seen.values()];
}
