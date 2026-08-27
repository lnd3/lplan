# Plan Changelog

Append-only record of all status and priority changes.

Format: `YYYY-MM-DD | ID | old_status → new_status | note`

---

2026-08-22 | P003 | IN_PROGRESS → DONE | Tier 3 Phase 3 complete: Gantt and Burndown chart visualizations built. Analytics dashboard now shows: metrics tables + Gantt timeline + Burndown progress. All visualizations SVG-based, zero external deps.

2026-08-22 | P001 | DONE → DONE | Tier 1 delivery validated and dogfooded

2026-08-22 | P002 | IN_PROGRESS → DONE | All Tier 2 Operational/Governance/Visibility features shipped. Web UI (plan serve) and additional scaffolding added beyond scope.

2026-08-24 | P004 | IN_PROGRESS → DONE | Web Server & UI Refactoring complete: monolithic server.py split into modular JS (editor, tree, preview, status modules) + Flask server.

2026-08-24 | P005 | IN_PROGRESS → DONE | Master Plans & Strategic Vision Architecture complete: MasterPlan entity (M-prefix) implemented with cross-repo distribution support.

2026-08-24 | P006 | IN_PROGRESS → DONE | Thesis Framework Integration complete: Thesis entity (T-prefix) implemented with conviction levels and many-to-many thesis↔master_plan relationships.

2026-08-24 | M001 | NEW → IN_PROGRESS | Developer Experience Excellence master plan created; work started under P004/P007.

2026-08-24 | M002 | NEW → PLANNING | Scalability Foundation master plan created; not yet started.

2026-08-24 | T001, T002, T003 | NEW → HELD | Founding theses captured (strategy/execution separation, schema-driven validation, web visualization accessibility).

2026-08-26 | C001–C005 | NEW → STABLE | Concept entity type (C-prefix) added to lplan; five core concepts extracted from the framework itself (hierarchical entity model, modular architecture, event delegation, dependency graph analysis, YAML frontmatter format).

2026-08-27 | — | catch-up | CHANGELOG synced to actual entity state per WORKFLOW.md upkeep pass — no new work performed, this closes the audit-trail gap for 2026-08-24 through 2026-08-26.

2026-08-27 | P009 | NEW → IN_PROGRESS | External Maintenance catch-all project created, plus new WORKFLOW.md § "External Contribution Workflow (Drive-By Fixes)". Reason: recent lplan-source fixes were made by agents whose active context was an external repo's own plan, not lplan's — those fixes had no CHANGELOG/entity trail. P009 + the new convention give drive-by contributions a one-line-minimum logging path without requiring full WORKFLOW.md onboarding.

2026-08-27 | A016 | NEW → DONE | Tree-view clicks broke on apostrophes in titles (unescaped onclick attribute); master-plan nodes never highlighted and could render twice with duplicate DOM ids. Drive-by fix from superplan's context, backfilled retroactively.

2026-08-27 | A017 | NEW → DONE | Root badges extended to all parentless items; fixed actions with a project but no design vanishing from the tree entirely; page title/toolbar now show the actual repo name; Tree view's Full Doc button no longer dead-ends before Edit. Drive-by fix from superplan's context, backfilled retroactively.

2026-08-27 | A018 | NEW → DONE | Save/Cancel buttons never actually became visible in edit mode (CSS display:none reasserting itself); sidebar toggle glyph never updated (event.currentTarget bug); INDEX.md no longer offers Edit (it's regenerated on every view); repo name now prefers README.md's heading. Drive-by fix from superplan's context, backfilled retroactively.

2026-08-27 | A019 | NEW → DONE | Thesis<->master_plan link now shown in the content pane both directions; toggle-glyph rotation CSS rule removed (conflicted with the text-flip fix); master plans sidebar list now comprehensive, and a master plan's content pane shows its child projects recursively. Drive-by fix from superplan's context, backfilled retroactively.

2026-08-27 | P010, D004, A020-A023 | NEW → PLANNING/IDEA | Plan Health Dashboard scoped at user request: a live, hierarchy-wide status/progress view (rollups + stale/blocked/dangling-ref surfacing) to fill the gap between INDEX.md (static snapshot), Items view (flat table, no rollups), and Analytics dashboard (rollups, Project-only). Planning only — no implementation started.

2026-08-27 | P010, D004, A020, A021, A022 | IN_PROGRESS/IDEA → IN_PROGRESS/DONE | Implemented: new `status_overview.py` (pure rollup/staleness/dangling-ref functions), `/api/status-overview` route, `overview.js` frontend module, new "🩺 Status" toolbar tab. Verified via curl + a standalone script against lplan's own plan/ (matches `plan check-refs` exactly, correctly flags A015/P007/M001 as stale) and the existing 100-test suite still passes. P010 stays IN_PROGRESS (not DONE) and A023 stays IN_PROGRESS: the implementing sandbox had no headless browser, so the rendered UI itself was never visually checked, only its data/wiring.

2026-08-27 | A021 | fix | User tested in a real browser and found row/bar links didn't work — `/api/status-overview` never returned a `path`, so the frontend guessed a filename that didn't match. Fixed by threading `path_by_id` through `status_overview.py`; verified via curl that `/api/file` now resolves every returned path with 200. Exactly the kind of bug the missing-headless-browser caveat was flagging as a risk.
