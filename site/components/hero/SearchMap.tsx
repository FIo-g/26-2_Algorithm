"use client";

import { useEffect, useRef, useState, type CSSProperties, type KeyboardEvent } from "react";
import { MethodGlyph } from "@/components/sign/MethodGlyph";
import { SubPlate } from "@/components/sign/SubPlate";
import { formatInt, formatMinutesSeconds, formatPercentPoints } from "@/lib/format";
import { METHODS, type MethodId } from "@/lib/methods";
import { loadHero, segmentRanks, type GraphKey, type HeroAlgo, type HeroData } from "./data";
import { createRenderer } from "./gl";
import styles from "./hero.module.css";
import { createPlayer, type Player, type PlayerState } from "./player";

const PLAY_SECONDS = 7; // Dijkstra from 0 to the end
const MIN_SECONDS = 1.6; // so a search of a few dozen intersections is still watchable
const LIVE_DELAY_MS = 400; // the spoken readout waits for the clock to settle, so scrubbing does not flood it
const WIDE_ZOOM = 1.3; // wide screens: the network is this much larger than a fit to the sign height
const ROUTE_AT = 0.58; // wide screens: where the middle of the route sits, as a share of the map height
const VIEW_MARGIN = 0.08; // narrow screens: margin round the area the search covered
const DIM_WIDE: [number, number] = [0.16, 0.42]; // alpha of unlit roads and of the previous method's roads
const DIM_NARROW: [number, number] = [0.3, 0.55];
const SOURCE = "site/public/data/hero.json";
const FOLLOW_SPACER = "Same route, same travel time. Bidirectional settled NN.N% of what Dijkstra did."; // sets the plate's width and height before the real sentence exists
const WIDE = "(min-width: 900px)";
const DEFAULT_ORDER: MethodId[] = ["dijkstra", "astar", "bidir", "alt16"]; // replaced by the file's order once loaded
const GRAPH_NAME: Record<GraphKey, string> = { gangnam: "Gangnam-gu", seoul: "Seoul" };

type Problem = "load" | "gl" | null;

function samePath(a: HeroAlgo, b: HeroAlgo): boolean {
  const sameTime = Math.abs(a.time_s - b.time_s) <= 1e-9 * Math.abs(b.time_s);
  return sameTime && a.path.length === b.path.length && a.path.every((v, i) => v === b.path[i]);
}

// A share that can be well under one percent keeps enough digits to be non-zero.
function share(part: number, whole: number): string {
  const percent = (100 * part) / whole;
  return formatPercentPoints(percent, percent < 1 ? 2 : percent < 10 ? 1 : 0);
}

// Shown, and spoken, once a second method has finished with the same route and travel time as Dijkstra.
function followText(data: HeroData, method: MethodId, completed: MethodId[]): string {
  const current = data.algos[method];
  const baseline = data.algos.dijkstra;
  if (method === "dijkstra" || completed.length < 2 || !samePath(current, baseline)) return "";
  return `Same route, same travel time. ${METHODS[method].label} settled ${share(current.settled, baseline.settled)} of what Dijkstra did.`;
}

function Names({ ko, en }: { ko: string; en: string }) {
  return (
    <>
      <span lang="ko">{ko}</span>
      <span>{en}</span>
    </>
  );
}

type Corner = "ar" | "br" | "al" | "bl"; // above or below, right or left of the marker
type Rect = { x0: number; y0: number; x1: number; y1: number };
// Where the network sits in the map area. w and h are the network's size in CSS px, tx and ty shift it from the
// centre of the area. view is the part of the network that shows, and avoid lists text that covers the map. Both
// are in the network's own pixels.
type Layout = { w: number; h: number; tx: number; ty: number; view: Rect; avoid: Rect[] };

const LABEL_H = 46; // label size in CSS px, estimated from the text so no measuring pass is needed
const LABEL_GAP = 20;
const LABEL_INSET = 8;
const CORNERS: Corner[] = ["ar", "br", "al", "bl"];

function labelRect(corner: Corner, px: number, py: number, width: number): Rect {
  const above = corner[0] === "a";
  const right = corner[1] === "r";
  const x0 = right ? px - LABEL_INSET : px + LABEL_INSET - width;
  const y0 = above ? py - LABEL_GAP - LABEL_H : py + LABEL_GAP;
  return { x0, y0, x1: x0 + width, y1: y0 + LABEL_H };
}

