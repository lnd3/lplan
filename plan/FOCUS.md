# lplan Focus

*Rewritten each session. Overflow background/detail → [`FOCUS_context.md`](FOCUS_context.md).*
*Last synced: 2026-08-31*

---

## Active

**P001 — Tier 1 Engine** (IN_PROGRESS, reopened) — hosts core-engine follow-on work: A027 (parent-child status consistency), D008/A028 (project phase → Design/Action linking), A035 (duplicate entity ID detection — just added).

**P005 — Master Plans & Strategic Vision Architecture** (IN_PROGRESS, reopened) — hosts D009 (Master Plan Priority Stack), designed today, not yet implemented.

**P007 — Analytics & Reporting Dashboard** (IN_PROGRESS) — 7/9 tasks real and done; remaining scope is A015 (dependency-graph SVG exists but isn't wired into the live dashboard) plus two unstarted Phase 3 items (email delivery, historical trends).

**M001 — lplan Framework Development** (IN_PROGRESS, master plan) — tracks P001–P010's real history plus Phase 4 (cross-repo maturity).

**P009 — External Maintenance** (IN_PROGRESS, perpetual catch-all) — working as intended, now also the source of a caught bug (A034's merge left a duplicate ID — see A035).

---

## Blocked

None.

---

## Next

1. D009: implement the `priority_stack` field (schema, the two validator warnings, Tree view surfacing) once requested — design is done, code isn't
2. A027 check 2 (stale-BLOCKED parent after children resolve) — deferred by the external session, still open
3. D008 Phase 4 (checkbox extraction) — explicitly lower priority per D008 itself
4. P007/A015: decide whether to wire the dependency-graph SVG into the live Analytics dashboard, or leave it static-report-only and re-scope A015 down
5. P008 (Cross-Repo Planning Integration) — actual scope (cross-repo refs, upstream master plan sync) still unstarted; D005 doesn't count toward it despite being filed there, see P008's own Log
6. A035's known gap: duplicate-ID detection only runs in `plan validate`'s CLI entrypoint, not in server.py routes or `generate-index` — worth extending if duplicates recur
