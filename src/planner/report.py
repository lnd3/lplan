"""Generate static HTML reports for plan visibility."""

from datetime import date
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from .models import PlanEntity, Project, Design, Action, Status
from .parser import PlanParser
from .stats import compute_stats, compute_timeline
from .graph import DependencyGraph


def generate_html_report(
    entities: Dict[str, PlanEntity],
    projects: Dict[str, Project],
    graph: DependencyGraph,
    stats: Dict,
) -> str:
    """Generate self-contained HTML report.

    Creates a standalone HTML page with:
    - Summary statistics
    - Priority analysis table
    - Projects table (sortable)
    - Dependency graph visualization (SVG)

    Args:
        entities: All parsed entities
        projects: Project entities only
        graph: Dependency graph
        stats: Pre-computed stats from compute_stats

    Returns:
        HTML string (complete, self-contained page)
    """
    today = date.today().isoformat()

    # Compute timeline for graph layout
    timeline = compute_timeline(projects, graph)

    # Generate HTML
    html = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Plan Report</title>
<style>
:root {{
  --bg: #ffffff;
  --fg: #000000;
  --border: #cccccc;
  --stat-bg: #f5f5f5;
  --done-bg: #d4edda;
  --in-progress-bg: #fff3cd;
  --blocked-bg: #f8d7da;
  --idea-bg: #e2e3e5;
}}

@media (prefers-color-scheme: dark) {{
  :root:not([data-theme="light"]) {{
    --bg: #1e1e1e;
    --fg: #e0e0e0;
    --border: #444444;
    --stat-bg: #2d2d2d;
    --done-bg: #1b3d1f;
    --in-progress-bg: #3d3a1f;
    --blocked-bg: #3d1b22;
    --idea-bg: #2a2a2a;
  }}
}}

:root[data-theme="dark"] {{
  --bg: #1e1e1e;
  --fg: #e0e0e0;
  --border: #444444;
  --stat-bg: #2d2d2d;
  --done-bg: #1b3d1f;
  --in-progress-bg: #3d3a1f;
  --blocked-bg: #3d1b22;
  --idea-bg: #2a2a2a;
}}

* {{
  box-sizing: border-box;
}}

body {{
  background-color: var(--bg);
  color: var(--fg);
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  line-height: 1.6;
  margin: 0;
  padding: 20px;
}}

h1, h2, h3 {{
  margin-top: 1.5em;
  margin-bottom: 0.5em;
}}

h1 {{
  border-bottom: 2px solid var(--border);
  padding-bottom: 10px;
}}

table {{
  width: 100%;
  border-collapse: collapse;
  margin: 1em 0;
}}

th, td {{
  padding: 8px;
  text-align: left;
  border: 1px solid var(--border);
}}

th {{
  background-color: var(--stat-bg);
  font-weight: 600;
  cursor: pointer;
}}

th:hover {{
  opacity: 0.8;
}}

tr:nth-child(even) {{
  background-color: var(--stat-bg);
}}

.stat-card {{
  display: inline-block;
  background-color: var(--stat-bg);
  border: 1px solid var(--border);
  border-radius: 6px;
  padding: 15px;
  margin: 10px 10px 10px 0;
  text-align: center;
  min-width: 120px;
}}

.stat-value {{
  font-size: 1.8em;
  font-weight: bold;
  color: var(--fg);
}}

.stat-label {{
  font-size: 0.9em;
  color: var(--fg);
  opacity: 0.8;
}}

.status-done {{
  background-color: var(--done-bg);
}}

.status-in-progress {{
  background-color: var(--in-progress-bg);
}}

.status-blocked {{
  background-color: var(--blocked-bg);
}}

.status-idea {{
  background-color: var(--idea-bg);
}}

.graph-container {{
  overflow-x: auto;
  border: 1px solid var(--border);
  border-radius: 6px;
  padding: 10px;
  margin: 1em 0;
}}

svg {{
  display: block;
}}

.node {{
  stroke: var(--border);
  stroke-width: 1;
}}

