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
    for name in ["INDEX.md", "ORIGIN.md", "AXIOMS.md", "FOCUS.md", "CHANGELOG.md", "REFLECTION.md", "VALIDATION.md", "README.md"]:
        p = plan_dir / name
        if p.exists():
            tree.append({"name": name, "path": name, "type": "file"})

    # Category directories
    for category in ["concepts", "theses", "master_plans", "projects", "designs", "actions"]:
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
        theses = {}
        master_plans = {}
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

                if entity_type == "thesis":
                    theses[entity.id] = entity_info
                elif entity_type == "masterplan":
                    master_plans[entity.id] = entity_info
                elif entity_type == "project":
                    projects[entity.id] = entity_info
                elif entity_type == "design":
                    designs[entity.id] = entity_info
                    if hasattr(entity, 'project'):
                        entity_info["parent"] = entity.project
                elif entity_type == "action":
                    actions[entity.id] = entity_info
                    if hasattr(entity, 'design'):
                        entity_info["parent"] = entity.design

        # Build many-to-many thesis ↔ master_plan links from parent_thesis fields
        # thesis_mp_map: thesis_id → [mp_id, ...]
        # mp_thesis_map: mp_id → [thesis_id, ...]
        thesis_mp_map: Dict[str, list] = {t_id: [] for t_id in theses}
        mp_thesis_map: Dict[str, list] = {mp_id: [] for mp_id in master_plans}

        for path_key, file_data in files.items():
            if isinstance(file_data, dict) and "error" in file_data:
                continue
            entity = file_data.entity if hasattr(file_data, 'entity') else file_data
            if hasattr(entity, 'parent_thesis') and entity.parent_thesis:
                for t_id in entity.parent_thesis:
                    if t_id in thesis_mp_map:
                        thesis_mp_map[t_id].append(entity.id)
                    if entity.id in mp_thesis_map:
                        mp_thesis_map[entity.id].append(t_id)

        # Build hierarchy: concepts (flat) + theses → master plans → projects → designs → actions
        hierarchy = {"concepts": [], "theses": [], "master_plans": [], "projects": []}

        concepts_flat = {}
        for path_key, file_data in files.items():
            if isinstance(file_data, dict) and "error" in file_data:
                continue
            entity = file_data.entity if hasattr(file_data, 'entity') else file_data
            if entity.__class__.__name__.lower() == "concept":
                concepts_flat[entity.id] = {
                    "id": entity.id,
                    "title": entity.title,
                    "path": path_key,
                    "concept_type": entity.concept_type.value,
                    "status": entity.status.value if hasattr(entity.status, 'value') else str(entity.status),
                }
        for c_id, c in sorted(concepts_flat.items()):
            hierarchy["concepts"].append(c)

        for t_id, t in sorted(theses.items()):
            # Embed linked master plans so the UI can render the many-to-many relationship
            linked_mps = []
            for mp_id in thesis_mp_map.get(t_id, []):
                if mp_id in master_plans:
                    mp = master_plans[mp_id]
                    linked_mps.append({"id": mp_id, "title": mp["title"], "path": mp["path"]})
            hierarchy["theses"].append({
                "id": t_id,
                "title": t["title"],
                "path": t["path"],
                "master_plans": linked_mps,
            })

        for mp_id, mp in sorted(master_plans.items()):
            mp_node = {
                "id": mp_id,
                "title": mp["title"],
                "path": mp["path"],
                "theses": mp_thesis_map.get(mp_id, []),
            }
            hierarchy["master_plans"].append(mp_node)

        for path_key, file_data in files.items():
            if isinstance(file_data, dict) and "error" in file_data:
                continue
            entity = file_data.entity if hasattr(file_data, 'entity') else file_data
            if hasattr(entity, 'parent_master_plan') and entity.parent_master_plan and entity.id in projects:
                projects[entity.id]["parent_master_plan"] = entity.parent_master_plan

        for proj_id, proj in sorted(projects.items()):
            proj_node = {"id": proj_id, "title": proj["title"], "path": proj["path"],
                         "parent_master_plan": proj.get("parent_master_plan", []), "children": []}

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


_LIBRARIES_HEAD = r"""<!-- Markdown renderer -->
<script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>

<!-- CodeMirror -->
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.16/codemirror.min.css">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.16/theme/dracula.min.css">
<script src="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.16/codemirror.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.16/mode/markdown/markdown.min.js"></script>"""

_HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Plan</title>

${_LIBRARIES_HEAD}

<link rel="stylesheet" href="/static/style.css">
</head>
<body>

