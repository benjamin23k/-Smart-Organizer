#!/usr/bin/env bash
set -euo pipefail

# Background launcher for: smart-org watch
# Survives closing VSCode by using nohup + setsid.

APP_NAME="smart-organizer-watch"
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../" && pwd)"
REPO_ROOT="$PROJECT_DIR"

# You can override these:
#   export WATCH_CONFIG=/path/to/config.toml
#   export WATCH_PATH=/path/to/folder
#   export WATCH_OUTPUT_DIR=/path/to/output_base
#   export WATCH_DRY_RUN=1

CONFIG_TOML="${WATCH_CONFIG:-$REPO_ROOT/config.toml}"
WATCH_PATH="${WATCH_PATH:-}"
OUTPUT_DIR="${WATCH_OUTPUT_DIR:-}"
DRY_RUN="${WATCH_DRY_RUN:-0}"

STATE_DIR="${WATCH_STATE_DIR:-$HOME/.local/state/smart-organizer}"
LOG_DIR="${WATCH_LOG_DIR:-$HOME/.local/state/smart-organizer/logs}"
PID_FILE="$STATE_DIR/watch.pid"

mkdir -p "$STATE_DIR" "$LOG_DIR"

usage() {
  cat <<EOF
Usage: $(basename "$0") {start|stop|status|restart}

Environment variables (optional):
  WATCH_CONFIG=/path/to/config.toml
  WATCH_PATH=/path/to/watch-folder
  WATCH_OUTPUT_DIR=/path/to/output_base
  WATCH_DRY_RUN=1   (default 0)
  WATCH_STATE_DIR=...
  WATCH_LOG_DIR=...
EOF
}

is_running() {
  if [[ -f "$PID_FILE" ]]; then
    pid="$(cat "$PID_FILE" 2>/dev/null || true)"
    if [[ -n "${pid:-}" ]] && kill -0 "$pid" 2>/dev/null; then
      return 0
    fi
  fi
  return 1
}

start() {
  if is_running; then
    echo "Already running (pid=$(cat "$PID_FILE"))"
    exit 0
  fi

  cmd=(smart-org watch --config "$CONFIG_TOML")

  if [[ -n "$WATCH_PATH" ]]; then
    cmd+=("$WATCH_PATH")
  fi

  if [[ "$DRY_RUN" == "1" ]]; then
    cmd+=("--dry-run")
  fi

  if [[ -n "$OUTPUT_DIR" ]]; then
    cmd+=("--output-dir" "$OUTPUT_DIR")
  fi

  log_file="$LOG_DIR/watch_$(date +%Y%m%d_%H%M%S).log"

  # nohup + setsid to detach from terminal; redirect stdout/stderr to log.
  # shellcheck disable=SC2091
  nohup setsid "${cmd[@]}" >>"$log_file" 2>&1 &
  pid=$!

  # Give it a moment to start and then store PID
  sleep 0.2
  echo "$pid" > "$PID_FILE"

  echo "Started $APP_NAME"
  echo "PID: $pid"
  echo "Log: $log_file"
}

stop() {
  if ! is_running; then
    echo "Not running"
    rm -f "$PID_FILE" 2>/dev/null || true
    exit 0
  fi

  pid="$(cat "$PID_FILE")"
  echo "Stopping pid=$pid..."

  # Try graceful
  kill "$pid" 2>/dev/null || true
  sleep 0.5

  if kill -0 "$pid" 2>/dev/null; then
    kill -9 "$pid" 2>/dev/null || true
  fi

  rm -f "$PID_FILE" 2>/dev/null || true
  echo "Stopped."
}

status() {
  if is_running; then
    echo "RUNNING (pid=$(cat "$PID_FILE"))"
    exit 0
  fi
  echo "STOPPED"
  exit 1
}

restart() {
  stop
  start
}

cmd=${1:-}
case "$cmd" in
  start) start ;;
  stop) stop ;;
  status) status ;;
  restart) restart ;;
  -h|--help|help|"") usage ;;
  *) echo "Unknown command: $cmd"; usage; exit 2 ;;
esac

