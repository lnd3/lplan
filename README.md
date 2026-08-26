# lplan

> *To make decisions better, faster, and with less waste — in service of an
> existence that is finite and will not be repeated. That is sufficient reason
> to plan well.*

A planning framework that works as a git submodule. Six layers, each answering
one question:

| Layer | Q |
|-------|---|
| `ORIGIN.md` | Why plan at all? |
| `AXIOMS.md` | What constraints apply to every decision? |
| `theses/` T | What do I believe about the world? |
| `master_plans/` M | When are conditions right to act on it? |
| `projects/` P | What will we build? |
| `designs/` D | How? |
| `actions/` A | What, today? |

Plans scale by adding files. Each concern gets its own flat, readable document.

---

## Install & start

```bash
pip install pyyaml click networkx pydantic python-dateutil flask

git submodule add https://github.com/lnd3/lplan deps/lplan
./deps/lplan/bin/plan init ./plan --name "MyProject"
./deps/lplan/bin/plan serve ./plan --edit   # http://127.0.0.1:8000
```

---

## Daily commands

```bash
plan validate ./plan                    # always before committing
plan generate-index ./plan              # rebuild INDEX.md
plan serve ./plan --edit                # browser UI with editing
plan log P001 "done" ./plan --status DONE
plan blocked ./plan
plan priority ./plan
```

---

## File formats

**Thesis** — falsifiable belief. The key section is *What Would Change My Mind.*

```yaml
---
id: T001
title: Falsifiable belief about the world
status: HELD          # HELD · QUESTIONING · ABANDONED
conviction: 8         # 0–10
created: YYYY-MM-DD
updated: YYYY-MM-DD
---
```

**Master Plan** — a thesis made actionable by current conditions. Answers *when*, not *how*.

```yaml
---
id: M001
title: Strategic direction
status: IN_PROGRESS
stakeholder: Name
vision: What changes in the world when this succeeds?
priority: HIGH
parent_thesis: [T001]
goals:
  - Observable external outcome
created: YYYY-MM-DD
updated: YYYY-MM-DD
---
```

**Project**

```yaml
---
id: P001
title: Goal
status: IN_PROGRESS
priority: HIGH
priority_drivers: [strategic_edge]
parent_master_plan: [M001]
created: YYYY-MM-DD
updated: YYYY-MM-DD
---
```

**Design** / **Action** follow the same pattern with `project: P001` / `design: D001`.

---

## Workflow

The [WORKFLOW.md](WORKFLOW.md) in this repo describes **universal procedures** for all repos using lplan:
- Scale-based change rigor (Small/Medium/Large/Massive)
- Coherence rules (state consistency, decision traceability)
- External change detection (agent resumption patterns)
- Framework updates (how changes cascade)

**For your repo:** Copy [templates/WORKFLOW.md.template](templates/WORKFLOW.md.template) to your `plan/WORKFLOW.md` and fill in repo-specific details:
- Who updates FOCUS.md and when?
- How do you integrate with CI/CD?
- What's your escalation path for major decisions?

Your repo's WORKFLOW.md can then reference `deps/lplan/WORKFLOW.md` for universal procedures while defining local customizations.

---

## Status

Standard: `IDEA` · `PLANNING` · `IN_PROGRESS` · `BLOCKED` · `DONE` · `DEFERRED` · `CANCELLED`

Thesis: `HELD` · `QUESTIONING` · `ABANDONED`

---

## Docs

- [QUICK_REFERENCE.md](QUICK_REFERENCE.md)
- [VALIDATION.md](VALIDATION.md)
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- [IMPLEMENTATION.md](IMPLEMENTATION.md)
