# lplan Reflection

Learnings and patterns from building the lplan framework.

## Patterns That Worked

**Pydantic models everywhere.** Type safety caught bugs early and made the codebase self-documenting. No runtime validation surprises.

**Separation of concerns.** Parser, validator, graph, priority each own their domain. Adding new features (writer, stats, report) was orthogonal, no refactoring needed.

**Template-first documentation.** Writing examples first (QUICK_REFERENCE.md, templates/) clarified API design. Implementation followed naturally.

**Test-driven module development.** New modules (writer, report, watch) got unit tests before CLI integration. Caught integration bugs early.

**Dogfooding the framework on lplan's own plan/.** Caught UX gaps (e.g., "why do I have to manually regenerate INDEX.md?"). Keeps priorities real.

## Gotchas & Workarounds

**YAML frontmatter round-tripping.** Editing frontmatter + preserving body is finicky. The split-on-`---` approach works but fragile if markdown content contains `---`. Mitigation: document as "don't use `---` in Goal/Scope sections" or switch to TOML.

**Changelog appending.** Current implementation appends all entries on same line if not careful with newlines. Fixed by ensuring newlines between entries (see changelog fix in this cycle).

**HTML report SVG layout.** Simple phase-based column layout works but doesn't handle very wide graphs. For 50+ projects, Gantt chart may be better than dependency graph.

**Cross-repo refs.** `repo:ID` syntax assumes sibling directory structure. Doesn't work for monorepos or external GitHub repos. Documented as best-effort, not validated.

## Technical Debt

None urgent. Codebase is clean, tested, and maintainable.

## Process Notes

**FOCUS.md/CHANGELOG.md drift is easy to miss because entities themselves stay accurate.** Between 2026-08-24 and 2026-08-27, P004/P005/P006 were completed, M001/M002/T001-T003/C001-C005 were all created, but FOCUS.md still read "COMPLETE, all tiers delivered" and CHANGELOG.md's last entry was from 2026-08-22. The entity frontmatter was never wrong — only the two documents meant to summarize it went stale, because nothing forces their update the way a status field forces itself to be read. Several small, real UI commits (Concept-type addition, thesis↔master_plan link display, badge conventions) also landed with no P/D/A entity behind them at all, so there was nothing to trigger a CHANGELOG entry even in principle.

**Takeaway for future sessions**: treat "does FOCUS.md/CHANGELOG.md still match `git log` + entity frontmatter?" as a cheap check worth running whenever resuming work, not just after self-directed large changes — see WORKFLOW.md's External Change Detection section, which covers exactly this case but is easy to skip if you don't suspect drift.

## What's Next

Tier 1–3 and the Thesis/MasterPlan/Concept framework are all delivered. Open work:
- **P007 (Analytics & Reporting Dashboard)**: A015 SVG dependency graph is mid-flight (2/6 tasks), stalled since 2026-08-24.
- **P008 (Cross-Repo Planning Integration)**: unblocked, not started.
- **M002 (Scalability Foundation)**: master plan exists, no execution yet.
- **Process**: consider whether small UI-polish commits should get lightweight Action entities, or whether WORKFLOW.md should explicitly bless "commit-only, no entity" for cosmetic changes — right now it's ambiguous and led to the untracked-commit gap above.
