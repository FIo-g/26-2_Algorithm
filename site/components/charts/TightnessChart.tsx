// Chart C: median ratio of the first lower bound to the true travel time, per graph. 1.00 is exact.
// Source: results/e2_tightness.csv (ratio, pooled over bands). One small panel per graph, same grid as charts A and B.
import { Roundel } from "@/components/sign/Roundel";
import { formatDecimal, formatInt } from "@/lib/format";
import { METHODS, type MethodId } from "@/lib/methods";
import { GRAPH_IDS, GRAPH_LABELS, graphRow, type MedianTightness } from "@/lib/results";
import { AxisX, Marker, linearScale, type Tick } from "./primitives";
import styles from "./charts.module.css";
import panel from "./panel.module.css";

const TIGHTNESS_METHODS: MethodId[] = ["astar", "alt4", "alt8", "alt16"];

// viewBox is the width a card's drawing shows at on a 375 px phone (card padding inside the 319 px content).
const W = 304;
const BAR_H = 22;
const STEP = 34;
const TOP = 6;
const PLOT_LEFT = 96;
const PLOT_RIGHT = 264;
const AXIS_Y = TOP + TIGHTNESS_METHODS.length * STEP;
const H = AXIS_Y + 50;

export function TightnessChart({ rows }: { rows: MedianTightness[] }) {
  const x = linearScale([0, 1], [PLOT_LEFT, PLOT_RIGHT]);
  const ticks: Tick[] = [0, 0.25, 0.5, 0.75, 1].map((v) => ({ pos: x(v), label: formatDecimal(v, 2) }));

  return (
    <>
      <div className={styles.panels}>
        {GRAPH_IDS.map((graph) => {
          const bars = TIGHTNESS_METHODS.map((algo) => {
            const r = rows.find((row) => row.graph === graph && row.algo === algo);
            if (!r) throw new Error(`Missing ${graph} ${algo} in e2_tightness.csv`);
            return r;
          });
          const sorted = [...bars].sort((a, b) => b.medianRatio - a.medianRatio);
          const closest = sorted[0];
          const furthest = sorted[sorted.length - 1];
          const label =
            `Median ratio of the first lower bound to the true travel time, ${GRAPH_LABELS[graph]}. ` +
            `Closest to 1: ${METHODS[closest.algo].label} at ${formatDecimal(closest.medianRatio, 2)}. ` +
            `Furthest: ${METHODS[furthest.algo].label} at ${formatDecimal(furthest.medianRatio, 2)}.`;

          return (
            <figure key={graph} className={`chart ${styles.figure} ${panel.card}`}>
              <figcaption className={styles.groupHead}>
                <h4 className={styles.groupTitle}>{GRAPH_LABELS[graph]}</h4>
                <Roundel kph={graphRow(graph).vmaxKph} className={panel.roundelLarge} />
                <span className={styles.groupNote}>top speed in the graph</span>
              </figcaption>
              <svg className={`${panel.svg} ${panel.w304}`} viewBox={`0 0 ${W} ${H}`} role="img" aria-label={label}>
                {bars.map((r, i) => {
                  const yy = TOP + i * STEP;
                  return (
                    <g key={r.algo}>
                      <Marker method={r.algo} x={12} y={yy + BAR_H / 2} size={13} />
                      <text x={24} y={yy + BAR_H / 2} dominantBaseline="central" fontSize={13} fontWeight={700}>
                        {METHODS[r.algo].label}
                      </text>
                      <rect
                        x={PLOT_LEFT}
                        y={yy}
                        width={x(r.medianRatio) - PLOT_LEFT}
                        height={BAR_H}
                        style={{ fill: METHODS[r.algo].fill }}
                        className={panel.bar}
                      />
                      <text
                        x={x(r.medianRatio) + 6}
                        y={yy + BAR_H / 2}
                        dominantBaseline="central"
                        fontSize={13}
                        fontWeight={700}
                      >
                        {formatDecimal(r.medianRatio, 2)}
                      </text>
                    </g>
                  );
                })}
                <AxisX y={AXIS_Y} left={PLOT_LEFT} right={PLOT_RIGHT} ticks={ticks} title="Lower bound / true time" />
              </svg>
            </figure>
          );
        })}
      </div>
      <div className="visually-hidden">
        <table>
          <caption>Median lower bound / true time, by graph</caption>
          <thead>
            <tr>
              <th scope="col">Graph</th>
              <th scope="col">Method</th>
              <th scope="col">Median ratio</th>
              <th scope="col">Queries</th>
            </tr>
          </thead>
          <tbody>
            {rows
              .filter((r) => TIGHTNESS_METHODS.includes(r.algo))
              .map((r) => (
                <tr key={`${r.graph}-${r.algo}`}>
                  <td>{GRAPH_LABELS[r.graph]}</td>
                  <td>{METHODS[r.algo].label}</td>
                  <td>{formatDecimal(r.medianRatio, 2)}</td>
                  <td>{formatInt(r.count)}</td>
                </tr>
              ))}
          </tbody>
        </table>
      </div>
    </>
  );
}
