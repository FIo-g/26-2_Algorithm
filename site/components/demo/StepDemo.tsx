"use client";

import { useState, type KeyboardEvent } from "react";
import { MethodGlyph } from "@/components/sign/MethodGlyph";
import { SubPlate } from "@/components/sign/SubPlate";
import { METHOD_COPY, type MethodCopyId } from "@/lib/method-copy";
import type { MethodId } from "@/lib/methods";
import { DemoView } from "./DemoView";
import type { Demo } from "./types";
import styles from "./StepDemo.module.css";

const TABS: { id: MethodCopyId; method: MethodId; label: string }[] = [
  { id: "dijkstra", method: "dijkstra", label: "Dijkstra" },
  { id: "astar", method: "astar", label: "A*" },
  { id: "bidir", method: "bidir", label: "Bidirectional" },
  { id: "alt", method: "alt4", label: "ALT" },
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
      <p>{METHOD_COPY[tab.id]}</p>
      {demo && <DemoView key={demo.id} demo={demo} />}
    </div>
  );
}
