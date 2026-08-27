# lplan Workflow — Details & Reference

Deeper material referenced from `WORKFLOW.md`. Read the main file first — this is
for when you need the full mechanism, the worked examples, or the rationale
behind a rule, not for day-to-day use.

---

## External Change Detection (Agent Resumption)

When an agent resumes work (from memory state, stored commit hash, or context), the plan may have changed externally: another agent committed, changes were pulled from upstream, the user made direct edits, or an external process modified the codebase.

**Detection mechanism**: track the commit hash in agent memory; on resumption, compare it to current HEAD.

### Resumption checklist

```
On agent resume:
1. Get current commit hash: git rev-parse HEAD
2. Compare to remembered_commit_hash (from agent memory)

If they match:  → Continue with existing context (no external changes)
If they differ: → External change detected. Rebalance perception (below).
```

### Rebalancing steps

**Step 1 — identify scope**: `git diff <remembered_commit>..HEAD --name-only`

**Step 2 — categorize impact**:

| Changed File | Impact | Action |
|---|---|---|
| FOCUS.md | High | Re-read. May change what you're supposed to be doing. |
| CHANGELOG.md | Medium | Re-read recent entries. Understand what decisions were made. |
| REFLECTION.md | Medium | Skim for new learnings that might affect strategy. |
| INDEX.md | Low | Snapshot only. Less critical than source files. |
| Entity files (P/D/A/T/M/C) | High | Check if your work conflicts with changed entities. |
| Other files (src/, tests/, etc.) | Medium | Depends on your task. Re-read if related. |
| .git/*, docs/*, config | Low | Usually safe to ignore. |

**Step 3 — decide**:

```
No critical files changed → update commit hash, minimal refresh,
  log "External changes detected (N commits), non-critical files only"

FOCUS.md or relevant entities changed → re-read FOCUS.md, check affected
  entities for conflicts, consider pivoting/pausing if directions conflict,
  log "External changes detected, re-synced FOCUS.md and X entities"

Massive change (>20 files, critical paths modified) → pause work, do a
  full rebalance (FOCUS.md, INDEX.md, recent CHANGELOG), re-evaluate
  whether your current task still makes sense, may need to escalate,
  log "Major external changes detected (N commits, M files). Rebalancing..."
```

### Worked example

Agent stored `commit_hash = abc123` when it logged off; resumes at `def456` (3 commits, changed: FOCUS.md, `plan/projects/P007.md` status, `src/planner/static/status.js`, WORKFLOW.md).

```
Decision:
  → FOCUS.md changed: re-read for priority shifts
  → P007 changed: check if it affects current work
  → status.js changed: relevant if agent was working on UI
  → WORKFLOW.md changed: documentation only, low priority

Action:
  → Re-read FOCUS.md and P007; git show to see what changed in P007
  → If P007 status is now BLOCKED and agent was about to work on it: pivot
  → If unrelated: acknowledge, continue
  → Update memory: commit_hash = def456
  → Log: "Synced external changes: FOCUS and P007 updated, continuing with [current task]"
```

### Memory storage pattern

```json
{
  "last_commit_hash": "def456",
  "last_sync_time": "2026-08-26T15:30:00Z",
  "current_task": "Implement C005 YAML validation",
  "context": "..."
}
```

```python
current_hash = subprocess.check_output(["git", "rev-parse", "HEAD"]).decode().strip()
remembered_hash = memory.get("last_commit_hash")
external_change_detected = current_hash != remembered_hash
```

---

## Worked Examples by Change Magnitude

**Small** — Fixed a typo in P001's title. Update P001 frontmatter. Done — no CHANGELOG, no FOCUS.md, no REFLECTION.md.

**Medium** — P004 (Web Refactoring) completed.
```
✓ P004 status: IN_PROGRESS → DONE
✓ CHANGELOG: "2026-08-26 | P004 | IN_PROGRESS → DONE | Web refactoring complete, UI modularized (21.6KB server)"
✓ FOCUS.md: remove P004 from Active, note P005 (Master Plans) now unblocked
```

**Large** — Discovered the hierarchical entity model (Thesis→MasterPlan→Project→Design→Action) is fundamental and needs formalizing.
```
✓ Create C001-hierarchical-entity-model.md (Concept)
✓ Update related entities (P005, P006 now reference it)
✓ CHANGELOG: "2026-08-26 | C001 | NEW | Hierarchical entity model formalized as core concept"
✓ FOCUS.md: add "Concept documentation" to Active, note it enables future cross-repo work
✓ REFLECTION.md: "5-level hierarchy (T→M→P→D→A) emerged as natural scale structure.
   Future projects should use this layer mapping upfront."
```

**Massive** — API/schema design has a fundamental flaw; requires rearchitecting Status view and entity relationships, affects 3 active projects.
```
✓ Re-architect entity model; update all affected entity frontmatters
✓ CHANGELOG entries for each: C003 status→DRAFT, P007 priority→HIGH, P008 new blocker
✓ FOCUS.md complete rewrite: active work, blockers, deferred work
✓ REFLECTION.md: "Entity relationship model had O(n²) API-surface growth; graph-based
   model reduces to O(n). Always validate API surface early."
✓ plan generate-index
✓ Check theses: do T001/T002 still hold?
```

---

## Framework Updates (lplan Evolution)

When lplan itself changes (new entity types, fields, workflow updates, validation rules), existing users need to know what changed and whether they need to migrate.

**In the lplan repository**: update CHANGELOG.md (breaking vs non-breaking), update MIGRATION.md for major changes, update templates/schema docs, update WORKFLOW.md if procedures changed.

**Announcement checklist for lplan maintainers**:

1. **Tag the change type** — ✅ Non-breaking (new optional fields, new entity types — adopt gradually) or ⚠️ Breaking (required new fields, status enum changes, validation rule changes — may invalidate existing plans).
2. **Document the change**, e.g.:
   ```markdown
   # lplan v2.1 (2026-08-26)
   ## New: Concept Entity Type
   - Optional field: `type` (mode|term|pattern|constraint|rule|finding)
   - Status: STABLE | DRAFT | DEPRECATED — non-breaking
   ## New: Thesis Status Enum
   - HELD | QUESTIONING | ABANDONED — breaking for theses only
   ```
3. **Provide a migration guide if breaking**, e.g.:
   ```markdown
   # Migrating to lplan v2.1
   ## Thesis entities: update status to HELD | QUESTIONING | ABANDONED.
     Run `plan validate ./plan` to find outdated values. ~5 min/thesis.
   ## Project entities: new optional `parent_master_plan` field — unaffected until adopted.
   ```

**User-side: detecting lplan updates** — `git log --oneline deps/lplan`, read its CHANGELOG.md, assess impact (new features: adopt when ready; breaking: run `plan validate` and migrate; non-breaking: adopt immediately, gradually, or defer).

**Versioning** — semver: MAJOR = breaking schema/workflow changes, MINOR = non-breaking additions, PATCH = docs/non-functional.

**Maintainer workflow when changing lplan**: update code/templates/docs → classify breaking/non-breaking → CHANGELOG.md entry (`## vX.Y (date)` + impact + effort) → MIGRATION.md if breaking → bump version → update WORKFLOW.md if procedures changed → notify users.

---

## Extended Rationale

**Why "Bubbling Up" exists**: plan upkeep loses to whatever you're actually building almost every time — not because anyone decides to skip it, but because it's invisible work that's easy to defer to "later," and later never comes. One lplan session drifted FOCUS.md/CHANGELOG.md days behind real entity state *twice*, A015 sat IN_PROGRESS with no Log entry for three days, and P010 (the dashboard built specifically to catch this) only exists because a human pointed out the gap. A Log entry written immediately says what happened and why; one reconstructed at session's end says what you remember, filtered through everything that happened after — the parts worth writing down (a rejected approach, why you branched into new work) are exactly the parts that fade first.

**Why "External Contribution Workflow" exists**: lplan is dogfooded on its own `plan/` *and* consumed as a dependency by other repos. An agent working in one of those other repos sometimes needs to fix a bug inside lplan itself, but their active context is the *other* repo's plan. Requiring full WORKFLOW.md onboarding just to land a bug fix means the fix either doesn't happen or happens with no trail — so this gets a reduced-friction path instead of the normal magnitude rules.
