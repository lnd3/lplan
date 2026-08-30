# FOCUS Context

Overflow detail for `FOCUS.md` — background, breakdowns, and recent-history notes that don't fit the lean Active/Blocked/Next shape. First real usage of D005's companion-file convention (created 2026-08-30, alongside D005's implementation).

## Status breakdown

- **Projects**: 7/10 DONE (P001–P006, P010), 2 IN_PROGRESS (P007, P009), 1 PLANNING (P008)
- **Designs**: D005 (Template File Family Scaling, DONE, filed under P008 but scope doesn't match — see P008's Log), D007 (Analytics Architecture, DONE, written retroactively 2026-08-30 for P007)
- **Master Plans**: 1 IN_PROGRESS (M001, "lplan Framework Development" — rewritten 2026-08-30, see below). M002 (Scalability Foundation) moved to the accessibility-lplan repo 2026-08-30 — no longer part of lplan's own plan.
- **Theses**: 3 HELD (T001–T003), none QUESTIONING or ABANDONED
- **Concepts**: 5 STABLE (C001–C005)
- **Framework**: stable; primary interface is Web UI (`plan serve`), including the completed Plan Health Dashboard (P010); companion-file convention (D005) now has real tooling support

## M001 rewrite (2026-08-30)

M001 and M002 were both created 2026-08-24 as generic demo content to exercise the then-new MasterPlan entity type — neither ever described anything real about lplan or any other project. M002 turned out to actually describe accessibility-lplan's real infrastructure work, so it got moved there. M001 had nowhere else to go and lplan genuinely didn't have a real master plan of its own, so at user request it was rewritten in place: retitled "lplan Framework Development," vision/goals/scope reset to be about lplan itself, and its Tasks section restructured into 4 phases mapping the real P001–P010 history plus a forward-looking Phase 4 (cross-repo maturity: P008, D005 propagation to consumer repos, historical trend tracking). All 5 projects that reference it via `parent_master_plan` (P004–P007, P010) needed no changes — the ID and relationship stayed the same, only M001's own content changed. See M001's own Log for full detail.

## Recent drive-by changes (2026-08-30)

- **A024** — AI Agent Memory Maintenance documented in WORKFLOW.md + template (now condensed; detail in WORKFLOW_DETAILS.md). Prompted tightening of the policy-change drive-by rule.
- **A025** — Consumer repo structural alignment check added to WORKFLOW_DETAILS.md § Framework Updates. Running that check against this repo's own `plan/*.md` files found the FOCUS.md/REFLECTION.md drift fixed alongside D005's implementation (see below).
- **A026** — D005 implemented: `companions.py`, parser/validate/generate-index/check-refs support, template comment blocks on 8 templates. Dogfooded on this repo's own drifted FOCUS.md/REFLECTION.md and a real `D005_learnings.md` companion. Full checklist in A026.
- **A023/P010 closed** — the last open item (browser click-through verification) done via jsdom DOM execution against a live `plan serve`, 21/21 checks passed. See A023's Log.
- **P007/A015/P009 aligned** — P007 found to be 7/9 tasks done (impact analysis, Gantt, burndown, live dashboard all built but never checked off); A015's dependency-graph SVG confirmed built (`report.py`) but static-report-only, not live-dashboard-wired; new D007 design doc written retroactively, closing a `check-refs` orphan A015 had carried since creation. P009's stale `updated` date/Log fixed to reflect A024's earlier addition.

## Longer-running notes

- `plan check-refs` flags A011 as orphaned (dangling `design:` ref) and P009 as unused — known, intentionally left as a real dogfood case for P010 rather than fixed. Worth a cleanup pass eventually, not urgent.
