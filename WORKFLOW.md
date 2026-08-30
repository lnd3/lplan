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

If you keep a persistent memory file (e.g. `~/.claude/projects/.../memory/MEMORY.md`), its **Plans section** is the only plan content guaranteed in context at session start — `plan/FOCUS.md`/`INDEX.md` are not auto-loaded, read them explicitly.

- Update the Plans section whenever plan state changes (Level 1 — but skipping it means next session starts stale).
- Keep it under ~150 lines: one line per active (non-DONE/DEFERRED/CANCELLED) entity — ID, status/priority, one orienting fact. Prune past that; move detail to topic files, not memory.

Format and rationale: [`WORKFLOW_DETAILS.md` § AI Agent Memory Maintenance](WORKFLOW_DETAILS.md#ai-agent-memory-maintenance).

---

## Anti-Patterns

- **Workflow overhead** — a CHANGELOG entry for every typo. Scale with impact.
- **FOCUS.md staleness** — it says P001/P002 are active but you're actually on P005. Update it whenever reality shifts.
- **REFLECTION.md emptiness** — untouched for months. Add 1–2 sentences the moment something surprising happens.
- **Blocker invisibility** — a BLOCKED entity nowhere mentioned in FOCUS.md.

---

## External Contribution Workflow (Drive-By Fixes)

For an agent whose real task is in a *different* repo, but who touches lplan itself along the way. (Why this gets its own path instead of the rules above: [details](WORKFLOW_DETAILS.md#extended-rationale).)

**First, what kind of change is it:**

- **Trivial** (typo, one-liner in `src/`/`templates/`/`schema/`) → just commit.
- **Bug/layout fix** (most drive-by work — a defect fixed in isolation, behavior unchanged) → log one Action under **P009 – External Maintenance**, status `DONE` at creation, one Log line; one `CHANGELOG.md` line (`date | A0xx | NEW → DONE | ...`). Don't touch FOCUS.md, don't triage into P001–P008 — default to P009.
- **Anything that changes *policy*, not just code** — edits to `WORKFLOW.md`, `WORKFLOW_DETAILS.md`, `templates/*`, `CLAUDE.md`, or `README.md`; a new entity type, field, or status value; any new capability or behavior change → **never a silent drive-by `DONE`, no matter how small it looks.** These files are what every project using lplan inherits — see the generalization test below before even proposing one. **Flag it to the user explicitly, in your own words, before or immediately after landing it** — not just a CHANGELOG line they'd have to go looking for. Say what changed, why, and that it affects every lplan-based repo, not just the one you were working in. If you're not equipped to have that conversation, don't land it — do the full Level 3 treatment and let a maintainer decide instead.

**Before proposing a policy change, ask: does this generalize?** A rule worth adding to lplan should have real potential to improve outcomes for projects using lplan *in general* — not just codify how your originating repo happens to work. If it's genuinely repo-specific (a local convention, a project's own quirks), it belongs in *that* repo's own `plan/WORKFLOW.md`, not lplan's. When in doubt, err toward local and mention the idea to the user rather than upstreaming it uninvited.

**Mechanical hook**: commits touching lplan's source carry a `Lplan-Entity: A0xx` (or `Lplan-Entity: none (trivial)`) trailer, so this is greppable.

`P009-external-maintenance.md` is the catch-all for the Bug/layout fix case — it accumulates small `DONE` actions and never needs a FOCUS.md mention. Re-filing into specific projects is a normal-upkeep-pass job, not a drive-by one. Policy changes never go through P009 silently, regardless of how the commit is otherwise structured.

---

## Framework Updates (lplan Evolution)

When lplan itself changes (new entity types, fields, validation rules), document breaking vs. non-breaking in CHANGELOG.md, add a migration guide if breaking, and update WORKFLOW.md if procedures changed. Full checklist, versioning strategy (semver), and templates for announcements/migration guides: [`WORKFLOW_DETAILS.md` § Framework Updates](WORKFLOW_DETAILS.md#framework-updates-lplan-evolution).

---

## Summary

**The rhythm is not about time, it's about change.** Change scale = workflow scale. Coherence is enforced by rules, not frequency. Self-direct based on what matters. When in doubt, over-document rather than under-document.
