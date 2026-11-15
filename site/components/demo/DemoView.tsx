"use client";

import { useMemo, useState } from "react";
import { SubPlate } from "@/components/sign/SubPlate";
import { StopOctagon } from "@/components/sign/StopOctagon";
import { GridGraph } from "./GridGraph";
import { SmallGraph } from "./SmallGraph";
import { ALGO_LABEL, buildSteps, isStopPoint, num } from "./steps";
import type { Demo } from "./types";
import styles from "./StepDemo.module.css";

// One demo: a small directed graph (step through with Back and Next) or a grid (scrubber).
export function DemoView({ demo }: { demo: Demo }) {
  const run = demo.runs[0];
  const bidir = run.algo === "bidir";
  const isGrid = demo.vertices.length > 16;
  const steps = useMemo(() => buildSteps(run, bidir), [run, bidir]);
  const [index, setIndex] = useState(0);

  const step = steps[index];
  const last = index === steps.length - 1;
  const n = demo.vertices.length;
  const path = last ? run.path : [];
  const stop = last && isStopPoint(step.loop);
  const label = ALGO_LABEL[run.algo] ?? run.algo;
  const dijkstra = demo.runs.find((r) => r.algo === "dijkstra");
  const compare = isGrid && dijkstra && run.algo !== "dijkstra" ? dijkstra : null;
  const bound = run.h ? run.h[demo.s] : null;
  const loop = step.loop;
  const svgLabel = `${demo.title}, step ${index + 1} of ${steps.length}: ${step.settled.length} of ${n} intersections settled.`;
  const backId = `demo-back-${demo.id}`;
  const nextId = `demo-next-${demo.id}`;

  // A disabled button drops focus to <body>, so hand focus to the other button before the change.
  function move(to: number) {
    if (steps.length > 1 && to === 0) document.getElementById(nextId)?.focus();
    else if (steps.length > 1 && to === steps.length - 1) document.getElementById(backId)?.focus();
    setIndex(to);
  }

  const figure = isGrid ? (
    <GridGraph
      demo={demo}
      settled={step.settled}
      current={step.pop?.v ?? null}
      path={path}
      landmarks={demo.landmarks ?? []}
      label={svgLabel}
    />
  ) : (
    <SmallGraph
      demo={demo}
      settled={step.settled}
      current={step.pop?.v ?? null}
      path={path}
      label={svgLabel}
    />
  );

  return (
    <div className={styles.demo}>
      <h3>{demo.title}</h3>
      <p className="muted">
        Source {demo.s}, target {demo.t}. Settled intersections fill yellow and are listed under Settled. The ring
        marks the intersection being popped.
      </p>

      <div className="demo-split">
        <div className={styles.stage}>
          {figure}
          {isGrid && (
            <input
              type="range"
              className={styles.slider}
              min={1}
              max={steps.length}
              value={index + 1}
              aria-label="Step"
              aria-valuetext={`Step ${index + 1} of ${steps.length}`}
              onChange={(e) => setIndex(Number(e.target.value) - 1)}
            />
          )}
        </div>

        <div className={styles.side}>
          <div className={styles.controls}>
            <SubPlate id={backId} onClick={() => move(index - 1)} disabled={index === 0}>
              Back
            </SubPlate>
            <SubPlate id={nextId} onClick={() => move(index + 1)} disabled={last}>
              Next
            </SubPlate>
            <span className={`subplate ${styles.counter}`}>
              Step {index + 1} of {steps.length}
            </span>
          </div>

          {/* The one live region: narration and the settled list change together on each step. */}
          <div className={styles.live} aria-live="polite">
            <p className={styles.narration}>{step.narration}</p>
            <span className={`subplate ${styles.readout}`}>
              Settled {step.settled.length} of {n}: {step.settled.length ? step.settled.join(", ") : "none"}
            </span>
          </div>

          <dl className={styles.readouts}>
            {bidir && (
              <>
                <div className="subplate">
                  <dt>top_f</dt>
                  <dd>{loop?.top_f == null ? "none" : num(loop.top_f)}</dd>
                </div>
                <div className="subplate">
                  <dt>top_b</dt>
                  <dd>{loop?.top_b == null ? "none" : num(loop.top_b)}</dd>
                </div>
                <div className="subplate">
                  <dt>μ</dt>
                  <dd>{loop?.mu == null ? "not found yet" : num(loop.mu)}</dd>
                </div>
              </>
            )}
            {bound !== null && (
              <div className="subplate">
                <dt>Bound at source</dt>
                <dd>
                  {num(bound)} of true {num(run.dist)}
                </dd>
              </div>
            )}
            {last && (
              <div className="subplate">
                <dt>Result</dt>
                <dd>
                  Path {run.path.join(" → ")}, distance {num(run.dist)}
                </dd>
              </div>
            )}
          </dl>

          {stop && (
            <p className={styles.stop}>
              <StopOctagon className={styles.octagon} />
              <span>Stop rule met: top_f + top_b reaches μ.</span>
            </p>
          )}
          {compare && (
            <p>
              {label} settled {run.settled} of {n}; {ALGO_LABEL.dijkstra} settled {compare.settled}.
            </p>
          )}
        </div>
      </div>

      <p className={styles.source}>
        From <code>{demo.source_test.split("::").flatMap((part, i) => (i === 0 ? [part] : ["::", <wbr key={i} />, part]))}</code>
      </p>
    </div>
  );
}
