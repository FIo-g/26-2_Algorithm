import type { MethodId } from "@/lib/methods";

export type PlayerState = {
  method: MethodId;
  ghost: MethodId | null; // previous method, drawn at its full extent
  clock: number; // intersections settled so far
  playing: boolean;
  finished: boolean; // the clock has reached the method's settled count
};

type Options = {
  first: MethodId;
  settled: Record<string, number>; // settled count per method
  total: number; // scrubber maximum: Dijkstra's settled count
  seconds: number; // how long Dijkstra takes from 0 to the end
  minSeconds: number; // floor for the other methods, so a tiny search is still watchable
  draw(clock: number, method: MethodId, ghost: MethodId | null): void;
  onFrame(clock: number, method: MethodId): void; // every painted frame
  onState(state: PlayerState): void; // discrete changes only
};

// The clock counts intersections settled. Dijkstra runs 0 to total in `seconds`. A method with fewer settled
// intersections runs proportionally faster to its own end, then stops there.
export function createPlayer(o: Options) {
  let method = o.first;
  let ghost: MethodId | null = null;
  let clock = 0;
  let playing = false;
  let raf = 0;
  let last = 0;

  const finished = () => clock >= o.settled[method];
  const emit = () => o.onState({ method, ghost, clock, playing, finished: finished() });
  const paint = () => {
    o.draw(clock, method, ghost);
    o.onFrame(clock, method);
  };
  const stop = () => {
    if (raf) cancelAnimationFrame(raf);
    raf = 0;
    playing = false;
  };
  const rate = () => {
    const s = o.settled[method];
    return s / Math.max((o.seconds * s) / o.total, o.minSeconds);
  };

  function tick(now: number) {
    const dt = Math.min((now - last) / 1000, 0.1);
    last = now;
    clock = Math.min(clock + rate() * dt, o.settled[method]);
    paint();
    if (finished()) {
      playing = false;
      raf = 0;
      emit();
    } else {
      raf = requestAnimationFrame(tick);
    }
  }

  function play() {
    stop();
    if (finished()) clock = 0;
    playing = true;
    last = performance.now();
    paint();
    raf = requestAnimationFrame(tick);
    emit();
  }

  function jumpToEnd() {
    stop();
    clock = o.settled[method];
    paint();
    emit();
  }

  return {
    start(animate: boolean) {
      if (animate) play();
      else jumpToEnd();
    },
    play,
    pause() {
      stop();
      emit();
    },
    seek(value: number) {
      stop();
      clock = Math.min(Math.max(value, 0), o.total);
      paint();
      emit();
    },
    select(next: MethodId, animate: boolean) {
      if (next === method) return;
      stop();
      ghost = method;
      method = next;
      clock = 0;
      if (animate) play();
      else jumpToEnd();
    },
    redraw: paint,
    dispose: stop,
  };
}

export type Player = ReturnType<typeof createPlayer>;
