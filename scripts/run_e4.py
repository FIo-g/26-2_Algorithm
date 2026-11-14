"""E4 (RQ3): fixed routes vs SUMO's built-in periodic re-routing on the Anyang 3x3 network.

Signals and assumed demand come from the Anyang SUMO project (ANYANG_DIR). Signal plans: W = Webster
fixed-time, A = queue-responsive (compares waiting vehicles every second), B = offset coordination.
Every strategy runs with the same harness, demand, signals and seed; re-routing strategies only add
SUMO's rerouting device.

  python scripts/run_e4.py run --python <python with numpy>   # SUMO runs, skips finished ones
  python scripts/run_e4.py kpi                                 # results/e4_*.csv, figures/fig_e_reroute.png
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import os
import subprocess
import sys
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
ANYANG = Path(os.environ.get("ANYANG_DIR", r"C:\Users\sunri\Documents\SUMO\anyang"))
# (signal plan, demand level): Webster at two demands; plans A and B as a sensitivity check at medium (spec E4)
CASES = (("W", "medium"), ("W", "high"), ("A", "medium"), ("B", "medium"))
PLAN_NAMES = {"W": "Webster", "A": "queue-responsive", "B": "offset coordination"}
SEEDS = (1, 2, 3, 4, 5)
PROBS = {"fixed": 0.0, "reroute30": 0.3, "reroute100": 1.0}  # share of vehicles with the rerouting device
STRATEGIES = tuple(PROBS)
PERIOD_S = 60      # an equipped vehicle re-routes every 60 s
SMOOTH_STEPS = 60  # edge travel times: 60 s moving average (plan: 60 s smoothing)
END_S = 18000      # 5 h: demand runs 2 h, the rest lets queues clear


def run_dir(plan: str, level: str, strategy: str, seed: int) -> Path:
    return ANYANG / "experiments" / "e4_runs" / f"{plan}_{strategy}_{level}_s{seed}"


def sumo_args(strategy: str) -> list[str]:
    if not PROBS[strategy]:
        return []  # fixed routes: the route file's routes, no device
    return ["--device.rerouting.probability", str(PROBS[strategy]),
            "--device.rerouting.period", str(PERIOD_S),
            "--device.rerouting.adaptation-steps", str(SMOOTH_STEPS),
            "--routing-algorithm", "dijkstra"]


def one(plan: str, level: str, strategy: str, seed: int) -> int:
    sys.path.insert(0, str(ANYANG / "build" / "scripts"))
    import run_sim  # needs SUMO_HOME and numpy

    m = run_sim.run(plan, level, seed, end=END_S, out=str(run_dir(plan, level, strategy, seed)), fcd=None,
                    measure=False, extra=sumo_args(strategy))
    return 1 if m["errors"] else 0


def run_all(python: str, workers: int) -> int:
    todo = [(p, lv, st, s) for p, lv in CASES for st in STRATEGIES for s in SEEDS
            if not (run_dir(p, lv, st, s) / "done.json").exists()]
    print(f"todo {len(todo)} runs, workers {workers}", flush=True)

    def go(job):
        d = run_dir(*job)
        d.mkdir(parents=True, exist_ok=True)
        with open(d / "console.log", "w", encoding="utf-8") as fh:
            rc = subprocess.run([python, __file__, "one", *map(str, job)], stdout=fh, stderr=subprocess.STDOUT).returncode
        print(f"{d.name} rc={rc}", flush=True)
        return rc

    with ThreadPoolExecutor(workers) as ex:
        bad = [j for j, rc in zip(todo, ex.map(go, todo)) if rc]
    print(f"failed {bad}", flush=True)
    return 1 if bad else 0


def trips(path) -> list[tuple[float, bool, bool, bool]]:
    """(duration_s, arrived, departed, has_rerouting_device) per vehicle.

    SUMO writes unfinished vehicles with arrival=-1 and their time in the network so far as duration,
    so that duration is a lower bound; vehicles that never departed have depart=-1 and duration 0."""
    out = []
    for _, el in ET.iterparse(path):
        if el.tag == "tripinfo":
            out.append((float(el.get("duration")), float(el.get("arrival")) >= 0, float(el.get("depart")) >= 0,
                        any(d.startswith("routing_") for d in el.get("devices", "").split())))
            el.clear()
    return out


def p95(xs: list[float]) -> float:
    s = sorted(xs)
    return s[max(0, math.ceil(0.95 * len(s)) - 1)]  # nearest-rank, same as routing.bench._p95


GROUPS = {"all": lambda eq: True, "equipped": lambda eq: eq, "unequipped": lambda eq: not eq}
METRICS = ("arrived_pct", "mean_tt_s", "p95_tt_s", "mean_tt_arrived_s")


def run_rows(plan, level, strategy, seed, trips_) -> list[dict]:
    """mean_tt_s/p95_tt_s cover every departed vehicle (a lower bound when some did not arrive);
    mean_tt_arrived_s covers arrived vehicles only, which flatters a run where many got stuck."""
    rows = []
    for group, keep in GROUPS.items():
        if group != "all" and strategy != "reroute30":
            continue  # only the 30% runs mix equipped and unequipped vehicles
        sel = [t for t in trips_ if keep(t[3])]
        dep = [d for d, _, departed, _ in sel if departed]
        arr = [d for d, arrived, _, _ in sel if arrived]
        if not dep:
            continue
        rows.append({"plan": plan, "level": level, "strategy": strategy, "seed": seed, "group": group,
                     "vehicles": len(sel), "arrived": len(arr), "arrived_pct": round(100 * len(arr) / len(sel), 2),
                     "mean_tt_s": round(sum(dep) / len(dep), 2), "p95_tt_s": p95(dep),
                     "mean_tt_arrived_s": round(sum(arr) / len(arr), 2) if arr else ""})
    return rows


def summarize(rows: list[dict]) -> list[dict]:
    """Average each metric over seeds; change_pct compares mean_tt_s with fixed routes in the same case."""
    order = lambda k: (CASES.index(k[:2]) if k[:2] in CASES else len(CASES), STRATEGIES.index(k[2]),
                       list(GROUPS).index(k[3]))
    keys = sorted({(r["plan"], r["level"], r["strategy"], r["group"]) for r in rows}, key=order)
    out = []
    for p, lv, st, g in keys:
        rs = [r for r in rows if (r["plan"], r["level"], r["strategy"], r["group"]) == (p, lv, st, g)]
        o = {"plan": p, "level": lv, "strategy": st, "group": g, "seeds": len(rs)}
        for f in METRICS:
            vals = [r[f] for r in rs if r[f] != ""]
            o[f] = round(sum(vals) / len(vals), 2) if vals else ""
        o["mean_tt_min_s"] = min(r["mean_tt_s"] for r in rs)
        o["mean_tt_max_s"] = max(r["mean_tt_s"] for r in rs)
        out.append(o)
    base = {(o["plan"], o["level"]): o["mean_tt_s"] for o in out if o["strategy"] == "fixed" and o["group"] == "all"}
    for o in out:
        b = base.get((o["plan"], o["level"]))
        o["change_pct"] = round(100 * (o["mean_tt_s"] / b - 1), 2) if b else ""
    return out


def write_csv(path: Path, rows: list[dict]) -> None:
    with open(path, "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


def fig_e(summary: list[dict], path: Path) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    bars = [("fixed", "all", "fixed\nroutes"), ("reroute30", "equipped", "30%:\nequipped"),
            ("reroute30", "unequipped", "30%:\nothers"), ("reroute30", "all", "30%:\nall"),
            ("reroute100", "all", "100%\nre-route")]
    colors = {"fixed": "#7f7f7f", "reroute30": "#6baed6", "reroute100": "#08519c"}
    hatch = {"equipped": "//", "unequipped": "..", "all": ""}
    # plan A infers each vehicle's turning movement from its OD's original route (signal_a.collect), so it
    # miscounts re-routed vehicles; its numbers stay in the CSV but are not a fair re-routing comparison
    cases = [c for c in CASES if c[0] != "A" and any((o["plan"], o["level"]) == c for o in summary)]
    fig, axes = plt.subplots(2, len(cases), figsize=(3.6 * len(cases), 7), squeeze=False)
    for c, (plan, lv) in enumerate(cases):
        by = {(o["strategy"], o["group"]): o for o in summary if (o["plan"], o["level"]) == (plan, lv)}
        got = [b for b in bars if (b[0], b[1]) in by]
        x = list(range(len(got)))
        for r, (field, label) in enumerate([("mean_tt_s", "Mean travel time (s)\n(unarrived: time so far)"),
                                            ("arrived_pct", "Arrived within 5 h (%)")]):
            ax = axes[r][c]
            vals = [by[(s, g)][field] for s, g, _ in got]
            err = None
            if field == "mean_tt_s":
                err = [[v - by[(s, g)]["mean_tt_min_s"] for (s, g, _), v in zip(got, vals)],
                       [by[(s, g)]["mean_tt_max_s"] - v for (s, g, _), v in zip(got, vals)]]
            ax.bar(x, vals, yerr=err, capsize=3, color=[colors[s] for s, *_ in got],
                   hatch=[hatch[g] for _, g, _ in got], edgecolor="black", linewidth=0.5)
            for i, v in enumerate(vals):
                ax.text(i, v, f"{v:.0f}" if field == "mean_tt_s" else f"{v:.1f}", ha="center", va="bottom", fontsize=8)
            ax.set_xticks(x, [lab for *_, lab in got], fontsize=8)
            ax.set_ylabel(label if c == 0 else "")
            if field == "arrived_pct":
                ax.set_ylim(0, 105)
            if r == 0:
                ax.set_title(f"{plan} ({PLAN_NAMES[plan]}), {lv} demand", fontsize=9)
    fig.suptitle("E4: fixed routes vs periodic re-routing (Anyang 3x3, assumed demand, 5 seeds, SUMO)\n"
                 "error bars: min-max of per-seed means", fontsize=10)
    fig.tight_layout()
    fig.savefig(path, dpi=150)


def kpi() -> None:
    rows = []
    for p, lv in CASES:
        for st in STRATEGIES:
            for s in SEEDS:
                f = run_dir(p, lv, st, s) / "tripinfo.xml"
                if f.exists():
                    rows += run_rows(p, lv, st, s, trips(f))
    summary = summarize(rows)
    write_csv(REPO / "results" / "e4_runs.csv", rows)
    write_csv(REPO / "results" / "e4_summary.csv", summary)
    version = subprocess.run(["sumo", "--version"], capture_output=True, text=True).stdout.splitlines()[0]
    manifest = {"sumo": version, "cases": CASES, "plans": PLAN_NAMES, "seeds": SEEDS, "probs": PROBS,
                "period_s": PERIOD_S, "adaptation_steps": SMOOTH_STEPS, "routing_algorithm": "dijkstra",
                "baseline": "fixed: same harness, demand, signals and seed, no rerouting device",
                "end_s": END_S, "teleport": "off (--time-to-teleport -1)",
                "note_plan_A": "A infers turning movements from each OD's original route, so re-routed vehicles are "
                               "miscounted; A rows are kept but excluded from figure (e) and conclusions"}
    (REPO / "results" / "e4_manifest.json").write_text(json.dumps(manifest, indent=1), encoding="utf-8")
    fig_e(summary, REPO / "figures" / "fig_e_reroute.png")
    for o in summary:
        print(o)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--python", default=sys.executable)
    r.add_argument("--workers", type=int, default=10)
    o = sub.add_parser("one")
    o.add_argument("plan", choices=list(PLAN_NAMES))
    o.add_argument("level", choices=sorted({lv for _, lv in CASES}))
    o.add_argument("strategy", choices=list(PROBS))
    o.add_argument("seed", type=int)
    sub.add_parser("kpi")
    a = ap.parse_args(argv)
    if a.cmd == "run":
        return run_all(a.python, a.workers)
    if a.cmd == "one":
        return one(a.plan, a.level, a.strategy, a.seed)
    kpi()
    return 0


if __name__ == "__main__":
    sys.exit(main())
