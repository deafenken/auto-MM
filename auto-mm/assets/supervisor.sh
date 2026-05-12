#!/usr/bin/env bash
# supervisor.sh — keep auto-mm running across crashes for the full contest window.
#
# Usage:
#   nohup bash auto-mm/assets/supervisor.sh <run_slug> > supervisor.log 2>&1 &
#
# Flags:
#   --poll <seconds>      override poll interval (default: from run.yaml or 1200)
#   --max-runtime <h>     hard ceiling in hours (default: until deadline or STOP)
#   --invoke <command>    how to invoke the agent (default: claude --resume "/auto-mm resume <slug>")
#   --help                print this
#
# What it does:
#   1. Reads runs/<slug>/run.yaml to learn the deadline and poll interval.
#   2. In a forever loop:
#       a. If STOP exists → exit 0.
#       b. If PAUSE exists → sleep poll_seconds, loop.
#       c. If deadline passed → exit 0 with a final summary.
#       d. If another agent is alive (heartbeat fresh, pid alive) → sleep, loop.
#       e. Otherwise, invoke the agent command. Capture exit code.
#       f. Sleep poll_seconds (with exponential backoff on repeated failures).
#
# This script never inspects modeling state. It only re-invokes the orchestrator,
# which is the only place that owns state interpretation.

set -uo pipefail

print_help() {
    sed -n '2,/^$/p' "$0" | sed 's/^# \{0,1\}//'
    exit 0
}

SLUG=""
POLL_SECONDS=""
MAX_RUNTIME_HOURS=""
INVOKE_CMD=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        --poll) POLL_SECONDS="$2"; shift 2 ;;
        --max-runtime) MAX_RUNTIME_HOURS="$2"; shift 2 ;;
        --invoke) INVOKE_CMD="$2"; shift 2 ;;
        --help|-h) print_help ;;
        -*) echo "unknown flag: $1" >&2; exit 2 ;;
        *) SLUG="$1"; shift ;;
    esac
done

if [[ -z "$SLUG" ]]; then
    echo "supervisor.sh: missing <run_slug>" >&2
    print_help
fi

RUN_DIR="runs/${SLUG}"
if [[ ! -d "$RUN_DIR" ]]; then
    echo "supervisor.sh: runs/${SLUG} does not exist. Start with the orchestrator first." >&2
    exit 1
fi

# Pull poll_seconds from run.yaml if not overridden
if [[ -z "$POLL_SECONDS" ]]; then
    POLL_SECONDS=$(awk '/poll_seconds:/ {print $2; exit}' "$RUN_DIR/run.yaml" 2>/dev/null || echo "1200")
fi

# Default invoke command — adjust to your local Claude Code CLI if different
if [[ -z "$INVOKE_CMD" ]]; then
    INVOKE_CMD="claude --print --dangerously-skip-permissions \"/auto-mm resume ${SLUG}\""
fi

deadline_utc=$(awk '/deadline_utc:/ {print $2; exit}' "$RUN_DIR/run.yaml" 2>/dev/null || echo "")
start_ts=$(date +%s)
fail_count=0

log() { echo "[supervisor $(date -u +%Y-%m-%dT%H:%M:%SZ)] $*"; }

is_pid_alive() {
    local pid="$1"
    [[ -n "$pid" ]] && kill -0 "$pid" 2>/dev/null
}

heartbeat_fresh() {
    local heartbeat="$RUN_DIR/.heartbeat"
    [[ -f "$heartbeat" ]] || return 1
    local ts pid
    ts=$(python3 -c "import json,sys; print(json.load(open('$heartbeat')).get('ts_utc',''))" 2>/dev/null)
    pid=$(python3 -c "import json,sys; print(json.load(open('$heartbeat')).get('pid',''))" 2>/dev/null)
    [[ -z "$ts" || -z "$pid" ]] && return 1
    local heartbeat_age
    heartbeat_age=$(python3 -c "
import datetime as dt
ts = dt.datetime.fromisoformat('$ts'.replace('Z','+00:00'))
now = dt.datetime.now(dt.timezone.utc)
print(int((now-ts).total_seconds()))
")
    [[ "$heartbeat_age" -lt 300 ]] && is_pid_alive "$pid"
}

deadline_passed() {
    [[ -z "$deadline_utc" ]] && return 1
    python3 -c "
import datetime as dt
d = dt.datetime.fromisoformat('$deadline_utc'.replace('Z','+00:00'))
now = dt.datetime.now(dt.timezone.utc)
import sys; sys.exit(0 if now > d else 1)
"
}

max_runtime_exceeded() {
    [[ -z "$MAX_RUNTIME_HOURS" ]] && return 1
    local elapsed_h
    elapsed_h=$(( ($(date +%s) - start_ts) / 3600 ))
    [[ "$elapsed_h" -ge "$MAX_RUNTIME_HOURS" ]]
}

log "starting supervisor for slug=${SLUG} poll=${POLL_SECONDS}s deadline=${deadline_utc:-<unknown>}"

while true; do
    if [[ -f "$RUN_DIR/STOP" ]]; then
        log "STOP file present — clean exit"
        exit 0
    fi

    if [[ -f "$RUN_DIR/PAUSE" ]]; then
        log "PAUSE — sleeping ${POLL_SECONDS}s"
        sleep "$POLL_SECONDS"
        continue
    fi

    if deadline_passed; then
        log "deadline passed — clean exit"
        exit 0
    fi

    if max_runtime_exceeded; then
        log "max-runtime ceiling hit — clean exit"
        exit 0
    fi

    if heartbeat_fresh; then
        log "another agent appears alive — sleeping ${POLL_SECONDS}s"
        sleep "$POLL_SECONDS"
        continue
    fi

    log "invoking: $INVOKE_CMD"
    if eval "$INVOKE_CMD"; then
        fail_count=0
        log "invocation completed cleanly"
    else
        fail_count=$((fail_count + 1))
        log "invocation failed (count=$fail_count)"
    fi

    # Exponential backoff capped at 1h on repeated failures
    if [[ "$fail_count" -gt 0 ]]; then
        backoff=$(( POLL_SECONDS * (1 << (fail_count > 5 ? 5 : fail_count - 1)) ))
        [[ "$backoff" -gt 3600 ]] && backoff=3600
        log "backoff sleep ${backoff}s"
        sleep "$backoff"
    else
        sleep "$POLL_SECONDS"
    fi
done
