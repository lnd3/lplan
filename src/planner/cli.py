"""CLI interface for planner framework."""

import json
import sys
from datetime import date
from pathlib import Path
from typing import Optional

import click

from . import __version__
from .parser import PlanParser
from .validator import SchemaValidator
from .priority import PriorityEngine
from .graph import DependencyGraph
from .models import Project, Status
from .stats import compute_stats, compute_timeline, compute_estimates, compute_velocity
from .writer import update_entity_frontmatter, append_log_entry
from .index_gen import generate_index, write_index, append_changelog, detect_repo_name
from .init import init_plan
from .refs import check_references
from .git_ops import governed_commit
from .report import write_report
from .watch import watch_plan
from .impact import analyze_impact
from .metrics import compute_all_metrics
from .bottleneck import detect_bottlenecks
from .capacity import analyze_capacity


@click.group()
@click.version_option(version=__version__)
def main() -> None:
    """Planner Framework - Structured project planning with dependency analysis."""
    pass


@main.command()
@click.argument("plan_dir", type=click.Path(exists=True), default=".")
def validate(plan_dir: str) -> None:
    """Validate a plan directory against schema."""
    plan_path = Path(plan_dir)

    click.echo(f"Validating plan directory: {plan_path}")
    click.echo()

    # Parse all files
    try:
        files = PlanParser.parse_directory(plan_path)
    except Exception as e:
        click.echo(f"Error parsing files: {e}", err=True)
        sys.exit(1)

    # Separate valid entities and errors
    entities = {}
    errors = []

    for filepath, result in files.items():
        if isinstance(result, dict) and "error" in result:
            errors.append((filepath, result["error"]))
        else:
            entities[result.entity.id] = result.entity

    # Validate each entity
    validator = SchemaValidator()
    entity_errors = 0

    for entity_id, entity in entities.items():
        if not validator.validate_entity(entity):
            entity_errors += 1
            for error in validator.errors:
                click.echo(f"  ✗ {error}", err=True)

    # Validate relationships
    if not validator.validate_relationships(entities):
        for error in validator.errors:
            click.echo(f"  ✗ {error}", err=True)

    # Report
    click.echo()
    click.echo("=" * 50)

    if errors:
        click.echo(f"✗ {len(errors)} files had parse errors:", err=True)
        for filepath, error in errors:
            click.echo(f"  {filepath}: {error}", err=True)

    if entity_errors > 0:
        click.echo(f"✗ {entity_errors} entities failed validation", err=True)
        sys.exit(1)

    if validator.errors:
        click.echo(f"✗ {len(validator.errors)} relationship errors", err=True)
        sys.exit(1)

    click.echo(f"✓ Validation passed ({len(entities)} entities)")
    if validator.warnings:
        click.echo(f"  ({len(validator.warnings)} warnings)")


@main.command()
@click.argument("plan_dir", type=click.Path(exists=True), default=".")
def priority(plan_dir: str) -> None:
    """Analyze project priorities."""
    plan_path = Path(plan_dir)

    try:
        files = PlanParser.parse_directory(plan_path)
    except Exception as e:
        click.echo(f"Error parsing files: {e}", err=True)
        sys.exit(1)

    # Extract projects
    projects: dict = {}
    for result in files.values():
        if not isinstance(result, dict) or "error" not in result:
            if isinstance(result.entity, Project):
                projects[result.entity.id] = result.entity

    if not projects:
        click.echo("No projects found")
        sys.exit(0)

    # Analyze priorities
    engine = PriorityEngine()
    click.echo("Project Priorities")
    click.echo("=" * 70)

    for project_id in sorted(projects.keys()):
        project = projects[project_id]
        analysis = engine.analyze_project(project)

        status = "✓" if analysis["match"] else "✗"
        click.echo(
            f"{status} {project_id}: {analysis['declared_priority']:6} "
            f"(score={analysis['score']:5.1f}, status={analysis['status']})"
        )

        if not analysis["match"]:
            click.echo(
                f"    ⚠ Mismatch: drivers compute to {analysis['computed_priority']}"
            )

        if analysis["unknown_drivers"]:
            click.echo(f"    ⚠ Unknown drivers: {', '.join(analysis['unknown_drivers'])}")

    click.echo()
    click.echo("Driver Definitions")
    click.echo("=" * 70)
    weights = engine.get_driver_weights()
    for driver, weight in sorted(weights.items()):
        click.echo(f"  {driver:35} {weight:+5.1f}")


