"use client";

import { useEffect, useRef, useState, type KeyboardEvent, type ReactNode } from "react";
import { SubPlate } from "@/components/sign/SubPlate";
import styles from "./GraphPicker.module.css";

export type GraphOption = { id: string; label: string };

export type GraphPickerProps = {
  name: string; // unique per picker, prefixes element ids
  label: string; // aria-label of the radio group
  options: GraphOption[];
  initial: string;
  panels: Record<string, ReactNode>; // rendered on the server, one per option id
};

const KEY_STEP: Record<string, number> = { ArrowRight: 1, ArrowDown: 1, ArrowLeft: -1, ArrowUp: -1 };

// Switches server-rendered content by road graph. Every panel is in the HTML; unselected ones are hidden.
// shortcut: the choice is local state, not in the URL, so a reload returns to the initial graph.
export function GraphPicker({ name, label, options, initial, panels }: GraphPickerProps) {
  const [selected, setSelected] = useState(initial);
  const bar = useRef<HTMLDivElement>(null);

  // Below 900px the row scrolls sideways. Scroll the row itself: scrollIntoView would also move the page.
  useEffect(() => {
    const row = bar.current;
    const plate = row?.querySelector<HTMLElement>('[aria-checked="true"]');
    if (!row || !plate) return;
    const start = plate.offsetLeft;
    const end = start + plate.offsetWidth;
    if (start < row.scrollLeft) row.scrollLeft = start;
    else if (end > row.scrollLeft + row.clientWidth) row.scrollLeft = end - row.clientWidth;
  }, [selected]);

  function onKeyDown(event: KeyboardEvent<HTMLDivElement>) {
    if (!(event.key in KEY_STEP)) return;
    event.preventDefault();
    const at = options.findIndex((o) => o.id === selected);
    const next = options[(at + KEY_STEP[event.key] + options.length) % options.length];
    setSelected(next.id);
    // preventScroll: moving focus must not scroll the page; the effect above scrolls the row.
    document.getElementById(`${name}-radio-${next.id}`)?.focus({ preventScroll: true });
  }

  return (
    <div>
      <div ref={bar} role="radiogroup" aria-label={label} className={styles.bar} onKeyDown={onKeyDown}>
        {options.map((o) => (
          <SubPlate
            key={o.id}
            id={`${name}-radio-${o.id}`}
            role="radio"
            checked={o.id === selected}
            tabIndex={o.id === selected ? 0 : -1}
            aria-controls={`${name}-panel-${o.id}`}
            onClick={() => setSelected(o.id)}
          >
            {o.label}
          </SubPlate>
        ))}
      </div>
      {options.map((o) => (
        <div key={o.id} id={`${name}-panel-${o.id}`} hidden={o.id !== selected}>
          {panels[o.id]}
        </div>
      ))}
    </div>
  );
}
