import path from "node:path";
import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // The build reads ../results/*.csv, so tracing must include the repository root.
  outputFileTracingRoot: path.join(import.meta.dirname, ".."),
  // STATIC_EXPORT=1 writes plain files to out/, for hosts that cannot read ../results at build.
  output: process.env.STATIC_EXPORT === "1" ? "export" : undefined,
};

export default nextConfig;