@main.command()
@click.argument("project_id")
@click.argument("plan_dir", type=click.Path(exists=True), default=".")
def deps(project_id: str, plan_dir: str) -> None:
    """Show dependencies for a project."""
    plan_path = Path(plan_dir)

    try:
        files = PlanParser.parse_directory(plan_path)
    except Exception as e:
        click.echo(f"Error parsing files: {e}", err=True)
        sys.exit(1)

    # Extract projects
    projects = {}
    for result in files.values():
        if not isinstance(result, dict) or "error" not in result:
            if isinstance(result.entity, Project):
                projects[result.entity.id] = result.entity

    if project_id not in projects:
        click.echo(f"Project {project_id} not found", err=True)
        sys.exit(1)

    project = projects[project_id]
    graph = DependencyGraph(projects)

    click.echo(f"Project: {project_id} - {project.title}")
    click.echo("=" * 70)

    # Direct dependencies
    direct_deps = graph.get_blocking_deps(project_id)
    if direct_deps:
        click.echo("\nDirect Dependencies (blocks this project):")
        for dep in direct_deps:
            if dep in projects:
                p = projects[dep]
                click.echo(f"  - {dep}: {p.title} ({p.status.value})")
            else:
                click.echo(f"  - {dep} (external)")
    else:
        click.echo("\nNo direct dependencies")

    # Transitive dependencies
    trans_deps = graph.get_transitive_deps(project_id)
    if trans_deps:
        click.echo(f"\nTransitive Dependencies ({len(trans_deps)} total):")
        for dep in sorted(trans_deps):
            p = projects[dep]
            click.echo(f"  - {dep}: {p.title}")
    else:
        click.echo("\nNo transitive dependencies")

    # Projects that depend on this one
    dependents = graph.get_blocked_by(project_id)
    if dependents:
        click.echo("\nProjects Depending On This:")
        for dep in dependents:
            if dep in projects:
                p = projects[dep]
                click.echo(f"  - {dep}: {p.title} ({p.status.value})")
            else:
                click.echo(f"  - {dep} (external)")
    else:
        click.echo("\nNo projects depend on this one")


@main.command()
@click.argument("plan_dir", type=click.Path(exists=True), default=".")
def blocked(plan_dir: str) -> None:
    """List blocked projects and their blockers."""
    plan_path = Path(plan_dir)

    try:
        files = PlanParser.parse_directory(plan_path)
    except Exception as e:
        click.echo(f"Error parsing files: {e}", err=True)
        sys.exit(1)

    # Extract projects
    projects = {}
    for result in files.values():
        if not isinstance(result, dict) or "error" not in result:
            if isinstance(result.entity, Project):
                projects[result.entity.id] = result.entity

    # Filter blocked projects
    blocked_projects = {
        pid: p for pid, p in projects.items() if p.status.value == "BLOCKED"
    }

    if not blocked_projects:
        click.echo("No blocked projects")
        sys.exit(0)

    graph = DependencyGraph(projects)

    click.echo("Blocked Projects")
    click.echo("=" * 70)

    for project_id in sorted(blocked_projects.keys()):
        project = blocked_projects[project_id]
        deps = graph.get_blocking_deps(project_id)

        click.echo(f"\n{project_id}: {project.title}")
        click.echo(f"  Status: {project.status.value}")
        click.echo(f"  Priority: {project.priority.value}")

        if deps:
            click.echo("  Blocked by:")
            for dep in deps:
                if dep in projects:
                    p = projects[dep]
                    click.echo(f"    - {dep}: {p.title} ({p.status.value})")
                else:
                    click.echo(f"    - {dep} (external)")
        else:
            click.echo("  (No blocking dependencies found)")


