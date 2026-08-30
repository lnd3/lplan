# FOCUS Context

Overflow detail for `FOCUS.md` — background, breakdowns, and recent-history notes that don't fit the lean Active/Blocked/Next shape. First real usage of D005's companion-file convention (created 2026-08-30, alongside D005's implementation).

## Status breakdown

- **Projects**: 6/10 DONE (P001–P006), 3 IN_PROGRESS (P007, P009, P010), 1 PLANNING (P008)
- **Designs**: D005 (Template File Family Scaling) now DONE — filed under P008 but scope doesn't match, see P008's Log
- **Master Plans**: 1 IN_PROGRESS (M001). M002 (Scalability Foundation) moved to the accessibility-lplan repo 2026-08-30 — no longer part of lplan's own plan.
- **Theses**: 3 HELD (T001–T003), none QUESTIONING or ABANDONED
- **Concepts**: 5 STABLE (C001–C005)
- **Framework**: stable; primary interface is Web UI (`plan serve`), including the Plan Health Dashboard (P010); companion-file convention (D005) now has real tooling support

## P010 detail

Backend (`status_overview.py`, `/api/status-overview`), frontend (`overview.js`, "🩺 Status" tab), and the needs-attention panel are built and data-verified against lplan's own plan/. What's left: A023's visual/click-through check in an actual browser — the original implementing sandbox had no headless browser, so this was verified via API responses and static wiring only.

## Recent drive-by changes (2026-08-30)

- **A024** — AI Agent Memory Maintenance documented in WORKFLOW.md + template (now condensed; detail in WORKFLOW_DETAILS.md). Prompted tightening of the policy-change drive-by rule.
- **A025** — Consumer repo structural alignment check added to WORKFLOW_DETAILS.md § Framework Updates. Running that check against this repo's own `plan/*.md` files found the FOCUS.md/REFLECTION.md drift fixed alongside D005's implementation (see below).
- **A026** — D005 implemented: `companions.py`, parser/validate/generate-index/check-refs support, template comment blocks on 8 templates. Dogfooded on this repo's own drifted FOCUS.md/REFLECTION.md and a real `D005_learnings.md` companion. Full checklist in A026.

## Longer-running notes

- A015 stale since 2026-08-24 — P010's own staleness panel now flags this automatically the moment someone opens the Status tab.
- `plan check-refs` flags A011/A015 as orphaned (dangling `design:` refs) and P009 as unused — known, intentionally left as real dogfood cases for P010 rather than fixed. Worth a cleanup pass eventually, not urgent.
