"""Local web server for browsing and editing plan files."""

from __future__ import annotations

import json
import os
import signal
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict, Optional


_PID_FILE = ".plan-server.pid"


def _pid_path(plan_dir: Path) -> Path:
    return plan_dir / _PID_FILE


def _write_pid(plan_dir: Path, host: str, port: int, edit: bool, validate_on_save: bool) -> None:
    _pid_path(plan_dir).write_text(json.dumps({
        "pid": os.getpid(),
        "host": host,
        "port": port,
        "edit": edit,
        "validate_on_save": validate_on_save,
    }), encoding="utf-8")


def _read_pid(plan_dir: Path) -> Optional[Dict[str, Any]]:
    p = _pid_path(plan_dir)
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return None


def _remove_pid(plan_dir: Path) -> None:
    try:
        _pid_path(plan_dir).unlink()
    except FileNotFoundError:
        pass


def _kill_server(plan_dir: Path) -> bool:
    """Send SIGTERM to the running server. Returns True if a process was found."""
    info = _read_pid(plan_dir)
    if not info:
        return False

    pid = info["pid"]
    try:
        os.kill(pid, signal.SIGTERM)
        # Wait briefly for the process to exit
        for _ in range(20):
            time.sleep(0.1)
            try:
                os.kill(pid, 0)  # check if still alive
            except ProcessLookupError:
                break
    except ProcessLookupError:
        pass  # already dead

    _remove_pid(plan_dir)
    return True


def _check_flask() -> None:
    try:
        import flask  # noqa: F401
    except ImportError:
        print("Flask is required for 'plan serve'. Install it with:")
        print("  pip install flask")
        sys.exit(1)


def _build_tree(plan_dir: Path) -> list[Dict[str, Any]]:
    """Build file tree for the plan directory."""
    tree = []

    # Top-level files first
    for name in ["INDEX.md", "FOCUS.md", "CHANGELOG.md", "REFLECTION.md", "VALIDATION.md", "README.md"]:
        p = plan_dir / name
        if p.exists():
            tree.append({"name": name, "path": name, "type": "file"})

    # Category directories
    for category in ["projects", "designs", "actions"]:
        cat_dir = plan_dir / category
        if not cat_dir.exists():
            continue
        files = sorted(
            ({"name": f.name, "path": f"{category}/{f.name}", "type": "file"}
             for f in cat_dir.glob("*.md")),
            key=lambda x: x["name"],
        )
        if files:
            tree.append({"name": category, "path": category, "type": "dir", "children": files})

    return tree


def _build_hierarchy(plan_dir: Path) -> Dict[str, Any]:
    """Build hierarchy based on actual parent-child relationships."""
    from planner.parser import PlanParser

    try:
        parser = PlanParser()
        files = parser.parse_directory(plan_dir)

        # Collect all entities with their parents
        projects = {}
        designs = {}
        actions = {}

        for path_key, file_data in files.items():
            if isinstance(file_data, dict) and "error" in file_data:
                continue

            # Extract entity from PlanFile
            entity = file_data.entity if hasattr(file_data, 'entity') else file_data

            if hasattr(entity, 'id') and hasattr(entity, 'title'):
                entity_type = entity.__class__.__name__.lower()
                entity_info = {
                    "id": entity.id,
                    "title": entity.title,
                    "path": path_key,
                    "children": []
                }

                if entity_type == "project":
                    projects[entity.id] = entity_info
                elif entity_type == "design":
                    designs[entity.id] = entity_info
                    if hasattr(entity, 'project'):
                        entity_info["parent"] = entity.project
                elif entity_type == "action":
                    actions[entity.id] = entity_info
                    if hasattr(entity, 'design'):
                        entity_info["parent"] = entity.design

        # Build hierarchy: projects with their designs and actions
        hierarchy = {"projects": []}

        for proj_id, proj in sorted(projects.items()):
            proj_node = {"id": proj_id, "title": proj["title"], "path": proj["path"], "children": []}

            # Add designs for this project
            for design_id, design in sorted(designs.items()):
                if design.get("parent") == proj_id:
                    design_node = {"id": design_id, "title": design["title"], "path": design["path"], "children": []}

                    # Add actions for this design
                    for action_id, action in sorted(actions.items()):
                        if action.get("parent") == design_id:
                            action_node = {"id": action_id, "title": action["title"], "path": action["path"]}
                            design_node["children"].append(action_node)

                    proj_node["children"].append(design_node)

            hierarchy["projects"].append(proj_node)

        return hierarchy
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"projects": [], "error": str(e)}


def _read_file(plan_dir: Path, rel_path: str) -> str:
    """Read a file relative to plan_dir. Raises ValueError on path traversal."""
    target = (plan_dir / rel_path).resolve()
    if not str(target).startswith(str(plan_dir.resolve())):
        raise ValueError("Path traversal denied")
    return target.read_text(encoding="utf-8")


def _write_file(plan_dir: Path, rel_path: str, content: str) -> None:
    """Write a file relative to plan_dir. Raises ValueError on path traversal."""
    target = (plan_dir / rel_path).resolve()
    if not str(target).startswith(str(plan_dir.resolve())):
        raise ValueError("Path traversal denied")
    target.write_text(content, encoding="utf-8")


def _validate(plan_dir: Path) -> tuple[bool, str]:
    """Run plan validate and return (passed, output)."""
    result = subprocess.run(
        [sys.executable, "-m", "planner.cli", "validate", str(plan_dir)],
        capture_output=True,
        text=True,
    )
    output = result.stdout + result.stderr
    return result.returncode == 0, output


def _auto_regenerate_index(plan_dir: Path) -> None:
    """Regenerate INDEX.md from current entities (called on view)."""
    try:
        result = subprocess.run(
            [sys.executable, "-m", "planner.cli", "generate-index", str(plan_dir)],
            capture_output=True,
            text=True,
            timeout=5,
        )
        # Silent success; if it fails, just return stale INDEX.md
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass


_HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Plan</title>

<!-- Markdown renderer -->
<script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>

<!-- CodeMirror -->
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.16/codemirror.min.css">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.16/theme/dracula.min.css">
<script src="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.16/codemirror.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.16/mode/markdown/markdown.min.js"></script>