@main.command()
@click.argument("plan_dir", type=click.Path(exists=True), default=".")
def graph_report(plan_dir: str) -> None:
    """Generate dependency graph analysis report."""
    plan_path = Path(plan_dir)

    try:
        files = PlanParser.parse_directory(plan_path)
    except Exception as e:
        click.echo(f"Error parsing files: {e}", err=True)
        sys.exit(1)

    # Extract projects
    projects = {}
    for result in files.values():
        if not isinstance(result, dict) or "error" not in result:
            if isinstance(result.entity, Project):
                projects[result.entity.id] = result.entity

    if not projects:
        click.echo("No projects found")
        sys.exit(0)

    graph = DependencyGraph(projects)
    report = graph.get_report()

    click.echo("Dependency Graph Analysis")
    click.echo("=" * 70)
    click.echo(f"Total projects: {report['total_projects']}")
    click.echo(f"Total dependencies: {report['total_edges']}")
    click.echo(f"Has cycles: {'✗ YES' if report['has_cycles'] else '✓ No'}")

    if report["cycles"]:
        click.echo(f"\nCycles detected ({len(report['cycles'])}):")
        for cycle in report["cycles"]:
            click.echo(f"  {' → '.join(cycle)} → {cycle[0]}")

    if report["root_projects"]:
        click.echo(f"\nRoot projects (no dependencies):")
        for pid in report["root_projects"]:
            p = projects[pid]
            click.echo(f"  - {pid}: {p.title}")

    if report["leaf_projects"]:
        click.echo(f"\nLeaf projects (no dependents):")
        for pid in report["leaf_projects"]:
            p = projects[pid]
            click.echo(f"  - {pid}: {p.title}")

    if report["cross_repo_refs"]:
        click.echo(f"\nCross-repo references ({len(report['cross_repo_refs'])}):")
        for ref in sorted(report["cross_repo_refs"]):
            click.echo(f"  - {ref}")


@main.command()
@click.argument("plan_dir", type=click.Path(exists=True), default=".")
def stats(plan_dir: str) -> None:
    """Show aggregate statistics."""
    plan_path = Path(plan_dir)

    try:
        files = PlanParser.parse_directory(plan_path)
    except Exception as e:
        click.echo(f"Error parsing files: {e}", err=True)
        sys.exit(1)

    entities = {}
    for result in files.values():
        if not isinstance(result, dict) or "error" not in result:
            entities[result.entity.id] = result.entity

    stat_data = compute_stats(entities)

    click.echo("Plan Statistics")
    click.echo("=" * 70)
    click.echo(f"Projects: {stat_data['projects_total']}")
    click.echo(f"Designs: {stat_data['designs_total']}")
    click.echo(f"Actions: {stat_data['actions_total']}")
    click.echo(f"% Done: {stat_data['percent_done']:.1f}%")
    click.echo(f"Blocked: {stat_data['blocked_count']}")
    click.echo(f"Priority Mismatches: {stat_data['priority_mismatches']}")
    click.echo(f"\nBy Status:")
    for status, count in sorted(stat_data['by_status'].items()):
        click.echo(f"  {status}: {count}")


@main.command()
@click.argument("plan_dir", type=click.Path(exists=True), default=".")
def timeline(plan_dir: str) -> None:
    """Show project execution phases."""
    plan_path = Path(plan_dir)

    try:
        files = PlanParser.parse_directory(plan_path)
    except Exception as e:
        click.echo(f"Error parsing files: {e}", err=True)
        sys.exit(1)

    projects = {}
    for result in files.values():
        if not isinstance(result, dict) or "error" not in result:
            if isinstance(result.entity, Project):
                projects[result.entity.id] = result.entity

    if not projects:
        click.echo("No projects found")
        sys.exit(0)

    graph = DependencyGraph(projects)
    phases = compute_timeline(projects, graph)

    click.echo("Project Execution Timeline")
    click.echo("=" * 70)

    for phase_num, project_ids in phases:
        click.echo(f"\nPhase {phase_num} (can run in parallel):")
        for pid in sorted(project_ids):
            p = projects[pid]
            click.echo(f"  - {pid}: {p.title} ({p.status.value})")


@main.command()
@click.argument("plan_dir", type=click.Path(exists=True), default=".")
def estimate(plan_dir: str) -> None:
    """Show time estimate rollup."""
    plan_path = Path(plan_dir)

    try:
        files = PlanParser.parse_directory(plan_path)
    except Exception as e:
        click.echo(f"Error parsing files: {e}", err=True)
        sys.exit(1)

    projects = {}
    for result in files.values():
        if not isinstance(result, dict) or "error" not in result:
            if isinstance(result.entity, Project):
                projects[result.entity.id] = result.entity

    if not projects:
        click.echo("No projects found")
        sys.exit(0)

    est_data = compute_estimates(projects)

    click.echo("Time Estimates")
    click.echo("=" * 70)
    click.echo(f"Total Effort: {est_data['total_effort_days']} days")
    click.echo(f"Projects with Estimates: {est_data['projects_with_estimates']}")
    click.echo(f"Projects without Estimates: {est_data['projects_without_estimates']}")

    if est_data['by_status']:
        click.echo(f"\nBy Status:")
        for status, (days, count) in sorted(est_data['by_status'].items()):
            click.echo(f"  {status}: {days} days ({count} projects)")


