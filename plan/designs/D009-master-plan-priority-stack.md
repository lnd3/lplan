---
id: D009
title: Master Plan Priority Stack
status: IDEA
project: P005
created: 2026-08-31
updated: 2026-08-31
doc_link: ""
---

## What

An optional `priority_stack` field on `MasterPlan`: an ordered list of child Project IDs expressing *relative execution priority* among that master plan's projects — which one to work on first when several are live and competing for the same attention, not which one matters most in the abstract.

Out of scope: ranking Designs/Actions within a Project (the user's own instinct, and mine — see the exploratory discussion this design follows from), master-plan-to-master-plan ranking, and anything that touches `depends`/`enables` mechanics directly.

## Why

`priority` (HIGH/MEDIUM/LOW) is an absolute, per-project tier — it doesn't tell you which of two HIGH projects to pick up first when they start overlapping or interacting. `depends`/`enables` express hard ordering (B literally cannot start until A finishes) — but the motivating problem here is *soft* contention: projects that technically could run in parallel, but interact or overlap enough in practice that someone still has to pick an order. Neither existing field captures that. This mirrors D008's own reasoning almost exactly (phases needed a human-authored ordering signal that neither `status` nor the entity graph provided) — same shape of gap, one layer up the hierarchy.

Alternatives considered:
- **Reuse `priority` with finer-grained values** (e.g. HIGH-1, HIGH-2). Rejected — conflates two different questions (how important is this vs. what order should we work on it), and doesn't scale past a handful of tiers.
- **A numeric `stack_rank` field on Project itself.** Rejected — scatters the ordering across N project files instead of keeping it as one ordered list the master plan owns; also makes reordering (swap #2 and #3) require editing two files instead of one.
- **Reuse `depends`.** Rejected outright — `depends` is a hard constraint the graph/validator already enforce cycle-detection and blocking on; overloading it with soft priority would corrupt that meaning for every existing consumer (`DependencyGraph`, `plan blocked`, `plan graph-report`, timeline/capacity computation).

## How

### Field

```python
class MasterPlan(PlanEntity):
    ...
    priority_stack: List[str] = Field(default_factory=list)  # ordered Project IDs, index 0 = highest
```

Frontmatter:
```yaml
priority_stack:
  - P010
  - P007
  - P008
```

### Semantics

- **Ordered, not exhaustive.** A master plan can leave projects out of the stack entirely — only list the ones actually in contention. Projects not listed are simply unranked relative to each other, not deprioritized. This matches the motivating story directly: you don't need a stack until projects start overlapping, and even then only the overlapping ones need ranking.
- **Index 0 = do this one first.** Simple ordinal, not a numeric score — avoids the "what if I want to insert between 2 and 3" problem numeric ranks have; reordering is just moving a list entry.
- **Advisory, not enforced.** Nothing blocks work on a lower-ranked project — same posture as `priority` today. The validator can warn on inconsistency (below) but never errors.

### Validator warnings (new, in `validate_relationships`, alongside A027's checks)

1. **Stack entry isn't actually a child.** A `priority_stack` entry whose Project doesn't list this master plan in its own `parent_master_plan` → warn (`"priority_stack references PXXX, which doesn't list this master plan in parent_master_plan"`). Catches copy-paste errors and stale entries after a project gets reassigned.
2. **Stack contradicts a hard dependency.** If project A is ranked above project B in the stack, but B is in A's `depends` list (A can't even start until B finishes) — warn. This is the one place `priority_stack` and `depends` need to be checked *against* each other, without either mechanism knowing about the other structurally.
3. **Duplicate entries.** The same Project ID appears twice in one stack → warn.

All three are warnings, matching A027's and D008's precedent: soft signals a human resolves, not hard failures.

### UI surfacing

Master Plan's `EntityViewer` content pane (Tree view — see `TreeView.showTreeRoot`'s existing master-plan content pane, which already lists child projects) renders the child-project list in `priority_stack` order first, then any remaining (unranked) children after, visually separated. A ranked entry gets a small ordinal badge (`#1`, `#2`, ...) next to its existing project badge — same visual weight as the progress-percentage badge added earlier, not a new UI pattern.

## Where

**Architectural placement**: `models.py` (field), `parser.py`'s `_parse_master_plan` (frontmatter → model), `validator.py`'s `validate_relationships` (the two new warning checks), `tree.js`'s master-plan content-pane rendering (ordering + ordinal badge). No server.py route changes needed — `priority_stack` rides along on the same `MasterPlan` object every existing endpoint already serializes.

**Data ownership**: Lives entirely in the master plan's own frontmatter, authored by whoever owns that master plan — same lifecycle as `parent_thesis` or `goals`. Not derived, not generated.

## Constraints

- `priority_stack` entries are Project IDs only — no other entity type, and not other master plans (see What → Out of scope).
- Must not require every child project to appear — enforcing exhaustiveness would turn an opt-in convenience into busywork every time a new project is added to the master plan.
- Must not affect `project_rollup()`/`master_plan_rollup()` (A030's checkbox-based progress math) — this is an ordering signal, not a completion signal. Keeping them orthogonal avoids the two features fighting over what a "number" on a master plan means.

## Migration

Non-breaking. `priority_stack` defaults to an empty list; every existing `MasterPlan` file loads unchanged and simply has no stack until someone adds one.

## Testability

Field parsing, empty-list default, and all three validator warnings (non-child entry, depends-contradiction, duplicate) are all pure — testable the same way A027's and D008's checks are, no Flask required.

## Key Decisions

- **Decision**: ordered list, not numeric rank — matches how humans actually think about "do this, then this, then this," and reordering is a list-edit, not a renumbering exercise.
- **Decision**: warnings, never errors — `priority_stack` is advisory the same way `priority` itself is; nothing about it should be able to block `plan validate`.
- **Decision**: scoped to Master Plan → Project only, explicitly *not* extended to Project → Design/Action in this design, even though the user raised it as a plausible future need — see Open Questions.

## Open Questions

- Should Projects eventually get an equivalent `priority_stack` over their own Designs/Actions, for when those start overlapping the way projects did? Deferred per the exploratory discussion that preceded this design: D008's phase model already provides ordering at that layer for most cases, so building a second ordering mechanism there risks solving a problem phases may already cover. Revisit only if a real case surfaces where phases don't resolve it — same bar the master-plan-level need had to clear.
- Should the "stack contradicts `depends`" validator check also look at *transitive* dependencies, not just direct ones? Starting with direct-only for the first pass; transitive checking is a straightforward extension if direct-only turns out insufficient in practice.

## Related

- Project: P005
- Related: D008 (Project Phase → Design/Action Linking — same "advisory ordering the graph doesn't capture" shape, one layer down), A027 (parent-child status consistency — same warnings-not-errors validator posture)

## Log

2026-08-31 — Design written at user request, following an exploratory discussion about whether Project-level ordering was also needed (concluded: not yet, D008's phases likely already cover it — see Open Questions). Not yet implemented — schema/validator/UI work tracked separately once implementation is requested.
