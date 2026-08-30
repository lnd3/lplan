# lplan Focus

*Rewritten each session. Overflow background/detail → [`FOCUS_context.md`](FOCUS_context.md).*
*Last synced: 2026-08-30*

---

## Active

**P001 — Tier 1 Engine** (IN_PROGRESS, reopened) — hosting A027 (validator: parent-child status consistency) and D008/A028 (project phase → Design/Action linking). Both landed externally from TradeFlow, then had tests added and D008's Phases 1–3 implemented here today.

**P007 — Analytics & Reporting Dashboard** (IN_PROGRESS) — turned out much closer to done than its record showed: metrics/impact/Gantt/burndown/live-dashboard/static-report all built. Real remaining scope: A015's dependency-graph SVG isn't wired into the live dashboard, plus two unstarted Phase 3 items (email delivery, historical trends).

**M001 — lplan Framework Development** (IN_PROGRESS, master plan) — rewritten today to be lplan's actual master plan (was placeholder demo content since 2026-08-20). Tracks P001–P010's real history plus Phase 4 (cross-repo maturity, still ahead).

**P009 — External Maintenance** (IN_PROGRESS, perpetual catch-all) — working as intended; see `FOCUS_context.md` for recent entries.

---

**Recent, not otherwise active**: P010's rollup math now prefers Tasks/Phases checkboxes over child-entity counts (A030) — found and fixed a real stale-checkbox gap in P002/P003 (both DONE, 0% checked despite real completed work) while dogfooding it.

---

## Blocked

None.

---

## Next

1. A027 check 2 (stale-BLOCKED parent after children resolve) — deferred by the external session, still open
2. D008 Phase 4 (checkbox extraction) — explicitly lower priority per D008 itself
3. P007/A015: decide whether to wire the dependency-graph SVG into the live Analytics dashboard, or leave it static-report-only and re-scope A015 down
4. P008 (Cross-Repo Planning Integration) — actual scope (cross-repo refs, upstream master plan sync) still unstarted; D005 doesn't count toward it despite being filed there, see P008's own Log
5. M001 Phase 4: propagate D005 (companion files) + the alignment check to TradeFlow/superplan/accessibility-lplan