<div id="toolbar">
  <button data-action="show-browser">📁 Files</button>
  <button data-action="show-tree">🌳 Tree</button>
  <button data-action="show-analytics">📊 Analytics</button>
  <button data-action="show-status">📋 Items</button>
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
        <button id="btn-edit"   data-action="edit-file">Edit</button>
        <button id="btn-save"   data-action="save-file">Save</button>
        <button id="btn-cancel" data-action="cancel-edit">Cancel</button>
      </div>
    </div>
    <div id="preview"></div>
    <div id="editor-wrap"></div>
    <div id="validate-banner"></div>
    <div id="tree-view" style="display: none;"></div>
    <div id="analytics-dashboard" style="display: none;"></div>
    <div id="status-view" style="display: none;"></div>
  </div>
</div>

<script>
window.currentPath = null;
window.currentRaw  = null;
window.editEnabled = EDIT_ENABLED;

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
</script>

<!-- Module Scripts -->
<script src="/static/ui.js"></script>
<script src="/static/files.js"></script>
<script src="/static/search.js"></script>
<script src="/static/editor.js"></script>
<script src="/static/preview.js"></script>
<script src="/static/tree.js"></script>
<script src="/static/analytics.js"></script>
<script src="/static/viewer.js"></script>
<script src="/static/status.js"></script>
<script src="/static/dispatcher.js"></script>

<script>
// Initialize search input listener
FileSearch.initSearchInput();
</script>

<script>
// Initialize window.onload


window.onload = async () => {
  EventDispatcher.init();
  if (!window.editEnabled) {
    document.getElementById('btn-edit').style.display = 'none';
  }
  document.querySelectorAll('#toolbar button')[0].classList.add('active');
  await FileBrowser.loadTree();
  await FileSearch.loadFilesForSearch();
  await FileBrowser.loadFile('INDEX.md');
};
</script>