<style>
  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

  body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    font-size: 14px;
    background: #1e1e2e;
    color: #cdd6f4;
    height: 100vh;
    display: flex;
    flex-direction: column;
    overflow: hidden;
  }

  /* ── Toolbar ── */
  #toolbar {
    display: flex;
    align-items: center;
    gap: 0;
    padding: 0;
    background: #181825;
    border-bottom: 1px solid #313244;
    flex-shrink: 0;
  }
  #toolbar button {
    padding: 12px 24px;
    border: none;
    border-bottom: 3px solid transparent;
    background: transparent;
    cursor: pointer;
    font-size: 14px;
    font-weight: 600;
    color: #a6adc8;
    transition: all 0.2s;
  }
  #toolbar button:hover {
    color: #cdd6f4;
    background: rgba(200, 214, 244, 0.05);
  }
  #toolbar button.active {
    color: #89b4fa;
    border-bottom-color: #89b4fa;
  }
  #btn-edit   { background: #313244; color: #cdd6f4; }
  #btn-save   { background: #a6e3a1; color: #1e1e2e; display: none; }
  #btn-cancel { background: #45475a; color: #cdd6f4; display: none; }

  /* ── File toolbar ── */
  #file-toolbar {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 8px 12px;
    background: #1e1e2e;
    border-bottom: 1px solid #313244;
    flex-shrink: 0;
  }
  #file-toolbar .path {
    color: #a6adc8;
    font-size: 12px;
    flex: 1;
    font-weight: 500;
  }
  .file-controls {
    display: flex;
    gap: 6px;
  }
  .file-controls button {
    padding: 4px 10px;
    border-radius: 4px;
    border: 1px solid #313244;
    cursor: pointer;
    font-size: 12px;
    font-weight: 500;
    background: #313244;
    color: #cdd6f4;
  }
  .file-controls #btn-save {
    background: #a6e3a1;
    color: #1e1e2e;
    border-color: #94e2d5;
  }
  .file-controls #btn-cancel {
    background: #45475a;
    color: #cdd6f4;
    border-color: #45475a;
  }

  /* ── Main layout ── */
  #main {
    display: flex;
    flex: 1;
    overflow: hidden;
  }

  /* ── Sidebar ── */
  #sidebar {
    width: 220px;
    flex-shrink: 0;
    background: #181825;
    border-right: 1px solid #313244;
    overflow-y: auto;
    padding: 0;
    display: flex;
    flex-direction: column;
  }
  #sidebar-search {
    flex-shrink: 0;
    padding: 8px;
    border-bottom: 1px solid #313244;
  }
  #search-input {
    width: 100%;
    padding: 6px 8px;
    background: #0f111b;
    border: 1px solid #313244;
    border-radius: 4px;
    color: #cdd6f4;
    font-size: 12px;
    box-sizing: border-box;
  }
  #search-input::placeholder {
    color: #6c7086;
  }
  #search-input:focus {
    outline: none;
    border-color: #89b4fa;
    box-shadow: 0 0 0 2px rgba(137, 180, 250, 0.1);
  }
  #search-dropdown {
    position: absolute;
    top: 100%;
    left: 8px;
    right: 8px;
    background: #0f111b;
    border: 1px solid #313244;
    border-top: none;
    border-radius: 0 0 4px 4px;
    max-height: 300px;
    overflow-y: auto;
    z-index: 10;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.4);
  }
  #sidebar-search {
    position: relative;
  }
  .search-result-item {
    padding: 8px 12px;
    border-bottom: 1px solid #313244;
    cursor: pointer;
    transition: background 0.15s;
  }
  .search-result-item:hover {
    background: #313244;
  }
  .search-result-item:last-child {
    border-bottom: none;
  }
  .search-result-file {
    font-weight: 600;
    color: #89b4fa;
    font-size: 12px;
    margin-bottom: 2px;
  }
  .search-result-preview {
    color: #a6adc8;
    font-size: 11px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }
  #sidebar-content {
    flex: 1;
    overflow-y: auto;
    padding: 8px 0;
  }
  .tree-item.hidden {
    display: none;
  }
  .tree-item.match {
    background: #313244;
    color: #89b4fa;
  }
  .tree-dir.hidden {
    display: none;
  }
  .tree-item {
    display: block;
    padding: 2px 0;
    cursor: pointer;
    font-size: 12px;
    color: #bac2de;
    margin: 0;
  }
  .tree-item > div:first-child {
    display: flex;
    align-items: center;
    gap: 4px;
    padding: 2px 4px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }
  .tree-item.active {
    background: #313244;
    border-radius: 2px;
  }
  .tree-item.active > div:first-child {
    color: #89b4fa;
    background: #313244;
    border-radius: 2px;
  }
  .tree-dir {
    padding: 6px 12px 2px;
    font-size: 11px;
    font-weight: 600;
    color: #6c7086;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    cursor: pointer;
    display: flex;
    align-items: center;
    gap: 4px;
  }
  .tree-dir:hover { color: #9399b2; }
  .tree-dir .arrow { display: inline-block; width: 12px; font-size: 14px; text-align: center; transition: transform 0.15s; }
  .tree-dir.collapsed .arrow { transform: rotate(-90deg); }

  /* ── Resize handle ── */
  #resize-handle {
    width: 4px;
    background: #313244;
    cursor: col-resize;
    flex-shrink: 0;
    transition: background 0.15s;
  }
  #resize-handle:hover {
    background: #45475a;
  }
  #resize-handle.active {
    background: #89b4fa;
  }
  .tree-children.hidden { display: none; }

  /* ── Content ── */
  #content {
    flex: 1;
    overflow: hidden;
    display: flex;
    flex-direction: column;
  }

  /* Preview */
  #preview {
    flex: 1;
    overflow-y: auto;
    padding: 32px 48px;
    line-height: 1.7;
  }
  #preview h1 { font-size: 1.8em; color: #89b4fa; margin-bottom: 12px; border-bottom: 1px solid #313244; padding-bottom: 8px; }
  #preview h2 { font-size: 1.3em; color: #cba6f7; margin: 24px 0 8px; }
  #preview h3 { font-size: 1.1em; color: #f38ba8; margin: 16px 0 6px; }
  #preview p  { margin: 8px 0; color: #cdd6f4; }
  #preview a  { color: #89b4fa; text-decoration: none; }
  #preview a:hover { text-decoration: underline; }
  #preview code {
    background: #313244;
    padding: 1px 5px;
    border-radius: 3px;
    font-family: "JetBrains Mono", "Fira Code", monospace;
    font-size: 0.88em;
    color: #f38ba8;
  }
  #preview pre {
    background: #181825;
    border: 1px solid #313244;
    border-radius: 6px;
    padding: 14px 18px;
    overflow-x: auto;
    margin: 12px 0;
  }
  #preview pre code { background: none; padding: 0; color: #a6e3a1; }
  #preview table {
    border-collapse: collapse;
    width: 100%;
    margin: 12px 0;
    font-size: 13px;
  }
  #preview th {
    background: #313244;
    color: #89b4fa;
    text-align: left;
    padding: 8px 12px;
    border-bottom: 2px solid #45475a;
  }
  #preview td {
    padding: 6px 12px;
    border-bottom: 1px solid #313244;
    color: #cdd6f4;
  }
  #preview tr:hover td { background: #1e1e2e; }
  #preview ul, #preview ol { padding-left: 22px; margin: 6px 0; }
  #preview li { margin: 3px 0; }
  #preview li input[type=checkbox] {
    margin-right: 6px;
    appearance: none;
    -webkit-appearance: none;
    width: 14px;
    height: 14px;
    border: 1.5px solid #6c7086;
    border-radius: 3px;
    vertical-align: middle;
    position: relative;
    top: -1px;
    cursor: default;
    background: transparent;
  }
  #preview li input[type=checkbox]:checked {
    background: #89b4fa;
    border-color: #89b4fa;
  }
  #preview li input[type=checkbox]:checked::after {
    content: '';
    position: absolute;
    left: 2px;
    top: -1px;
    width: 4px;
    height: 8px;
    border: 2px solid #1e1e2e;
    border-top: none;
    border-left: none;
    transform: rotate(45deg);
  }
  #preview blockquote {
    border-left: 3px solid #89b4fa;
    padding-left: 14px;
    color: #9399b2;
    margin: 10px 0;
  }
  #preview hr { border: none; border-top: 1px solid #313244; margin: 20px 0; }

  /* Editor */
  #editor-wrap { flex: 1; display: none; flex-direction: column; overflow: hidden; }
  .CodeMirror { flex: 1; height: 100% !important; font-family: "JetBrains Mono", "Fira Code", monospace; font-size: 13px; line-height: 1.6; }
  .CodeMirror-scroll { overflow-y: auto !important; }

  /* Validation banner */
  #validate-banner {
    display: none;
    padding: 8px 16px;
    font-size: 12px;
    font-family: monospace;
    white-space: pre-wrap;
    border-top: 1px solid #313244;
    max-height: 120px;
    overflow-y: auto;
  }
  #validate-banner.ok    { background: #1e3a2f; color: #a6e3a1; }
  #validate-banner.error { background: #3a1e1e; color: #f38ba8; }

  /* Tree View */
  #tree-view {
    padding: 20px;
    overflow-y: auto;
  }
  .tree-hierarchy {
    list-style: none;
    padding: 0;
    margin: 0;
  }
  .tree-hierarchy li {
    margin: 0;
  }
  .tree-node {
    cursor: pointer;
    color: #bac2de;
    user-select: none;
  }
  .tree-toggle {
    display: inline-block;
    width: 16px;
    margin-right: 4px;
    text-align: center;
    cursor: pointer;
    font-size: 14px;
    color: #a6adc8;
    user-select: none;
    transition: transform 0.15s;
  }
  .tree-item.expanded .tree-toggle {
    transform: rotate(90deg);
  }
  .tree-node-project, .tree-node-design, .tree-node-action {
    /* Plain text styling - no colors, sizes, or margins */
  }
  .tree-node.active {
    background: #313244;
    color: #a6e3a1;
    font-weight: 600;
  }

  /* Analytics Dashboard */
  #analytics-dashboard {
    padding: 20px;
    overflow-y: auto;
  }
  .analytics-header {
    font-size: 1.5em;
    color: #89b4fa;
    margin-bottom: 20px;
    border-bottom: 1px solid #313244;
    padding-bottom: 10px;
  }
  .analytics-section {
    margin-bottom: 30px;
  }
  .section-title {
    font-size: 1.1em;
    color: #cba6f7;
    margin-bottom: 12px;
  }
  .stat-cards {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
    gap: 12px;
    margin-bottom: 20px;
  }
  .stat-card {
    background: #313244;
    border: 1px solid #45475a;
    border-radius: 6px;
    padding: 12px;
    text-align: center;
  }
  .stat-card-value {
    font-size: 1.8em;
    font-weight: bold;
    color: #89b4fa;
    margin-bottom: 4px;
  }
  .stat-card-label {
    font-size: 0.85em;
    color: #a6adc8;
  }
  .analytics-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 0.95em;
  }
  .analytics-table th {
    background: #313244;
    color: #89b4fa;
    padding: 8px;
    text-align: left;
    border-bottom: 1px solid #45475a;
  }
  .analytics-table td {
    padding: 8px;
    border-bottom: 1px solid #1e1e2e;
    color: #cdd6f4;
  }
  .analytics-table tr:hover {
    background: #313244;
  }
  .warning-box {
    background: #3a2a1e;
    border-left: 3px solid #f38ba8;
    padding: 10px 12px;
    margin-bottom: 8px;
    border-radius: 3px;
    color: #f38ba8;
    font-size: 0.9em;
  }
  .positive {
    color: #a6e3a1;
  }
  .critical {
    color: #f38ba8;
  }
