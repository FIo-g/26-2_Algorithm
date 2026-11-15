// Helpers for the results section: distance band wording, the main E2 rows and the ALT claim check.
// Numbers still come from lib/results.ts. Band ids are parsed here, never retyped.
import { BANDS, GRAPH_IDS, loadE2Summary, type E2Row } from "./results";

// Main results only: scenario "free", kind "full".
export function mainE2Rows(): E2Row[] {
  return loadE2Summary().filter((r) => r.scenario === "free" && r.kind === "full");
}

// Parses a band id such as "<3km", "3-10km" or ">10km".
function parseBand(bin: string): { op: string; lo: string; hi: string | undefined } {
  const m = /^(<|>)?(\d+)(?:-(\d+))?km$/.exec(bin);
  if (!m) throw new Error(`Unknown distance band "${bin}"`);
  return { op: m[1] ?? "", lo: m[2], hi: m[3] };
}

// Axis label: "<3 km", "3–10 km", ">10 km".
export function bandAxisLabel(bin: string): string {
  const { op, lo, hi } = parseBand(bin);
  return hi === undefined ? `${op}${lo} km` : `${lo}–${hi} km`;
}

// Sentence form: "under 3 km", "3 to 10 km", "over 10 km".
export function bandPhrase(bin: string): string {
  const { op, lo, hi } = parseBand(bin);
  if (op === "<") return `under ${lo} km`;
  if (op === ">") return `over ${lo} km`;
  return `${lo} to ${hi} km`;
}

// The results heading says ALT looks at the fewest roads and runs fastest. Throws, so the build fails,
// if any non-ALT method beats the best ALT variant on speed or on settled share in some graph and band.
export function checkAltClaim(): void {
  const rows = mainE2Rows();
  for (const graph of GRAPH_IDS) {
    for (const bin of BANDS) {
      const here = rows.filter((r) => r.graph === graph && r.bin === bin);
      const alt = here.filter((r) => r.algo.startsWith("alt"));
      if (alt.length === 0) throw new Error(`No ALT rows for ${graph} ${bin} in e2_summary.csv`);
      const bestSpeedup = Math.max(...alt.map((r) => r.speedup));
      const fewestSettled = Math.min(...alt.map((r) => r.settledRatio));
      for (const r of here.filter((x) => !x.algo.startsWith("alt"))) {
        if (r.speedup > bestSpeedup || r.settledRatio < fewestSettled) {
          throw new Error(`ALT claim fails: ${r.algo} beats ALT on ${graph} ${bin}`);
        }
      }
    }
  }
}
