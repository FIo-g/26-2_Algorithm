// Helpers for the results section: distance band wording and the main E2 rows.
// Numbers still come from lib/results.ts. Band ids are parsed here, never retyped.
import { loadE2Summary, type E2Row } from "./results";

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