</style>
</head>
<body>

<div id="toolbar">
  <button onclick="showBrowser()">📁 Files</button>
  <button onclick="showTree()">🌳 Tree</button>
  <button onclick="showAnalytics()">📊 Analytics</button>
</div>

<div id="main">
  <div id="sidebar">
    <div id="sidebar-search">
      <input type="text" id="search-input" placeholder="🔍 Search files..." />
      <div id="search-dropdown" style="display: none;"></div>
    </div>
    <div id="sidebar-content"></div>
  </div>
  <div id="resize-handle"></div>
  <div id="content">
    <div id="file-toolbar">
      <span class="path" id="current-path">—</span>
      <div class="file-controls">
        <button id="btn-edit"   onclick="enterEdit()">Edit</button>
        <button id="btn-save"   onclick="saveFile()">Save</button>
        <button id="btn-cancel" onclick="cancelEdit()">Cancel</button>
      </div>
    </div>
    <div id="preview"></div>
    <div id="editor-wrap"></div>
    <div id="validate-banner"></div>
    <div id="tree-view" style="display: none;"></div>
    <div id="analytics-dashboard" style="display: none;"></div>
  </div>
</div>

<script>
let currentPath = null;
let currentRaw  = null;
let editor      = null;
let editEnabled = EDIT_ENABLED;

// ── Sidebar ───────────────────────────────────────────────────────────────
async function loadTree() {
  const res  = await fetch('/api/tree');
  const tree = await res.json();
  const sb   = document.getElementById('sidebar-content');
  sb.innerHTML = '';
  renderTree(sb, tree);
}

function renderTree(parent, nodes) {
  for (const node of nodes) {
    if (node.type === 'file') {
      const el = document.createElement('div');
      el.className = 'tree-item';
      el.textContent = node.name;
      el.dataset.path = node.path;
      el.onclick = () => loadFile(node.path);
      parent.appendChild(el);
    } else {
      // Directory header
      const hdr = document.createElement('div');
      hdr.className = 'tree-dir';
      const toggle = document.createElement('span');
      toggle.className = 'arrow';
      toggle.textContent = node.children && node.children.length > 0 ? '-' : '·';
      hdr.appendChild(toggle);
      const nameSpan = document.createElement('span');
      nameSpan.textContent = node.name;
      hdr.appendChild(nameSpan);
      parent.appendChild(hdr);

      // Children container
      const children = document.createElement('div');
      children.className = 'tree-children';
      renderTree(children, node.children);
      parent.appendChild(children);

      hdr.onclick = () => {
        hdr.classList.toggle('collapsed');
        children.classList.toggle('hidden');
        if (node.children && node.children.length > 0) {
          toggle.textContent = children.classList.contains('hidden') ? '+' : '-';
        }
      };
    }
  }
}

// ── Resize handle ─────────────────────────────────────────────────────────
let isResizing = false;
const resizeHandle = document.getElementById('resize-handle');
const sidebar = document.getElementById('sidebar');

resizeHandle.addEventListener('mousedown', (e) => {
  isResizing = true;
  resizeHandle.classList.add('active');
  document.body.style.cursor = 'col-resize';
});

document.addEventListener('mousemove', (e) => {
  if (!isResizing) return;
  const mainRect = document.getElementById('main').getBoundingClientRect();
  const newWidth = e.clientX - mainRect.left;
  if (newWidth > 100 && newWidth < 500) {
    sidebar.style.width = newWidth + 'px';
  }
});

document.addEventListener('mouseup', () => {
  if (isResizing) {
    isResizing = false;
    resizeHandle.classList.remove('active');
    document.body.style.cursor = 'auto';
  }
});

// ── File search ───────────────────────────────────────────────────────────
const searchInput = document.getElementById('search-input');
const searchDropdown = document.getElementById('search-dropdown');
let allFiles = [];
let fileContents = {};

async function loadFilesForSearch() {
  try {
    const res = await fetch('/api/tree');
    const tree = await res.json();
    allFiles = [];
    collectFiles(tree, allFiles);
  } catch (e) {
    console.error('Failed to load files for search:', e);
  }
}

function collectFiles(nodes, arr) {
  for (const node of nodes) {
    if (node.type === 'file') {
      arr.push(node);
    } else if (node.children) {
      collectFiles(node.children, arr);
    }
  }
}

searchInput.addEventListener('input', async (e) => {
  const query = e.target.value.toLowerCase().trim();

  if (!query) {
    searchDropdown.style.display = 'none';
    return;
  }

  const results = [];

  // Search through all files
  for (const file of allFiles) {
    try {
      // Get file content
      const res = await fetch(`/api/file?path=${encodeURIComponent(file.path)}`);
      if (!res.ok) continue;
      const content = await res.text();

      // Search in filename
      const fileName = file.name.toLowerCase();
      const fileMatch = fileName.includes(query);

      // Search in content
      const contentLines = content.split('\n');
      const matches = [];
      contentLines.forEach((line, idx) => {
        if (line.toLowerCase().includes(query)) {
          const preview = line.trim().substring(0, 70);
          matches.push(preview);
        }
      });

      if (fileMatch || matches.length > 0) {
        results.push({
          path: file.path,
          name: file.name,
          preview: matches[0] || '(filename match)',
          matchType: fileMatch ? 'name' : 'content'
        });
      }
    } catch (e) {
      // Skip files that fail to load
    }

    // Limit to first 20 results for performance
    if (results.length >= 20) break;
  }

  // Render results
  if (results.length === 0) {
    searchDropdown.innerHTML = '<div style="padding: 12px; color: #6c7086; text-align: center; font-size: 12px;">No matches found</div>';
    searchDropdown.style.display = '';
    return;
  }

  searchDropdown.innerHTML = results.map((r, i) => `
    <div class="search-result-item" onclick="loadFile('${r.path}')">
      <div class="search-result-file">${r.name}</div>
      <div class="search-result-preview">${r.preview}</div>
    </div>
  `).join('');
  searchDropdown.style.display = '';
});

// Close dropdown when clicking outside
document.addEventListener('click', (e) => {
  if (!e.target.closest('#sidebar-search')) {
    searchDropdown.style.display = 'none';
  }
});

// ── File loading ──────────────────────────────────────────────────────────
async function loadFile(path) {
  const res = await fetch(`/api/file?path=${encodeURIComponent(path)}`);
  if (!res.ok) { showError(`Failed to load: ${path}`); return; }
  currentRaw  = await res.text();
  currentPath = path;

  // Update sidebar highlight
  document.querySelectorAll('.tree-item').forEach(el => {
    el.classList.toggle('active', el.dataset.path === path);
  });

  document.getElementById('current-path').textContent = path;
  hideBanner();
  showPreview(currentRaw);

  // Extract and display parent context
  displayParentContext(currentRaw, path);
}

