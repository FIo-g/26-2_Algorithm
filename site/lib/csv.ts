import fs from "node:fs";
import path from "node:path";

export type CsvRow = Record<string, string>;

const cache = new Map<string, CsvRow[]>();

// Quoted fields may contain commas and doubled quotes. Newlines inside quotes are not supported.
export function parseCsv(text: string): CsvRow[] {
  const rows: string[][] = [];
  let row: string[] = [];
  let field = "";
  let quoted = false;
  for (let i = 0; i < text.length; i++) {
    const c = text[i];
    if (quoted) {
      if (c === '"' && text[i + 1] === '"') { field += '"'; i++; }
      else if (c === '"') quoted = false;
      else field += c;
    } else if (c === '"') quoted = true;
    else if (c === ",") { row.push(field); field = ""; }
    else if (c === "\n" || c === "\r") {
      if (c === "\r" && text[i + 1] === "\n") i++;
      row.push(field); field = "";
      if (row.some((v) => v !== "")) rows.push(row);
      row = [];
    } else field += c;
  }
  row.push(field);
  if (row.some((v) => v !== "")) rows.push(row);
  const [header, ...body] = rows;
  return body.map((values) => Object.fromEntries(header.map((h, j) => [h, values[j] ?? ""])));
}

// Results live one level above site/ (the repository root), so resolve from cwd, which is site/ during build.
function resultsPath(name: string): string {
  return path.join(process.cwd(), "..", "results", name);
}

export function resultsExists(name: string): boolean {
  return fs.existsSync(resultsPath(name));
}

export function readResults(name: string): CsvRow[] {
  const hit = cache.get(name);
  if (hit) return hit;
  const rows = parseCsv(fs.readFileSync(resultsPath(name), "utf8"));
  cache.set(name, rows);
  return rows;
}

export function readResultsJson(name: string): unknown {
  return JSON.parse(fs.readFileSync(resultsPath(name), "utf8"));
}
