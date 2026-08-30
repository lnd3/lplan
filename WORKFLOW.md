# lplan Workflow Guide

Deeper mechanism, worked examples, and rationale for everything here live in
[`WORKFLOW_DETAILS.md`](WORKFLOW_DETAILS.md) — this file is the operating
summary. Follow it top to bottom for normal work; jump to details only when
a rule doesn't tell you enough to act.

## Core Principle

**Workflow rigor scales with change magnitude.** The more you change, the more you need to maintain coherence across the plan. Self-direct based on your sense of need, not calendar-based triggers.

---

## Change Magnitude → What to Update

| Level | Trigger | Update |
|---|---|---|
| **1 · Small** | typo, date fix, single status bump | Entity only. Done. |
| **2 · Medium** | entity completes/blocks, dependency resolves | + one `CHANGELOG.md` line (date, ID, transition, why) |
| **3 · Large** | multiple entities change, direction shift, new pattern discovered | + `FOCUS.md` rewrite/major edit + `REFLECTION.md` entry (what did we learn?) |
| **4 · Massive** | hypothesis disproven, architecture revised | All of Large + `plan generate-index` + review whether any Thesis/Master Plan status should shift |

Ask "how much changed?", not "how much time passed." Worked examples for each level: [`WORKFLOW_DETAILS.md` § Worked Examples](WORKFLOW_DETAILS.md#worked-examples-by-change-magnitude).

**When resuming after a gap** (new session, handed off from another agent): check whether the plan changed under you before trusting your own memory of it — see [`WORKFLOW_DETAILS.md` § External Change Detection](WORKFLOW_DETAILS.md#external-change-detection-agent-resumption).

---

## Coherence Rules (Always)

Regardless of change magnitude:

1. **State consistency** — an IN_PROGRESS entity appears in FOCUS.md's Active section, or CHANGELOG.md explains why it's paused.
2. **Decision traceability** — a changed priority/status/depends/enables is explained in CHANGELOG.md or the entity's Log.
3. **Blocker visibility** — a BLOCKED project/design is named in FOCUS.md, with what unblocks it.
4. **Learning capture** — a surprising discovery goes in REFLECTION.md, even as 1–2 sentences.

---

## Bubbling Up: Update *During* Work, Not Just After

The common failure isn't "forgot to update the plan" — it's "was going to, at the end, and the end kept moving." Update in the flow of the work, at these moments:

1. **Task branching** — new scope surfaces → log it (new Action, or a Log note) before starting it.
2. **Decision points** — chose A over B → write the *why* into the Log right then, not from memory later.
3. **Intermediate checkpoints** — long task → drop a one-line Log update partway through, so an interruption doesn't lose the trail.
4. **Task completion** — check the box the moment it's true, not batched.
5. **Bubbling up the hierarchy** — check one level up, every time:

   | Completed/changed | Check | Why |
   |---|---|---|
   | Action | parent Design — all children done? | Keeps rollups honest |
   | Design | parent Project | Same, one level up |
   | Project | `parent_master_plan` | Master Plans are what stakeholders actually read |
   | Master Plan shifts | `parent_thesis` — still supported? | Theses should track reality |
   | Anything BLOCKED | FOCUS.md's Blocked section | Coherence Rule 3, applied the moment you learn it |

Full rationale (why this needed spelling out): [`WORKFLOW_DETAILS.md` § Extended Rationale](WORKFLOW_DETAILS.md#extended-rationale).

---

## Files and Their Purpose

| File | Purpose | Update trigger |
|---|---|---|
| **FOCUS.md** | "What are we doing right now?" | Whenever active work shifts |
| **CHANGELOG.md** (append-only) | "What decisions were made, when?" | Status/priority changes, resolved blockers |
| **REFLECTION.md** (append-only) | "What did we learn?" | Non-obvious discoveries or constraints |
| **INDEX.md** (generated) | Current state snapshot | `plan generate-index`, after large+ changes |
| **Entity files** (P/D/A/T/M/C) | Source of truth per entity | Continuously, as work happens |

---

## AI Agent Memory Maintenance

When an AI agent maintains a persistent memory file (e.g. `~/.claude/projects/.../memory/MEMORY.md`), that file's **Plans section** is the only plan content guaranteed to be in context at session start without an explicit read. Keep it current and compact.

### Rules

**At session start** — read `plan/FOCUS.md` and `plan/INDEX.md` before working. These are not auto-loaded; they must be explicitly read.

**When plan state changes** — update MEMORY.md's Plans section to match. This is a Level 1 change (entity only), but failing to do it means the next session starts with stale context.

**When MEMORY.md exceeds ~150 lines** — prune it. Move verbose detail into topic files (already linked from MEMORY.md); keep only the *non-obvious* rule or the *pointer* to where to look. Bug fix details belong in git history, not memory.

**What the Plans section should contain** — one line per active entity (non-DONE, non-DEFERRED, non-CANCELLED): ID, status/priority, and the single most useful orienting fact. DONE items can be removed. Example:

```markdown
## Plans
- P003 `PLANNING/HIGH` — Headless bot. Phase 1 next: ECS world + tick loop.
- D018 `PLANNING` — BotSession control surface (P003). 5-step migration, Step 1 next.
- A011 `IN_PROGRESS` — Account Registry implementation.
```

### Automation target

`plan generate-index` (or a dedicated `plan export-memory` command) should regenerate the Plans section automatically, so it never goes stale. Until that is implemented, update it manually when plan status changes.

---

## Anti-Patterns

- **Workflow overhead** — a CHANGELOG entry for every typo. Scale with impact.
- **FOCUS.md staleness** — it says P001/P002 are active but you're actually on P005. Update it whenever reality shifts.
- **REFLECTION.md emptiness** — untouched for months. Add 1–2 sentences the moment something surprising happens.
- **Blocker invisibility** — a BLOCKED entity nowhere mentioned in FOCUS.md.

---

## External Contribution Workflow (Drive-By Fixes)

For an agent whose real task is in a *different* repo, but who fixes something in lplan's own `src/`, `templates/`, or `schema/` along the way. (Why this gets its own path instead of the rules above: [details](WORKFLOW_DETAILS.md#extended-rationale).)

- **Trivial** (typo, one-liner) → just commit.
- **Bug/layout fix** (most drive-by work) → log one Action under **P009 – External Maintenance**, status `DONE` at creation, one Log line; one `CHANGELOG.md` line (`date | A0xx | NEW → DONE | ...`). Don't touch FOCUS.md, don't triage into P001–P008 — default to P009.
- **New capability/entity type/behavior change** → out of scope for drive-by. Flag to a maintainer, or do the full Level 3 treatment yourself. **Tell the user** plainly that this needs real planning in lplan itself, not a patch made in passing — they may not know lplan has its own workflow at all.
- **Mechanical hook**: commits touching lplan's source carry a `Lplan-Entity: A0xx` (or `Lplan-Entity: none (trivial)`) trailer, so this is greppable.

`P009-external-maintenance.md` is the catch-all — it accumulates small `DONE` actions and never needs a FOCUS.md mention. Re-filing into specific projects is a normal-upkeep-pass job, not a drive-by one.

---

## Framework Updates (lplan Evolution)

When lplan itself changes (new entity types, fields, validation rules), document breaking vs. non-breaking in CHANGELOG.md, add a migration guide if breaking, and update WORKFLOW.md if procedures changed. Full checklist, versioning strategy (semver), and templates for announcements/migration guides: [`WORKFLOW_DETAILS.md` § Framework Updates](WORKFLOW_DETAILS.md#framework-updates-lplan-evolution).

---

## Summary

**The rhythm is not about time, it's about change.** Change scale = workflow scale. Coherence is enforced by rules, not frequency. Self-direct based on what matters. When in doubt, over-document rather than under-document.