@main.command()
@click.argument("plan_dir", type=click.Path(exists=True), default=".")
def velocity(plan_dir: str) -> None:
    """Show velocity metrics from completed estimates."""
    plan_path = Path(plan_dir)

    try:
        files = PlanParser.parse_directory(plan_path)
    except Exception as e:
        click.echo(f"Error parsing files: {e}", err=True)
        sys.exit(1)

    projects = {}
    for result in files.values():
        if not isinstance(result, dict) or "error" not in result:
            if isinstance(result.entity, Project):
                projects[result.entity.id] = result.entity

    if not projects:
        click.echo("No projects found")
        sys.exit(0)

    vel_data = compute_velocity(projects)

    click.echo("Velocity Analysis")
    click.echo("=" * 70)

    if vel_data['completed_projects'] == 0:
        click.echo("No completed projects with full estimate data")
        sys.exit(0)

    click.echo(f"Completed Projects: {vel_data['completed_projects']}")
    click.echo(f"Average Variance: {vel_data['average_variance_percent']:+.1f}%")

    if vel_data['projects']:
        click.echo(f"\nProject Details:")
        for proj in vel_data['projects']:
            click.echo(
                f"  {proj['id']}: {proj['effort_days']} days estimated, "
                f"{proj['actual_days']} days actual ({proj['variance_percent']:+.1f}%)"
            )


@main.command()
@click.argument("entity_id")
@click.argument("note")
@click.argument("plan_dir", type=click.Path(exists=True), default=".")
@click.option("--status", help="Also update status to this value")
def log(entity_id: str, note: str, plan_dir: str, status: Optional[str]) -> None:
    """Append log entry to an entity."""
    plan_path = Path(plan_dir)

    try:
        files = PlanParser.parse_directory(plan_path)
    except Exception as e:
        click.echo(f"Error parsing files: {e}", err=True)
        sys.exit(1)

    # Find the entity file
    entity_file = None
    for result in files.values():
        if not isinstance(result, dict) or "error" not in result:
            if result.entity.id == entity_id:
                entity_file = result.entity
                break

    if not entity_file:
        click.echo(f"Entity {entity_id} not found", err=True)
        sys.exit(1)

    # Find the file path
    entity_path = None
    for fpath, result in files.items():
        if not isinstance(result, dict) or "error" not in result:
            if result.entity.id == entity_id:
                entity_path = Path(fpath)
                break

    if not entity_path:
        click.echo(f"Could not find file for {entity_id}", err=True)
        sys.exit(1)

    try:
        # Update status if requested
        if status:
            update_entity_frontmatter(
                entity_path,
                {"status": status, "updated": date.today().isoformat()}
            )
            append_changelog(plan_path, entity_id, entity_file.status.value, status, note)

        # Append log entry
        append_log_entry(entity_path, note)
        click.echo(f"✓ Logged: {entity_id}")

    except Exception as e:
        click.echo(f"Error updating entity: {e}", err=True)
        sys.exit(1)


@main.command()
@click.argument("entity_id")
@click.argument("plan_dir", type=click.Path(exists=True), default=".")
@click.option("--status", help="Update status")
@click.option("--priority", help="Update priority")
def update(entity_id: str, plan_dir: str, status: Optional[str], priority: Optional[str]) -> None:
    """Update entity frontmatter fields."""
    plan_path = Path(plan_dir)

    if not status and not priority:
        click.echo("No updates specified (use --status or --priority)", err=True)
        sys.exit(1)

    try:
        files = PlanParser.parse_directory(plan_path)
    except Exception as e:
        click.echo(f"Error parsing files: {e}", err=True)
        sys.exit(1)

    # Find the entity file
    entity_file = None
    entity_path = None
    for fpath, result in files.items():
        if not isinstance(result, dict) or "error" not in result:
            if result.entity.id == entity_id:
                entity_file = result.entity
                entity_path = Path(fpath)
                break

    if not entity_file:
        click.echo(f"Entity {entity_id} not found", err=True)
        sys.exit(1)

    # Build updates
    updates = {"updated": date.today().isoformat()}
    if status:
        updates["status"] = status
    if priority:
        updates["priority"] = priority

    try:
        update_entity_frontmatter(entity_path, updates)
        click.echo(f"✓ Updated: {entity_id}")
    except Exception as e:
        click.echo(f"Error updating entity: {e}", err=True)
        sys.exit(1)


