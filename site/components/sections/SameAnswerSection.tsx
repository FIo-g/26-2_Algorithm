import { CautionTriangle } from "@/components/sign/CautionTriangle";
import { Plate } from "@/components/sign/Plate";
import { Roundel } from "@/components/sign/Roundel";
import { formatInt, formatPercentPoints } from "@/lib/format";
import {
  BANDS,
  GRAPH_IDS,
  GRAPH_LABELS,
  getE2,
  graphRow,
  maxspeedMissingRangePercent,
} from "@/lib/results";
import styles from "./SameAnswerSection.module.css";

// Query counts per graph and band come from e2_summary.csv (the Dijkstra rows, one per query set).
function queryCountsPerBand(): number[] {
  const counts = GRAPH_IDS.map((graph) => BANDS.map((band) => getE2(graph, band, "dijkstra").n));
  const perBand = counts[0][0];
  if (counts.some((row) => row.some((n) => n !== perBand))) {
    throw new Error("Query counts differ across graphs or bands; the copy below assumes one count");
  }
  return counts[0];
}

export function SameAnswerSection() {
  const perBand = queryCountsPerBand();
  const perGraph = perBand.reduce((sum, n) => sum + n, 0);
  const missing = maxspeedMissingRangePercent();

  return (
    <Plate tone="white" id="same-answer" labelledBy="same-answer-title">
      <h2 id="same-answer-title">Every method had to match Dijkstra before we timed it</h2>
      <p>
        Each method&apos;s travel time must equal Dijkstra&apos;s within a relative error of 1e-9, and its path must be
        a real path in the graph. We ran {formatInt(perGraph)} queries per graph, {formatInt(perBand[0])} in each
        distance band, with random seed 42. Only after a method passed did we measure its time.
      </p>
      <p className="source">Query counts: results/e2_summary.csv</p>

      <table aria-label="Three road graphs" className={styles.table}>
        <thead>
          <tr>
            <th scope="col">Graph</th>
            <th scope="col" className="num">Intersections</th>
            <th scope="col" className="num">Road segments</th>
            <th scope="col" className={styles.speedCol}>Top speed</th>
            <th scope="col" className="num">No posted speed</th>
          </tr>
        </thead>
        <tbody>
          {GRAPH_IDS.map((id) => {
            const row = graphRow(id);
            return (
              <tr key={id}>
                <td data-label="Graph">{GRAPH_LABELS[id]}</td>
                <td data-label="Intersections" className="num">{formatInt(row.n)}</td>
                <td data-label="Road segments" className="num">{formatInt(row.m)}</td>
                <td data-label="Top speed" className={styles.speedCol}>
                  <Roundel kph={row.vmaxKph} className={styles.roundel} />
                </td>
                <td data-label="No posted speed" className="num">
                  {formatPercentPoints(row.maxspeedMissingFraction * 100)}
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
      <p className="source">Source: results/graph_table.csv</p>

      <p className="caveat">
        <CautionTriangle />
        <span>
          Caveat: travel times are estimates. Between {formatPercentPoints(missing.min)} and{" "}
          {formatPercentPoints(missing.max)} of roads have no posted speed in OpenStreetMap, so we filled them in from
          the road class.
        </span>
      </p>
    </Plate>
  );
}
