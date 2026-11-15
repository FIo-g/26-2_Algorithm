import type { CSSProperties } from "react";
import type { Demo } from "./types";
import styles from "./StepDemo.module.css";

const S = 1000; // viewBox size
const M = 80; // margin
const R = 40; // disc radius
const white: CSSProperties = { fill: "var(--white)", stroke: "var(--white)" };
const yellow: CSSProperties = { fill: "var(--yellow)", stroke: "var(--yellow)" };
const blue: CSSProperties = { fill: "var(--blue)", stroke: "var(--white)" };

type Props = {
  demo: Demo;
  settled: number[];
  current: number | null;
  path: number[];
  landmarks: number[];
  label: string;
};

// Grid of discs. Settled discs fill yellow; unsettled discs are hollow. Edges come in both directions with equal weight, so each pair is drawn once.
export function GridGraph({ demo, settled, current, path, landmarks, label }: Props) {
  const pos = new Map(demo.vertices.map((v) => [v.id, { x: M + v.x * (S - 2 * M), y: M + v.y * (S - 2 * M) }]));
  const done = new Set(settled);
  const edgeKeys = new Set(demo.edges.map((e) => `${e.u}>${e.v}`));
  const onPath = new Set<string>();
  for (let i = 0; i + 1 < path.length; i++) {
    onPath.add(`${path[i]}>${path[i + 1]}`);
    onPath.add(`${path[i + 1]}>${path[i]}`);
  }

  return (
    <svg viewBox={`0 0 ${S} ${S}`} role="img" aria-label={label} className={styles.grid}>
      {demo.edges.map((e) => {
        if (e.u > e.v && edgeKeys.has(`${e.v}>${e.u}`)) return null;
        const a = pos.get(e.u);
        const b = pos.get(e.v);
        if (!a || !b) return null;
        const onP = onPath.has(`${e.u}>${e.v}`);
        return (
          <line
            key={`${e.u}-${e.v}`}
            x1={a.x}
            y1={a.y}
            x2={b.x}
            y2={b.y}
            strokeWidth={onP ? 14 : 6}
            strokeLinecap="round"
            opacity={onP ? 1 : 0.5}
            style={onP ? yellow : white}
          />
        );
      })}
      {landmarks.map((id) => {
        const p = pos.get(id);
        if (!p) return null;
        const side = 2 * R + 24;
        return (
          <rect
            key={`lm-${id}`}
            x={p.x - side / 2}
            y={p.y - side / 2}
            width={side}
            height={side}
            fill="none"
            strokeWidth={6}
            style={white}
          />
        );
      })}
      {demo.vertices.map((v) => {
        const p = pos.get(v.id);
        if (!p) return null;
        const isDone = done.has(v.id);
        const mark = v.id === demo.s ? "S" : v.id === demo.t ? "T" : null;
        return (
          <g key={v.id}>
            {current === v.id && <circle cx={p.x} cy={p.y} r={R + 16} fill="none" strokeWidth={6} style={white} />}
            <circle cx={p.x} cy={p.y} r={R} strokeWidth={isDone ? 0 : 5} style={isDone ? yellow : blue} />
            {mark && (
              <text
                x={p.x}
                y={p.y}
                fontSize={44}
                fontWeight={800}
                textAnchor="middle"
                dominantBaseline="central"
                style={{ fill: isDone ? "var(--black)" : "var(--white)" }}
              >
                {mark}
              </text>
            )}
          </g>
        );
      })}
    </svg>
  );
}
