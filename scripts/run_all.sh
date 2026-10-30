#!/usr/bin/env bash
# Final benchmark (plan Task 22): every check and experiment on ONE machine in one go.
# Usage: bash scripts/run_all.sh [--dry-run] [--allow-collector]
#   --dry-run          print the commands only
#   --allow-collector  run even if the speed collector is running here (it skews timings)
# Env: RESULTS_DIR (default results), PY (default .venv/bin/python)
set -euo pipefail
cd "$(dirname "$0")/.."

RESULTS_DIR="${RESULTS_DIR:-results}"
PY="${PY:-.venv/bin/python}"
COLLECTOR_PATTERN="${COLLECTOR_PATTERN:-routing.speeds.collect}"

dry_run=0
allow_collector=0
for arg in "$@"; do
  case "$arg" in
    --dry-run) dry_run=1 ;;
    --allow-collector) allow_collector=1 ;;
    *) echo "unknown option: $arg" >&2; exit 64 ;;
  esac
done

collector_running=no
if pgrep -f "$COLLECTOR_PATTERN" >/dev/null 2>&1; then collector_running=yes; fi
if [[ $collector_running == yes && $allow_collector -eq 0 ]]; then
  echo "speed collector is running on this machine; stop it or pass --allow-collector" >&2
  exit 2
fi

# Real speeds are added only when Task 20 adopted them, and only for gss (collection covers 3 districts).
# The first line must be exactly ADOPT or REJECT; anything else (e.g. **ADOPT**) stops the run
# instead of silently dropping the real-speed scenarios.
real=""
decision="$RESULTS_DIR/match_decision.md"
if [[ -f "$decision" ]]; then
  first="$(head -n 1 "$decision" | tr -d '[:space:]')"
  case "$first" in
    ADOPT) real=" --real" ;;
    REJECT) ;;
    *) echo "first line of $decision must be exactly ADOPT or REJECT (got '$first')" >&2; exit 65 ;;
  esac
fi

cmds=(
  "$PY -m pytest tests/test_correctness.py"
  "$PY scripts/check_exact.py data/graphs/gangnam_graph_v1.pkl data/queries/gangnam_q_seed42.csv"
  "$PY scripts/check_exact.py data/graphs/gss_graph_v1.pkl data/queries/gss_q_seed42.csv"
  "$PY scripts/check_exact.py data/graphs/seoul_graph_v1.pkl data/queries/seoul_q_seed42.csv"
  "$PY scripts/run_e1.py data/graphs/gangnam_graph_v1.pkl"
  "$PY scripts/run_e2.py gangnam gss seoul"
  "$PY scripts/run_e3.py seoul --overwrite"
  "$PY scripts/run_e3.py gss$real --overwrite"
  "$PY scripts/make_figures.py all"
)

if [[ $dry_run -eq 1 ]]; then
  printf '%s\n' "${cmds[@]}"
  exit 0
fi

mkdir -p "$RESULTS_DIR"
{
  echo "start: $(date '+%Y-%m-%dT%H:%M:%S%z')"
  $PY -VV
  sysctl -n machdep.cpu.brand_string 2>/dev/null || uname -m
  echo "collector running: $collector_running"
} > "$RESULTS_DIR/machine.txt"

for c in "${cmds[@]}"; do
  echo "+ $c"
  $c
done

echo "end: $(date '+%Y-%m-%dT%H:%M:%S%z')" >> "$RESULTS_DIR/machine.txt"
