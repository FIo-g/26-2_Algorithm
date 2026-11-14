import type { CSSProperties } from "react";
import { num } from "./steps";
import type { Demo } from "./types";
import styles from "./StepDemo.module.css";

const R = 24; // vertex radius in viewBox units; the viewBox is 520 wide
const white: CSSProperties = { fill: "var(--white)", stroke: "var(--white)" };
const yellow: CSSProperties = { fill: "var(--yellow)", stroke: "var(--yellow)" };

type Props = { demo: Demo; settled: number[]; current: number | null; path: number[]; label: string };

// Directed graph drawn with arrowheads. Weights sit on a blue tab so the edge line does not cross them.
export function SmallGraph({ demo, settled, current, path, label }: Props) {
  const pos = new Map(demo.vertices.map((v) => [v.id, { x: 40 + v.x * 440, y: 40 + v.y * 260 }]));
  const done = new Set(settled);
  const onPath = new Set<string>();
  for (let i = 0; i + 1 < path.length; i++) onPath.add(`${path[i]}>${path[i + 1]}`);

  return (
    <svg viewBox="0 0 520 340" role="img" aria-label={label} className={styles.svg}>
      <defs>
        {(["edge", "path"] as const).map((kind) => (
          <marker
            key={kind}
            id={`arrow-${demo.id}-${kind}`}
            viewBox="0 0 10 10"
            refX="10"
            refY="5"
            markerWidth="16"
            markerHeight="16"
            markerUnits="userSpaceOnUse"
            orient="auto"
          >
            <path d="M0,0 L10,5 L0,10 z" style={kind === "path" ? yellow : white} />
          </marker>
        ))}
      </defs>
      {demo.edges.map((e) => {
        const a = pos.get(e.u);
        const b = pos.get(e.v);
        if (!a || !b) return null;
        const len = Math.hypot(b.x - a.x, b.y - a.y);
        const ux = (b.x - a.x) / len;
        const uy = (b.y - a.y) / len;
        const onP = onPath.has(`${e.u}>${e.v}`);
        const x1 = a.x + ux * R;
        const y1 = a.y + uy * R;
        const x2 = b.x - ux * (R + 2);
        const y2 = b.y - uy * (R + 2);
        const lx = (x1 + x2) / 2 - uy * 20; // label offset to the left of the edge
        const ly = (y1 + y2) / 2 + ux * 20;
        const text = num(e.w);
        const w = text.length * 15 + 12;
        return (
          <g key={`${e.u}-${e.v}`}>
            <line
              x1={x1}
              y1={y1}
              x2={x2}
              y2={y2}
              strokeWidth={onP ? 7 : 3}
              style={onP ? yellow : white}
              markerEnd={`url(#arrow-${demo.id}-${onP ? "path" : "edge"})`}
            />
            <rect x={lx - w / 2} y={ly - 15} width={w} height={30} style={{ fill: "var(--blue)" }} />
            <text
              x={lx}
              y={ly}
              fontSize={24}
              fontWeight={700}
              textAnchor="middle"
              dominantBaseline="central"
              style={{ fill: "var(--white)" }}
            >
              {text}
            </text>
          </g>
        );
      })}
      {demo.vertices.map((v) => {
        const p = pos.get(v.id);
        if (!p) return null;
        return (
          <g key={v.id}>
            {current === v.id && (
              <circle cx={p.x} cy={p.y} r={R + 8} fill="none" strokeWidth={5} style={white} />
            )}
            <circle cx={p.x} cy={p.y} r={R} style={done.has(v.id) ? yellow : white} />
            <text
              x={p.x}
              y={p.y}
              fontSize={26}
              fontWeight={800}
              textAnchor="middle"
              dominantBaseline="central"
              style={{ fill: "var(--black)" }}
            >
              {v.id}
            </text>
          </g>
        );
      })}
    </svg>
  );
}
