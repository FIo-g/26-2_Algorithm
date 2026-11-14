import path from "node:path";
import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // The build reads ../results/*.csv, so tracing must include the repository root.
  outputFileTracingRoot: path.join(import.meta.dirname, ".."),
};

export default nextConfig;