function displayParentContext(markdown, path) {
  const lines = markdown.split('\n');
  let inFrontmatter = false;
  let parent = null;

  for (const line of lines) {
    if (line.trim() === '---') {
      if (!inFrontmatter) {
        inFrontmatter = true;
        continue;
      } else {
        break;
      }
    }
    if (inFrontmatter && line.includes('parent:')) {
      const match = line.match(/parent:\s*(.+)/);
      if (match) parent = match[1].trim();
    }
  }

  // Display parent as breadcrumb if found
  const pathEl = document.getElementById('current-path');
  if (parent) {
    const type = path.split('/')[0];
    let icon = '📁';
    if (type === 'projects') icon = '📋';
    else if (type === 'designs') icon = '🎨';
    else if (type === 'actions') icon = '✓';

    pathEl.innerHTML = `<span style="opacity: 0.6;">${parent}</span> <span style="opacity: 0.8;">/</span> <span style="font-weight: 500;">${icon} ${path.split('/').pop()}</span>`;
  } else {
    pathEl.textContent = path;
  }
}

async function autoValidateAndPriority() {
  try {
    const validateRes = await fetch('/api/command', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ command: 'validate' })
    });
    const validateData = await validateRes.json();

    const priorityRes = await fetch('/api/command', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ command: 'priority' })
    });
    const priorityData = await priorityRes.json();

    // Show banner with results
    let bannerClass = (validateData.ok && priorityData.ok) ? 'ok' : 'error';
    let bannerText = validateData.output + '\n\n' + priorityData.output;

    const banner = document.getElementById('validate-banner');
    banner.textContent = bannerText;
    banner.className = bannerClass;
    banner.style.display = '';
  } catch (e) {
    console.error('Auto-validation failed:', e);
  }
}

function showPreview(markdown) {
  cancelEdit();
  const preview = document.getElementById('preview');

  // Use preformatted text for CHANGELOG and REFLECTION
  if (currentPath === 'CHANGELOG.md' || currentPath === 'REFLECTION.md') {
    preview.innerHTML = `<pre style="font-family: monospace; font-size: 12px; white-space: pre-wrap; word-wrap: break-word; color: #bac2de;">${markdown.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')}</pre>`;
  } else if (markdown.startsWith('---')) {
    // If content starts with YAML frontmatter, display with formatting
    const parts = markdown.split('---');
    if (parts.length >= 3) {
      const frontmatter = parts[1].trim();
      const body = parts.slice(2).join('---').trim();

      let html = '<div style="padding: 8px 12px;">';

      // Format frontmatter as a table-like structure
      if (frontmatter) {
        html += '<div style="font-size: 11px; color: #6c7086; margin-bottom: 12px;">';
        frontmatter.split('\n').forEach(line => {
          if (line.trim()) {
            const [key, ...valueParts] = line.split(':');
            const value = valueParts.join(':').trim();
            html += `<div style="margin-bottom: 2px;"><span style="color: #6c7086;">${key}:</span> <span style="color: #a6adc8;">${value}</span></div>`;
          }
        });
        html += '</div>';
      }

      // Show body content
      if (body) {
        marked.setOptions({ gfm: true, breaks: false });
        html += marked.parse(body);
      }

      html += '</div>';
      preview.innerHTML = html;
      interceptLinks(preview);
    } else {
      marked.setOptions({ gfm: true, breaks: false });
      preview.innerHTML = marked.parse(markdown);
      interceptLinks(preview);
    }
  } else {
    marked.setOptions({ gfm: true, breaks: false });
    preview.innerHTML = marked.parse(markdown);
    interceptLinks(preview);
  }
  preview.style.display = '';
}

