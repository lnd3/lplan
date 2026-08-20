"""CLI interface for planner framework."""

import json
import sys
from pathlib import Path
from typing import Optional

import click

from . import __version__
from .parser import PlanParser
from .validator import SchemaValidator
from .priority import PriorityEngine
from .graph import DependencyGraph
from .models import Project


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


if __name__ == "__main__":
    main()
