---
id: C002
title: Modular Architecture
type: pattern
status: STABLE
created: 2026-08-21
updated: 2026-08-26
related:
  - P004
  - D003
  - A004
---

## Goal

Break monolithic code into separate, independently-testable modules, each with a single responsibility and clear exports.

## Pattern Description

### Structure

- **One file = one responsibility** (FileBrowser handles files, TreeView handles hierarchy, etc.)
- **Class-based modules** — each file exports a single class
- **Explicit exports** — `window.ClassName = ClassName` for consumption
- **No implicit dependencies** — state passed explicitly, not in globals

### Frontend Application

**Before (P004):**
- 71KB monolithic server.py
- HTML generation mixed with business logic
- 1,568 lines in single file
- CSS inlined in Python constants

**After (P004):**
- 21.6KB server.py (70% reduction)
- 8 separate JavaScript modules (ui.js, files.js, tree.js, status.js, etc.)
- 9.7KB external stylesheet (style.css)
- Each module independently testable

### Modules in lplan

- **UI** — utility methods (showBanner, showError)
- **FileBrowser** — file tree navigation
- **FileSearch** — search with fuzzy matching
- **FileEditor** — CodeMirror integration
- **FilePreview** — markdown rendering
- **TreeView** — hierarchical navigation
- **Analytics** — dashboard and charts
- **StatusView** (ItemsView) — table with filtering/sorting
- **EntityViewer** — modal popup for entity details
- **Dispatcher** — centralized event routing

## Benefits

- **Maintainability** — each module has clear scope
- **Testability** — modules can be tested in isolation
- **Reusability** — same module used across multiple pages
- **Onboarding** — new developers understand scope quickly
- **Extensibility** — new modules follow established patterns

## Trade-offs

- **Requires discipline** — easy to create tangled dependencies
- **Event coordination** — multiple modules need careful state sync
- **Initial complexity** — more files to navigate vs monolithic

## Log

2026-08-26 — Formalized as reusable pattern.
2026-08-21 — Pattern validated through P004 refactoring (100 tests passing).