function interceptLinks(container) {
  container.querySelectorAll('a[href]').forEach(a => {
    const href = a.getAttribute('href');
    // Intercept relative links that look like plan files (.md, or path within plan dirs)
    if (!href.startsWith('http://') && !href.startsWith('https://') && !href.startsWith('#')) {
      a.addEventListener('click', e => {
        e.preventDefault();
        // Normalize: strip leading ./ and anchors
        let path = href.replace(/^\.\//, '').split('#')[0];
        loadFile(path);
      });
      a.style.cursor = 'pointer';
    } else if (href.startsWith('http://') || href.startsWith('https://')) {
      // External links open in new tab
      a.target = '_blank';
      a.rel = 'noopener noreferrer';
    }
  });
}

// ── Analytics Dashboard ────────────────────────────────────────────────────
async function showBrowser() {
  // Update tab styling
  const buttons = document.querySelectorAll('#toolbar button');
  buttons.forEach(btn => btn.classList.remove('active'));
  buttons[0].classList.add('active'); // Files button

  document.getElementById('file-toolbar').style.display = 'flex';
  document.getElementById('preview').style.display = '';
  document.getElementById('tree-view').style.display = 'none';
  document.getElementById('analytics-dashboard').style.display = 'none';
  document.getElementById('sidebar').style.display = '';

  // Reload file tree (in case it was replaced by Tree view)
  await loadTree();
}

async function showTree() {
  // Update tab styling
  const buttons = document.querySelectorAll('#toolbar button');
  buttons.forEach(btn => btn.classList.remove('active'));
  buttons[1].classList.add('active'); // Tree button

  document.getElementById('file-toolbar').style.display = 'none';
  document.getElementById('preview').style.display = 'none';
  document.getElementById('tree-view').style.display = 'none';
  document.getElementById('analytics-dashboard').style.display = 'none';

  // Use sidebar for tree navigation like Files view
  document.getElementById('sidebar').style.display = '';
  const sidebarContent = document.getElementById('sidebar-content');
  sidebarContent.innerHTML = '<div style="text-align: center; color: #a6adc8; padding: 20px;">Loading tree...</div>';

  try {
    const res = await fetch('/api/hierarchy');
    const hierarchy = await res.json();

    // Store complete hierarchy for later access
    treeHierarchy = hierarchy.projects || [];

    const html = buildTreeHTML(treeHierarchy);
    sidebarContent.innerHTML = html;

    // Show first project by default
    const preview = document.getElementById('preview');
    if (treeHierarchy.length > 0) {
      await showTreeRoot(treeHierarchy[0].id, treeHierarchy[0].title, 'project', treeHierarchy[0].path);
    } else {
      preview.style.display = '';
      preview.innerHTML = '<div style="padding: 20px; color: #a6adc8; text-align: center;">No items in hierarchy</div>';
    }
  } catch (e) {
    console.error('Failed to load hierarchy:', e);
    sidebarContent.innerHTML = '<div style="color: #f38ba8; padding: 20px;">Failed to load hierarchy</div>';
  }
}

let treeHierarchy = null;
let selectedTreeItem = null;

function buildTreeHTML(projects, indent = 0) {
  let html = '';
  for (const project of projects) {
    const hasChildren = project.children && project.children.length > 0;
    const paddingLeft = indent * 20;

    html += `<div class="tree-item" style="padding-left: ${paddingLeft}px;" id="tree-${project.id}">
      <div style="display: flex; align-items: center;">
        <span class="tree-toggle" onclick="toggleTreeItem(event, '${project.id}', ${hasChildren})">${hasChildren ? '+' : '·'}</span>
        <div class="tree-node tree-node-project" onclick='showTreeRoot("${project.id}", "${project.title}", "project", "${project.path}")' data-id="${project.id}">${project.title}</div>
      </div>
      ${buildChildrenHTML(project, indent + 1)}
    </div>`;
  }
  return html;
}

function buildChildrenHTML(parent, indent) {
  if (!parent.children || parent.children.length === 0) return '';

  let html = `<div id="children-${parent.id}" class="tree-children" style="display: none;">`;
  for (const child of parent.children) {
    const hasGrandchildren = child.children && child.children.length > 0;
    const paddingLeft = indent * 20;
    const childType = parent.children[0].id.charAt(0) === 'D' ? 'design' : 'action';

    html += `<div class="tree-item" style="padding-left: ${paddingLeft}px;" id="tree-${child.id}">
      <div style="display: flex; align-items: center;">
        <span class="tree-toggle" onclick="toggleTreeItem(event, '${child.id}', ${hasGrandchildren})">${hasGrandchildren ? '+' : '·'}</span>
        <div class="tree-node tree-node-design" onclick='showTreeRoot("${child.id}", "${child.title}", "${childType}", "${child.path}")' data-id="${child.id}">${child.title}</div>
      </div>
      ${buildChildrenHTML(child, indent + 1)}
    </div>`;
  }
  html += '</div>';
  return html;
}

function toggleTreeItem(event, id, hasChildren) {
  if (!hasChildren) return;
  event.stopPropagation();

  const childrenDiv = document.getElementById(`children-${id}`);
  const toggle = event.currentTarget;
  const treeItem = document.getElementById(`tree-${id}`);

  if (childrenDiv) {
    const isHidden = childrenDiv.style.display === 'none';
    childrenDiv.style.display = isHidden ? '' : 'none';
    toggle.textContent = isHidden ? '-' : '+';
    if (treeItem) {
      treeItem.classList.toggle('expanded');
    }
  }
}

function highlightTreeItem(id) {
  // Remove highlight from previous selection
  if (selectedTreeItem) {
    const prevItem = document.getElementById(`tree-${selectedTreeItem}`);
    if (prevItem) prevItem.classList.remove('active');
  }

  // Add highlight to new selection
  const item = document.getElementById(`tree-${id}`);
  if (item) {
    item.classList.add('active');
    selectedTreeItem = id;
  }
}

async function showTreeRoot(id, title, type, path) {
  // Support both old param format and new element format
  if (typeof id === 'object' && id.dataset) {
    const element = id;
    id = element.dataset.id;
    title = element.dataset.title;
    type = element.dataset.type;
    path = element.dataset.path;
  }

  // Highlight selected item in tree
  highlightTreeItem(id);

  const preview = document.getElementById('preview');
  preview.style.display = '';
  preview.innerHTML = '<div style="text-align: center; color: #a6adc8;">Loading...</div>';

  try {
    // Fetch file to get frontmatter
    const res = await fetch(`/api/file?path=${encodeURIComponent(path)}`);
    if (!res.ok) throw new Error('File not found');
    const content = await res.text();

    // Parse frontmatter
    const frontmatterMatch = content.match(/^---\n([\s\S]*?)\n---/);
    const body = content.split('---').slice(2).join('---').trim();
    const meta = {};

    if (frontmatterMatch) {
      const lines = frontmatterMatch[1].split('\n');
      for (const line of lines) {
        if (line.includes(':')) {
          const [key, val] = line.split(':').map(s => s.trim());
          meta[key] = val;
        }
      }
    }

    // Get preview content
    const preview_text = meta.ingress || (body.length > 100000 ? body.substring(0, 100000) + '\n... (truncated)' : body);

    // Find current node and render hierarchy
    const currentNode = findNodeInHierarchy(id, treeHierarchy);
    if (!currentNode) throw new Error('Node not found');

    const hierarchyHTML = await renderHierarchyView(currentNode, type, 1);

    // Format type label
    const typeLabel = type.charAt(0).toUpperCase() + type.slice(1);
    const typeIcon = type === 'project' ? '📋' : (type === 'design' ? '🎨' : '✓');
    const typeColor = type === 'project' ? '#89b4fa' : (type === 'design' ? '#a6adc8' : '#9399b2');

    preview.innerHTML = `
      <div style="padding: 8px 12px; max-width: 1000px; margin: 0 auto;">
        <!-- Row 1: Title -->
        <h1 style="color: #cdd6f4; margin: 0 0 2px 0; font-size: 20px; font-weight: 700; line-height: 1.2;">${title}</h1>

        <!-- Row 2: Meta info on one line (type, id, created, status, priority) + Description -->
        <div style="font-size: 10px; color: #6c7086; margin-bottom: 4px;">
          ${typeIcon} ${typeLabel} • ${id}
          ${meta.created ? ` • Created: <span style="color: #a6adc8;">${meta.created}</span>` : ''}
          ${meta.status ? ` • Status: <span style="color: #a6adc8;">${meta.status}</span>` : ''}
          ${meta.priority ? ` • Priority: <span style="color: #a6adc8;">${meta.priority}</span>` : ''}
        </div>
        ${meta.description ? `<div style="color: #a6adc8; font-size: 12px; margin-bottom: 8px;">${meta.description}</div>` : ''}

        <!-- Row 3: Expandable content area with + button -->
        ${preview_text ? `<div style="margin-bottom: 8px; background: rgba(88, 166, 255, 0.1); border-radius: 2px; border: 1px solid rgba(88, 166, 255, 0.2);">
          <div style="padding: 4px 8px; display: flex; align-items: center; gap: 4px; color: #a6adc8; font-size: 10px; cursor: pointer;" onclick="const expanded = this.parentElement.querySelector('.content-expanded'); expanded.style.display = expanded.style.display === 'none' ? '' : 'none'; this.querySelector('.expand-btn').textContent = expanded.style.display === 'none' ? '+' : '-';">
            <span class="expand-btn" style="flex-shrink: 0; width: 12px; text-align: center; font-weight: bold; font-size: 14px; transition: transform 0.15s;">+</span>
            <span>Content</span>
          </div>
          <div class="content-expanded" style="display: none; padding: 4px 8px; border-top: 1px solid rgba(88, 166, 255, 0.2); color: #a6adc8; font-size: 11px; white-space: pre-wrap; word-wrap: break-word; line-height: 1.4; resize: vertical; overflow: auto; max-height: 200px; min-height: 100px;">${preview_text}</div>
        </div>` : ''}

        <!-- Children section with collapse toggle -->
        ${hierarchyHTML ? `<div style="margin-top: 8px;">
          <div style="display: flex; align-items: center; gap: 4px; cursor: pointer; padding: 4px 8px; margin-bottom: 4px;" onclick="const section = this.nextElementSibling; const toggle = this.querySelector('.children-toggle'); section.style.display = section.style.display === 'none' ? '' : 'none'; toggle.textContent = section.style.display === 'none' ? '+' : '-';">
            <span class="children-toggle" style="flex-shrink: 0; width: 12px; font-size: 14px; transition: transform 0.15s;">-</span>
            <span style="font-size: 11px; font-weight: 600; color: #6c7086; text-transform: uppercase;">${type === 'project' ? 'Designs' : 'Actions'}</span>
          </div>
          <div style="padding-top: 8px;">
            ${hierarchyHTML}
          </div>
        </div>` : ''}

        <div style="margin-top: 8px; padding-top: 8px;">
          <button onclick="loadFile('${path}')" style="padding: 4px 8px; background: transparent; color: #89b4fa; border: 1px solid #45475a; border-radius: 2px; cursor: pointer; font-size: 11px; transition: transform 0.15s;">📄 Full Doc</button>
        </div>
      </div>
    `;
  } catch (e) {
    console.error(e);
    preview.innerHTML = `<div style="color: #f38ba8; padding: 20px;">Error loading entity</div>`;
  }
}

function findNodeInHierarchy(id, nodes) {
  for (const node of nodes) {
    if (node.id === id) return node;
    if (node.children) {
      const found = findNodeInHierarchy(id, node.children);
      if (found) return found;
    }
  }
  return null;
}

async function renderHierarchyView(node, type, depth = 0) {
  if (!node.children || node.children.length === 0) return '';

  const childType = type === 'project' ? 'design' : 'action';
  const typeIcon = childType === 'design' ? '🎨' : '✓';
  const bgColor = childType === 'design' ? 'rgba(166, 172, 200, 0.1)' : 'rgba(147, 153, 178, 0.1)';
  const borderColor = childType === 'design' ? 'rgba(166, 172, 200, 0.2)' : 'rgba(147, 153, 178, 0.2)';

  let html = `<div style="margin-left: ${depth * 32}px; margin-top: 8px; padding-top: 8px;">`;

  for (const child of node.children) {
    const hasGrandchildren = child.children && child.children.length > 0;
    const toggleId = `hierarchy-${child.id}`;
    const contentId = `hierarchy-content-${child.id}`;

    // Fetch child data for full display
    let childMeta = {};
    let childPreview = '';
    try {
      const res = await fetch(`/api/file?path=${encodeURIComponent(child.path)}`);
      if (res.ok) {
        const content = await res.text();
        const frontmatterMatch = content.match(/^---\n([\s\S]*?)\n---/);
        const body = content.split('---').slice(2).join('---').trim();
        if (frontmatterMatch) {
          const lines = frontmatterMatch[1].split('\n');
          for (const line of lines) {
            if (line.includes(':')) {
              const [key, val] = line.split(':').map(s => s.trim());
              childMeta[key] = val;
            }
          }
        }
        childPreview = childMeta.ingress || (body.length > 100000 ? body.substring(0, 100000) + '\n... (truncated)' : body);
      }
    } catch (e) {
      console.error('Failed to load child data:', e);
    }

    // 3-row layout for each child item with type-specific colors
    html += `<div style="padding: 8px; background: ${bgColor}; border-radius: 2px; margin-bottom: 4px; border: 1px solid ${borderColor};">
      <!-- Row 1: Title -->
      <h3 style="color: #cdd6f4; margin: 0 0 2px 0; font-size: 14px; font-weight: 700;">${child.title}</h3>

      <!-- Row 2: Meta info on one line -->
      <div style="font-size: 10px; color: #6c7086; margin-bottom: 4px;">
        ${typeIcon} ${childType} • ${child.id}
        ${childMeta.created ? ` • Created: <span style="color: #a6adc8;">${childMeta.created}</span>` : ''}
        ${childMeta.status ? ` • Status: <span style="color: #a6adc8;">${childMeta.status}</span>` : ''}
        ${childMeta.priority ? ` • Priority: <span style="color: #a6adc8;">${childMeta.priority}</span>` : ''}
      </div>
      ${childMeta.description ? `<div style="color: #a6adc8; font-size: 11px; margin-bottom: 4px;">${childMeta.description}</div>` : ''}

      <!-- Row 3: Expandable content area with + button -->
      ${childPreview ? `<div style="background: #1e1e2e; border-radius: 2px; margin-bottom: 8px;">
        <div style="padding: 4px 8px; display: flex; align-items: center; gap: 4px; color: #a6adc8; font-size: 10px; cursor: pointer;" onclick="const expanded = this.parentElement.querySelector('.content-expanded'); expanded.style.display = expanded.style.display === 'none' ? '' : 'none'; this.querySelector('.expand-btn').textContent = expanded.style.display === 'none' ? '+' : '-';">
          <span class="expand-btn" style="flex-shrink: 0; width: 12px; text-align: center; font-weight: bold;">+</span>
          <span>Content</span>
        </div>
        <div class="content-expanded" style="display: none; padding: 4px 8px; border-top: 1px solid #313244; color: #a6adc8; font-size: 11px; white-space: pre-wrap; word-wrap: break-word; line-height: 1.4; resize: vertical; overflow: auto; max-height: 200px; min-height: 100px;">${childPreview}</div>
      </div>` : ''}

      <!-- Children of this item (if any, with toggle arrow) -->
      ${hasGrandchildren ? `
        <div style="display: flex; align-items: center; gap: 4px; margin-top: 4px; cursor: pointer;" onclick="const kids = document.getElementById('${toggleId}-children'); const toggle = document.getElementById('${toggleId}-toggle'); const wrapper = toggle.parentElement; kids.style.display = kids.style.display === 'none' ? '' : 'none'; toggle.textContent = kids.style.display === 'none' ? '+' : '-'; wrapper.classList.toggle('expanded');">
          <span id="${toggleId}-toggle" class="tree-toggle" style="flex-shrink: 0; font-size: 14px; transition: transform 0.15s;">+</span>
          <span style="font-size: 10px; color: #6c7086; font-weight: 600;">${childType === 'design' ? 'Actions' : 'Items'}</span>
        </div>
        <div id="${toggleId}-children" style="display: none; padding-top: 8px; margin-top: 8px;">
          ${await renderHierarchyView(child, childType, depth + 1)}
        </div>
      ` : ''}
    </div>`;
  }

  html += '</div>';
  return html;
}

function toggleHierarchyNode(event, id) {
  const childrenDiv = document.getElementById(`${id}-children`);
  const toggle = document.getElementById(`${id}-toggle`);

  if (childrenDiv) {
    const isHidden = childrenDiv.style.display === 'none';
    childrenDiv.style.display = isHidden ? '' : 'none';
    toggle.textContent = isHidden ? '-' : '+';
  }
}

async function generateReport() {
  const reportBtn = document.getElementById('report-btn');
  const originalText = reportBtn.textContent;
  reportBtn.textContent = '⏳ Generating...';
  reportBtn.disabled = true;

  try {
    const res = await fetch('/api/command', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ command: 'report' })
    });
    const data = await res.json();

    if (data.ok) {
      reportBtn.textContent = '✓ Report generated';
      window.open('/report', '_blank');
      setTimeout(() => {
        reportBtn.textContent = originalText;
        reportBtn.disabled = false;
      }, 2000);
    } else {
      reportBtn.textContent = '✗ Error';
      setTimeout(() => {
        reportBtn.textContent = originalText;
        reportBtn.disabled = false;
      }, 2000);
    }
  } catch (e) {
    console.error('Report generation failed:', e);
    reportBtn.textContent = '✗ Failed';
    setTimeout(() => {
      reportBtn.textContent = originalText;
      reportBtn.disabled = false;
    }, 2000);
  }
}

