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

## Status

Standard: `IDEA` · `PLANNING` · `IN_PROGRESS` · `BLOCKED` · `DONE` · `DEFERRED` · `CANCELLED`

Thesis: `HELD` · `QUESTIONING` · `ABANDONED`

---

## Docs

- [QUICK_REFERENCE.md](QUICK_REFERENCE.md)
- [VALIDATION.md](VALIDATION.md)
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- [IMPLEMENTATION.md](IMPLEMENTATION.md)
