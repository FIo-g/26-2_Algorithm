import { formatInt } from "@/lib/format";
import { BANDS, GRAPH_IDS, getE2 } from "@/lib/results";

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

  return (
    <section id="same-answer" className="flow-section" aria-labelledby="same-answer-title">
      <h2 id="same-answer-title">Every method had to match Dijkstra before we timed it</h2>
      <p>
        Each method&apos;s travel time must equal Dijkstra&apos;s within a relative error of 1e-9, and its path must be
        a real path in the graph. We ran {formatInt(perGraph)} queries per graph, {formatInt(perBand[0])} in each
        distance band, with random seed 42. Only after a method passed did we measure its time.
      </p>
      <p className="source">Query counts: results/e2_summary.csv</p>
    </section>
  );
}
