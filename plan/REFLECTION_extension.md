# REFLECTION Extension

Detail for `REFLECTION.md` entries too long for a one-liner. Anchors match the `→` references in the main file.

## focus-changelog-drift

**FOCUS.md/CHANGELOG.md drift is easy to miss because entities themselves stay accurate.** Between 2026-08-24 and 2026-08-27, P004/P005/P006 were completed, M001/M002/T001-T003/C001-C005 were all created, but FOCUS.md still read "COMPLETE, all tiers delivered" and CHANGELOG.md's last entry was from 2026-08-22. The entity frontmatter was never wrong — only the two documents meant to summarize it went stale, because nothing forces their update the way a status field forces itself to be read. Several small, real UI commits (Concept-type addition, thesis↔master_plan link display, badge conventions) also landed with no P/D/A entity behind them at all, so there was nothing to trigger a CHANGELOG entry even in principle.

**Takeaway**: treat "does FOCUS.md/CHANGELOG.md still match `git log` + entity frontmatter?" as a cheap check worth running whenever resuming work, not just after self-directed large changes — see WORKFLOW_DETAILS.md's External Change Detection section, which covers exactly this case but is easy to skip if you don't suspect drift.

## bubbling-up-origin

The FOCUS/CHANGELOG drift above wasn't a one-off. Implementing P010 itself, plan-entity updates got batched to the end of each work chunk rather than written as things actually happened — decisions, sub-tasks, and two live bugs the user found were all logged in retrospect, reconstructed rather than captured in the moment. The pattern repeats because the incentive is always "finish the actual work first, plan hygiene after" — and after keeps slipping. This is now addressed directly in WORKFLOW.md § "Bubbling Up: Maintain the Plan During Work, Not Just After," which names the specific moments (task branching, decisions, checkpoints, completion, one-level-up propagation) rather than relying on general mindfulness, since general reminders are exactly what this pattern shows gets skipped under load.