function inside(r: Rect, x: number, y: number): boolean {
  return x >= r.x0 && x <= r.x1 && y >= r.y0 && y <= r.y1;
}

function overlaps(a: Rect, b: Rect): boolean {
  return a.x0 < b.x1 && a.x1 > b.x0 && a.y0 < b.y1 && a.y1 > b.y0;
}

function labelWidth(label: { ko: string; en: string }): number {
  return Math.max(label.en.length * 8.2, label.ko.length * 14.5) + 24;
}

// Fits the network into the map area. A phone zooms to the area Dijkstra searched, so the lit roads fill the area. A
// wide screen sizes the network by the width of the sign and puts the middle of the route a bit below the middle of
// the sign, so the north and south of the city run off under the keyline and the route clears the text and the controls.
function computeLayout(data: HeroData, slot: HTMLElement, root: HTMLElement | null): Layout | null {
  const sw = slot.clientWidth;
  const sh = slot.clientHeight;
  if (sw === 0 || sh === 0) return null;
  const aspect = data.graph.aspect;
  const wide = window.matchMedia(WIDE).matches;
  const pos = data.positions;
  let w: number;
  let h: number;
  let tx = 0;
  let ty = 0;
  if (wide) {
    w = Math.min(sw, sh * aspect * WIDE_ZOOM);
    h = w / aspect;
    let lo = 1;
    let hi = 0;
    for (const v of data.algos.dijkstra.path) {
      lo = Math.min(lo, pos[2 * v + 1]);
      hi = Math.max(hi, pos[2 * v + 1]);
    }
    const reach = Math.max(0, (h - sh) / 2); // never shift far enough to show an empty edge
    ty = Math.min(reach, Math.max(-reach, (ROUTE_AT - 0.5) * sh - ((lo + hi) / 2 - 0.5) * h));
  } else {
    let x0 = 1;
    let x1 = 0;
    let y0 = 1;
    let y1 = 0;
    for (const v of data.traces.dijkstra) {
      x0 = Math.min(x0, pos[2 * v]);
      x1 = Math.max(x1, pos[2 * v]);
      y0 = Math.min(y0, pos[2 * v + 1]);
      y1 = Math.max(y1, pos[2 * v + 1]);
    }
    const mx = VIEW_MARGIN * (x1 - x0);
    const my = VIEW_MARGIN * (y1 - y0);
    x0 = Math.max(0, x0 - mx);
    x1 = Math.min(1, x1 + mx);
    y0 = Math.max(0, y0 - my);
    y1 = Math.min(1, y1 + my);
    w = Math.min(sw / (x1 - x0), (sh * aspect) / (y1 - y0));
    h = w / aspect;
    tx = -((x0 + x1) / 2 - 0.5) * w;
    ty = -((y0 + y1) / 2 - 0.5) * h;
  }
  const ox = (sw - w) / 2 + tx; // where the network's top left corner is, in the map area
  const oy = (sh - h) / 2 + ty;
  const avoid: Rect[] = [];
  if (wide && root) {
    const at = slot.getBoundingClientRect();
    root.querySelectorAll("[data-avoid]").forEach((el) => {
      const r = el.getBoundingClientRect();
      avoid.push({ x0: r.left - at.left - ox, y0: r.top - at.top - oy, x1: r.right - at.left - ox, y1: r.bottom - at.top - oy });
    });
  }
  return { w, h, tx, ty, view: { x0: -ox, y0: -oy, x1: sw - ox, y1: sh - oy }, avoid };
}