async function showAnalytics() {
  // Update tab styling
  const buttons = document.querySelectorAll('#toolbar button');
  buttons.forEach(btn => btn.classList.remove('active'));
  buttons[2].classList.add('active'); // Analytics button

  document.getElementById('file-toolbar').style.display = 'none';
  document.getElementById('preview').style.display = 'none';
  document.getElementById('tree-view').style.display = 'none';
  document.getElementById('sidebar').style.display = 'none';

  const dashboard = document.getElementById('analytics-dashboard');
  dashboard.style.display = '';
  dashboard.innerHTML = '<div style="text-align: center; color: #a6adc8;">Loading analytics...</div>';

  try {
    const res = await fetch('/api/analytics');
    if (!res.ok) {
      const text = await res.text();
      console.error('Analytics API error:', res.status, text);
      dashboard.innerHTML = `<div class="warning-box">API Error: ${res.status}</div><pre style="color: #f38ba8; font-size: 0.8em;">${text}</pre>`;
      return;
    }

    const data = await res.json();
    console.log('Analytics data:', data);

    if (!data.ok) {
      const errMsg = data.error || 'Unknown error';
      console.error('Analytics error:', errMsg);
      dashboard.innerHTML = `<div class="warning-box">Error: ${errMsg}</div>`;
      return;
    }

    renderAnalyticsDashboard(data.data);
  } catch (e) {
    console.error('Analytics fetch failed:', e);
    dashboard.innerHTML = `<div class="warning-box">Failed to load analytics: ${e.message}</div><pre style="color: #f38ba8; font-size: 0.8em;">${e.stack}</pre>`;
  }
}

