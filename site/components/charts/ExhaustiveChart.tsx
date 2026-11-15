// Chart D: exhaustive search time per query against subgraph size, log time axis. Source: results/e1.csv.
// Timed-out queries are drawn at the limit as open markers.
// Two drawings of the same data: a narrow one (viewBox 320, shown on phones) and a wide one (viewBox 704, shown from 900 px).
// Each viewBox equals its CSS width, so the 13 px text is not scaled.
import { formatDecimal, formatInt, formatSeconds } from "@/lib/format";
import type { E1Row } from "@/lib/results";
import { AxisX, AxisY, DirectLabel, linearScale, linearTicks, logScale, logTicks, type Tick } from "./primitives";
import styles from "./charts.module.css";
import panel from "./panel.module.css";

const H = 270;
const LEFT = 86; // room for the widest tick label and the rotated title
const TOP = 12;
const BOTTOM = 220;

// Seconds below one second are shown in milliseconds.
function formatTick(s: number): string {
  return s >= 1 ? `${formatDecimal(s, 0)} s` : `${Number((s * 1000).toPrecision(3))} ms`;
}

function ScatterSvg({ W, rows, limitS, className }: { W: number; rows: E1Row[]; limitS: number; className: string }) {
  const PLOT_RIGHT = W - 14;
  const timedOut = rows.filter((r) => r.timedOut);
  const minTimedN = Math.min(...timedOut.map((r) => r.actualN));
  const minT = Math.min(...rows.map((r) => r.exTimeS));
  const lo = 10 ** Math.floor(Math.log10(minT));
  const y = logScale([lo, limitS], [BOTTOM, TOP]);
  const maxN = Math.max(...rows.map((r) => r.actualN));
  const x = linearScale([0, maxN], [LEFT, PLOT_RIGHT]);

  const yTicks: Tick[] = logTicks([lo, limitS])
    .filter((v) => v >= lo && v <= limitS)
    .map((v) => ({ pos: y(v), label: formatTick(v) }));
  const xTicks: Tick[] = linearTicks([0, maxN], 5).map((v) => ({ pos: x(v), label: formatInt(v) }));

  const label =
    `Exhaustive search time per query, log scale. ${timedOut.length} of ${rows.length} queries hit the ` +
    `${formatDecimal(limitS, 0)} second limit, the smallest at ${minTimedN} intersections.`;

  return (
    <svg className={`${panel.svg} ${className}`} viewBox={`0 0 ${W} ${H}`} role="img" aria-label={label}>
      <AxisY x={LEFT} top={TOP} bottom={BOTTOM} ticks={yTicks} title="Search time, log scale" gridTo={PLOT_RIGHT} titleOffset={72} />
      <AxisX y={BOTTOM} left={LEFT} right={PLOT_RIGHT} ticks={xTicks} title="Intersections in the subgraph" />
      <line x1={LEFT} x2={PLOT_RIGHT} y1={y(limitS)} y2={y(limitS)} className={panel.limit} />
      <DirectLabel x={LEFT + 8} y={TOP + 14} text={`Limit ${formatDecimal(limitS, 0)} s`} />
      {rows.map((r) => {
        const cx = x(r.actualN);
        const cy = y(Math.min(r.exTimeS, limitS));
        const note = `${r.actualN} intersections, query ${r.qid}: ${r.timedOut ? "timed out" : formatSeconds(r.exTimeS)}`;
        return r.timedOut ? (
          <circle key={`${r.actualN}-${r.qid}`} cx={cx} cy={cy} r={4} fill="var(--white)" stroke="var(--black)" strokeWidth={2}>
            <title>{note}</title>
          </circle>
        ) : (
          <circle key={`${r.actualN}-${r.qid}`} cx={cx} cy={cy} r={3} fill="var(--black)">
            <title>{note}</title>
          </circle>
        );
      })}
    </svg>
  );
}

export function ExhaustiveChart({ rows, limitS }: { rows: E1Row[]; limitS: number }) {
  const sizes = [...new Set(rows.map((r) => r.actualN))].sort((a, b) => a - b);

  return (
    <>
      <figure className={`chart ${styles.figure}`}>
        <div className={panel.narrowOnly}>
          <ScatterSvg W={320} rows={rows} limitS={limitS} className={panel.w320} />
        </div>
        <div className={panel.wideOnly}>
          <ScatterSvg W={704} rows={rows} limitS={limitS} className={panel.w704} />
        </div>
      </figure>
      <div className="visually-hidden">
        <table>
          <caption>Exhaustive search per subgraph size</caption>
          <thead>
            <tr>
              <th scope="col">Intersections</th>
              <th scope="col">Queries</th>
              <th scope="col">Timed out</th>
              <th scope="col">Slowest query</th>
            </tr>
          </thead>
          <tbody>
            {sizes.map((n) => {
              const group = rows.filter((r) => r.actualN === n);
              const slowest = Math.max(...group.map((r) => r.exTimeS));
              return (
                <tr key={n}>
                  <td>{formatInt(n)}</td>
                  <td>{formatInt(group.length)}</td>
                  <td>{formatInt(group.filter((r) => r.timedOut).length)}</td>
                  <td>{formatSeconds(slowest)}</td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </>
  );
}
