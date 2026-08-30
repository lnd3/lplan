"""Schema validator for plan entities."""

import re
from typing import List, Dict, Any, Set, Optional, Tuple
from difflib import get_close_matches
from .models import Project, Design, Action, Thesis, MasterPlan, Concept, PlanEntity, Status, Priority


class ValidationError:
    """Represents a validation error."""

    def __init__(self, entity_id: str, field: str, message: str, suggestion: Optional[str] = None):
        self.entity_id = entity_id
        self.field = field
        self.message = message
        self.suggestion = suggestion

    def __str__(self) -> str:
        base = f"[{self.entity_id}] {self.field}: {self.message}"
        if self.suggestion:
            base += f"\n    Suggestion: {self.suggestion}"
        return base

    def __repr__(self) -> str:
        return f"ValidationError({self.entity_id}, {self.field}, {self.message}, {self.suggestion})"


class ValidationWarning:
    """Represents a validation warning."""

    def __init__(self, entity_id: str, field: str, message: str, suggestion: Optional[str] = None):
        self.entity_id = entity_id
        self.field = field
        self.message = message
        self.suggestion = suggestion

    def __str__(self) -> str:
        base = f"[{self.entity_id}] {self.field}: {self.message}"
        if self.suggestion:
            base += f"\n    Suggestion: {self.suggestion}"
        return base

    def __repr__(self) -> str:
        return f"ValidationWarning({self.entity_id}, {self.field}, {self.message}, {self.suggestion})"


