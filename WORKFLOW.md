# lplan Workflow Guide

## Core Principle

**Workflow rigor scales with change magnitude.**

- **Small changes** → minimal workflow overhead (update entity, done)
- **Medium changes** → moderate workflow (update entity + CHANGELOG entry)
- **Large changes** → full workflow (entity + CHANGELOG + FOCUS.md + REFLECTION.md)

The more you change, the more you need to maintain coherence across the plan. Self-direct based on your sense of need, not calendar-based triggers.

---

## External Change Detection (Agent Resumption)

When an agent resumes work (from memory state, stored commit hash, or context), the plan may have changed externally:
- Another agent made commits
- Manual changes were pulled from upstream
- User made direct edits
- External processes modified the codebase

**Detection mechanism**: Track commit hash in agent memory. On resumption, check if current HEAD differs.

### Resumption Checklist

```
On agent resume:
1. Get current commit hash: git rev-parse HEAD
2. Compare to remembered_commit_hash (from agent memory)

If they match:
  → Continue with existing context (no external changes)

If they differ:
  → External change detected. Rebalance perception.
```

### Rebalancing Steps (when external change detected)

**Step 1: Identify scope of change**
```bash
git diff <remembered_commit>..HEAD --name-only
```

**Step 2: Categorize impact**

| Changed File | Impact | Action |
|---|---|---|
| FOCUS.md | High | Re-read. May change what you're supposed to be doing. |
| CHANGELOG.md | Medium | Re-read recent entries. Understand what decisions were made. |
| REFLECTION.md | Medium | Skim for new learnings that might affect strategy. |
| INDEX.md | Low | Snapshot only. Less critical than source files. |
| Entity files (P/D/A/T/M/C) | High | Check if your work conflicts with changed entities. |
| Other files (src/, tests/, etc.) | Medium | Depends on your task. Re-read if related to your work. |
| .git/*, docs/*, config | Low | Usually safe to ignore. |

**Step 3: Decision**

```
If no critical files (FOCUS.md, entities, relevant code) changed:
  → Update commit hash in memory
  → Continue with minimal context refresh
  → Log: "External changes detected (N commits), non-critical files only"

If FOCUS.md or relevant entities changed:
  → Re-read FOCUS.md to understand current priorities
  → Check affected entities for conflicts with your work
  → Consider pivoting or pausing if directions conflict
  → Log: "External changes detected, re-synced FOCUS.md and X entities"

If massive change (>20 files, critical paths modified):
  → Pause work
  → Do full rebalance: re-read FOCUS.md, INDEX.md, CHANGELOG recent entries
  → Re-evaluate whether your current task still makes sense
  → May need to escalate to human decision
  → Log: "Major external changes detected (N commits, M files). Rebalancing..."
```

### Example: Agent Resumption Scenario

**Scenario**: Agent stored `commit_hash = abc123` when it logged off. It resumes and checks.

```
Current HEAD: def456
Commits changed: abc123..def456 (3 commits)

Changed files:
  - FOCUS.md (modified)
  - plan/projects/P007.md (status changed)
  - src/planner/static/status.js (refactored)
  - WORKFLOW.md (documentation)

Decision:
  → FOCUS.md changed: Re-read to see if priorities shifted
  → P007 changed: Check if it affects current work
  → status.js changed: Relevant if agent was working on UI
  → WORKFLOW.md changed: Documentation only, low priority

Action:
  → Re-read FOCUS.md and P007
  → Check git show to see what changed in P007
  → If P007 status now BLOCKED and agent was about to work on it: pivot
  → If unrelated: acknowledge external change, continue work
  → Update memory: commit_hash = def456
  → Log: "Synced external changes: FOCUS and P007 updated, continuing with [current task]"
```

### Memory Storage Pattern

For agents using memory, store:

```json
{
  "last_commit_hash": "def456",
  "last_sync_time": "2026-08-26T15:30:00Z",
  "current_task": "Implement C005 YAML validation",
  "context": "..."
}
```

On resume:
```python
# At start of agent session
import subprocess
current_hash = subprocess.check_output(["git", "rev-parse", "HEAD"]).decode().strip()
remembered_hash = memory.get("last_commit_hash")

if current_hash != remembered_hash:
    print(f"External change detected: {remembered_hash[:8]}..{current_hash[:8]}")
    # Trigger rebalance
    external_change_detected = True
else:
    external_change_detected = False
    print(f"No external changes (still at {current_hash[:8]})")
```

---

## Change Magnitude Levels

### Level 1: Small Change (Single Entity Update)
**Example**: Fix a typo, update a date, bump a status from IDEA to PLANNING

**Workflow trigger**: "This barely affects the plan"

**Actions**:
- Update the entity frontmatter or Log section
- Done. No other files need updating.

**Example**: `A001 status: IDEA → PLANNING`

---

### Level 2: Medium Change (Entity State Transition)
**Example**: Project completes, design gets blocked, dependency resolves

**Workflow trigger**: "This matters for coherence and audit trail"

**Actions**:
1. **Update the entity** (P001 status: IN_PROGRESS → DONE)
2. **Log to CHANGELOG.md**
   - *Why*: Creates audit trail. Someone later asks "when did P001 finish?" — CHANGELOG is the answer.
   - *What*: Date | Entity ID | State transition | Reason/decision
   - *Example*: `2026-08-26 | P001 | IN_PROGRESS → DONE | Tier 1 engine complete`
3. **Update FOCUS.md if applicable**
   - *Why*: If this project was a blocker or active work, FOCUS.md should reflect it's now done or shifted
   - *What*: Remove from Active section, move to Completed, or note unblocking if it unblocked others

---

### Level 3: Large Change (Multiple Entities or Direction Shift)
**Example**: Pivot strategy, resolve critical blocker that unblocks 5 projects, discover major constraint, major refactoring

**Workflow trigger**: "This changes how we think about the plan going forward"

**Actions**:
1. **Update all affected entities** (frontmatter, status, priority, depends/enables)
2. **CHANGELOG.md entries** for each significant change
   - Include *why* the decision was made, not just *what* changed
   - Example: `2026-08-26 | P005 priority → HIGH | Master plan feature unblocks P008 cross-repo work`
3. **FOCUS.md rewrite** (or major edit)
   - *What are we doing now* in light of this change?
   - Which blockers are resolved, which are new?
   - Priority order shift?
   - Active vs deferred work?
4. **REFLECTION.md entry**
   - *Why*: Large changes often reveal non-obvious patterns or assumptions that should shape future planning
   - *What*: What did we learn? What constraint became visible? What changes how we'll structure future work?
   - *Example*: "Master plan architecture revealed that strategy/execution separation is critical. Future projects should declare parent_master_plan upfront, not retrofit it."

---

### Level 4: Massive Change (Reframing or Major Learning)
**Example**: Hypothesis disproven, fundamental architectural decision revised, major new capability discovered

**Workflow trigger**: "This changes the game. Everything else needs to be re-evaluated in light of this."

**Actions**:
1. All of Level 3
2. **INDEX.md regeneration** (run `plan generate-index`)
   - *Why*: Massive changes often affect visibility and relationships
3. **Consider entity lifecycle adjustments**
   - Should any theses move from HELD to QUESTIONING?
   - Should any master plans be deferred or reactivated?
   - Should any concepts be marked DEPRECATED?
4. **Extended REFLECTION.md section**
   - Document the discovery process (what led us here?)
   - Document the implications (what changes now?)
   - Document the decision (why this direction, not alternatives?)

---

## Coherence Rules (Always)

Regardless of change magnitude, maintain these invariants:

### Rule 1: State Consistency
- **If** an entity's frontmatter status is IN_PROGRESS
- **Then** either:
  - It appears in FOCUS.md Active section, OR
  - CHANGELOG.md explains why it's paused/blocked

### Rule 2: Decision Traceability
- **If** an entity's priority, status, or depends/enables changed
- **Then** CHANGELOG.md or entity Log section explains why

### Rule 3: Blocker Visibility
- **If** a project/design is BLOCKED
- **Then** FOCUS.md explicitly states the blocker and what unblocks it

### Rule 4: Learning Capture
- **If** you made a surprising discovery or encountered an unexpected constraint
- **Then** REFLECTION.md records it (even brief: 1-2 sentences is enough)

---

## Practical Workflow: Decision Points

When you're using lplan, hit these decision points:

### After Significant Work (Level 2+)
```
Ask yourself: "How much changed?"

[ Small ] → Update entity, done
[ Medium ] → Update entity + CHANGELOG + maybe FOCUS.md
[ Large ] → Entity + CHANGELOG + FOCUS.md + REFLECTION.md
[ Massive ] → Full workflow + re-evaluate related entities + INDEX regenerate
```

### When Priorities Shift
```
Q: Are the changes fundamental or tactical?

Tactical (reordering existing work) → FOCUS.md update only
Fundamental (strategy shifted) → CHANGELOG entry explaining why + REFLECTION.md on implications
```

### When You Discover a Constraint
```
Q: Does this affect future planning?

No impact → Log it in entity Log section
Moderate impact → REFLECTION.md + update related entities if blocked
High impact → Full Level 3 workflow + consider revising theses/master plans
```

### When Work Completes or Blocks
```
Always: Update entity status
Medium+ change:
  - Add CHANGELOG entry
  - Update FOCUS.md if this was active work or blocking others
  - REFLECTION.md if you learned something non-obvious
```

---

## Workflow Checklist by Change Magnitude

### Small Change Checklist
- [ ] Entity updated (frontmatter or Log)
- [ ] Done

### Medium Change Checklist
- [ ] Entity updated
- [ ] CHANGELOG.md entry added (date, ID, transition, why)
- [ ] FOCUS.md updated if applicable (blocker resolved, active work shifted)

### Large Change Checklist
- [ ] All affected entities updated
- [ ] CHANGELOG.md entries for each significant change (include reasoning)
- [ ] FOCUS.md rewritten or substantially revised
- [ ] REFLECTION.md entry capturing non-obvious learnings
- [ ] Related entities checked (did this resolve/create new dependencies?)

### Massive Change Checklist
- [ ] All of Large Change
- [ ] INDEX.md regenerated (`plan generate-index`)
- [ ] Theses/Master Plans reviewed (any status shifts needed?)
- [ ] Extended REFLECTION.md covering discovery → decision → implications

---

## Files and Their Purpose

### FOCUS.md (Living Document)
**Update frequency**: With work sessions and direction shifts  
**Purpose**: "What are we doing right now?"  
**Contains**: Active work, blockers, next priorities, recently unblocked items  
**Update trigger**: Whenever your sense of "what's active" changes significantly

### CHANGELOG.md (Append-Only Audit Trail)
**Update frequency**: When entity states transition meaningfully  
**Purpose**: "What decisions were made and when?"  
**Contains**: Date, entity ID, state transition, decision rationale  
**Update trigger**: Status changes, priority changes, resolved blockers, strategic shifts

### REFLECTION.md (Append-Only Learnings)
**Update frequency**: When you discover non-obvious patterns or constraints  
**Purpose**: "What did we learn that changes how we plan?"  
**Contains**: Discoveries, surprising constraints, decision rationale for non-obvious choices, patterns  
**Update trigger**: Whenever you realize "this changes how we should structure future work"

### INDEX.md (Generated Dashboard)
**Update frequency**: After large/massive changes, or manually when you want a snapshot  
**Purpose**: "Current state of all entities"  
**Contains**: All projects, designs, actions organized by status and priority  
**Update trigger**: Run `plan generate-index` after large refactorings or at natural breakpoints

### Entity Files (P/D/A/T/M/C)
**Update frequency**: Continuous as work happens  
**Purpose**: Source of truth for individual entities  
**Contains**: Frontmatter (structured data) + Body (Goal/Scope/Tasks/Log)  
**Update trigger**: Every status change, every decision, every learning specific to that entity

---

## Anti-Patterns

### ❌ Workflow Overhead
Updating CHANGELOG.md for every single typo or minor adjustment. That's noise.

**Fix**: Scale with impact. Typos don't need changelog entries. Status transitions do.

### ❌ FOCUS.md Staleness
FOCUS.md says "Active: P001, P002" but you're actually working on P005. Nobody trusts it.

**Fix**: Update FOCUS.md whenever your actual active work shifts. It should always reflect reality.

### ❌ REFLECTION.md Emptiness
REFLECTION.md untouched for months. No learning captured.

**Fix**: The moment you realize something surprising or important, add 1-2 sentences. Doesn't need to be polished.

### ❌ Blocker Invisibility
A project is BLOCKED but FOCUS.md doesn't mention it. Only discoverable by reading frontmatter.

**Fix**: BLOCKED projects and their blockers belong in FOCUS.md. Always.

---

## Examples

### Example 1: Small Change
**What happened**: Fixed typo in P001 title (was "Tier 1 - Pythom" → "Tier 1 - Python")

**Workflow**:
```
✓ Update P001 frontmatter
✓ Done (no CHANGELOG, no FOCUS.md, no REFLECTION.md needed)
```

---

### Example 2: Medium Change
**What happened**: P004 (Web Refactoring) completed today

**Workflow**:
```
✓ Update P004 status: IN_PROGRESS → DONE
✓ Add CHANGELOG entry:
  "2026-08-26 | P004 | IN_PROGRESS → DONE | Web refactoring complete, UI modularized (21.6KB server)"
✓ Update FOCUS.md:
  - Remove P004 from Active
  - Add to Completed
  - Note that P005 (Master Plans) is now unblocked
```

---

### Example 3: Large Change
**What happened**: Discovered that hierarchical entity model (Thesis→MasterPlan→Project→Design→Action) is fundamental to lplan. Needs documentation and formalization.

**Workflow**:
```
✓ Create C001-hierarchical-entity-model.md (Concept)
✓ Update related entities (P005, P006 now reference this)
✓ CHANGELOG entry:
  "2026-08-26 | C001 | NEW | Hierarchical entity model formalized as core concept"
✓ Update FOCUS.md:
  - Add to Active: "Concept documentation" as ongoing
  - Note that this enables future cross-repo work
✓ REFLECTION.md entry:
  "Pattern recognition: 5-level hierarchy (T→M→P→D→A) emerged as natural scale structure
   for planning. Future projects should use this layer mapping upfront. Enables better
   traceability from vision to execution."
```

---

### Example 4: Massive Change
**What happened**: Realized that API/schema design has a fundamental flaw. Requires rearchitecting Status view, rethinking entity relationships, affects 3 active projects.

**Workflow**:
```
✓ Re-architect entity model (T, P, D, A, M, C all updated as needed)
✓ Update all affected entity frontmatters (reprioritize, add blockers, mark as BLOCKED as needed)
✓ CHANGELOG entries for each:
  "2026-08-26 | C003 | STATUS→DRAFT | Event delegation pattern requires rethinking for async events"
  "2026-08-26 | P007 | PRIORITY→HIGH | Analytics dashboard unblocked by C003 rearchitecture"
  "2026-08-26 | P008 | NEW BLOCKER | Awaiting C003 completion to proceed with cross-repo API"
✓ FOCUS.md complete rewrite:
  - Active work now: C003 fix, P007 redesign
  - Blockers: P008 waiting on C003
  - Deferred: P006 until C003 stable
✓ REFLECTION.md entry:
  "Constraint discovery: Entity relationship model had O(n²) growth in API surface.
   Rearchitecting to graph-based model reduces to O(n). This changes how we'll design
   future entity types. Always validate API surface early."
✓ Run `plan generate-index` to snapshot new state
✓ Check theses: Do T001/T002 still hold? (Yes, but implementation changed)
```

---

---

## Framework Updates (lplan Evolution)

When lplan itself changes (new entity types, new fields, workflow updates, validation rules), existing users need to understand what changed and whether they need to migrate.

### Communicating Framework Changes

**In the lplan repository**:
- Update CHANGELOG.md to document breaking vs non-breaking changes
- Update MIGRATION.md (if exists) or add migration guide for major changes
- Update templates and schema documentation
- Update WORKFLOW.md if procedures change

**Announcement checklist for lplan maintainers**:

1. **Tag the change type**:
   - ✅ **Non-breaking**: New optional fields, new entity types (can be adopted gradually)
   - ⚠️ **Breaking**: Required new fields, status enum changes, validation rule changes (may invalidate existing plans)

2. **Document the change**:
   ```markdown
   # lplan v2.1 (2026-08-26)

   ## New: Concept Entity Type
   - Can be used for validated abstractions (modes, terms, patterns, constraints, rules, findings)
   - Optional field: `type` with values mode|term|pattern|constraint|rule|finding
   - Status: STABLE | DRAFT | DEPRECATED
   - Non-breaking: existing plans work unchanged

   ## New: Thesis Status Enum
   - Theses now accept: HELD | QUESTIONING | ABANDONED
   - Previously: general statuses only
   - Breaking for theses; non-breaking for other entities

   ## Updated: WORKFLOW.md
   - Added scale-based workflow (change magnitude → workflow rigor)
   - Added external change detection for agent resumption
   - See MIGRATION.md for how this affects existing workflows
   ```

3. **Provide migration guide** (if breaking):
   ```markdown
   # Migrating to lplan v2.1

   ## If you have Thesis entities:
   - Status values changed. Update theses to use: HELD | QUESTIONING | ABANDONED
   - Run: `plan validate ./plan` to find outdated status values
   - Migration effort: ~5 minutes per thesis

   ## If you have Project entities:
   - New optional field: `parent_master_plan`
   - Existing projects unaffected (field is optional)
   - Adopt gradually as you link projects to master plans

   ## If you use FOCUS.md:
   - Workflow changed: see WORKFLOW.md for scale-based procedures
   - Update FOCUS.md structure? Optional, old format still works
   - Recommended migration: adopt new scale-based workflow on next major change
   ```

### User-Side: Detecting lplan Updates

When users pull lplan updates:

**Checklist**:
```
1. Check git log for lplan repo
   git log --oneline deps/lplan | head -20

2. Read what changed
   cat deps/lplan/CHANGELOG.md | head -50

3. Assess impact
   - New optional features? (✅ adopt when ready)
   - Breaking changes? (⚠️ may need plan updates)
   - Workflow changes? (⚠️ update procedures)

4. If breaking changes, migrate
   - Run plan validate to find issues
   - Update entities as needed
   - Commit migration: "Migrate to lplan vX.Y: [what changed]"

5. If non-breaking, decide
   - Adopt new features immediately? (Concept type, new fields)
   - Adopt gradually? (When relevant to your work)
   - Defer? (Still works with old approach)
```

### Example: Adding Concept Type (Non-Breaking)

**Announcement**:
```
New in lplan: Concept entity type
- Use for validated abstractions that affect multiple projects
- Non-breaking: existing plans work unchanged
- Optional adoption: start using when you identify patterns worth formalizing
```

**User migration**:
- No action required to stay current
- Adopt when useful: extract patterns into concepts as they emerge
- Example: when you discover "event delegation is a pattern we'll use everywhere"
  - Create C001-event-delegation.md
  - Reference from related project/design entities
  - Update REFLECTION.md on why this pattern matters

---

### Example: Adding Required Field (Breaking)

**Announcement**:
```
Breaking in lplan v2.1: Projects now require parent_master_plan field

- This field links projects to strategic master plans
- Existing projects missing this field will fail validation
- Migration required: either add parent_master_plan or leave empty (if independent)
```

**User migration**:
1. Pull lplan changes
2. Run `plan validate ./plan` → errors on projects without field
3. For each project, decide:
   - Does it serve a master plan? Add to parent_master_plan field
   - Is it independent? Add `parent_master_plan: []` to frontmatter
4. Re-run validate: should pass
5. Commit: `plan validate pass after lplan v2.1 migration`

---

### Versioning Strategy

lplan versions follow semver:
- **MAJOR** (1.0 → 2.0): Breaking changes to schema or workflow
- **MINOR** (1.5 → 1.6): Non-breaking additions (new fields, new entity types)
- **PATCH** (1.5.1 → 1.5.2): Documentation, non-functional changes

**Breaking changes**: New required fields, status enum changes, validation rule changes  
**Non-breaking**: New optional fields, new entity types, new procedures (old ones still work)

---

### Workflow for lplan Maintainers: Announcing Changes

When you change lplan (add entity type, change validation, update procedures):

1. **Update the code/templates/docs** in lplan repo
2. **Classify the change**: breaking or non-breaking?
3. **Update CHANGELOG.md** (in lplan repo):
   ```markdown
   ## vX.Y (date)
   - [BREAKING/NEW] Description of change
   - Migration impact: [who needs to do what]
   - Migration effort: [quick/moderate/significant]
   ```
4. **Update MIGRATION.md** (if breaking)
5. **Bump version** in appropriate location (MAJOR/MINOR/PATCH)
6. **Update this WORKFLOW.md** if procedures changed
7. **Notify users** (via README, announcement, etc.)

---

## Summary

**The rhythm is not about time, it's about change.**

- **Change scale = Workflow scale**
- **Coherence is enforced by rules, not by frequency**
- **Self-direct based on your sense of what matters**
- **When in doubt, over-document rather than under-document**

Use lplan as a living tool, not a static template. The workflow adapts to what you're actually building.
