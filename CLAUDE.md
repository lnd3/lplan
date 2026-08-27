# lplan

This repo is both a tool (used as a dependency by other repos for their own planning) and self-planned using its own `plan/` directory.

**If you're here to fix something in `src/`, `templates/`, or `schema/` and your actual task lives in a different repo:** don't skip logging it. Read `WORKFLOW.md` § "External Contribution Workflow (Drive-By Fixes)" before committing — it's a short, scaled-down convention (usually just one `CHANGELOG.md` line, sometimes one Action under `plan/projects/P009-external-maintenance.md`) so the fix doesn't vanish from lplan's own audit trail the way recent ones did.

**If you're advancing something already in `plan/`:** follow `WORKFLOW.md`'s normal magnitude-scaled rules instead.

**Tell the user, don't just silently comply.** Before you commit a drive-by change here, say so in plain terms: which entity (if any) you filed it under, and if it looks bigger than "bug fix" — a new capability, entity type, or behavior change — say explicitly that this needs to be planned and done in lplan itself, not patched in passing from another repo's context. The user may not be tracking that this repo has its own plan/workflow; don't assume they know a "quick fix" here actually needs a real project.
