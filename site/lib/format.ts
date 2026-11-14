// Formatting only. No result values are typed here; callers pass values from lib/results.ts.

const intFormat = new Intl.NumberFormat("en-US");

export function formatInt(value: number): string {
  return intFormat.format(Math.round(value));
}

export function formatDecimal(value: number, digits: number): string {
  return value.toLocaleString("en-US", { minimumFractionDigits: digits, maximumFractionDigits: digits });
}

// Takes a fraction (0.25 becomes "25%").
export function formatPercent(fraction: number, digits = 0): string {
  return `${formatDecimal(fraction * 100, digits)}%`;
}

// Takes a value already in percent (25 becomes "25%").
export function formatPercentPoints(percent: number, digits = 0): string {
  return `${formatDecimal(percent, digits)}%`;
}

export function formatMultiplier(value: number, digits = 1): string {
  return `${formatDecimal(value, digits)}×`;
}

// Durations of a single query: milliseconds below one second, seconds below a minute, then minutes.
export function formatSeconds(seconds: number): string {
  if (seconds < 1) return `${formatDecimal(seconds * 1000, 2)} ms`;
  if (seconds < 60) return `${formatDecimal(seconds, 2)} s`;
  return formatMinutesSeconds(seconds);
}

// Travel times: "12 min 5 s".
export function formatMinutesSeconds(seconds: number): string {
  const total = Math.round(seconds);
  return `${Math.floor(total / 60)} min ${total % 60} s`;
}

// Decimal megabytes (10^6 bytes), the unit README section 3 uses.
export function formatMegabytes(bytes: number, digits = 1): string {
  return `${formatDecimal(bytes / 1e6, digits)} MB`;
}