@main.command()
@click.argument("plan_dir", type=click.Path(exists=True), default=".")
@click.option("--repo-name", default=None, help="Repository name (auto-detected from parent dir if not provided)")
def generate_index(plan_dir: str, repo_name: str) -> None:
    """Generate or update INDEX.md."""
    plan_path = Path(plan_dir)

    # Auto-detect repo name if not provided
    if not repo_name:
        repo_name = detect_repo_name(plan_path)

    try:
        files = PlanParser.parse_directory(plan_path)
    except Exception as e:
        click.echo(f"Error parsing files: {e}", err=True)
        sys.exit(1)

    entities = {}
    for result in files.values():
        if not isinstance(result, dict) or "error" not in result:
            entities[result.entity.id] = result.entity

    try:
        write_index(plan_path, entities, repo_name)
        click.echo(f"✓ Generated INDEX.md (repo: {repo_name})")
    except Exception as e:
        click.echo(f"Error generating index: {e}", err=True)
        sys.exit(1)


@main.command()
@click.argument("plan_dir", type=click.Path())
@click.option("--name", required=True, help="Repository name")
@click.option("--first-project", help="Optional first project title")
def init(plan_dir: str, name: str, first_project: Optional[str]) -> None:
    """Initialize a new plan directory."""
    plan_path = Path(plan_dir)

    try:
        init_plan(plan_path, name, first_project)
        click.echo(f"✓ Initialized plan directory: {plan_path}")
    except Exception as e:
        click.echo(f"Error initializing plan: {e}", err=True)
        sys.exit(1)


@main.command()
@click.argument("plan_dir", type=click.Path(exists=True), default=".")
def check_refs(plan_dir: str) -> None:
    """Check for reference errors and orphaned entities."""
    plan_path = Path(plan_dir)

    try:
        files = PlanParser.parse_directory(plan_path)
    except Exception as e:
        click.echo(f"Error parsing files: {e}", err=True)
        sys.exit(1)

    entities = {}
    for result in files.values():
        if not isinstance(result, dict) or "error" not in result:
            entities[result.entity.id] = result.entity

    report = check_references(entities, plan_path)

    click.echo("Reference Check Report")
    click.echo("=" * 70)
    click.echo(f"References Checked: {report['local_refs_checked']}")

    if report['unresolvable_refs']:
        click.echo(f"\nUnresolvable References ({len(report['unresolvable_refs'])}):")
        for ref_info in report['unresolvable_refs']:
            click.echo(f"  ✗ {ref_info['from']}: {ref_info['ref']} ({ref_info['hint']})")

    if report['orphaned_designs']:
        click.echo(f"\nOrphaned Designs ({len(report['orphaned_designs'])}):")
        for design_id in report['orphaned_designs']:
            click.echo(f"  ⚠ {design_id}")

    if report['orphaned_actions']:
        click.echo(f"\nOrphaned Actions ({len(report['orphaned_actions'])}):")
        for action_id in report['orphaned_actions']:
            click.echo(f"  ⚠ {action_id}")

    if report['unused_projects']:
        click.echo(f"\nUnused Projects ({len(report['unused_projects'])}):")
        for project_id in report['unused_projects']:
            click.echo(f"  ℹ {project_id}")

    if report['errors']:
        click.echo(f"\nErrors ({len(report['errors'])}):")
        for error in report['errors']:
            click.echo(f"  ✗ {error}")
        sys.exit(1)


@main.command()
@click.argument("plan_dir", type=click.Path(exists=True), default=".")
@click.option("-m", "--message", required=True, help="Commit message")
def commit(plan_dir: str, message: str) -> None:
    """Commit plan changes with validation."""
    plan_path = Path(plan_dir)

    try:
        governed_commit(plan_path, message)
    except RuntimeError as e:
        click.echo(f"{e}", err=True)
        sys.exit(1)


