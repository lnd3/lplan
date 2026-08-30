"""Data models for Plan Framework entities: Project, Design, Action."""

from datetime import date
from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, field_validator


class Status(str, Enum):
    """Entity status. HELD/QUESTIONING/ABANDONED are thesis-specific."""
    IDEA = "IDEA"
    PLANNING = "PLANNING"
    IN_PROGRESS = "IN_PROGRESS"
    BLOCKED = "BLOCKED"
    DONE = "DONE"
    DEFERRED = "DEFERRED"
    CANCELLED = "CANCELLED"
    HELD = "HELD"             # Thesis: currently believed and acted on
    QUESTIONING = "QUESTIONING"  # Thesis: evidence is mixed, re-evaluating
    ABANDONED = "ABANDONED"   # Thesis: evidence contradicts; no longer held
    STABLE = "STABLE"         # Concept: well-understood, not expected to change
    DRAFT = "DRAFT"           # Concept: provisional definition, may be refined
    DEPRECATED = "DEPRECATED" # Concept: superseded by a better concept


class Priority(str, Enum):
    """Project priority level."""
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class ExternalDependency(BaseModel):
    """External dependency (not formalized as a project)."""
    repo: str
    feature: str
    status: str
    blocking: bool = False


class Estimate(BaseModel):
    """Optional time estimate for a project."""
    effort_days: Optional[float] = None
    confidence: Optional[str] = None  # low, medium, high
    started: Optional[date] = None
    completed: Optional[date] = None


class PlanEntity(BaseModel):
    """Base model for all plan entities."""
    id: str
    title: str
    status: Status
    created: date
    updated: date
    description: Optional[str] = None

    @field_validator("id")
    @classmethod
    def validate_id(cls, v: str) -> str:
        """Validate ID format: starts with letter, followed by digits."""
        if not v or not v[0].isalpha() or not v[1:].isdigit():
            raise ValueError(f"Invalid ID format: {v}. Expected format like P001, D001, A001")
        return v

    @field_validator("updated")
    @classmethod
    def validate_dates(cls, updated: date, info: Any) -> date:
        """Validate that updated >= created."""
        if "created" in info.data and updated < info.data["created"]:
            raise ValueError("updated date must be >= created date")
        return updated


class ConceptType(str, Enum):
    """Discriminator for Concept entries."""
    MODE = "mode"           # An operating configuration with defined properties
    TERM = "term"           # A technical term with a precise definition
    PATTERN = "pattern"     # A recurring design or behavioral pattern
    CONSTRAINT = "constraint"  # A hard rule that limits design space
    RULE = "rule"           # A validated behavioral rule or heuristic
    FINDING = "finding"     # A validated empirical result worth preserving


class Concept(PlanEntity):
    """Concept entity — stable named abstraction: mode, term, pattern, constraint, rule, finding."""
    concept_type: ConceptType
    related: List[str] = Field(default_factory=list)  # Plan IDs, schema files, result files

    @field_validator("status")
    @classmethod
    def validate_concept_status(cls, v: Status) -> Status:
        return v


class Thesis(PlanEntity):
    """Thesis entity - unconstrained belief about the world, above master plans."""
    conviction: Optional[int] = None  # 0–10: how strongly this is held right now

    @field_validator("status")
    @classmethod
    def validate_thesis_status(cls, v: Status) -> Status:
        """Theses use HELD, QUESTIONING, or ABANDONED."""
        return v

    @field_validator("conviction")
    @classmethod
    def validate_conviction(cls, v: Optional[int]) -> Optional[int]:
        if v is not None and not (0 <= v <= 10):
            raise ValueError("conviction must be between 0 and 10")
        return v


class MasterPlan(PlanEntity):
    """Master Plan entity - constrained possibility seeded by a thesis."""
    stakeholder: str
    priority: Optional[Priority] = None
    vision: Optional[str] = None
    goals: List[str] = Field(default_factory=list)
    scope: Optional[str] = None
    parent_thesis: List[str] = Field(default_factory=list)  # Theses this master plan acts on

    @field_validator("status")
    @classmethod
    def validate_master_plan_status(cls, v: Status) -> Status:
        """Master plans can have all statuses."""
        return v


class Project(PlanEntity):
    """Project entity - high-level goal."""
    priority: Priority
    priority_drivers: List[str]
    depends: List[str] = Field(default_factory=list)
    external_dependencies: List[ExternalDependency] = Field(default_factory=list)
    enables: List[str] = Field(default_factory=list)
    project: Optional[str] = None  # Parent project if nested
    estimate: Optional[Estimate] = None
    parent_master_plan: List[str] = Field(default_factory=list)  # Master plans this project serves
    stakeholder: Optional[str] = None  # Stakeholder driving this project

    @field_validator("status")
    @classmethod
    def validate_project_status(cls, v: Status) -> Status:
        """Projects can have all statuses."""
        return v

    @field_validator("priority_drivers")
    @classmethod
    def validate_priority_drivers(cls, v: List[str]) -> List[str]:
        """Priority drivers must be non-empty list."""
        if not v:
            raise ValueError("priority_drivers must not be empty")
        return v


class Design(PlanEntity):
    """Design entity - detailed specification."""
    project: str  # Parent project ID
    external_dependencies: List[ExternalDependency] = Field(default_factory=list)
    phase: Optional[str] = None  # D008: which project phase this Design anchors

    @field_validator("status")
    @classmethod
    def validate_design_status(cls, v: Status) -> Status:
        """Designs cannot be BLOCKED."""
        if v == Status.BLOCKED:
            raise ValueError("Designs cannot have BLOCKED status")
        return v


class Action(PlanEntity):
    """Action entity - concrete task."""
    design: Optional[str] = None  # Parent design
    project: Optional[str] = None  # Associated project
    priority: Optional[Priority] = None  # Actions may have priority if independent
    phase: Optional[str] = None  # D008: which project phase this Action belongs to (optional)


class PlanFile(BaseModel):
    """Parsed plan file with frontmatter and content."""
    entity: PlanEntity
    goal: Optional[str] = None
    scope: Optional[str] = None
    linked: Optional[str] = None
    tasks: Optional[List[str]] = None
    log: Optional[List[str]] = None
    raw_content: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "entity": self.entity.model_dump(),
            "goal": self.goal,
            "scope": self.scope,
            "linked": self.linked,
            "tasks": self.tasks,
            "log": self.log,
        }