.edge {{
  stroke: var(--border);
  stroke-width: 1;
  fill: none;
  marker-end: url(#arrowhead);
}}

.label {{
  font-size: 11px;
  text-anchor: middle;
  dominant-baseline: middle;
}}

.meta {{
  font-size: 0.9em;
  color: var(--fg);
  opacity: 0.7;
  margin-top: 2em;
}}
</style>
</head>
<body>

<h1>Plan Report</h1>
<p class="meta">Generated: {today}</p>

<h2>Summary</h2>
"""

    # Add stat cards
    html += f"""<div class="stat-cards">
<div class="stat-card">
<div class="stat-value">{stats.get('projects_total', 0)}</div>
<div class="stat-label">Projects</div>
</div>
<div class="stat-card">
<div class="stat-value">{stats.get('designs_total', 0)}</div>
<div class="stat-label">Designs</div>
</div>
<div class="stat-card">
<div class="stat-value">{stats.get('actions_total', 0)}</div>
<div class="stat-label">Actions</div>
</div>
<div class="stat-card">
<div class="stat-value">{stats.get('percent_done', 0):.0f}%</div>
<div class="stat-label">Done</div>
</div>
<div class="stat-card">
<div class="stat-value">{stats.get('blocked_count', 0)}</div>
<div class="stat-label">Blocked</div>
</div>
</div>
"""

    # Add priority analysis table
    html += """<h2>Projects</h2>
<table>
<thead>
<tr>
<th>ID</th>
<th>Title</th>
<th>Status</th>
<th>Priority</th>
</tr>
</thead>
<tbody>
"""

    for pid, project in sorted(projects.items()):
        status_class = f"status-{project.status.value.lower()}"
        html += f"""<tr class="{status_class}">
<td><strong>{pid}</strong></td>
<td>{project.title}</td>
<td>{project.status.value}</td>
<td>{project.priority.value}</td>
</tr>
"""

    html += """</tbody>
</table>
"""

    # Add dependency graph (SVG)
    html += """<h2>Dependency Graph</h2>
<div class="graph-container">
"""

    if projects and timeline:
        svg_html = _generate_dependency_graph_svg(projects, graph, timeline)
        html += svg_html
    else:
        html += "<p><em>No projects to visualize</em></p>"

    html += """</div>

<div class="meta">
<p><small>Static HTML report. Open in any web browser. No external dependencies.</small></p>
</div>

</body>
</html>
"""

    return html


def _generate_dependency_graph_svg(
    projects: Dict[str, Project],
    graph: DependencyGraph,
    timeline: List[Tuple[int, List[str]]],
) -> str:
    """Generate SVG dependency graph visualization.

    Args:
        projects: Dict of projects
        graph: Dependency graph
        timeline: Phases from compute_timeline

    Returns:
        SVG markup string
    """
    # Layout parameters
    phase_width = 200
    node_width = 150
    node_height = 60
    node_padding = 20
    gap_between_phases = 50

    # Compute positions
    positions: Dict[str, Tuple[int, int]] = {}
    max_y = 0

    for phase, project_ids in timeline:
        x = phase * phase_width + gap_between_phases
        for i, project_id in enumerate(project_ids):
            y = i * (node_height + node_padding) + node_padding
            positions[project_id] = (x, y)
            max_y = max(max_y, y + node_height)

    # SVG dimensions with margin
    margin = 30
    svg_width = max([x for x, y in positions.values()]) + node_width + margin * 2 if positions else 400
    svg_height = max_y + margin * 2 if max_y > 0 else 200

    svg = f'<svg width="{svg_width}" height="{svg_height}" xmlns="http://www.w3.org/2000/svg">\n'

    # Arrow marker
    svg += '''<defs>
<marker id="arrowhead" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto">
<polygon points="0 0, 10 3, 0 6" fill="currentColor" />
</marker>
</defs>
'''

    # Draw edges (dependencies)
    for project_id, project in projects.items():
        if project_id not in positions:
            continue

        x1, y1 = positions[project_id]
        center_y1 = y1 + node_height // 2

        for dep_id in project.depends:
            if dep_id not in positions:
                continue

            x2, y2 = positions[dep_id]
            center_y2 = y2 + node_height // 2

            # Draw line from project to dependency
            svg += f'<line x1="{x1}" y1="{center_y1}" x2="{x2 + node_width}" y2="{center_y2}" class="edge" />\n'

    # Draw nodes (projects)
    for project_id, project in projects.items():
        if project_id not in positions:
            continue

        x, y = positions[project_id]

        # Status color
        status_color = {
            "DONE": "#90EE90",
            "IN_PROGRESS": "#FFD700",
            "BLOCKED": "#FF6B6B",
            "PLANNING": "#87CEEB",
            "IDEA": "#D3D3D3",
            "DEFERRED": "#A9A9A9",
            "CANCELLED": "#808080",
        }.get(project.status.value, "#E0E0E0")

        svg += f'''<rect x="{x}" y="{y}" width="{node_width}" height="{node_height}"
  class="node" fill="{status_color}" rx="4" ry="4" />\n'''

        # Project ID (title of rect)
        svg += f'''<text x="{x + node_width // 2}" y="{y + 20}" class="label" font-weight="bold">
{project_id}
</text>\n'''

        # Project title (shortened)
        title_short = project.title[:20] + "..." if len(project.title) > 20 else project.title
        svg += f'''<text x="{x + node_width // 2}" y="{y + 45}" class="label" font-size="10">
{title_short}
</text>\n'''

    svg += '</svg>\n'
    return svg


def write_report(
    plan_dir: Path,
    entities: Dict[str, PlanEntity],
    output_path: Path,
) -> Path:
    """Write HTML report to file.

    Args:
        plan_dir: Path to plan directory (for context)
        entities: All parsed entities
        output_path: Path to write report.html

    Returns:
        Path to written report file
    """
    # Separate entities
    projects = {eid: e for eid, e in entities.items() if isinstance(e, Project)}

    # Compute stats and graph
    stats = compute_stats(entities)

    if projects:
        graph = DependencyGraph(projects)
    else:
        graph = DependencyGraph({})

    # Generate HTML
    html = generate_html_report(entities, projects, graph, stats)

    # Write to file
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html, encoding="utf-8")

    return output_path
