"""Burndown chart generation for progress tracking."""

from datetime import date, timedelta
from typing import Dict, List, Tuple
from .models import Project, Status


def generate_burndown_svg(
    projects: Dict[str, Project],
    width: int = 800,
    height: int = 300,
) -> str:
    """Generate SVG burndown chart.

    Args:
        projects: Dict of projects
        width: SVG width in pixels
        height: SVG height in pixels

    Returns:
        SVG string
    """
    if not projects:
        return '<svg width="800" height="200"><text x="10" y="20">No projects</text></svg>'

    # Count status distribution
    done_count = sum(1 for p in projects.values() if p.status == Status.DONE)
    total_count = len(projects)
    in_progress_count = sum(1 for p in projects.values() if p.status == Status.IN_PROGRESS)
    planning_count = sum(1 for p in projects.values() if p.status == Status.PLANNING)

    # SVG parameters
    margin_left = 40
    margin_top = 30
    margin_right = 20
    margin_bottom = 40
    chart_width = width - margin_left - margin_right
    chart_height = height - margin_top - margin_bottom

    svg = f'<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg" style="background: #1e1e2e;">\n'

    # Title
    svg += f'<text x="10" y="20" font-size="14" font-weight="bold" fill="#89b4fa">Burndown - Project Completion</text>\n'

    # Axes
    svg += f'<line x1="{margin_left}" y1="{margin_top}" x2="{margin_left}" y2="{margin_top + chart_height}" stroke="#45475a" stroke-width="2"/>\n'
    svg += f'<line x1="{margin_left}" y1="{margin_top + chart_height}" x2="{margin_left + chart_width}" y2="{margin_top + chart_height}" stroke="#45475a" stroke-width="2"/>\n'

    # Y-axis labels (0-100%)
    for pct in [0, 25, 50, 75, 100]:
        y = margin_top + chart_height - (pct / 100) * chart_height
        svg += f'<text x="15" y="{y + 3}" font-size="10" fill="#a6adc8" text-anchor="end">{pct}%</text>\n'
        svg += f'<line x1="{margin_left - 5}" y1="{y}" x2="{margin_left}" y2="{y}" stroke="#45475a" stroke-width="1"/>\n'

    # Grid lines
    for pct in [25, 50, 75]:
        y = margin_top + chart_height - (pct / 100) * chart_height
        svg += f'<line x1="{margin_left}" y1="{y}" x2="{margin_left + chart_width}" y2="{y}" stroke="#313244" stroke-width="1" stroke-dasharray="2,2"/>\n'

    # X-axis label
    svg += f'<text x="{margin_left + chart_width / 2}" y="{height - 10}" font-size="11" fill="#a6adc8" text-anchor="middle">Project Progress</text>\n'

    # Calculate percentages for stacked bar
    done_pct = (done_count / total_count * 100) if total_count > 0 else 0
    in_progress_pct = (in_progress_count / total_count * 100) if total_count > 0 else 0
    planning_pct = (planning_count / total_count * 100) if total_count > 0 else 0

    # Burndown bar (stacked horizontal)
    bar_y = margin_top + chart_height - 60
    bar_height = 40

    # DONE (green)
    done_width = (done_pct / 100) * chart_width
    svg += f'<rect x="{margin_left}" y="{bar_y}" width="{done_width}" height="{bar_height}" fill="#a6e3a1" stroke="#45475a" stroke-width="1"/>\n'

    # IN_PROGRESS (yellow)
    in_prog_width = (in_progress_pct / 100) * chart_width
    svg += f'<rect x="{margin_left + done_width}" y="{bar_y}" width="{in_prog_width}" height="{bar_height}" fill="#f9e2af" stroke="#45475a" stroke-width="1"/>\n'

    # PLANNING (blue)
    planning_width = (planning_pct / 100) * chart_width
    svg += f'<rect x="{margin_left + done_width + in_prog_width}" y="{bar_y}" width="{planning_width}" height="{bar_height}" fill="#89b4fa" stroke="#45475a" stroke-width="1"/>\n'

    # Percentage labels
    if done_pct > 10:
        svg += f'<text x="{margin_left + done_width / 2}" y="{bar_y + bar_height / 2 + 4}" font-size="12" font-weight="bold" fill="#1e1e2e" text-anchor="middle">{done_pct:.0f}%</text>\n'

    if in_progress_pct > 10:
        svg += f'<text x="{margin_left + done_width + in_prog_width / 2}" y="{bar_y + bar_height / 2 + 4}" font-size="12" font-weight="bold" fill="#1e1e2e" text-anchor="middle">{in_progress_pct:.0f}%</text>\n'

    # Legend
    legend_y = bar_y - 40
    legend_items = [
        ("DONE", "#a6e3a1", done_count),
        ("IN_PROGRESS", "#f9e2af", in_progress_count),
        ("PLANNING", "#89b4fa", planning_count),
    ]

    legend_x = margin_left
    for label, color, count in legend_items:
        svg += f'<rect x="{legend_x}" y="{legend_y}" width="12" height="12" fill="{color}" stroke="#45475a"/>\n'
        svg += f'<text x="{legend_x + 16}" y="{legend_y + 10}" font-size="11" fill="#cdd6f4">{label} ({count})</text>\n'
        legend_x += 150

    svg += '</svg>\n'
    return svg


def compute_burndown_projection(
    projects: Dict[str, Project],
    days_ahead: int = 30,
) -> Dict:
    """Compute projected burndown based on current progress.

    Args:
        projects: Dict of projects
        days_ahead: Number of days to project

    Returns:
        Dict with projection data
    """
    today = date.today()
    total = len(projects)
    done_count = sum(1 for p in projects.values() if p.status == Status.DONE)
    in_progress = sum(1 for p in projects.values() if p.status == Status.IN_PROGRESS)

    # Simple projection: assume all in-progress complete in next 7 days,
    # then plan items start at linear rate
    projection = []

    for day in range(days_ahead):
        current_date = today + timedelta(days=day)

        # Assume linear progress after in-progress items
        if day <= 7 and in_progress > 0:
            # Complete in-progress items gradually
            completed_today = done_count + (in_progress * day // 7)
        else:
            # Linear progress on remaining
            remaining = total - done_count - in_progress
            days_since = max(1, day - 7)
            completed_today = done_count + in_progress + min(
                remaining, remaining * days_since // max(14, days_ahead - 7)
            )

        pct = (completed_today / total * 100) if total > 0 else 0

        projection.append({
            "date": current_date.isoformat(),
            "completed": completed_today,
            "percent": round(pct, 1),
        })

    return {
        "start_date": today.isoformat(),
        "total_projects": total,
        "currently_done": done_count,
        "projection": projection,
    }
