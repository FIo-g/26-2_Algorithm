import { MethodGlyph } from "@/components/sign/MethodGlyph";
import styles from "@/components/charts/congestion.module.css";
import { formatInt } from "@/lib/format";
import { METHOD_IDS, METHODS, type MethodId } from "@/lib/methods";
import type { AccuracyRow } from "@/lib/results";

// Row order, top to bottom. Scenarios not listed here go last, in file order.
const SCENARIO_ORDER = ["control", "random30", "synth03", "synth08", "synth18"];

// Plain-language row label from a scenario id, e.g. "synth08" is congestion at 08 h.
export function scenarioLabel(id: string): string {
  if (id === "control") return "Control (some roads made faster)";
  const random = /^random(\d+)$/.exec(id);
  if (random) return `Random ${random[1]}% of edges slowed`;
  const hour = /^synth(\d+)$/.exec(id);
  // 03 h is in the file, but its profile is all 1.0 in src/routing/congestion.py: free flow.
  if (hour && hour[1] === "03") return "03 h (all multipliers 1.0, same as free flow)";
  if (hour) return `${hour[1]} h congestion`;
  return id;
}

const rank = (s: string) => {
  const i = SCENARIO_ORDER.indexOf(s);
  return i === -1 ? SCENARIO_ORDER.length : i;
};

// Zero cells stay quiet. Non-zero cells are red and carry the number, so colour is not the only cue.
const quiet = { color: "var(--steel-ink)" };
const wrong = { background: "var(--red)", color: "var(--white)", fontWeight: 800 };

// Scenario by method grid of wrong answers. A real table, so the numbers are read by screen readers too.
export function AccuracyGrid({ title, rows, source }: { title: string; rows: AccuracyRow[]; source: string }) {
  if (rows.length === 0) throw new Error(`AccuracyGrid "${title}" has no rows`);
  const scenarios = [...new Set(rows.map((r) => r.scenario))].sort((a, b) => rank(a) - rank(b));

  const at = (scenario: string, algo: MethodId): AccuracyRow => {
    const row = rows.find((r) => r.scenario === scenario && r.algo === algo);
    if (!row) throw new Error(`No accuracy row for ${scenario} ${algo}`);
    return row;
  };

  return (
    <>
      <div className="table-scroll" role="region" aria-label={title} tabIndex={0}>
        <table className={styles.table}>
          <caption style={{ textAlign: "left", fontWeight: 800, paddingBottom: "0.5rem" }}>{title}</caption>
          <thead>
            <tr>
              <th scope="col">Scenario</th>
              {METHOD_IDS.map((id) => (
                <th scope="col" key={id} className="num">
                  <span style={{ display: "inline-flex", alignItems: "center", gap: "0.3em", whiteSpace: "nowrap" }}>
                    <MethodGlyph method={id} />
                    {METHODS[id].label}
                  </span>
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {scenarios.map((s) => (
              <tr key={s}>
                <th scope="row">{scenarioLabel(s)}</th>
                {METHOD_IDS.map((id) => {
                  const row = at(s, id);
                  return (
                    <td key={id} className="num" data-label={METHODS[id].label} style={row.nWrong > 0 ? wrong : quiet}>
                      {formatInt(row.nWrong)}
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <p className="small muted">Source: {source}</p>
    </>
  );
}
