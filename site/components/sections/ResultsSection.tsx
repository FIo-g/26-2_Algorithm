import { MethodGlyph } from "@/components/sign/MethodGlyph";
import { Roundel } from "@/components/sign/Roundel";
import { StopOctagon } from "@/components/sign/StopOctagon";
import { ExhaustiveChart } from "@/components/charts/ExhaustiveChart";
import { PANEL_METHODS } from "@/components/charts/MethodPanels";
import { SettledChart } from "@/components/charts/SettledChart";
import { SpeedupChart } from "@/components/charts/SpeedupChart";
import { TightnessChart } from "@/components/charts/TightnessChart";
import { GraphPicker } from "@/components/ui/GraphPicker";
import { formatDecimal, formatInt, formatMegabytes, formatMultiplier, formatPercent, formatSeconds } from "@/lib/format";
import { METHODS } from "@/lib/methods";
import {
  GRAPH_IDS,
  GRAPH_LABELS,
  e1FirstTimeout,
  e1TimeLimitS,
  getE2,
  graphRow,
  loadAltPrep,
  loadE1,
  loadE1Grid,
  medianTightness,
  type AltPrepRow,
  type E2Row,
  type GraphId,
  type MedianTightness,
} from "@/lib/results";
import { bandPhrase, checkAltClaim, mainE2Rows } from "@/lib/results-section";
import styles from "./ResultsSection.module.css";

// Everything the reader sees for one graph. Only the picker shows one at a time.
function GraphPanel({
  graph,
  e2,
  altPrep,
  tightness,
}: {
  graph: GraphId;
  e2: E2Row[];
  altPrep: AltPrepRow[];
  tightness: MedianTightness[];
}) {
  const name = GRAPH_LABELS[graph];
  const row = graphRow(graph);
  const lead = getE2(graph, ">10km", "alt16");

  return (
    <div>
      <dl className={styles.facts}>
        <div>
          <dt>Intersections</dt>
          <dd>{formatInt(row.n)}</dd>
        </div>
        <div>
          <dt>Road segments</dt>
          <dd>{formatInt(row.m)}</dd>
        </div>
        <div>
          <dt>Top speed</dt>
          <dd>
            <Roundel kph={row.vmaxKph} />
          </dd>
        </div>
      </dl>
      <p className={styles.source}>Source: results/graph_table.csv.</p>

      <p className={styles.lead}>
        {`On trips ${bandPhrase(">10km")} in ${name}, ${METHODS[lead.algo].label} settled ${formatPercent(lead.settledRatio, 0)} of what Dijkstra settled and ran ${formatMultiplier(lead.speedup)} as fast.`}
      </p>

      <ul className={styles.key} aria-label="Method key">
        {PANEL_METHODS.map((m) => (
          <li key={m}>
            <MethodGlyph method={m} />
            <span>{METHODS[m].label}</span>
          </li>
        ))}
      </ul>
      <div className={styles.pair}>
        <div>
          <p className={styles.chartTitle}>Share of intersections settled, relative to Dijkstra</p>
          <SettledChart rows={e2} graph={graph} />
          <p className={styles.source}>Source: results/e2_summary.csv, column settled_ratio.</p>
        </div>
        <div>
          <p className={styles.chartTitle}>Speed relative to Dijkstra</p>
          <SpeedupChart rows={e2} graph={graph} />
          <p className={styles.source}>Source: results/e2_summary.csv, column speedup.</p>
        </div>
      </div>

      <div className={styles.pair}>
        <div>
        <h3>How close each bound gets to the true time</h3>
        <p>The straight-line bound assumes the whole trip at the graph top speed.</p>
        <TightnessChart rows={tightness} graph={graph} />
        <p className={styles.source}>
          Source: results/e2_tightness.csv, column ratio, median per method. 1.00 is exact.
        </p>

        </div>
        <div>
        <h3>What ALT&apos;s preprocessing costs</h3>
        <div className="table-scroll" tabIndex={0} role="region" aria-label={`Preprocessing cost of ALT landmarks, ${name}`}>
          <table>
            <thead>
              <tr>
                <th scope="col" className="num">Landmarks</th>
                <th scope="col" className="num">Preprocessing</th>
                <th scope="col" className="num">Memory</th>
                <th scope="col" className="num">Break-even queries</th>
              </tr>
            </thead>
            <tbody>
              {altPrep
                .filter((r) => r.graph === graph)
                .map((r) => (
                  <tr key={r.k}>
                    <td className="num">{formatInt(r.k)}</td>
                    <td className="num">{formatSeconds(r.prepS)}</td>
                    <td className="num">{formatMegabytes(r.nbytes)}</td>
                    <td className="num">{formatInt(r.breakevenQueries)}</td>
                  </tr>
                ))}
            </tbody>
          </table>
        </div>
        <p className={styles.source}>Source: results/e2_alt_prep.csv. Break-even is rounded up to whole queries.</p>
        </div>
      </div>
    </div>
  );
}

export function ResultsSection() {
  checkAltClaim();
  const e2 = mainE2Rows();
  const altPrep = loadAltPrep();
  const tightness = medianTightness();
  const grid = loadE1Grid();
  const e1 = loadE1();
  const limit = e1TimeLimitS();
  const firstTimeout = e1FirstTimeout();
  const panels = Object.fromEntries(
    GRAPH_IDS.map((g) => [g, <GraphPanel key={g} graph={g} e2={e2} altPrep={altPrep} tightness={tightness} />]),
  );

  return (
    <section id="results" className="flow-section" aria-labelledby="results-title">
      <h2 id="results-title">ALT looks at the fewest roads and runs fastest</h2>

      <GraphPicker
        name="results"
        label="Road graph"
        options={(["seoul", "gss", "gangnam"] as const).map((id) => ({ id, label: GRAPH_LABELS[id] }))}
        initial="seoul"
        panels={panels}
      />

      <div className={styles.signHead}>
        <StopOctagon className={styles.bigStop} />
        <h3>Why not just try every path?</h3>
      </div>
      {firstTimeout && limit !== null && (
        <p>{`At ${formatInt(firstTimeout.n)} intersections, ${firstTimeout.timedOut} of ${firstTimeout.total} queries hit the ${formatDecimal(limit, 0)} second limit.`}</p>
      )}
      {limit !== null && <ExhaustiveChart rows={e1} limitS={limit} />}
      <p className={styles.source}>
        Source: results/e1.csv. Timed-out queries are drawn at the limit as open markers.
      </p>

      <details className={styles.details}>
        <summary>Simple paths in a k by k grid</summary>
        <div className="table-scroll" tabIndex={0} role="region" aria-label="Simple paths in a k by k grid">
          <table>
            <thead>
              <tr>
                <th scope="col">Grid</th>
                <th scope="col" className="num">Intersections</th>
                <th scope="col" className="num">Simple paths</th>
                <th scope="col">Source of count</th>
                <th scope="col" className="num">Count time</th>
              </tr>
            </thead>
            <tbody>
              {grid.map((r) => (
                <tr key={r.k}>
                  <th scope="row">{`${formatInt(r.k)} × ${formatInt(r.k)}`}</th>
                  <td className="num">{formatInt(r.n)}</td>
                  <td className="num">{formatInt(r.paths)}</td>
                  <td>{r.source === "counted" ? "Counted by us" : r.source}</td>
                  <td className="num">{r.countS === null ? "not timed" : formatSeconds(r.countS)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <p className={styles.source}>Source: results/e1_grid.csv.</p>
      </details>
    </section>
  );
}
