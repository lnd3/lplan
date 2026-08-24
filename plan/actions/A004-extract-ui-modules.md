---
id: A004
title: Extract UI utility module from monolithic server.py
status: DONE
created: 2026-08-21
updated: 2026-08-24
description: Extract UI utility functions (showBanner, hideBanner, showError) into standalone ui.js module.
design: D003
project: P004
priority: HIGH
---

## Goal

Extract the UI utility functions that other modules depend on into a clean, reusable ui.js module. This is a prerequisite for modularizing the rest of the codebase.

## Scope

- Create src/planner/static/ui.js
- Export UI class with showBanner, hideBanner, showError methods
- Update index.html to load ui.js first (dependency for other modules)
- Test that banner/error displays work as before

## Tasks

- [x] Create ui.js with UI class
- [x] Implement showBanner, hideBanner methods
- [x] Implement showError method with timeout
- [x] Export UI to window.UI
- [x] Update HTML template to include ui.js script tag

## Log

2026-08-24 — Completed. ui.js module extracted and tested.
2026-08-21 — Task started as part of UI refactoring.
