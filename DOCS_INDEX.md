# Documentation Index

Navigation for lplan's documentation. Planning workflow lives in [`WORKFLOW.md`](WORKFLOW.md) (+ [`WORKFLOW_DETAILS.md`](WORKFLOW_DETAILS.md)) — this index is for the tool docs below it.

| Doc | Use it for |
|---|---|
| [`README.md`](README.md) | Framework overview and philosophy |
| [`QUICK_REFERENCE.md`](QUICK_REFERENCE.md) ⭐ | CLI commands, entity types, install — the daily cheat sheet |
| [`TROUBLESHOOTING.md`](TROUBLESHOOTING.md) | Diagnosing installation, validation, and dependency-graph issues |
| [`IMPLEMENTATION.md`](IMPLEMENTATION.md) | Architecture — data models, priority engine, dependency graph, extension points |
| [`tests/`](tests/) | Usage examples via test cases |

## "How do I...?"

| Question | Answer |
|---|---|
| Is my plan valid? | `plan validate ./plan` |
| What are project priorities? | `plan priority ./plan` |
| What depends on P001? | `plan deps P001 ./plan` |
| What's blocking progress? | `plan blocked ./plan` |
| Any circular dependencies? | `plan graph-report ./plan` |

Fixes for specific errors: [`TROUBLESHOOTING.md`](TROUBLESHOOTING.md).

## Quick Start

```bash
pip install pyyaml click networkx pydantic python-dateutil
export PYTHONPATH="${PWD}/src"
plan validate ./plan/
```

See [`QUICK_REFERENCE.md`](QUICK_REFERENCE.md) for everything past that.
