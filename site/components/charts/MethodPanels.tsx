// Shared line panels for charts A and B: one panel per graph, x is the trip-length band, one line per method.
import { BANDS, GRAPH_IDS, GRAPH_LABELS, type E2Row } from "@/lib/results";
import { METHODS, type MethodId } from "@/lib/methods";
import { bandAxisLabel, bandPhrase } from "@/lib/results-section";
import { AxisX, AxisY, DirectLabel, Marker, linearScale, linearTicks, spreadLabels, type Tick } from "./primitives";
import styles from "./charts.module.css";
import panel from "./panel.module.css";

export const PANEL_METHODS: MethodId[] = ["astar", "bidir", "alt4", "alt8", "alt16"];

// viewBox is the width a panel shows at on a 375 px phone, so the 13 px text is not scaled.
const W = 320;
const H = 250;
const LEFT = 72;
const PLOT_RIGHT = 204;
const LABEL_X = 214; // direct labels sit right of the plot
const BRACKET_X = 208;
const TOP = 12;
const BOTTOM = 200;
const LABEL_GAP = 15;
const LABEL_MAX_Y = BOTTOM - 8; // keeps the lowest label off the x-axis tick labels
const GROUP_SHIFT = 8; // if an ALT label has to move this far, the three ALT labels become one bracketed group

type Props = {
  rows: E2Row[]; // main results, methods to draw (the reference is not a row)
  value: (r: E2Row) => number;
  tickFormat: (v: number) => string; // axis ticks and the reference label: short
  valueFormat: (v: number) => string; // screen-reader text, tooltips: exact
  yTitle: string;
  reference: number; // Dijkstra reference, drawn at this value
  referenceLabel: string;
};

// Trip-length tick labels are short ("<3", "3–10", ">10"); the axis title says km.
const bandTick = (bin: string) => bandAxisLabel(bin).replace(" km", "");

