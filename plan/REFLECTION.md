# lplan Reflection

Format: `YYYY-MM-DD | CATEGORY | insight`
Categories: GOTCHA · PATTERN · LEARNING · WARNING · DECISION · CONSTRAINT · FINDING

*Reformatted 2026-08-30 to match `templates/REFLECTION.md.template` — this file had drifted into markdown sections (the exact "section headers instead of pipe entries" drift D005 was written to prevent). Detail for multi-paragraph entries lives in [`REFLECTION_extension.md`](REFLECTION_extension.md), anchor-matched.*

---

2026-08-20 | PATTERN | Pydantic models everywhere — type safety caught bugs early, code stayed self-documenting, no runtime validation surprises.
2026-08-20 | PATTERN | Separation of concerns — parser/validator/graph/priority each own their domain; new modules (writer, stats, report) were orthogonal additions, no refactoring needed.
2026-08-20 | PATTERN | Template-first documentation — writing examples first (QUICK_REFERENCE.md, templates/) clarified API design before implementation.
2026-08-20 | PATTERN | Test-driven module development — new modules (writer, report, watch) got unit tests before CLI integration, caught integration bugs early.
2026-08-20 | PATTERN | Dogfooding the framework on lplan's own plan/ caught real UX gaps (e.g. "why do I have to manually regenerate INDEX.md?").
2026-08-20 | GOTCHA | YAML frontmatter round-tripping is fragile if markdown body contains `---` — mitigate by avoiding `---` in Goal/Scope sections, or switch to TOML.
2026-08-20 | GOTCHA | CHANGELOG.md appending merges entries onto one line without explicit newlines between them — fixed by ensuring newlines on append.
2026-08-20 | GOTCHA | HTML report SVG layout (phase-based columns) doesn't handle very wide graphs — Gantt chart likely better than dependency graph past 50+ projects.
2026-08-20 | GOTCHA | Cross-repo refs (`repo:ID` syntax) assume sibling directory structure — doesn't work for monorepos or external GitHub repos; best-effort, not validated.
2026-08-24 | FINDING | Codebase had no urgent technical debt as of this checkpoint — clean, tested, maintainable.
2026-08-27 | LEARNING | FOCUS.md/CHANGELOG.md drift is easy to miss because entity frontmatter itself stays accurate — only the summary docs go stale, since nothing forces their re-read the way a status field does. → REFLECTION_extension.md#focus-changelog-drift
2026-08-27 | LEARNING | Plan-entity updates get batched to session-end rather than logged as things actually happen, because "finish the real work first" always wins in the moment — addressed by WORKFLOW.md § Bubbling Up. → REFLECTION_extension.md#bubbling-up-origin
2026-08-27 | FINDING | Open question: should small UI-polish commits get lightweight Action entities, or should WORKFLOW.md explicitly bless "commit-only, no entity" for cosmetic changes? Still unresolved as of this writing.
