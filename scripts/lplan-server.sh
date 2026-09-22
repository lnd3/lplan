#!/usr/bin/env bash
# Dev-convenience wrapper around `plan serve`/`stop`/`restart` — mirrors
# the start/stop/restart/status/logs shape used by cinder's and
# EphemNet's own scripts/*.sh. Not required to use lplan; `bin/plan
# serve|stop|restart` already work standalone. This just adds
# background-with-logging on top, since `plan serve` runs in the
# foreground and neither `plan stop` nor `plan restart` capture output
# to a file.
#
# Usage (run from the CONSUMING repo's root, same convention as
# `./deps/lplan/bin/plan validate ./plan`):
#   ./deps/lplan/scripts/lplan-server.sh start [plan_dir]
#   ./deps/lplan/scripts/lplan-server.sh stop [plan_dir]
#   ./deps/lplan/scripts/lplan-server.sh restart [plan_dir]
#   ./deps/lplan/scripts/lplan-server.sh status [plan_dir]
#   ./deps/lplan/scripts/lplan-server.sh logs [plan_dir]
#   ./deps/lplan/scripts/lplan-server.sh list
set -euo pipefail

SELF_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LPLAN_ROOT="$(dirname "$SELF_DIR")"
PLAN_BIN="$LPLAN_ROOT/bin/plan"

PLAN_DIR="${2:-./plan}"
HOST="${LPLAN_HOST:-127.0.0.1}"
PORT="${LPLAN_PORT:-8000}"
EDIT="${LPLAN_EDIT:-}"

PID_FILE="$PLAN_DIR/.plan-server.pid"
LOG_FILE="$PLAN_DIR/.plan-server.log"

usage() {
	cat <<EOF
Usage: $(basename "$0") <command> [plan_dir]

Commands:
  start     Start the plan web server in the background, logging to plan_dir/.plan-server.log
  stop      Stop the running plan web server
  restart   Stop then start (preserves this script's own host/port/edit config, not "plan restart"'s)
  status    Show whether a plan server is running for plan_dir
  logs      Follow the plan server's log file
  list      Show this command list

plan_dir defaults to ./plan (run this from the repo root, same
convention as './deps/lplan/bin/plan validate ./plan').

Config (env vars):
  LPLAN_HOST=${HOST}
  LPLAN_PORT=${PORT}
  LPLAN_EDIT=${EDIT:-(unset = read-only)}

This wraps $PLAN_BIN — it doesn't replace 'plan serve/stop/restart',
which still work fine standalone in the foreground.
EOF
}

running_pid() {
	if [ -f "$PID_FILE" ]; then
		pid="$(python3 -c "import json,sys; print(json.load(open('$PID_FILE')).get('pid',''))" 2>/dev/null || true)"
		if [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null; then
			echo "$pid"
			return 0
		fi
	fi
	return 1
}

cmd_start() {
	if pid="$(running_pid)"; then
		echo "plan server already running for $PLAN_DIR (pid $pid)"
		return
	fi
	edit_args=()
	[ -n "$EDIT" ] && edit_args+=(--edit)
	nohup "$PLAN_BIN" serve "$PLAN_DIR" --host "$HOST" --port "$PORT" "${edit_args[@]}" \
		>"$LOG_FILE" 2>&1 &
	disown
	sleep 0.5
	if pid="$(running_pid)"; then
		echo "plan server started (pid $pid) at http://${HOST}:${PORT}, logging to ${LOG_FILE}"
	else
		echo "plan server failed to start — check ${LOG_FILE}:" >&2
		tail -n 20 "$LOG_FILE" >&2 || true
		exit 1
	fi
}

cmd_stop() {
	"$PLAN_BIN" stop "$PLAN_DIR"
}

cmd_restart() {
	cmd_stop
	cmd_start
}

cmd_status() {
	if pid="$(running_pid)"; then
		echo "running (pid $pid), plan_dir $PLAN_DIR"
	else
		echo "not running"
	fi
}

cmd_logs() {
	if [ ! -f "$LOG_FILE" ]; then
		echo "no log file yet ($LOG_FILE) — start the server first" >&2
		exit 1
	fi
	tail -f "$LOG_FILE"
}

case "${1:-}" in
start | up) cmd_start ;;
stop | down) cmd_stop ;;
restart) cmd_restart ;;
status) cmd_status ;;
logs | log) cmd_logs ;;
list | help | "") usage ;;
*)
	usage
	exit 1
	;;
esac
