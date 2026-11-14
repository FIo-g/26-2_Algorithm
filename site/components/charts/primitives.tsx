// Chart building blocks. Pure functions and server-rendered SVG only. No chart library.
import { GlyphShape } from "@/components/sign/MethodGlyph";
import { METHODS, type MethodId } from "@/lib/methods";

export type Scale = ((value: number) => number) & { domain: [number, number]; range: [number, number] };

// Linear map from domain to pixel range. A flat domain maps to the middle of the range.
export function linearScale(domain: [number, number], range: [number, number]): Scale {
  const [d0, d1] = domain;
  const [r0, r1] = range;
  const fn = (v: number) => (d1 === d0 ? (r0 + r1) / 2 : r0 + ((v - d0) / (d1 - d0)) * (r1 - r0));
  return Object.assign(fn, { domain, range });
}

// Log10 map. Values must be positive.
export function logScale(domain: [number, number], range: [number, number]): Scale {
  if (domain[0] <= 0 || domain[1] <= 0) throw new Error("logScale needs a positive domain");
  const lin = linearScale([Math.log10(domain[0]), Math.log10(domain[1])], range);
  return Object.assign((v: number) => lin(Math.log10(v)), { domain, range });
}

// Round tick values at 1, 2 or 5 times a power of ten, about `count` of them across the domain.
export function linearTicks(domain: [number, number], count = 5): number[] {
  const [lo, hi] = domain[0] <= domain[1] ? domain : [domain[1], domain[0]];
  const raw = (hi - lo) / Math.max(1, count);
  const magnitude = 10 ** Math.floor(Math.log10(raw || 1));
  const step = [1, 2, 5, 10].map((m) => m * magnitude).find((s) => s >= raw) ?? 10 * magnitude;
  const first = Math.ceil(lo / step) * step;
  const ticks: number[] = [];
  for (let v = first; v <= hi + step / 1e9; v += step) ticks.push(Number(v.toFixed(12)));
  return ticks;
}

// Powers of ten covering the domain.
export function logTicks(domain: [number, number]): number[] {
  const lo = Math.floor(Math.log10(domain[0]));
  const hi = Math.ceil(Math.log10(domain[1]));
  const ticks: number[] = [];
  for (let e = lo; e <= hi; e++) ticks.push(10 ** e);
  return ticks;
}

// Pushes labels apart vertically so none overlap. Output is in the same order as the input.
// With maxY, the lowest label is held at or above maxY and the others are pushed up to make room.
// Relaxation: neighbours that overlap are pushed apart by half the overlap each, so a cluster grows around
// its own centre instead of all sliding one way. shortcut: fixed 200 passes, enough for a few labels per panel.
export function spreadLabels(positions: number[], minGap: number, maxY = Infinity): number[] {
  const order = positions.map((p, i) => ({ p, i })).sort((a, b) => a.p - b.p);
  const ys = order.map(({ p }) => Math.min(p, maxY));
  for (let pass = 0; pass < 200; pass++) {
    for (let k = 1; k < ys.length; k++) {
      const overlap = ys[k - 1] + minGap - ys[k];
      if (overlap > 0) {
        ys[k - 1] -= overlap / 2;
        ys[k] += overlap / 2;
      }
    }
    for (let k = 0; k < ys.length; k++) ys[k] = Math.min(ys[k], maxY);
  }
  const out = new Array<number>(positions.length);
  order.forEach(({ i }, k) => (out[i] = ys[k]));
  return out;
}

export type Tick = { pos: number; label: string };

// Y axis: a black 2 px line at x, with ticks to its left and a rotated title. Gridlines optional.
export function AxisY({
  x,
  top,
  bottom,
  ticks,
  title,
  gridTo,
  titleOffset = 44,
}: {
  x: number;
  top: number;
  bottom: number;
  ticks: Tick[];
  title: string;
  gridTo?: number; // draw hairline gridlines out to this x
  titleOffset?: number; // distance from the axis to the rotated title; wider tick labels need more
}) {
  return (
    <g className="axis-y">
      <line x1={x} x2={x} y1={top} y2={bottom} className="chart-axis" />
      {ticks.map((t) => (
        <g key={`${t.pos}-${t.label}`}>
          {gridTo !== undefined && <line x1={x} x2={gridTo} y1={t.pos} y2={t.pos} className="chart-hairline" />}
          <line x1={x - 5} x2={x} y1={t.pos} y2={t.pos} className="chart-axis" />
          <text x={x - 8} y={t.pos} textAnchor="end" dominantBaseline="central" fontSize={13}>
            {t.label}
          </text>
        </g>
      ))}
      <text
        transform={`translate(${x - titleOffset} ${(top + bottom) / 2}) rotate(-90)`}
        textAnchor="middle"
        fontSize={13}
        fontWeight={700}
      >
        {title}
      </text>
    </g>
  );
}

// X axis: a black 2 px line at y, with tick labels below and a title under them.
export function AxisX({
  y,
  left,
  right,
  ticks,
  title,
}: {
  y: number;
  left: number;
  right: number;
  ticks: Tick[];
  title: string;
}) {
  return (
    <g className="axis-x">
      <line x1={left} x2={right} y1={y} y2={y} className="chart-axis" />
      {ticks.map((t) => (
        <g key={`${t.pos}-${t.label}`}>
          <line x1={t.pos} x2={t.pos} y1={y} y2={y + 5} className="chart-axis" />
          <text x={t.pos} y={y + 18} textAnchor="middle" fontSize={13}>
            {t.label}
          </text>
        </g>
      ))}
      <text x={(left + right) / 2} y={y + 40} textAnchor="middle" fontSize={13} fontWeight={700}>
        {title}
      </text>
    </g>
  );
}

// Marker for a method, drawn with the same geometry as MethodGlyph. (x, y) is the centre, size in px.
export function Marker({ method, x, y, size = 12 }: { method: MethodId; x: number; y: number; size?: number }) {
  return (
    <g transform={`translate(${x - size / 2} ${y - size / 2}) scale(${size / 24})`} data-method={METHODS[method].label}>
      <g stroke="currentColor" strokeWidth={2} strokeLinejoin="round">
        <GlyphShape method={method} />
      </g>
    </g>
  );
}

// Direct label at the end of a line, in the series text colour. Name the series in the text itself.
export function DirectLabel({
  x,
  y,
  text,
  anchor = "start",
}: {
  x: number;
  y: number;
  text: string;
  anchor?: "start" | "end";
}) {
  return (
    <text x={x} y={y} textAnchor={anchor} dominantBaseline="central" fontSize={13} fontWeight={700}>
      {text}
    </text>
  );
}