function renderAnalyticsDashboard(analytics) {
  try {
    const dashboard = document.getElementById('analytics-dashboard');
    if (!dashboard) throw new Error('Dashboard element not found');
    if (!analytics) throw new Error('Analytics data is null');

    const metrics = analytics.metrics || {};
    const bottlenecks = analytics.bottlenecks || {};
    const capacity = analytics.capacity || {};
    const impactful = analytics.impactful_projects || [];

    console.log('Rendering with:', { metrics, bottlenecks, capacity, impactful });
    console.log('Analytics keys:', Object.keys(analytics));
    if (typeof metrics !== 'object') throw new Error('Metrics is not an object: ' + typeof metrics);

    let html = '<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">';
  html += '<div class="analytics-header" style="margin: 0;">📊 Analytics Dashboard</div>';
  html += '<button id="report-btn" onclick="generateReport()" style="padding: 8px 16px; background: #313244; color: #89b4fa; border: 1px solid #45475a; border-radius: 4px; cursor: pointer; font-weight: bold;">📊 Generate Report</button>';
  html += '</div>';

  // Summary Stats
  html += '<div class="analytics-section">';
  html += '<div class="section-title">Summary</div>';
  html += '<div class="stat-cards">';

  const projectCount = Object.keys(metrics).length || 0;
  html += `<div class="stat-card">
    <div class="stat-card-value">${projectCount}</div>
    <div class="stat-card-label">Projects</div>
  </div>`;

  html += `<div class="stat-card">
    <div class="stat-card-value">${capacity.total_effort_days || 0}</div>
    <div class="stat-card-label">Days (Total)</div>
  </div>`;

  html += `<div class="stat-card">
    <div class="stat-card-value">${capacity.critical_path_days || 0}</div>
    <div class="stat-card-label">Days (Critical Path)</div>
  </div>`;

  html += `<div class="stat-card">
    <div class="stat-card-value">${capacity.compression_ratio || 1}x</div>
    <div class="stat-card-label">Parallelization Ratio</div>
  </div>`;

  html += '</div></div>';

  // Bottlenecks
  if (bottlenecks.summary) {
    html += '<div class="analytics-section">';
    html += '<div class="section-title">⚠ Bottlenecks</div>';
    html += `<div class="warning-box">${bottlenecks.summary}</div>`;
    if (bottlenecks.blocking_count > 0) {
      html += `<p><strong>${bottlenecks.blocking_count}</strong> blocking project(s)</p>`;
    }
    if (bottlenecks.chain_count > 0) {
      html += `<p><strong>${bottlenecks.chain_count}</strong> deep dependency chain(s)</p>`;
    }
    html += '</div>';
  }

  // Most Impactful Projects
  if (Array.isArray(impactful) && impactful.length > 0) {
    html += '<div class="analytics-section">';
    html += '<div class="section-title">🎯 Most Impactful Projects</div>';
    html += '<table class="analytics-table">';
    html += '<tr><th>Project</th><th>Unblocks</th><th>Downstream</th><th>Impact</th></tr>';

    for (const p of impactful) {
      html += `<tr>
        <td><strong>${p.project_id}</strong></td>
        <td>${p.num_unblocked || 0}</td>
        <td>${p.num_downstream || 0}</td>
        <td>${(p.impact_ratio * 100).toFixed(0)}%</td>
      </tr>`;
    }

    html += '</table></div>';
  }

  // Project Metrics
  const metricKeys = Object.keys(metrics || {});
  if (metricKeys.length > 0) {
    html += '<div class="analytics-section">';
    html += '<div class="section-title">📈 Project Metrics</div>';
    html += '<table class="analytics-table">';
    html += '<tr><th>Project</th><th>Fan-In</th><th>Fan-Out</th><th>Depth</th><th>Criticality</th></tr>';

    try {
      for (const [pid, m] of Object.entries(metrics)) {
        const critColor = (m.criticality || 0) > 0.7 ? 'critical' : '';
        html += `<tr>
          <td><strong>${m.project_id || pid}</strong></td>
          <td>${m.fan_in || 0}</td>
          <td>${m.fan_out || 0}</td>
          <td>${m.depth || 0}</td>
          <td><span class="${critColor}">${(m.criticality || 0).toFixed(2)}</span></td>
        </tr>`;
      }
    } catch (e) {
      console.error('Error rendering metrics:', e);
      html += '<tr><td colspan="5">Error rendering metrics table</td></tr>';
    }

    html += '</table></div>';
  }

  // Timeline
  if (capacity.timeline_phases && Array.isArray(capacity.timeline_phases)) {
    html += '<div class="analytics-section">';
    html += '<div class="section-title">📅 Timeline Phases</div>';
    html += '<table class="analytics-table">';
    html += '<tr><th>Phase</th><th>Projects</th><th>Effort</th><th>Duration</th></tr>';

    for (const phase of capacity.timeline_phases) {
      html += `<tr>
        <td>Phase ${phase.phase}</td>
        <td>${phase.project_count}</td>
        <td>${phase.total_effort_days} days</td>
        <td>~${phase.ideal_duration_days} days</td>
      </tr>`;
    }

    html += '</table></div>';
  } else if (capacity.timeline_phases) {
    console.warn('timeline_phases exists but is not an array:', capacity.timeline_phases);
  }

    // Add charts section
  html += '<div class="analytics-section">';
  html += '<div class="section-title">📈 Charts</div>';
  html += '<div id="charts-container" style="display: grid; grid-template-columns: 1fr; gap: 20px;"></div>';
  html += '</div>';

  dashboard.innerHTML = html;

  // Load and render charts
  loadCharts();
  } catch (e) {
    console.error('Error rendering analytics:', e);
    const dashboard = document.getElementById('analytics-dashboard');
    dashboard.innerHTML = `<div class="warning-box">Rendering error: ${e.message}</div><pre style="color: #f38ba8; font-size: 0.8em;">${e.stack}</pre>`;
  }
}

async function loadCharts() {
  try {
    const container = document.getElementById('charts-container');
    if (!container) return;

    // Load Gantt chart
    try {
      const ganttRes = await fetch('/api/chart/gantt');
      const ganttData = await ganttRes.json();
      if (ganttData.ok && ganttData.svg) {
        const ganttDiv = document.createElement('div');
        ganttDiv.innerHTML = `<div class="section-title">📅 Gantt Chart</div>${ganttData.svg}`;
        container.appendChild(ganttDiv);
      }
    } catch (e) {
      console.error('Error loading Gantt:', e);
    }

    // Load Burndown chart
    try {
      const burndownRes = await fetch('/api/chart/burndown');
      const burndownData = await burndownRes.json();
      if (burndownData.ok && burndownData.svg) {
        const burndownDiv = document.createElement('div');
        burndownDiv.innerHTML = `<div class="section-title">🔥 Burndown Chart</div>${burndownData.svg}`;
        container.appendChild(burndownDiv);
      }
    } catch (e) {
      console.error('Error loading Burndown:', e);
    }
  } catch (e) {
    console.error('Error loading charts:', e);
  }
}

// ── Edit / Save ───────────────────────────────────────────────────────────
function enterEdit() {
  if (!editEnabled || !currentRaw) return;

  const preview = document.getElementById('preview');
  const wrap    = document.getElementById('editor-wrap');

  preview.style.display = 'none';
  wrap.style.display    = 'flex';

  document.getElementById('btn-edit').style.display   = 'none';
  document.getElementById('btn-save').style.display   = '';
  document.getElementById('btn-cancel').style.display = '';

  if (!editor) {
    const textarea = document.createElement('textarea');
    wrap.appendChild(textarea);
    editor = CodeMirror.fromTextArea(textarea, {
      mode: 'markdown',
      theme: 'dracula',
      lineNumbers: true,
      lineWrapping: true,
      autofocus: true,
    });
    editor.getWrapperElement().style.flex = '1';
  }
  editor.setValue(currentRaw);
  editor.refresh();
}

function cancelEdit() {
  document.getElementById('editor-wrap').style.display  = 'none';
  document.getElementById('preview').style.display      = '';
  document.getElementById('btn-edit').style.display     = editEnabled ? '' : 'none';
  document.getElementById('btn-save').style.display     = 'none';
  document.getElementById('btn-cancel').style.display   = 'none';
  hideBanner();
}

async function saveFile() {
  if (!editor || !currentPath) return;
  const content = editor.getValue();

  const res = await fetch(`/api/file?path=${encodeURIComponent(currentPath)}`, {
    method: 'POST',
    headers: { 'Content-Type': 'text/plain; charset=utf-8' },
    body: content,
  });

  const data = await res.json();

  if (!res.ok || !data.ok) {
    showBanner(false, data.output || 'Save failed.');
    return;
  }

  currentRaw = content;
  showBanner(true, data.output || '✓ Saved');
  cancelEdit();
  showPreview(currentRaw);

  // Run validation and priority check after any save
  if (currentPath !== 'README.md' && currentPath !== 'FOCUS.md' && currentPath !== 'REFLECTION.md') {
    setTimeout(() => autoValidateAndPriority(), 300);
  }
}

// ── Banner ────────────────────────────────────────────────────────────────
function showBanner(ok, text) {
  const el = document.getElementById('validate-banner');
  el.className = ok ? 'ok' : 'error';
  el.textContent = text;
  el.style.display = '';
}
function hideBanner() {
  document.getElementById('validate-banner').style.display = 'none';
}
function showError(msg) {
  document.getElementById('preview').innerHTML =
    `<p style="color:#f38ba8">${msg}</p>`;
}


// ── Init ──────────────────────────────────────────────────────────────────
window.onload = async () => {
  if (!editEnabled) {
    document.getElementById('btn-edit').style.display = 'none';
  }
  // Set Files tab as active by default
  document.querySelectorAll('#toolbar button')[0].classList.add('active');
  await loadTree();
  await loadFilesForSearch();
  loadFile('INDEX.md');
};
</script>