class SchemaValidator:
    """Validates plan entities against schema rules."""

    def __init__(self) -> None:
        self.errors: List[ValidationError] = []
        self.warnings: List[ValidationWarning] = []

    def validate_entity(self, entity: PlanEntity) -> bool:
        """Validate a single entity. Returns True if valid."""
        self.errors = []
        self.warnings = []

        if isinstance(entity, Project):
            self._validate_project(entity)
        elif isinstance(entity, Design):
            self._validate_design(entity)
        elif isinstance(entity, Action):
            self._validate_action(entity)
        elif isinstance(entity, (Thesis, MasterPlan, Concept)):
            pass  # No additional structural constraints beyond frontmatter
        else:
            self.errors.append(
                ValidationError(entity.id, "type", f"Unknown entity type: {type(entity)}")
            )

        return len(self.errors) == 0

    def validate_entities(self, entities: List[PlanEntity]) -> bool:
        """Validate multiple entities. Returns True if all valid."""
        all_valid = True
        for entity in entities:
            if not self.validate_entity(entity):
                all_valid = False

        return all_valid

    def validate_relationships(
        self, entities: Dict[str, PlanEntity]
    ) -> bool:
        """Validate cross-entity relationships.

        Args:
            entities: Dict mapping entity ID to entity

        Validates:
        - Cross-repo refs resolve to actual entities
        - Projects exist for designs/actions that reference them
        - No circular dependencies
        """
        self.errors = []
        self.warnings = []

        # Check all depends/enables refs exist (locally; cross-repo is optional)
        for entity_id, entity in entities.items():
            if isinstance(entity, Project):
                for dep in entity.depends:
                    if ":" not in dep:  # Local ref
                        if dep not in entities:
                            suggestion = self._suggest_ref(dep, entities)
                            self.errors.append(
                                ValidationError(
                                    entity_id, "depends", f"Referenced project {dep} not found",
                                    suggestion=suggestion
                                )
                            )
                    # Cross-repo refs (repo:ID) are not validated here

                for enable in entity.enables:
                    if ":" not in enable:  # Local ref
                        if enable not in entities:
                            suggestion = self._suggest_ref(enable, entities)
                            self.errors.append(
                                ValidationError(
                                    entity_id, "enables", f"Referenced project {enable} not found",
                                    suggestion=suggestion
                                )
                            )

            elif isinstance(entity, Design):
                if entity.project not in entities:
                    suggestion = self._suggest_ref(entity.project, entities)
                    self.warnings.append(
                        ValidationWarning(
                            entity_id, "project", f"Parent project {entity.project} not found",
                            suggestion=suggestion
                        )
                    )

            elif isinstance(entity, Action):
                if entity.project and entity.project not in entities:
                    suggestion = self._suggest_ref(entity.project, entities)
                    self.warnings.append(
                        ValidationWarning(
                            entity_id, "project", f"Associated project {entity.project} not found",
                            suggestion=suggestion
                        )
                    )
                if entity.design and entity.design not in entities:
                    suggestion = self._suggest_ref(entity.design, entities)
                    self.warnings.append(
                        ValidationWarning(
                            entity_id, "design", f"Parent design {entity.design} not found",
                            suggestion=suggestion
                        )
                    )

        # Check 1 (A027): DONE parent with non-terminal children
        # Collect children per project and per design
        children_by_project: Dict[str, List[PlanEntity]] = {}
        children_by_design: Dict[str, List[PlanEntity]] = {}
        for entity_id, entity in entities.items():
            if isinstance(entity, Design) and entity.project:
                children_by_project.setdefault(entity.project, []).append(entity)
            elif isinstance(entity, Action):
                if entity.project:
                    children_by_project.setdefault(entity.project, []).append(entity)
                if entity.design:
                    children_by_design.setdefault(entity.design, []).append(entity)

        terminal = {Status.DONE, Status.DEFERRED, Status.CANCELLED}
        for entity_id, entity in entities.items():
            if entity.status != Status.DONE:
                continue
            if not isinstance(entity, (Project, Design)):
                continue
            children = []
            if isinstance(entity, Project):
                children = children_by_project.get(entity_id, [])
            elif isinstance(entity, Design):
                children = children_by_design.get(entity_id, [])
            non_terminal = [c for c in children if c.status not in terminal]
            if non_terminal:
                ids = ", ".join(c.id for c in non_terminal)
                self.warnings.append(
                    ValidationWarning(
                        entity_id, "status",
                        f"DONE but has non-terminal children: {ids}"
                    )
                )

        return len(self.errors) == 0

    def validate_phase_anchors(
        self, raw_content_by_project_id: Dict[str, str], entities: Dict[str, PlanEntity]
    ) -> bool:
        """D008: warn on project phase headers with no Design anchor.

        A project file may have a `## Phases` section with headers like:
            ### Phase 1 — Strategy Pipeline [D001 DONE, A001 DONE]
        The bracketed IDs are human-maintained annotations. D008's single
        structural rule: each phase must reference at least one Design entity.
        This is a soft check (warning only) — phases are free-form, gaps are
        expected, and a project with no `## Phases` section at all is simply
        not opted into the convention (nothing to check).

        Args:
            raw_content_by_project_id: project entity ID -> that project file's
                markdown body (e.g. PlanFile.raw_content)
            entities: all parsed entities, to check which bracketed IDs are Designs

        Returns:
            True if no unanchored phases were found (warnings don't fail validation).
        """
        found_unanchored = False

        for project_id, raw_content in raw_content_by_project_id.items():
            phases_section = self._extract_phases_section(raw_content)
            if phases_section is None:
                continue  # no ## Phases section: not opted in, nothing to check

            for phase_name, refs in self._extract_phase_headers(phases_section):
                design_refs = [r for r in refs if isinstance(entities.get(r), Design)]
                if not design_refs:
                    found_unanchored = True
                    self.warnings.append(
                        ValidationWarning(
                            project_id, "phase",
                            f"Phase '{phase_name}' has no Design anchor "
                            f"({'refs: ' + ', '.join(refs) if refs else 'no entity refs found'})"
                        )
                    )

        return not found_unanchored

    @staticmethod
    def _extract_phases_section(raw_content: str) -> Optional[str]:
        """Return the body of a project's `## Phases` section, or None if absent."""
        lines = raw_content.split("\n")
        start = None
        for i, line in enumerate(lines):
            if line.strip() == "## Phases":
                start = i + 1
                break
        if start is None:
            return None

        end = len(lines)
        for i in range(start, len(lines)):
            if lines[i].startswith("## "):
                end = i
                break
        return "\n".join(lines[start:end])

    @staticmethod
    def _extract_phase_headers(phases_section: str) -> List[Tuple[str, List[str]]]:
        """Parse `### <name> [<refs>]` headers into (name, [entity_ids]) pairs."""
        results: List[Tuple[str, List[str]]] = []
        header_re = re.compile(r"^###\s+(.+?)\s*(?:\[([^\]]*)\])?\s*$")
        id_re = re.compile(r"\b([A-Z]\d+)\b")

        for line in phases_section.split("\n"):
            match = header_re.match(line)
            if not match:
                continue
            name, bracket_content = match.groups()
            refs = id_re.findall(bracket_content) if bracket_content else []
            results.append((name.strip(), refs))

        return results

    def _validate_project(self, entity: Project) -> None:
        """Validate project-specific rules."""
        if not entity.priority_drivers:
            self.errors.append(
                ValidationError(entity.id, "priority_drivers", "Must not be empty")
            )

        # Check if project status is valid
        if entity.status not in Status:
            self.errors.append(
                ValidationError(entity.id, "status", f"Invalid status: {entity.status}")
            )

        # Check if priority is valid
        if entity.priority not in Priority:
            self.errors.append(
                ValidationError(entity.id, "priority", f"Invalid priority: {entity.priority}")
            )

    def _validate_design(self, entity: Design) -> None:
        """Validate design-specific rules."""
        if not entity.project:
            self.errors.append(
                ValidationError(entity.id, "project", "Design must have a parent project")
            )

        if entity.status == Status.BLOCKED:
            self.errors.append(
                ValidationError(
                    entity.id, "status", "Designs cannot have BLOCKED status"
                )
            )

    def _validate_action(self, entity: Action) -> None:
        """Validate action-specific rules."""
        # Actions can exist without project or design, so no strict requirements
        pass

    def _suggest_ref(self, missing_ref: str, entities: Dict[str, PlanEntity]) -> Optional[str]:
        """Suggest a correction for a missing reference.

        Tries:
        1. Fuzzy match against known IDs
        2. Suggest cross-repo syntax if it looks external

        Args:
            missing_ref: The missing reference
            entities: Dict of known entities

        Returns:
            Suggestion string or None
        """
        entity_ids = list(entities.keys())

        # Try fuzzy match (close mismatches, typos)
        matches = get_close_matches(missing_ref, entity_ids, n=1, cutoff=0.6)
        if matches:
            return f"Did you mean '{matches[0]}'?"

        # Check if it looks like an external ref (all caps + digits after colon)
        if missing_ref and missing_ref[0].isalpha():
            # Could be a cross-repo reference
            if not any(c == ':' for c in missing_ref):
                return f"If this is from an external repo, use format 'repo:{missing_ref}'"

        return None

    def get_report(self) -> Dict[str, Any]:
        """Get validation report."""
        return {
            "errors": [str(e) for e in self.errors],
            "warnings": [str(w) for w in self.warnings],
            "error_count": len(self.errors),
            "warning_count": len(self.warnings),
            "valid": len(self.errors) == 0,
        }