@main.command()
@click.argument("plan_dir", type=click.Path(exists=True), default=".")
@click.option("-o", "--output", type=click.Path(), help="Output file path")
def report(plan_dir: str, output: Optional[str]) -> None:
    """Generate HTML report."""
    plan_path = Path(plan_dir)

    if not output:
        output = str(plan_path / "report.html")

    output_path = Path(output)

    try:
        files = PlanParser.parse_directory(plan_path)
    except Exception as e:
        click.echo(f"Error parsing files: {e}", err=True)
        sys.exit(1)

    entities = {}
    for result in files.values():
        if not isinstance(result, dict) or "error" not in result:
            entities[result.entity.id] = result.entity

    try:
        write_report(plan_path, entities, output_path)
        click.echo(f"✓ Report written: {output_path}")
    except Exception as e:
        click.echo(f"Error generating report: {e}", err=True)
        sys.exit(1)


@main.command()
@click.argument("project_id")
@click.argument("plan_dir", type=click.Path(exists=True), default=".")
def impact(project_id: str, plan_dir: str) -> None:
    """Show impact of completing a project."""
    plan_path = Path(plan_dir)

    try:
        files = PlanParser.parse_directory(plan_path)
    except Exception as e:
        click.echo(f"Error parsing files: {e}", err=True)
        sys.exit(1)

    projects = {}
    for result in files.values():
        if not isinstance(result, dict) or "error" not in result:
            if isinstance(result.entity, Project):
                projects[result.entity.id] = result.entity

    if project_id not in projects:
        click.echo(f"Project {project_id} not found", err=True)
        sys.exit(1)

    graph = DependencyGraph(projects)
    impact_data = analyze_impact(project_id, projects, graph)

    click.echo(f"Impact Analysis: {impact_data['project_id']} - {impact_data['title']}")
    click.echo("=" * 70)
    click.echo(f"Status: {impact_data['status']}")
    click.echo(f"\nDirectly unblocks: {impact_data['num_unblocked']} project(s)")
    if impact_data["unblocks"]:
        for uid in impact_data["unblocks"]:
            click.echo(f"  - {uid}: {projects[uid].title if uid in projects else '(external)'}")

    click.echo(f"\nDownstream impact: {impact_data['num_downstream']} project(s)")
    if impact_data["downstream"]:
        for did in impact_data["downstream"][:5]:
            click.echo(f"  - {did}")
        if len(impact_data["downstream"]) > 5:
            click.echo(f"  ... and {len(impact_data['downstream']) - 5} more")

    click.echo(f"\nBlocked by: {len(impact_data['blocked_by'])} project(s)")
    if impact_data["blocked_by"]:
        for bid in impact_data["blocked_by"]:
            click.echo(f"  - {bid}")

    click.echo(f"\nOverall impact ratio: {impact_data['impact_ratio']:.0%}")


@main.command()
@click.argument("plan_dir", type=click.Path(exists=True), default=".")
def metrics(plan_dir: str) -> None:
    """Show project metrics (fan-in, depth, criticality)."""
    plan_path = Path(plan_dir)

    try:
        files = PlanParser.parse_directory(plan_path)
    except Exception as e:
        click.echo(f"Error parsing files: {e}", err=True)
        sys.exit(1)

    projects = {}
    for result in files.values():
        if not isinstance(result, dict) or "error" not in result:
            if isinstance(result.entity, Project):
                projects[result.entity.id] = result.entity

    if not projects:
        click.echo("No projects found")
        sys.exit(0)

    graph = DependencyGraph(projects)
    metrics_data = compute_all_metrics(projects, graph)

    click.echo("Project Metrics")
    click.echo("=" * 70)
    click.echo(f"{'ID':<6} {'Fan-In':<8} {'Fan-Out':<8} {'Depth':<7} {'Criticality':<12}")
    click.echo("-" * 70)

    for project_id in sorted(metrics_data.keys()):
        m = metrics_data[project_id]
        click.echo(
            f"{m['project_id']:<6} {m['fan_in']:<8} {m['fan_out']:<8} "
            f"{m['depth']:<7} {m['criticality']:<12.2f}"
        )


