import styles from "@/components/charts/congestion.module.css";
import { formatMinutesSeconds, formatPercentPoints } from "@/lib/format";
import type { E4Row } from "@/lib/results";

const STRATEGY_ORDER = ["fixed", "reroute30", "reroute100"];

// Mean travel time over all departed vehicles (group "all"), with the change against fixed routes.
export function SumoTable({ rows }: { rows: E4Row[] }) {
  const all = rows.filter((r) => r.group === "all");
  if (all.length === 0) throw new Error("e4_summary.csv has no rows for group all");
  const cases = [...new Map(all.map((r) => [`${r.plan}|${r.level}`, [r.plan, r.level] as const])).values()];
  const seeds = [...new Set(all.map((r) => r.seeds))].sort((a, b) => a - b).join(", ");

  return (
    <>
      <div className="table-scroll" role="region" aria-label="Mean travel time by re-routing share" tabIndex={0}>
        <table className={styles.table}>
          <caption style={{ textAlign: "left", paddingBottom: "0.5rem" }}>
            Mean over all departed vehicles. Seeds per row: {seeds}.
          </caption>
          <thead>
            <tr>
              <th scope="col">Signal plan</th>
              <th scope="col">Demand</th>
              <th scope="col">Strategy</th>
              <th scope="col" className="num">Arrived</th>
              <th scope="col" className="num">Mean travel time</th>
              <th scope="col" className="num">Change vs fixed</th>
            </tr>
          </thead>
          <tbody>
            {cases.flatMap(([plan, level]) =>
              STRATEGY_ORDER.map((strategy) => {
                const r = all.find((x) => x.plan === plan && x.level === level && x.strategy === strategy);
                if (!r) throw new Error(`No e4 row for ${plan} ${level} ${strategy} all`);
                const change =
                  strategy === "fixed" ? "Baseline" : r.changePct === null ? "" : `${r.changePct > 0 ? "+" : ""}${formatPercentPoints(r.changePct, 1)}`;
                return (
                  <tr key={`${plan}-${level}-${strategy}`}>
                    <td data-label="Signal plan">{plan}</td>
                    <td data-label="Demand">{level}</td>
                    <td data-label="Strategy">{strategy}</td>
                    <td className="num" data-label="Arrived">{formatPercentPoints(r.arrivedPct, 1)}</td>
                    <td className="num" data-label="Mean travel time">{formatMinutesSeconds(r.meanTtS)}</td>
                    <td className="num" data-label="Change vs fixed">{change}</td>
                  </tr>
                );
              }),
            )}
          </tbody>
        </table>
      </div>
      <p className="small muted">Source: results/e4_summary.csv</p>
    </>
  );
}
