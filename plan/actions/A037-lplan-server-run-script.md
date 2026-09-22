---
id: A037
title: lplan-server.sh run script (start/stop/restart/status/logs/list)
status: DONE
priority: LOW
priority_drivers:
  - convenience
created: 2026-09-22
updated: 2026-09-22
depends: []
external_dependencies: []
enables: []
---

## Goal

Add a dev-convenience shell wrapper around `plan serve`/`stop`/`restart`
so every repo consuming lplan as a submodule (currently: superplan,
cinder, EphemNet, persona) can background the plan web server with log
capture, matching the start/stop/restart/status/logs shape already
established in cinder's and EphemNet's own `scripts/*.sh` — instead of
each repo growing its own copy-pasted wrapper independently.

## What was built

`scripts/lplan-server.sh`: `start` (backgrounds `plan serve` via
`nohup`, redirects stdout/stderr to `plan_dir/.plan-server.log`),
`stop`/`restart` (delegate to `plan stop`/self stop+start — `plan
restart` itself doesn't redirect output to a log file, hence not
delegating restart wholesale), `status` (reads the same
`.plan-server.pid` the Python CLI already writes), `logs` (tail -f),
`list` (prints the command usage — no separate discovery mechanism
existed). Config via `LPLAN_HOST`/`LPLAN_PORT`/`LPLAN_EDIT` env vars.
Takes `plan_dir` as an optional second arg (default `./plan`), run
from the consuming repo's root — same convention as `./deps/lplan/bin/plan
validate ./plan`.

Deliberately doesn't touch `src/`, `cli.py`, or the PID-file format —
reads/writes the exact same `.plan-server.pid` JSON `_write_pid`/
`_read_pid` in `server.py` already produce, so it stays compatible
with `plan stop`/`plan restart` run directly.

## Log

2026-09-22 — Built and verified live: started against a scratch `plan
init`'d directory, confirmed HTTP 200, confirmed the log file captured
Flask's request log, confirmed `stop` cleared the PID file and `status`
correctly reported not-running afterward. Filed as an Action here per
WORKFLOW.md's drive-by convention rather than silently absorbed into
superplan's own plan — flagged explicitly to the user as a new
capability (not a bug fix), since it's a new script under `scripts/`,
not an edit to `WORKFLOW.md`/`templates/*`/`CLAUDE.md`/`README.md`, so
it doesn't require the full Level 3 policy-change treatment, but it's
also not a "defect fixed in isolation" — logging it explicitly here
rather than defaulting to a bare CHANGELOG line.