// Picks a corner for each label so that it covers neither the route nor the other marker nor the other label nor
// the heading, and stays inside the part of the map that shows. Ties keep the first corner in CORNERS.
function placeLabels(data: HeroData, layout: Layout | null): [Corner, Corner] {
  if (!layout) return ["ar", "ar"];
  const { view, avoid } = layout;
  const { s, t, sLabel, tLabel } = data.graph.query;
  const at = (v: number): [number, number] => [data.positions[2 * v] * layout.w, data.positions[2 * v + 1] * layout.h];
  const route: [number, number][] = [];
  const path = data.algos.dijkstra.path;
  for (let i = 1; i < path.length; i++) {
    const [ax, ay] = at(path[i - 1]);
    const [bx, by] = at(path[i]);
    const steps = Math.max(1, Math.ceil(Math.hypot(bx - ax, by - ay) / 6));
    for (let k = 0; k <= steps; k++) route.push([ax + ((bx - ax) * k) / steps, ay + ((by - ay) * k) / steps]);
  }
  const pick = (self: [number, number], other: [number, number], width: number, taken: Rect | null): Corner => {
    let best: Corner = "ar";
    let bestScore = Infinity;
    for (const corner of CORNERS) {
      const r = labelRect(corner, self[0], self[1], width);
      let score = 0;
      for (const [x, y] of route) if (inside(r, x, y)) score += 1;
      if (inside(r, other[0], other[1])) score += 50;
      if (taken && overlaps(r, taken)) score += 100;
      for (const a of avoid) if (overlaps(r, a)) score += 100;
      score += Math.max(0, view.x0 - r.x0) + Math.max(0, r.x1 - view.x1) + Math.max(0, view.y0 - r.y0) + Math.max(0, r.y1 - view.y1);
      if (score < bestScore) {
        best = corner;
        bestScore = score;
      }
    }
    return best;
  };
  const sp = at(s);
  const tp = at(t);
  const startCorner = pick(sp, tp, labelWidth(sLabel), null);
  const endCorner = pick(tp, sp, labelWidth(tLabel), labelRect(startCorner, sp[0], sp[1], labelWidth(sLabel)));
  return [startCorner, endCorner];
}

function Pin({ data, vertex, end, corner }: { data: HeroData; vertex: number; end: boolean; corner: Corner }) {
  const x = data.positions[2 * vertex];
  const y = data.positions[2 * vertex + 1];
  const label = end ? data.graph.query.tLabel : data.graph.query.sLabel;
  const place = `${corner[0] === "a" ? styles.above : styles.below} ${corner[1] === "r" ? styles.right : styles.left}`;
  return (
    <div className={`${styles.pin} ${place}`} style={{ left: `${x * 100}%`, top: `${y * 100}%` }}>
      <span className={`${styles.disc} ${end ? styles.discEnd : styles.discStart}`} />
      <SubPlate className={styles.label}>
        <Names ko={label.ko} en={label.en} />
      </SubPlate>
    </div>
  );
}

// No WebGL2 (or no data): the heading stays, and the same facts are given as text.
function Fallback({ data }: { data: HeroData | null }) {
  if (!data) {
    return (
      <div className={styles.fallback}>
        <p>The map data could not be loaded.</p>
      </div>
    );
  }
  const { sLabel, tLabel } = data.graph.query;
  return (
    <div className={styles.fallback}>
      <p>
        This browser cannot draw the map. The route runs from <span lang="ko">{sLabel.ko}</span> {sLabel.en} to{" "}
        <span lang="ko">{tLabel.ko}</span> {tLabel.en}.
      </p>
      <table>
        <caption className="visually-hidden">Intersections settled and travel time for each method</caption>
        <thead>
          <tr>
            <th scope="col">Method</th>
            <th scope="col" className="num">
              Intersections settled
            </th>
            <th scope="col" className="num">
              Estimated travel time
            </th>
          </tr>
        </thead>
        <tbody>
          {data.order.map((id) => (
            <tr key={id}>
              <th scope="row">{METHODS[id].label}</th>
              <td className="num">{formatInt(data.algos[id].settled)}</td>
              <td className="num">{formatMinutesSeconds(data.algos[id].time_s)}</td>
            </tr>
          ))}
        </tbody>
      </table>
      <p className={`source ${styles.source}`}>
        Replay of {SOURCE}, written by scripts/export_site_data.py
      </p>
    </div>
  );
}

