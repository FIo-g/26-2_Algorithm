import styles from "@/components/charts/congestion.module.css";
import { formatDecimal, formatInt, formatPercentPoints } from "@/lib/format";
import type { E4Row } from "@/lib/results";

// Rows in the deck's order. Plan A is left out: its controller miscounts re-routed vehicles.
export const SUMO_CASES = [
  { plan: "W", level: "medium" },
  { plan: "B", level: "medium" },
  { plan: "W", level: "high" },
];

const STRATEGIES = ["fixed", "reroute30", "reroute100"] as const;
const COLUMNS: Record<(typeof STRATEGIES)[number], string> = {
  fixed: "Fixed routes",
  reroute30: "30% re-route",
  reroute100: "100% re-route",
};
const DEMAND: Record<string, string> = { medium: "normal", high: "heavy" };

export function findE4(rows: E4Row[], plan: string, level: string, strategy: string, group = "all"): E4Row {
  const r = rows.find((x) => x.plan === plan && x.level === level && x.strategy === strategy && x.group === group);
  if (!r) throw new Error(`No e4 row for ${plan} ${level} ${strategy} ${group}`);
  return r;
}

// Whole seconds, except an exact half keeps one decimal (449.5 s).
export function formatTravelS(seconds: number): string {
  return seconds % 1 === 0.5 ? formatDecimal(seconds, 1) : formatInt(seconds);
}

// Two decimals from 99 up, so 99.75% cannot read as 100%.
export function formatArrived(pct: number): string {
  if (pct === 100) return "100%";
  return `${formatDecimal(pct, pct >= 99 ? 2 : 1)}%`;
}

function cellFor(r: E4Row, fixed: E4Row): { value: string; note: string } {
  const bound = r.arrivedPct < 100;
  const value = `${bound ? "at least " : ""}${formatTravelS(r.meanTtS)} s`;
  if (bound) return { value, note: `${formatArrived(r.arrivedPct)} arrived` };
  if (r.strategy === "fixed") return { value, note: "" };
  if (fixed.arrivedPct < 100) return { value, note: "100% arrived" };
  if (r.changePct === null) throw new Error(`No change_pct for ${r.plan} ${r.level} ${r.strategy}`);
  return { value, note: `${r.changePct > 0 ? "+" : ""}${formatPercentPoints(r.changePct, 1)}` };
}

function caseLabel(plans: Record<string, string>, plan: string, level: string): string {
  const name = plans[plan];
  if (!name) throw new Error(`e4_manifest.json has no plan name for ${plan}`);
  const cap = name.charAt(0).toUpperCase() + name.slice(1);
  // "Webster" alone does not say it is a signal plan; the offset name already does.
  const head = plan === "W" ? `${cap} timing` : cap;
  return `${head}, ${DEMAND[level]} demand`;
}

// Mean travel time over all departed vehicles (group "all"), with the change against fixed routes.
export function SumoTable({ rows, plans }: { rows: E4Row[]; plans: Record<string, string> }) {
  return (
    <div className="table-scroll" role="region" aria-label="Mean travel time by re-routing share" tabIndex={0} style={{ marginBottom: "1.5rem" }}>
      <table className={`${styles.table} ${styles.sumo}`}>
        <caption style={{ textAlign: "left", paddingBottom: "0.5rem" }}>Mean travel time over all departed vehicles.</caption>
        <thead>
          <tr>
            <th scope="col">Case</th>
            {STRATEGIES.map((s) => (
              <th scope="col" className="num" key={s}>
                {COLUMNS[s]}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {SUMO_CASES.map(({ plan, level }) => {
            const fixed = findE4(rows, plan, level, "fixed");
            return (
              <tr key={`${plan}-${level}`}>
                <th scope="row">{caseLabel(plans, plan, level)}</th>
                {STRATEGIES.map((s) => {
                  const c = cellFor(findE4(rows, plan, level, s), fixed);
                  return (
                    <td className="num" data-label={COLUMNS[s]} key={s}>
                      {c.value}
                      {c.note && <span className={styles.count}>{c.note}</span>}
                    </td>
                  );
                })}
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
