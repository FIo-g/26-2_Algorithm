"use client";

import { useState, type KeyboardEvent } from "react";
import { MethodGlyph } from "@/components/sign/MethodGlyph";
import { SubPlate } from "@/components/sign/SubPlate";
import type { MethodId } from "@/lib/methods";
import { DemoView } from "./DemoView";
import type { Demo } from "./types";
import styles from "./StepDemo.module.css";

const TABS: { id: string; method: MethodId; label: string; text: string }[] = [
  {
    id: "dijkstra",
    method: "dijkstra",
    label: "Dijkstra",
    text: "Always settles the closest unsettled intersection. Never looks at a settled one again.",
  },
  {
    id: "astar",
    method: "astar",
    label: "A*",
    text: "Adds a lower bound on the remaining time (straight-line distance divided by the top speed), so it leans toward the destination.",
  },
  {
    id: "bidir",
    method: "bidir",
    label: "Bidirectional",
    text: "Searches from both ends and stops when the two frontiers together cannot beat the best route found.",
  },
  {
    id: "alt",
    method: "alt4",
    label: "ALT",
    text: "A* with a tighter bound built from precomputed distances to a few landmarks and the triangle inequality.",
  },
];

const KEY_STEP: Record<string, number> = { ArrowRight: 1, ArrowDown: 1, ArrowLeft: -1, ArrowUp: -1 };

// Method chooser (a radio group, arrow keys move) and the step demo for the chosen method.
export function StepDemo({ demos }: { demos: Demo[] }) {
  const [selected, setSelected] = useState("dijkstra");
  const tab = TABS.find((t) => t.id === selected) ?? TABS[0];
  const demo = demos.find((d) => d.id === tab.id);

  function onKeyDown(event: KeyboardEvent<HTMLDivElement>) {
    if (!(event.key in KEY_STEP)) return;
    event.preventDefault();
    const at = TABS.indexOf(tab);
    const next = TABS[(at + KEY_STEP[event.key] + TABS.length) % TABS.length];
    setSelected(next.id);
    document.getElementById(`method-${next.id}`)?.focus();
  }

  return (
    <div>
      <div role="radiogroup" aria-label="Method" className={styles.tabs} onKeyDown={onKeyDown}>
        {TABS.map((t) => (
          <SubPlate
            key={t.id}
            id={`method-${t.id}`}
            role="radio"
            checked={t.id === tab.id}
            tabIndex={t.id === tab.id ? 0 : -1}
            onClick={() => setSelected(t.id)}
          >
            <MethodGlyph method={t.method} />
            {t.label}
          </SubPlate>
        ))}
      </div>
      <p>{tab.text}</p>
      {demo && <DemoView key={demo.id} demo={demo} />}
    </div>
  );
}