export function SearchMap() {
  const [data, setData] = useState<HeroData | null>(null);
  const [problem, setProblem] = useState<Problem>(null);
  const [ui, setUi] = useState<PlayerState>({
    method: "dijkstra",
    ghost: null,
    clock: 0,
    playing: false,
    finished: false,
  });
  const [live, setLive] = useState("");
  const [completed, setCompleted] = useState<MethodId[]>([]);
  const [layout, setLayout] = useState<Layout | null>(null);
  const slotRef = useRef<HTMLDivElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const scrubRef = useRef<HTMLInputElement>(null);
  const counterRef = useRef<HTMLSpanElement>(null);
  const playerRef = useRef<Player | null>(null);
  const reducedRef = useRef(false);

  // Fetch after mount. A wide screen gets the whole city, a narrow one gets Gangnam-gu.
  useEffect(() => {
    const abort = new AbortController();
    const key: GraphKey = window.matchMedia(WIDE).matches ? "seoul" : "gangnam";
    loadHero(key, abort.signal)
      .then(setData)
      .catch(() => {
        if (!abort.signal.aborted) setProblem("load");
      });
    return () => abort.abort();
  }, []);

  // Size and place the network in the map area, again whenever the area or the text over it changes size.
  useEffect(() => {
    const slot = slotRef.current;
    if (!data || !slot) return;
    const root = slot.closest("section");
    const update = () => setLayout(computeLayout(data, slot, root));
    update();
    const observer = new ResizeObserver(update);
    observer.observe(slot);
    root?.querySelectorAll("[data-avoid]").forEach((el) => observer.observe(el));
    return () => observer.disconnect();
  }, [data]);

  // Renderer and clock live as long as the canvas does.
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!data || !canvas || problem) return;
    const ranks = data.order.map((id) => segmentRanks(data.edges, data.graph.n, data.traces[id]));
    const renderer = createRenderer(canvas, data.positions, data.edges, ranks, () => setProblem("gl"));
    if (!renderer) {
      queueMicrotask(() => setProblem("gl"));
      return;
    }
    const settled: Record<string, number> = {};
    for (const a of data.graph.algos) settled[a.id] = a.settled;
    let liveTimer = 0;
    const finished: MethodId[] = [];
    const wideQuery = window.matchMedia(WIDE);
    const spoken = (state: PlayerState): string => {
      const shown = Math.floor(Math.min(state.clock, settled[state.method]));
      const algo = data.algos[state.method];
      const done = state.finished
        ? ` Estimated travel time ${formatMinutesSeconds(algo.time_s)}. ${followText(data, state.method, finished)}`
        : "";
      return `${METHODS[state.method].label}: ${formatInt(shown)} of ${formatInt(data.graph.n)} intersections settled.${done}`;
    };

    const player = createPlayer({
      first: "dijkstra",
      settled,
      total: settled.dijkstra,
      seconds: PLAY_SECONDS,
      minSeconds: MIN_SECONDS,
      draw: (clock, method, ghost) =>
        renderer.draw(clock, data.order.indexOf(method), ghost ? data.order.indexOf(ghost) : -1),
      onFrame: (clock, method) => {
        const shown = Math.floor(Math.min(clock, settled[method]));
        if (counterRef.current) counterRef.current.textContent = formatInt(shown);
        if (scrubRef.current) {
          scrubRef.current.value = String(Math.floor(clock));
          scrubRef.current.setAttribute("aria-valuetext", `${formatInt(shown)} of ${formatInt(data.graph.n)} intersections settled`);
        }
      },
      // Assistive technology hears the readout only when the clock stops (finish, pause, a seek), once it has been still.
      onState: (state) => {
        setUi(state);
        if (state.finished && !finished.includes(state.method)) finished.push(state.method);
        window.clearTimeout(liveTimer);
        if (!state.playing) liveTimer = window.setTimeout(() => setLive(spoken(state)), LIVE_DELAY_MS);
        if (state.finished) setCompleted((done) => (done.includes(state.method) ? done : [...done, state.method]));
      },
    });
    playerRef.current = player;

    // Small screens draw dim roads brighter, so the part the search has not reached still reads as streets.
    const dim = () => renderer.setDim(...(wideQuery.matches ? DIM_WIDE : DIM_NARROW));
    dim();
    renderer.resize();
    const observer = new ResizeObserver(() => {
      renderer.resize();
      dim();
      player.redraw();
    });
    observer.observe(canvas);

    reducedRef.current = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    player.start(!reducedRef.current);

    return () => {
      window.clearTimeout(liveTimer);
      observer.disconnect();
      player.dispose();
      playerRef.current = null;
      renderer.dispose();
    };
  }, [data, problem]);

  if (problem) return <Fallback data={data} />;

  const corners = data ? placeLabels(data, layout) : (["ar", "ar"] as [Corner, Corner]);
  const order = data?.order ?? DEFAULT_ORDER;
  const ready = data !== null;
  const select = (id: MethodId) => playerRef.current?.select(id, !reducedRef.current);

  function onMethodKeys(event: KeyboardEvent<HTMLDivElement>) {
    const step =
      event.key === "ArrowRight" || event.key === "ArrowDown"
        ? 1
        : event.key === "ArrowLeft" || event.key === "ArrowUp"
          ? -1
          : 0;
    if (!step || !ready) return;
    event.preventDefault();
    const next = order[(order.indexOf(ui.method) + step + order.length) % order.length];
    select(next);
    document.getElementById(`hero-method-${next}`)?.focus();
  }

  const current = data?.algos[ui.method];
  const baseline = data?.algos.dijkstra;
  const follow = data && ui.finished ? followText(data, ui.method, completed) : "";
  const route =
    data && current && ui.finished
      ? current.path.map((v) => `${data.positions[2 * v]},${data.positions[2 * v + 1]}`).join(" ")
      : "";

  return (
    <>
      <div ref={slotRef} className={styles.slot}>
        {data && (
          <div
            className={styles.netbox}
            style={
              {
                "--aspect": data.graph.aspect,
                ...(layout ? { width: layout.w, transform: `translate(${layout.tx}px, ${layout.ty}px)` } : null),
              } as CSSProperties
            }
          >
            <canvas
              ref={canvasRef}
              className={styles.canvas}
              role="img"
              aria-label={`Road network of ${GRAPH_NAME[data.key]} drawn as thin lines. Roads turn white as the search from ${data.graph.query.sLabel.en} to ${data.graph.query.tLabel.en} settles them.`}
            />
            {route && (
              <svg
                className={styles.route}
                viewBox="0 0 1 1"
                preserveAspectRatio="none"
                aria-hidden="true"
                focusable="false"
              >
                <polyline className={styles.casing} points={route} />
                <polyline className={styles.line} points={route} />
              </svg>
            )}
            <Pin data={data} vertex={data.graph.query.s} end={false} corner={corners[0]} />
            <Pin data={data} vertex={data.graph.query.t} end corner={corners[1]} />
          </div>
        )}
      </div>

      <div className={styles.controls}>
        <div className={styles.row}>
          <div className={styles.methods} role="radiogroup" aria-label="Search method" onKeyDown={onMethodKeys}>
            {order.map((id) => (
              <SubPlate
                key={id}
                id={`hero-method-${id}`}
                role="radio"
                checked={id === ui.method}
                tabIndex={id === ui.method ? 0 : -1}
                disabled={!ready}
                className={styles.item}
                onClick={() => select(id)}
              >
                <MethodGlyph method={id} />
                {METHODS[id].label}
              </SubPlate>
            ))}
          </div>
          <SubPlate
            className={`${styles.item} ${styles.play}`}
            disabled={!ready}
            onClick={() => (ui.playing ? playerRef.current?.pause() : playerRef.current?.play())}
          >
            {ui.playing ? "Pause" : ui.finished ? "Replay" : "Play"}
          </SubPlate>
          <SubPlate className={`${styles.item} ${styles.scrub}`}>
            <input
              ref={scrubRef}
              type="range"
              min={0}
              max={baseline?.settled ?? 1}
              step={1}
              defaultValue={0}
              disabled={!ready}
              aria-label="Intersections settled"
              onInput={(event) => playerRef.current?.seek(Number(event.currentTarget.value))}
            />
          </SubPlate>
        </div>
        <div className={styles.row}>
          <SubPlate className={`${styles.item} ${ready ? "" : styles.pending}`}>
            <span aria-hidden="true">
              <span
                ref={counterRef}
                className={`${styles.counter} num`}
                style={{ minWidth: `${formatInt(baseline?.settled ?? 0).length}ch` }}
              >
                0
              </span>{" "}
              of {data ? formatInt(data.graph.n) : ""} intersections settled
            </span>
          </SubPlate>
          <SubPlate className={`${styles.item} ${ui.finished ? "" : styles.pending}`}>
            <span aria-hidden="true" className="num">
              Estimated travel time {current ? formatMinutesSeconds(current.time_s) : ""}
            </span>
          </SubPlate>
        </div>
        <SubPlate className={`${styles.item} ${styles.follow} ${follow ? "" : styles.followPending}`}>
          <span aria-hidden="true">{follow || FOLLOW_SPACER}</span>
        </SubPlate>
        <p className={`source ${styles.source}`}>
          Replay of {SOURCE}, written by scripts/export_site_data.py
        </p>
      </div>

      <p className="visually-hidden" aria-live="polite" aria-atomic="true">
        {live}
      </p>
    </>
  );
}
