import { CautionTriangle } from "@/components/sign/CautionTriangle";
import { MethodGlyph } from "@/components/sign/MethodGlyph";
import { Plate } from "@/components/sign/Plate";
import { StopOctagon } from "@/components/sign/StopOctagon";
import { ExhaustiveChart } from "@/components/charts/ExhaustiveChart";
import { PANEL_METHODS } from "@/components/charts/MethodPanels";
import { SettledChart } from "@/components/charts/SettledChart";
import { SpeedupChart } from "@/components/charts/SpeedupChart";
import { TightnessChart } from "@/components/charts/TightnessChart";
import { formatDecimal, formatInt, formatMegabytes, formatMultiplier, formatPercent, formatSeconds } from "@/lib/format";
import { METHODS } from "@/lib/methods";
import {
  GRAPH_LABELS,
  e1FirstTimeout,
  e1TimeLimitS,
  e2Slowdowns,
  getE2,
  loadAltPrep,
  loadE1,
  loadE1Grid,
  medianTightness,
} from "@/lib/results";
import { bandPhrase, mainE2Rows } from "@/lib/results-section";
import styles from "./ResultsSection.module.css";

// Two digits below 1×, so 0.69× is not read or shown as 0.7×.
const speedText = (v: number) => formatMultiplier(v, v < 1 ? 2 : 1);

// Four signs, one finding each: white (ALT looks at the fewest roads), yellow (slower cases),
// blue (why the bound is loose), white (why not try every path, and ALT's cost).
export function ResultsSection() {
  const e2 = mainE2Rows();
  const lead = getE2("seoul", ">10km", "alt16");
  const slow = e2Slowdowns();
  const slowAStar = slow.some((r) => r.algo === "astar");
  const altPrep = loadAltPrep();
  const grid = loadE1Grid();
  const e1 = loadE1();
  const limit = e1TimeLimitS();
  const firstTimeout = e1FirstTimeout();

  return (
    <>
      <Plate tone="white" id="results" labelledBy="results-title">
        <h2 id="results-title">ALT looks at the fewest roads. A* can lose to Dijkstra on long trips in small maps.</h2>
        <p className={styles.lead}>
          {`On trips ${bandPhrase(">10km")} across the Seoul graph, ${METHODS[lead.algo].label} settled ${formatPercent(lead.settledRatio, 0)} of what Dijkstra settled and ran ${formatMultiplier(lead.speedup)} as fast.`}
        </p>

        <p className={styles.chartTitle}>Share of intersections settled, relative to Dijkstra</p>
        <ul className={styles.key} aria-label="Method key">
          {PANEL_METHODS.map((m) => (
            <li key={m}>
              <MethodGlyph method={m} />
              <span>{METHODS[m].label}</span>
            </li>
          ))}
        </ul>
        <SettledChart rows={e2} />
        <p className={styles.source}>Source: results/e2_summary.csv, column settled_ratio.</p>

        <p className={styles.chartTitle}>Speed relative to Dijkstra</p>
        <SpeedupChart rows={e2} />
        <p className={styles.source}>Source: results/e2_summary.csv, column speedup.</p>
      </Plate>

      {slow.length > 0 && (
        <Plate tone="yellow" labelledBy="slow-title">
          <div className={styles.signHead}>
            <CautionTriangle className={styles.bigCaution} />
            <h2 id="slow-title">Some methods ran slower than Dijkstra</h2>
          </div>
          <p>{`The main results have ${slow.length} cases where a method ran slower than Dijkstra. Each one is listed here.`}</p>
          <div
            className="table-scroll"
            tabIndex={0}
            role="region"
            aria-label="Cases slower than Dijkstra"
          >
            <table>
              <thead>
                <tr>
                  <th scope="col">Method</th>
                  <th scope="col">Trip length</th>
                  <th scope="col">Graph</th>
                  <th scope="col" className="num">Speed</th>
                </tr>
              </thead>
              <tbody>
                {slow.map((r) => (
                  <tr key={`${r.graph}-${r.algo}-${r.bin}`}>
                    <td>{METHODS[r.algo].label}</td>
                    <td>{bandPhrase(r.bin)}</td>
                    <td>{GRAPH_LABELS[r.graph]}</td>
                    <td className="num">{speedText(r.speedup)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          {slowAStar && (
            <p>For A*, the bound removes few intersections on those trips, and computing it costs time at every one.</p>
          )}
        </Plate>
      )}

      <Plate tone="blue" labelledBy="bound-title">
        <h2 id="bound-title">Why the A* bound is loose</h2>
        <p>The straight-line bound assumes the whole trip at the graph top speed.</p>
        <TightnessChart rows={medianTightness()} />
        <p className={styles.source}>
          Source: results/e2_tightness.csv, column ratio, median per graph and method. 1.00 is exact.
        </p>
      </Plate>

      <Plate tone="white" labelledBy="exhaustive-title">
        <div className={styles.signHead}>
          <StopOctagon className={styles.bigStop} />
          <h2 id="exhaustive-title">Why not just try every path?</h2>
        </div>
        {firstTimeout && limit !== null && (
          <div className={styles.caveat}>
            <p>{`At ${formatInt(firstTimeout.n)} intersections, ${firstTimeout.timedOut} of ${firstTimeout.total} queries hit the ${formatDecimal(limit, 0)} second limit.`}</p>
          </div>
        )}
        {limit !== null && <ExhaustiveChart rows={e1} limitS={limit} />}
        <p className={styles.source}>
          Source: results/e1.csv. Timed-out queries are drawn at the limit as open markers.
        </p>

        <div
          className="table-scroll"
          tabIndex={0}
          role="region"
          aria-label="Simple paths in a k by k grid"
        >
          <table>
            <caption className={styles.source}>Simple corner-to-corner paths in a k by k grid</caption>
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

        <h3 className={styles.sub}>ALT is not free</h3>
        <div
          className="table-scroll"
          tabIndex={0}
          role="region"
          aria-label="Preprocessing cost of ALT landmarks"
        >
          <table>
            <caption className={styles.source}>Preprocessing cost of ALT landmarks</caption>
            <thead>
              <tr>
                <th scope="col">Graph</th>
                <th scope="col" className="num">Landmarks</th>
                <th scope="col" className="num">Preprocessing</th>
                <th scope="col" className="num">Memory</th>
                <th scope="col" className="num">Break-even queries</th>
              </tr>
            </thead>
            <tbody>
              {altPrep.map((r) => (
                <tr key={`${r.graph}-${r.k}`}>
                  <th scope="row">{GRAPH_LABELS[r.graph]}</th>
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
      </Plate>
    </>
  );
}