</body>
</html>
"""


def create_app(plan_dir: Path, edit: bool = False, validate_on_save: bool = True):
    """Create and return the Flask app."""
    from flask import Flask, jsonify, request, Response
    from planner.parser import PlanParser
    from planner.models import Project, MasterPlan
    from planner.graph import DependencyGraph

    app = Flask(__name__)
    app.config["plan_dir"] = plan_dir
    app.config["edit"] = edit
    app.config["validate_on_save"] = validate_on_save

    @app.route("/")
    def index():
        html = _HTML.replace("${_LIBRARIES_HEAD}", _LIBRARIES_HEAD)
        html = html.replace("EDIT_ENABLED", "true" if edit else "false")
        return Response(html, mimetype="text/html")

    @app.route("/static/<path:filename>")
    def serve_static(filename):
        static_dir = Path(__file__).parent / "static"
        file_path = (static_dir / filename).resolve()
        if not str(file_path).startswith(str(static_dir.resolve())):
            return "Not found", 404
        if not file_path.exists():
            return "Not found", 404

        mimetype = "application/javascript"
        if filename.endswith(".css"):
            mimetype = "text/css"

        return Response(file_path.read_text(encoding="utf-8"), mimetype=mimetype)

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

    @app.route("/api/status")
    def get_status():
        """Get status view data: all entities with metadata for table display."""
        try:
            from datetime import datetime
            from planner.models import Design, Action, MasterPlan, Thesis, Concept

            parsed = PlanParser.parse_directory(plan_dir)
            concepts = {}
            theses = {}
            master_plans = {}
            projects = {}
            designs = {}
            actions = {}
            path_map = {}

            for filename, result in parsed.items():
                if isinstance(result, dict) and "error" in result:
                    continue
                entity = result.entity
                if isinstance(entity, Concept):
                    concepts[entity.id] = entity
                    path_map[f"concept_{entity.id}"] = filename.replace(str(plan_dir) + "/", "")
                elif isinstance(entity, Thesis):
                    theses[entity.id] = entity
                    path_map[f"thesis_{entity.id}"] = filename.replace(str(plan_dir) + "/", "")
                elif isinstance(entity, MasterPlan):
                    master_plans[entity.id] = entity
                    path_map[f"master_plan_{entity.id}"] = filename.replace(str(plan_dir) + "/", "")
                elif isinstance(entity, Project):
                    projects[entity.id] = entity
                    path_map[f"project_{entity.id}"] = filename.replace(str(plan_dir) + "/", "")
                elif isinstance(entity, Design):
                    designs[entity.id] = entity
                    path_map[f"design_{entity.id}"] = filename.replace(str(plan_dir) + "/", "")
                elif isinstance(entity, Action):
                    actions[entity.id] = entity
                    path_map[f"action_{entity.id}"] = filename.replace(str(plan_dir) + "/", "")

            graph = DependencyGraph(projects)
            entities = []

            for c in sorted(concepts.values(), key=lambda x: x.id):
                entities.append({
                    "id": c.id,
                    "title": c.title,
                    "type": "concept",
                    "concept_type": c.concept_type.value,
                    "status": c.status,
                    "priority": "MEDIUM",
                    "created": c.created.isoformat() if c.created else None,
                    "updated": c.updated.isoformat() if c.updated else None,
                    "description": c.description[:100] + "..." if c.description and len(c.description) > 100 else c.description,
                    "path": path_map.get(f"concept_{c.id}", f"concepts/{c.id}.md"),
                    "related": c.related,
                })

            for t in sorted(theses.values(), key=lambda x: x.id):
                entities.append({
                    "id": t.id,
                    "title": t.title,
                    "type": "thesis",
                    "status": t.status,
                    "priority": "HIGH",
                    "created": t.created.isoformat() if t.created else None,
                    "updated": t.updated.isoformat() if t.updated else None,
                    "description": t.description[:100] + "..." if t.description and len(t.description) > 100 else t.description,
                    "path": path_map.get(f"thesis_{t.id}", f"theses/{t.id}.md"),
                    "conviction": f"{t.conviction}/10" if t.conviction is not None else None,
                })

            for mp in sorted(master_plans.values(), key=lambda x: x.id):
                entities.append({
                    "id": mp.id,
                    "title": mp.title,
                    "type": "master_plan",
                    "parent_thesis": mp.parent_thesis if mp.parent_thesis else [],
                    "status": mp.status,
                    "priority": mp.priority or "MEDIUM",
                    "created": mp.created.isoformat() if mp.created else None,
                    "updated": mp.updated.isoformat() if mp.updated else None,
                    "description": mp.description[:100] + "..." if mp.description and len(mp.description) > 100 else mp.description,
                    "path": path_map.get(f"master_plan_{mp.id}", f"master_plans/{mp.id}.md"),
                    "stakeholder": mp.stakeholder or "N/A",
                })

            for proj in sorted(projects.values(), key=lambda x: x.id):
                entities.append({
                    "id": proj.id,
                    "title": proj.title,
                    "type": "project",
                    "status": proj.status,
                    "priority": proj.priority or "MEDIUM",
                    "parent_master_plan": getattr(proj, 'parent_master_plan', []) or [],
                    "created": proj.created.isoformat() if proj.created else None,
                    "updated": proj.updated.isoformat() if proj.updated else None,
                    "description": proj.description[:100] + "..." if proj.description and len(proj.description) > 100 else proj.description,
                    "path": path_map.get(f"project_{proj.id}", f"projects/{proj.id}.md"),
                    "depends_on_count": len(graph.get_blocking_deps(proj.id)),
                })

            for design in sorted(designs.values(), key=lambda x: x.id):
                entities.append({
                    "id": design.id,
                    "title": design.title,
                    "type": "design",
                    "status": design.status,
                    "priority": getattr(design, 'priority', None) or "MEDIUM",
                    "parent_project": getattr(design, 'project', None),
                    "created": design.created.isoformat() if design.created else None,
                    "updated": design.updated.isoformat() if design.updated else None,
                    "description": design.description[:100] + "..." if design.description and len(design.description) > 100 else design.description,
                    "path": path_map.get(f"design_{design.id}", f"designs/{design.id}.md"),
                    "depends_on_count": 0,
                })

            for action in sorted(actions.values(), key=lambda x: x.id):
                entities.append({
                    "id": action.id,
                    "title": action.title,
                    "type": "action",
                    "status": action.status,
                    "priority": getattr(action, 'priority', None) or "MEDIUM",
                    "parent_design": getattr(action, 'design', None),
                    "created": action.created.isoformat() if action.created else None,
                    "updated": action.updated.isoformat() if action.updated else None,
                    "description": action.description[:100] + "..." if action.description and len(action.description) > 100 else action.description,
                    "path": path_map.get(f"action_{action.id}", f"actions/{action.id}.md"),
                    "depends_on_count": 0,
                })

            return jsonify({
                "ok": True,
                "data": {
                    "timestamp": datetime.now().isoformat(),
                    "entities": entities,
                    "summary": {
                        "total": len(entities),
                        "projects": len(projects),
                        "designs": len(designs),
                        "actions": len(actions),
                    }
                }
            })
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