</body>
</html>
"""


def create_app(plan_dir: Path, edit: bool = False, validate_on_save: bool = True):
    """Create and return the Flask app."""
    from flask import Flask, jsonify, request, Response
    from planner.parser import PlanParser
    from planner.models import Project
    from planner.graph import DependencyGraph

    app = Flask(__name__)
    app.config["plan_dir"] = plan_dir
    app.config["edit"] = edit
    app.config["validate_on_save"] = validate_on_save

    @app.route("/")
    def index():
        html = _HTML.replace("EDIT_ENABLED", "true" if edit else "false")
        return Response(html, mimetype="text/html")

    @app.route("/api/tree")
    def tree():
        return jsonify(_build_tree(plan_dir))

    @app.route("/api/hierarchy")
    def hierarchy():
        return jsonify(_build_hierarchy(plan_dir))

    @app.route("/api/file")
    def get_file():
        rel = request.args.get("path", "")

        # Auto-regenerate INDEX.md on view (no manual regeneration needed)
        if rel == "INDEX.md":
            _auto_regenerate_index(plan_dir)

        try:
            content = _read_file(plan_dir, rel)
            return Response(content, mimetype="text/plain; charset=utf-8")
        except (ValueError, FileNotFoundError) as e:
            return Response(str(e), status=404)

    @app.route("/api/file", methods=["POST"])
    def put_file():
        if not edit:
            return jsonify({"ok": False, "output": "Edit mode not enabled."}), 403

        rel = request.args.get("path", "")
        content = request.get_data(as_text=True)

        try:
            _write_file(plan_dir, rel, content)
        except (ValueError, OSError) as e:
            return jsonify({"ok": False, "output": str(e)}), 400

        if validate_on_save:
            passed, output = _validate(plan_dir)
            if not passed:
                # Restore original content on validation failure
                try:
                    original = _read_file(plan_dir, rel)
                    # We already wrote it — caller sees the error and keeps editing
                except Exception:
                    pass
                return jsonify({"ok": False, "output": output}), 422
            return jsonify({"ok": True, "output": output})

        return jsonify({"ok": True, "output": "✓ Saved"})

    @app.route("/api/command", methods=["POST"])
    def run_command():
        data = request.get_json(silent=True) or {}
        cmd = data.get("command", "")

        allowed = {"generate-index", "validate", "priority", "report"}
        if cmd not in allowed:
            return jsonify({"ok": False, "output": f"Unknown command: {cmd}"}), 400

        if cmd == "generate-index":
            args = [sys.executable, "-m", "planner.cli", "generate-index", str(plan_dir)]
        elif cmd == "report":
            report_path = plan_dir / "report.html"
            args = [sys.executable, "-m", "planner.cli", "report", str(plan_dir),
                    "--output", str(report_path)]
        else:
            args = [sys.executable, "-m", "planner.cli", cmd, str(plan_dir)]

        result = subprocess.run(args, capture_output=True, text=True)
        output = (result.stdout + result.stderr).strip()
        return jsonify({"ok": result.returncode == 0, "output": output or "✓ Done"})

    @app.route("/api/analytics")
    def get_analytics():
        """Get analytics data (metrics, impact, bottlenecks, capacity)."""
        try:
            from planner.metrics import compute_all_metrics
            from planner.impact import get_most_impactful_projects
            from planner.bottleneck import detect_bottlenecks
            from planner.capacity import analyze_capacity

            parsed = PlanParser.parse_directory(plan_dir)
            projects = {}
            for result in parsed.values():
                if not isinstance(result, dict) or "error" not in result:
                    if isinstance(result.entity, Project):
                        projects[result.entity.id] = result.entity

            if not projects:
                return jsonify({"ok": True, "data": {}})

            graph = DependencyGraph(projects)

            # Compute all analytics
            metrics = compute_all_metrics(projects, graph)
            impactful = get_most_impactful_projects(projects, graph, limit=5)
            bottlenecks = detect_bottlenecks(projects, graph)
            capacity = analyze_capacity(projects, graph)

            return jsonify({
                "ok": True,
                "data": {
                    "metrics": metrics,
                    "impactful_projects": impactful,
                    "bottlenecks": {
                        "summary": bottlenecks["summary"],
                        "blocking_count": len(bottlenecks["blocking_bottlenecks"]),
                        "chain_count": len(bottlenecks["deep_chains"]),
                    },
                    "capacity": {
                        "total_effort_days": capacity["total_effort_days"],
                        "critical_path_days": capacity["critical_path_days"],
                        "compression_ratio": capacity["compression_ratio"],
                        "timeline_phases": len(capacity["timeline_phases"]),
                    },
                },
            })
        except Exception as e:
            return jsonify({"ok": False, "error": str(e)}), 500

    @app.route("/api/analytics/<project_id>")
    def get_project_analytics(project_id: str):
        """Get analytics for a specific project."""
        try:
            from planner.impact import analyze_impact

            parsed = PlanParser.parse_directory(plan_dir)
            projects = {}
            for result in parsed.values():
                if not isinstance(result, dict) or "error" not in result:
                    if isinstance(result.entity, Project):
                        projects[result.entity.id] = result.entity

            if project_id not in projects:
                return jsonify({"ok": False, "error": "Project not found"}), 404

            graph = DependencyGraph(projects)
            impact = analyze_impact(project_id, projects, graph)

            return jsonify({"ok": True, "data": impact})
        except Exception as e:
            return jsonify({"ok": False, "error": str(e)}), 500

    @app.route("/api/chart/gantt")
    def get_gantt_chart():
        """Get Gantt chart SVG."""
        try:
            from planner.gantt import generate_gantt_svg

            parsed = PlanParser.parse_directory(plan_dir)
            projects = {}
            for result in parsed.values():
                if not isinstance(result, dict) or "error" not in result:
                    if isinstance(result.entity, Project):
                        projects[result.entity.id] = result.entity

            if not projects:
                return jsonify({"ok": True, "svg": "<svg></svg>"})

            graph = DependencyGraph(projects)
            svg = generate_gantt_svg(projects, graph)

            return jsonify({"ok": True, "svg": svg})
        except Exception as e:
            return jsonify({"ok": False, "error": str(e)}), 500

    @app.route("/api/chart/burndown")
    def get_burndown_chart():
        """Get burndown chart SVG."""
        try:
            from planner.burndown import generate_burndown_svg

            parsed = PlanParser.parse_directory(plan_dir)
            projects = {}
            for result in parsed.values():
                if not isinstance(result, dict) or "error" not in result:
                    if isinstance(result.entity, Project):
                        projects[result.entity.id] = result.entity

            if not projects:
                return jsonify({"ok": True, "svg": "<svg></svg>"})

            svg = generate_burndown_svg(projects)

            return jsonify({"ok": True, "svg": svg})
        except Exception as e:
            return jsonify({"ok": False, "error": str(e)}), 500

    @app.route("/report")
    def serve_report():
        report_path = plan_dir / "report.html"
        if not report_path.exists():
            return Response("Report not generated yet. Run Report from the Commands menu.",
                            status=404, mimetype="text/plain")
        return Response(report_path.read_text(encoding="utf-8"), mimetype="text/html")

    return app


def serve(plan_dir: Path, host: str = "127.0.0.1", port: int = 8000,
          edit: bool = False, validate_on_save: bool = True) -> None:
    """Start the plan web server."""
    _check_flask()
    app = create_app(plan_dir, edit=edit, validate_on_save=validate_on_save)

    edit_note = " (edit enabled)" if edit else " (read-only)"
    print(f"Plan server running at http://{host}:{port}{edit_note}")
    print("Press Ctrl+C to stop.  Use 'plan stop' or 'plan restart' from another terminal.")

    _write_pid(plan_dir, host, port, edit, validate_on_save)
    try:
        app.run(host=host, port=port, debug=False, use_reloader=False)
    finally:
        _remove_pid(plan_dir)


def stop(plan_dir: Path) -> None:
    """Stop a running plan server."""
    if _kill_server(plan_dir):
        print("Plan server stopped.")
    else:
        print("No running plan server found (no .plan-server.pid in plan dir).")


def restart(plan_dir: Path) -> None:
    """Restart a running plan server with the same options."""
    info = _read_pid(plan_dir)
    if not info:
        print("No running plan server found. Use 'plan serve' to start one.")
        sys.exit(1)

    host = info.get("host", "127.0.0.1")
    port = info.get("port", 8000)
    edit = info.get("edit", False)
    validate_on_save = info.get("validate_on_save", True)

    print(f"Restarting plan server (http://{host}:{port})...")
    _kill_server(plan_dir)

    # Spawn new server as detached subprocess so this process can exit
    args = [sys.executable, "-m", "planner.cli", "serve", str(plan_dir),
            "--host", host, "--port", str(port)]
    if edit:
        args.append("--edit")
    if not validate_on_save:
        args.append("--no-validate")

    subprocess.Popen(args, start_new_session=True)
    print("Plan server restarted.")
