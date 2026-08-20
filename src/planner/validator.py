"""Schema validator for plan entities."""

from typing import List, Dict, Any, Set, Optional
from difflib import get_close_matches
from .models import Project, Design, Action, PlanEntity, Status, Priority


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

        return len(self.errors) == 0

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
