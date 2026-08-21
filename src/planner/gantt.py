"""Gantt chart generation for project timelines."""

from datetime import date, timedelta
from typing import Dict, List, Tuple
from .models import Project, Status
from .stats import compute_timeline
from .graph import DependencyGraph


def generate_gantt_svg(
    projects: Dict[str, Project],
    graph: DependencyGraph,
    width: int = 800,
    height: int = 400,
) -> str:
    """Generate SVG Gantt chart.

    Args:
        projects: Dict of projects
        graph: Dependency graph
        width: SVG width in pixels
        height: SVG height in pixels

    Returns:
        SVG string
    """
    if not projects:
        return '<svg width="800" height="200"><text x="10" y="20">No projects</text></svg>'

    # Compute timeline phases
    timeline = compute_timeline(projects, graph)

    # Calculate date range based on estimates
    today = date.today()
    project_list = sorted(projects.items())

    # Estimate start/end dates
    start_date = today
    total_days = 0
    for _, project in project_list:
        if project.estimate and project.estimate.effort_days:
            total_days += project.estimate.effort_days

    end_date = start_date + timedelta(days=max(total_days, 5))
    date_range = (end_date - start_date).days

    # SVG parameters
    margin_left = 150
    margin_top = 30
    margin_right = 20
    margin_bottom = 30
    chart_width = width - margin_left - margin_right
    chart_height = height - margin_top - margin_bottom
    bar_height = 20
    bar_padding = 10
    total_chart_height = len(projects) * (bar_height + bar_padding) + bar_padding

    # Adjust height if needed
    if total_chart_height > chart_height:
        actual_height = total_chart_height + margin_top + margin_bottom
    else:
        actual_height = height

    # Color map by status
    status_colors = {
        Status.DONE: "#a6e3a1",
        Status.IN_PROGRESS: "#f9e2af",
        Status.PLANNING: "#89b4fa",
        Status.BLOCKED: "#f38ba8",
        Status.IDEA: "#bac2de",
        Status.DEFERRED: "#6c7086",
        Status.CANCELLED: "#45475a",
    }

    svg = f'<svg width="{width}" height="{actual_height}" xmlns="http://www.w3.org/2000/svg" style="background: #1e1e2e;">\n'

    # Title
    svg += f'<text x="10" y="20" font-size="14" font-weight="bold" fill="#89b4fa">Gantt Chart - Project Timeline</text>\n'

    # Timeline headers (dates)
    date_step = max(1, date_range // 10)  # Show ~10 date markers
    for i in range(0, date_range + 1, date_step):
        x = margin_left + (i / date_range) * chart_width
        d = start_date + timedelta(days=i)
        svg += f'<text x="{x}" y="{margin_top - 5}" font-size="10" fill="#a6adc8" text-anchor="middle">{d.strftime("%m/%d")}</text>\n'

    # Background grid
    for i in range(0, date_range + 1, date_step):
        x = margin_left + (i / date_range) * chart_width
        svg += f'<line x1="{x}" y1="{margin_top}" x2="{x}" y2="{margin_top + total_chart_height}" stroke="#313244" stroke-width="1"/>\n'

    # Projects
    y = margin_top + bar_padding
    for project_id, project in project_list:
        # Project label
        svg += f'<text x="10" y="{y + bar_height - 3}" font-size="11" fill="#cdd6f4" font-weight="bold">{project_id}</text>\n'

        # Bar
        if project.estimate and project.estimate.effort_days:
            bar_width = (project.estimate.effort_days / max(total_days, 1)) * chart_width
        else:
            bar_width = chart_width * 0.05  # Small placeholder bar

        color = status_colors.get(project.status, "#45475a")
        svg += f'<rect x="{margin_left}" y="{y}" width="{bar_width}" height="{bar_height}" fill="{color}" stroke="#45475a" stroke-width="1" rx="2"/>\n'

        # Status label on bar
        if bar_width > 40:
            svg += f'<text x="{margin_left + 5}" y="{y + bar_height - 3}" font-size="9" fill="#1e1e2e">{project.status.value[:3]}</text>\n'

        y += bar_height + bar_padding

    # Legend
    legend_y = margin_top + total_chart_height + 20
    legend_x = margin_left
    for status, color in list(status_colors.items())[:4]:
        svg += f'<rect x="{legend_x}" y="{legend_y}" width="10" height="10" fill="{color}"/>\n'
        svg += f'<text x="{legend_x + 15}" y="{legend_y + 9}" font-size="9" fill="#a6adc8">{status.value}</text>\n'
        legend_x += 100

    svg += '</svg>\n'
    return svg


def generate_gantt_data(
    projects: Dict[str, Project],
    graph: DependencyGraph,
) -> List[Dict]:
    """Generate structured Gantt data for charting libraries.

    Args:
        projects: Dict of projects
        graph: Dependency graph

    Returns:
        List of task dicts with: {id, name, start, duration_days, status, dependencies}
    """
    tasks = []
    today = date.today()

    for project_id, project in sorted(projects.items()):
        effort = project.estimate.effort_days if project.estimate else 0
        started = (
            project.estimate.started
            if project.estimate and project.estimate.started
            else today
        )

        # Calculate end date based on effort
        if effort:
            end = started + timedelta(days=effort)
        else:
            end = started + timedelta(days=1)

        # Get dependencies
        deps = list(graph.get_blocking_deps(project_id))

        tasks.append({
            "id": project_id,
            "name": project.title,
            "start": started.isoformat(),
            "end": end.isoformat(),
            "duration_days": effort or 1,
            "status": project.status.value,
            "dependencies": deps,
        })

    return tasks
