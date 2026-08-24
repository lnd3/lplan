---
id: D003
title: JavaScript Module Architecture
status: DONE
project: P004
created: 2026-08-21
updated: 2026-08-24
description: Modular class-based architecture for frontend JavaScript with clear exports and event delegation.
---

## Goal

Break monolithic JavaScript into separate, reusable modules that each own a specific UI concern. Each module exports a class that manages state and DOM interactions.

## Design Principles

- **Class-based modules**: Each file exports a single class (UI, FileBrowser, FileSearch, etc.)
- **Exports to window**: `window.ClassName = ClassName` for global access
- **Event delegation**: Single event listener on document; routes via data-attributes
- **Stateless styling**: CSS extracted to style.css; modules manage only behavior
- **No external dependencies**: jQuery, framework-free vanilla JS
- **Async/await patterns**: Promise-based data loading with proper error handling

## Modules

### UI Module
- Utility functions: showBanner, hideBanner, showError
- Dependency: None (loaded first)
- Used by: All other modules

### FileBrowser Module
- Manages file tree loading and display
- Methods: loadTree, renderTree, loadFile, showBrowser
- Dependency: UI, FilePreview
- DOM: #sidebar, #sidebar-content, #preview

### FileSearch Module
- Implements search with fuzzy matching
- Methods: loadFilesForSearch, initSearchInput
- Dependency: UI, FileEditor
- DOM: #search-dropdown, #search-input

### FileEditor Module
- Manages CodeMirror editor instance
- Methods: enterEdit, cancelEdit, saveFile
- Dependency: UI
- DOM: #editor-wrap, #editor

### FilePreview Module
- Renders markdown previews
- Methods: showPreview, interceptLinks, displayParentContext
- Dependency: marked library
- DOM: #preview

### TreeView Module
- Hierarchical tree navigation
- Methods: showTree, showTreeRoot, buildTreeHTML, toggleTreeItem
- Dependency: UI, FilePreview
- DOM: #tree-view, #sidebar

### Analytics Module
- Analytics dashboard rendering
- Methods: showAnalytics, renderAnalyticsDashboard, loadCharts
- Dependency: UI, mermaid library
- DOM: #analytics-dashboard

### StatusView Module
- Table view with filtering and sorting
- Methods: show, loadStatus, render, applyFilters
- Dependency: UI, EntityViewer
- DOM: #status-view

### EntityViewer Module
- Modal popup for entity details
- Methods: show, createModal
- Dependency: marked library
- DOM: document.body (creates modal)

### Dispatcher Module
- Centralized event delegation
- Methods: init
- Registers click handlers and routes via data-action attributes

## Event Flow

1. HTML defines data-action attribute on clickable elements
2. Dispatcher.init() attaches single click listener to document
3. Listener checks event.target.dataset.action
4. Routes to appropriate module method
5. Module updates state and rerenders as needed

## Code Structure

```
static/
  ui.js              (Utilities)
  files.js           (FileBrowser)
  search.js          (FileSearch)
  editor.js          (FileEditor)
  preview.js         (FilePreview)
  tree.js            (TreeView)
  analytics.js       (Analytics)
  status.js          (StatusView)
  viewer.js          (EntityViewer)
  dispatcher.js      (Event routing)
  style.css          (All styling)
```

## Benefits

- **Maintainability**: Each module has single responsibility
- **Testability**: Modules can be tested independently
- **Reusability**: Modules used across multiple pages
- **Performance**: Event delegation reduces listener count
- **Extensibility**: New modules follow established patterns

## Log

2026-08-24 — Design complete. All modules implemented and tested.
2026-08-21 — Design created during P004 planning.