@main.command()
@click.argument("plan_dir", type=click.Path(exists=True), default=".")
def bottlenecks(plan_dir: str) -> None:
    """Detect bottleneck projects."""
    plan_path = Path(plan_dir)

    try:
        files = PlanParser.parse_directory(plan_path)
    except Exception as e:
        click.echo(f"Error parsing files: {e}", err=True)
        sys.exit(1)

    projects = {}
    for result in files.values():
        if not isinstance(result, dict) or "error" not in result:
            if isinstance(result.entity, Project):
                projects[result.entity.id] = result.entity

    if not projects:
        click.echo("No projects found")
        sys.exit(0)

    graph = DependencyGraph(projects)
    bottleneck_data = detect_bottlenecks(projects, graph)

    click.echo("Bottleneck Detection")
    click.echo("=" * 70)
    click.echo(f"Summary: {bottleneck_data['summary']}")

    if bottleneck_data["blocking_bottlenecks"]:
        click.echo("\nBlocking Bottlenecks:")
        for b in bottleneck_data["blocking_bottlenecks"]:
            click.echo(f"  ⚠ {b['project_id']}: {b['title']} ({b['status']})")
            click.echo(f"     → {b['reason']}")

    if bottleneck_data["deep_chains"]:
        click.echo("\nDeep Dependency Chains:")
        for chain in bottleneck_data["deep_chains"][:3]:
            click.echo(f"  {chain['length']} projects: {' → '.join(chain['chain'])}")
            if chain.get("effort_days"):
                click.echo(f"     (~{chain['effort_days']} days estimated)")


@main.command()
@click.argument("plan_dir", type=click.Path(exists=True), default=".")
def capacity(plan_dir: str) -> None:
    """Analyze capacity and parallelization."""
    plan_path = Path(plan_dir)

    try:
        files = PlanParser.parse_directory(plan_path)
    except Exception as e:
        click.echo(f"Error parsing files: {e}", err=True)
        sys.exit(1)

    projects = {}
    for result in files.values():
        if not isinstance(result, dict) or "error" not in result:
            if isinstance(result.entity, Project):
                projects[result.entity.id] = result.entity

    if not projects:
        click.echo("No projects found")
        sys.exit(0)

    graph = DependencyGraph(projects)
    capacity_data = analyze_capacity(projects, graph)

    click.echo("Capacity Analysis")
    click.echo("=" * 70)
    click.echo(f"Total effort: {capacity_data['total_effort_days']} days")
    click.echo(f"Estimated projects: {capacity_data['estimated_projects']}/{len(projects)}")
    click.echo(f"Critical path: {capacity_data['critical_path_days']} days")
    click.echo(f"Parallelizable: {capacity_data['parallelizable_effort']} days")
    click.echo(f"Compression ratio: {capacity_data['compression_ratio']}x (perfect parallelization)")

    click.echo("\nTimeline Phases:")
    for phase in capacity_data["timeline_phases"]:
        click.echo(
            f"  Phase {phase['phase']}: {phase['project_count']} project(s), "
            f"{phase['total_effort_days']} days effort, "
            f"~{phase['ideal_duration_days']} days to complete"
        )


@main.command()
@click.argument("plan_dir", type=click.Path(exists=True), default=".")
@click.option("--interval", type=int, default=5, help="Poll interval in seconds")
def watch(plan_dir: str, interval: int) -> None:
    """Watch plan for changes."""
    plan_path = Path(plan_dir)

    try:
        watch_plan(plan_path, interval=interval)
    except KeyboardInterrupt:
        sys.exit(0)


@main.command()
@click.argument("plan_dir", type=click.Path(exists=True), default=".")
@click.option("--host", default="127.0.0.1", show_default=True, help="Host to bind to")
@click.option("--port", default=8000, show_default=True, help="Port to listen on")
@click.option("--edit", is_flag=True, default=False, help="Enable file editing")
@click.option("--no-validate", is_flag=True, default=False, help="Skip validation on save")
def serve(plan_dir: str, host: str, port: int, edit: bool, no_validate: bool) -> None:
    """Start a local web server to browse (and optionally edit) the plan."""
    from .server import serve as _serve
    plan_path = Path(plan_dir).resolve()
    try:
        _serve(plan_path, host=host, port=port, edit=edit, validate_on_save=not no_validate)
    except KeyboardInterrupt:
        sys.exit(0)


@main.command()
@click.argument("plan_dir", type=click.Path(exists=True), default=".")
def stop(plan_dir: str) -> None:
    """Stop a running plan web server."""
    from .server import stop as _stop
    _stop(Path(plan_dir).resolve())


@main.command()
@click.argument("plan_dir", type=click.Path(exists=True), default=".")
def restart(plan_dir: str) -> None:
    """Restart the plan web server with the same options."""
    from .server import restart as _restart
    _restart(Path(plan_dir).resolve())


if __name__ == "__main__":
    main()
