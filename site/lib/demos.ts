import { readFileSync } from "node:fs";
import path from "node:path";
import type { Demo } from "@/components/demo/types";

// Read at build time (static page). Server-only: never import this from a client component.
export function loadDemos(): Demo[] {
  const text = readFileSync(path.join(process.cwd(), "public", "data", "demos.json"), "utf8");
  const demos = (JSON.parse(text) as { demos: Demo[] }).demos;
  if (!Array.isArray(demos) || demos.length === 0) throw new Error("demos.json has no demos");
  return demos;
}