// Three panels share one y scale, so the same height means the same value in every panel.
export function MethodPanels({ rows, value, tickFormat, valueFormat, yTitle, reference, referenceLabel }: Props) {
  const top = Math.max(reference, ...rows.map(value));
  const y = linearScale([0, top], [BOTTOM, TOP]);
  const x = linearScale([0, BANDS.length - 1], [LEFT + 16, PLOT_RIGHT - 16]);
  const yTicks: Tick[] = linearTicks([0, top], 4).map((v) => ({ pos: y(v), label: tickFormat(v) }));
  const xTicks: Tick[] = BANDS.map((bin, i) => ({ pos: x(i), label: bandTick(bin) }));
  const refY = y(reference);

  return (
    <>
      <div className={styles.panels}>
        {GRAPH_IDS.map((graph) => {
          const panelRows = rows.filter((r) => r.graph === graph);
          const series = PANEL_METHODS.map((algo) => {
            const pts = BANDS.map((bin, i) => {
              const r = panelRows.find((p) => p.algo === algo && p.bin === bin);
              if (!r) throw new Error(`Missing ${graph} ${algo} ${bin} in e2_summary.csv`);
              return { r, x: x(i), y: y(value(r)) };
            });
            return { algo, pts, endY: pts[pts.length - 1].y };
          });

          // End labels: one per line if they stay near their line ends; otherwise the three ALT lines share one bracketed label.
          const altIdx = series.flatMap((s, i) => (s.algo.startsWith("alt") ? [i] : []));
          const single = spreadLabels([...series.map((s) => s.endY), refY], LABEL_GAP, LABEL_MAX_Y);
          const shift = Math.max(...altIdx.map((i) => Math.abs(single[i] - series[i].endY)));
          const grouped = shift > GROUP_SHIFT;
          const plain = series.map((_, i) => i).filter((i) => !altIdx.includes(i));
          const altMeanY = altIdx.reduce((sum, i) => sum + series[i].endY, 0) / altIdx.length;
          const groupedYs = spreadLabels(
            [...plain.map((i) => series[i].endY), altMeanY, refY],
            LABEL_GAP,
            LABEL_MAX_Y,
          );
          const labelY = (i: number) => (grouped ? groupedYs[plain.indexOf(i)] : single[i]);
          const altGroupY = groupedYs[plain.length];
          const refLabelY = grouped ? groupedYs[plain.length + 1] : single[series.length];
          const altTop = Math.min(...altIdx.map((i) => series[i].endY));
          const altBottom = Math.max(...altIdx.map((i) => series[i].endY));

          const sorted = [...panelRows].sort((a, b) => value(a) - value(b));
          const lo = sorted[0];
          const hi = sorted[sorted.length - 1];
          const label =
            `${GRAPH_LABELS[graph]}. ${yTitle}. ` +
            `Lowest: ${METHODS[lo.algo].label} at ${valueFormat(value(lo))} on trips ${bandPhrase(lo.bin)}. ` +
            `Highest: ${METHODS[hi.algo].label} at ${valueFormat(value(hi))} on trips ${bandPhrase(hi.bin)}. ` +
            `Reference: ${referenceLabel} at ${valueFormat(reference)}.`;

          return (
            <figure key={graph} className={`chart ${styles.figure}`}>
              <figcaption className={styles.caption}>{GRAPH_LABELS[graph]}</figcaption>
              <svg className={`${panel.svg} ${panel.w320}`} viewBox={`0 0 ${W} ${H}`} role="img" aria-label={label}>
                <AxisY x={LEFT} top={TOP} bottom={BOTTOM} ticks={yTicks} title={yTitle} gridTo={PLOT_RIGHT} titleOffset={52} />
                <AxisX y={BOTTOM} left={LEFT} right={PLOT_RIGHT} ticks={xTicks} title="Trip length, km" />
                <line x1={LEFT} x2={PLOT_RIGHT} y1={refY} y2={refY} className={panel.reference} />
                {series.map((s) => {
                  const points = s.pts.map((p) => `${p.x},${p.y}`).join(" ");
                  return (
                    <g key={s.algo}>
                      {s.algo.startsWith("alt") && <polyline className={panel.casing} points={points} />}
                      <polyline className={panel.line} style={{ stroke: METHODS[s.algo].fill }} points={points} />
                      {s.pts.map((p, j) => (
                        <g key={BANDS[j]}>
                          <title>{`${METHODS[s.algo].label}, trips ${bandPhrase(BANDS[j])}: ${valueFormat(value(p.r))}`}</title>
                          <Marker method={s.algo} x={p.x} y={p.y} size={13} />
                        </g>
                      ))}
                    </g>
                  );
                })}
                {series.map((s, i) =>
                  grouped && altIdx.includes(i) ? null : (
                    <DirectLabel key={s.algo} x={LABEL_X} y={labelY(i)} text={METHODS[s.algo].label} />
                  ),
                )}
                {grouped && (
                  <>
                    <path
                      className={panel.bracket}
                      d={`M ${BRACKET_X + 4} ${altTop} H ${BRACKET_X} V ${altBottom} H ${BRACKET_X + 4}`}
                    />
                    <DirectLabel x={LABEL_X} y={altGroupY} text="ALT (4/8/16)" />
                  </>
                )}
                <DirectLabel x={LABEL_X} y={refLabelY} text={`${referenceLabel} ${tickFormat(reference)}`} />
              </svg>
            </figure>
          );
        })}
      </div>
      <div className="visually-hidden">
        <table>
          <caption>{`${yTitle}, by graph and trip length`}</caption>
          <thead>
            <tr>
              <th scope="col">Graph</th>
              <th scope="col">Trip length</th>
              <th scope="col">Method</th>
              <th scope="col">Value</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((r) => (
              <tr key={`${r.graph}-${r.algo}-${r.bin}`}>
                <td>{GRAPH_LABELS[r.graph]}</td>
                <td>{bandPhrase(r.bin)}</td>
                <td>{METHODS[r.algo].label}</td>
                <td>{valueFormat(value(r))}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </>
  );
}
