"""Parser for plan files - extracts YAML frontmatter and markdown sections."""

from datetime import date
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import yaml
from .models import (
    Project, Design, Action, MasterPlan, Thesis, Concept, ConceptType, PlanEntity, PlanFile, Status, Priority,
    ExternalDependency
)


class PlanParser:
    """Parse markdown files with YAML frontmatter into plan entities."""

    @staticmethod
    def parse_file(filepath: Path) -> PlanFile:
        """Parse a single plan file.

        Expected format:
        ---
        id: P001
        title: ...
        status: ...
        ... (more YAML)
        ---

        ## Goal
        ...

        ## Scope
        ...

        ## Linked
        ...

        ## Tasks
        ...

        ## Log
        ...
        """
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        # Extract frontmatter
        if not content.startswith("---"):
            raise ValueError(f"File {filepath} does not start with frontmatter delimiter")

        # Split on the closing --- delimiter
        parts = content.split("---", 2)
        if len(parts) < 3:
            raise ValueError(f"File {filepath} has malformed frontmatter (no closing ---)")

        frontmatter_str = parts[1]
        body = parts[2].lstrip("\n")

        # Parse YAML
        try:
            frontmatter = yaml.safe_load(frontmatter_str)
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML in {filepath}: {e}")

        if not isinstance(frontmatter, dict):
            raise ValueError(f"Frontmatter in {filepath} is not a YAML object")

        # Extract sections from markdown body
        sections = PlanParser._extract_sections(body)

        # Infer entity type from ID prefix
        entity_id = frontmatter.get("id", "")
        entity_type = entity_id[0] if entity_id else None

        # Create appropriate entity
        entity: PlanEntity
        if entity_type == "T":
            entity = PlanParser._parse_thesis(frontmatter)
        elif entity_type == "M":
            entity = PlanParser._parse_master_plan(frontmatter)
        elif entity_type == "P":
            entity = PlanParser._parse_project(frontmatter)
        elif entity_type == "D":
            entity = PlanParser._parse_design(frontmatter)
        elif entity_type == "A":
            entity = PlanParser._parse_action(frontmatter)
        elif entity_type == "C":
            entity = PlanParser._parse_concept(frontmatter)
        else:
            raise ValueError(f"Unknown entity type from ID: {entity_id}")

        plan_file = PlanFile(
            entity=entity,
            goal=sections.get("goal"),
            scope=sections.get("scope"),
            linked=sections.get("linked"),
            tasks=sections.get("tasks"),
            log=sections.get("log"),
            raw_content=body,
        )

        return plan_file

    @staticmethod
    def parse_directory(plan_dir: Path) -> Dict[str, PlanFile]:
        """Parse all plan files in a directory structure.

        Returns dict mapping file path to parsed PlanFile.
        """
        results: Dict[str, PlanFile] = {}

        for subdirs in ["concepts", "theses", "master_plans", "projects", "designs", "actions"]:
            subdir = plan_dir / subdirs
            if not subdir.exists():
                continue

            for filepath in subdir.glob("*.md"):
                try:
                    plan_file = PlanParser.parse_file(filepath)
                    results[str(filepath)] = plan_file
                except Exception as e:
                    results[str(filepath)] = {"error": str(e)}  # type: ignore

        return results

    @staticmethod
    def _parse_project(data: Dict[str, Any]) -> Project:
        """Parse project frontmatter into Project model."""
        # Parse external_dependencies
        external_deps: List[ExternalDependency] = []
        if "external_dependencies" in data and data["external_dependencies"]:
            for dep in data["external_dependencies"]:
                if isinstance(dep, dict):
                    external_deps.append(ExternalDependency(**dep))

        # Convert date strings to date objects
        created = data.get("created")
        updated = data.get("updated")
        if isinstance(created, str):
            created = date.fromisoformat(created)
        if isinstance(updated, str):
            updated = date.fromisoformat(updated)

        # Parse estimate if present
        estimate = None
        if "estimate" in data and data["estimate"]:
            est_data = data["estimate"]
            if isinstance(est_data, dict):
                # Convert date strings in estimate
                for date_field in ("started", "completed"):
                    if date_field in est_data and isinstance(est_data[date_field], str):
                        est_data[date_field] = date.fromisoformat(est_data[date_field])
                from .models import Estimate
                estimate = Estimate(**est_data)

        return Project(
            id=data["id"],
            title=data["title"],
            status=Status(data["status"]),
            priority=Priority(data["priority"]),
            priority_drivers=data.get("priority_drivers", []),
            created=created,
            updated=updated,
            description=data.get("description"),
            depends=data.get("depends", []),
            external_dependencies=external_deps,
            enables=data.get("enables", []),
            project=data.get("project"),
            estimate=estimate,
            parent_master_plan=data.get("parent_master_plan", []),
            stakeholder=data.get("stakeholder"),
        )

    @staticmethod
    def _parse_design(data: Dict[str, Any]) -> Design:
        """Parse design frontmatter into Design model."""
        external_deps: List[ExternalDependency] = []
        if "external_dependencies" in data and data["external_dependencies"]:
            for dep in data["external_dependencies"]:
                if isinstance(dep, dict):
                    external_deps.append(ExternalDependency(**dep))

        created = data.get("created")
        updated = data.get("updated")
        if isinstance(created, str):
            created = date.fromisoformat(created)
        if isinstance(updated, str):
            updated = date.fromisoformat(updated)

        return Design(
            id=data["id"],
            title=data["title"],
            status=Status(data["status"]),
            project=data["project"],
            created=created,
            updated=updated,
            description=data.get("description"),
            external_dependencies=external_deps,
        )

    @staticmethod
    def _parse_action(data: Dict[str, Any]) -> Action:
        """Parse action frontmatter into Action model."""
        created = data.get("created")
        updated = data.get("updated")
        if isinstance(created, str):
            created = date.fromisoformat(created)
        if isinstance(updated, str):
            updated = date.fromisoformat(updated)

        priority = None
        if "priority" in data and data["priority"]:
            priority = Priority(data["priority"])

        return Action(
            id=data["id"],
            title=data["title"],
            status=Status(data["status"]),
            created=created,
            updated=updated,
            description=data.get("description"),
            design=data.get("design"),
            project=data.get("project"),
            priority=priority,
        )

    @staticmethod
    def _parse_concept(data: Dict[str, Any]) -> Concept:
        """Parse concept frontmatter into Concept model."""
        created = data.get("created")
        updated = data.get("updated")
        if isinstance(created, str):
            created = date.fromisoformat(created)
        if isinstance(updated, str):
            updated = date.fromisoformat(updated)
        return Concept(
            id=data["id"],
            title=data["title"],
            status=Status(data["status"]),
            created=created,
            updated=updated,
            description=data.get("description"),
            concept_type=ConceptType(data.get("type", "term")),
            related=data.get("related", []),
        )

    @staticmethod
    def _parse_thesis(data: Dict[str, Any]) -> Thesis:
        """Parse thesis frontmatter into Thesis model."""
        created = data.get("created")
        updated = data.get("updated")
        if isinstance(created, str):
            created = date.fromisoformat(created)
        if isinstance(updated, str):
            updated = date.fromisoformat(updated)

        return Thesis(
            id=data["id"],
            title=data["title"],
            status=Status(data["status"]),
            created=created,
            updated=updated,
            description=data.get("description"),
            conviction=data.get("conviction"),
        )

    @staticmethod
    def _parse_master_plan(data: Dict[str, Any]) -> MasterPlan:
        """Parse master plan frontmatter into MasterPlan model."""
        created = data.get("created")
        updated = data.get("updated")
        if isinstance(created, str):
            created = date.fromisoformat(created)
        if isinstance(updated, str):
            updated = date.fromisoformat(updated)

        priority = None
        if "priority" in data and data["priority"]:
            priority = Priority(data["priority"])

        return MasterPlan(
            id=data["id"],
            title=data["title"],
            status=Status(data["status"]),
            created=created,
            updated=updated,
            description=data.get("description"),
            stakeholder=data.get("stakeholder", ""),
            priority=priority,
            vision=data.get("vision"),
            goals=data.get("goals", []),
            scope=data.get("scope"),
            parent_thesis=data.get("parent_thesis", []),
        )

    @staticmethod
    def _extract_sections(body: str) -> Dict[str, Optional[str | List[str]]]:
        """Extract markdown sections from body."""
        sections: Dict[str, Optional[str | List[str]]] = {
            "goal": None,
            "scope": None,
            "linked": None,
            "tasks": None,
            "log": None,
        }

        # Split by section headers (## Section Name)
        lines = body.split("\n")
        current_section = None
        current_content: List[str] = []

        for line in lines:
            if line.startswith("## "):
                # Save previous section
                if current_section:
                    section_name = current_section.lower().replace("-", "").replace(" ", "")
                    content = "\n".join(current_content).strip()

                    if section_name == "tasks":
                        # Extract task items (lines starting with - [ ] or - [x])
                        tasks = [
                            l.strip()
                            for l in current_content
                            if l.strip().startswith("- [")
                        ]
                        sections["tasks"] = tasks if tasks else None
                    elif section_name == "log":
                        # Extract log entries (lines starting with YYYY-MM-DD)
                        logs = [
                            l.strip()
                            for l in current_content
                            if l.strip() and l[0].isdigit()
                        ]
                        sections["log"] = logs if logs else None
                    else:
                        sections[section_name] = content if content else None

                # Start new section
                current_section = line[3:].strip()
                current_content = []
            else:
                current_content.append(line)

        # Don't forget the last section
        if current_section:
            section_name = current_section.lower().replace("-", "").replace(" ", "")
            content = "\n".join(current_content).strip()

            if section_name == "tasks":
                tasks = [
                    l.strip()
                    for l in current_content
                    if l.strip().startswith("- [")
                ]
                sections["tasks"] = tasks if tasks else None
            elif section_name == "log":
                logs = [
                    l.strip()
                    for l in current_content
                    if l.strip() and l[0].isdigit()
                ]
                sections["log"] = logs if logs else None
            else:
                sections[section_name] = content if content else None

        return sections
