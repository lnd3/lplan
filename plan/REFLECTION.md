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

## What's Next

Tier 3 (advanced analytics) is the natural next step, but also consider:
- **Usability**: Auto-regenerate INDEX.md on view (plan serve)
- **Scalability**: Test with 50+ projects (report layout, validation perf)
- **Ecosystem**: GitHub integration, CI/CD hooks, Obsidian plugin (if dogfooding suggests it)
