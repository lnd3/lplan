# lplan Focus

*Last synced: 2026-08-27 (new project scoped: P010 Plan Health Dashboard — planning only, not started)*

## Active

**P007 — Analytics & Reporting Dashboard** (IN_PROGRESS)
- A015 — SVG dependency graph visualization (IN_PROGRESS): path generator done, node rendering/status colors/interactivity still open (2/6 tasks checked, no Log entries since 2026-08-24 — still stale, see Notes).

**M001 — Developer Experience Excellence** (IN_PROGRESS, master plan)
- 5-year vision; executed tactically through P004/P007-adjacent work, and now P010. No dedicated action currently logging progress against M001 itself — worth a Log entry next time work advances it.

**P009 — External Maintenance** (IN_PROGRESS, perpetual catch-all — see WORKFLOW.md § External Contribution Workflow)
- Not "active work" in the usual sense; stays IN_PROGRESS indefinitely as the landing spot for drive-by fixes. Now has A016–A019 (tree-view click/highlight/dedup fixes, root-badge coverage, Save/Cancel visibility, toggle glyphs, INDEX.md edit-disable, thesis↔master_plan bidirectional display) — the convention is working as intended.

## Planning (not started)

- **P008 — Cross-Repo Planning Integration**: depends on P001, P005, P006 (all DONE) — unblocked, not started.
- **P010 — Plan Health Dashboard**: hierarchy-wide status/progress view (rollups + needs-attention surfacing), scoped 2026-08-27 with D004 + A020–A023. Depends on P004 (done) and P007 (in progress, but not blocking — reuses P007's parsing/graph code, doesn't require P007's own tasks to finish). Not started.
- **M002 — Scalability Foundation**: master plan created 2026-08-22, no execution yet.

## Blocked

None.

## Status

- **Projects**: 6/9 DONE (P001–P006), 2 IN_PROGRESS (P007, P009), 2 PLANNING (P008, P010)
- **Master Plans**: 1 IN_PROGRESS (M001), 1 PLANNING (M002)
- **Theses**: 3 HELD (T001–T003), none QUESTIONING or ABANDONED
- **Concepts**: 5 STABLE (C001–C005)
- **Framework**: stable; primary interface is Web UI (`plan serve`)

## Notes for next session

- A015 has been sitting at "in progress, no Log update" since 2026-08-24 — still true as of this pass. This is exactly the kind of thing P010's staleness panel is meant to catch automatically once built.
- `plan check-refs` currently flags A008/A011/A015 as orphaned (their `design:` field points at D005/D006/D007, which don't exist as files) and P009 as unused. Not fixed here — noted because P010's A023 (dogfood) will use these as real test cases; if they get fixed before then, replace them with whatever check-refs flags at that time.
