"""Schemas for structured thinking templates."""

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class TemplateMode(str, Enum):
    """Supported template modes."""

    LEARNING = "learning"
    ARTICULATING = "articulating"
    PLANNING = "planning"
    IDEATING = "ideating"
    REFLECTING = "reflecting"


class SectionInputType(str, Enum):
    """Input types supported by template sections."""

    CONCEPT_SEARCH = "concept_search"
    FREEFORM = "freeform"
    SELECTION = "selection"


class TemplateSection(BaseModel):
    """A single section within a thinking template."""

    id: str
    prompt: str
    input_type: SectionInputType | None = None
    ai_behavior: str | None = None
    required: bool = False


class GraphMappingAction(BaseModel):
    """Action executed when a template completes."""

    action: str
    entity_type: str | None = None
    source_section: str | None = None
    link_to: str | None = None
    relationship: str | None = None
    metadata: dict[str, Any] | None = None
    add_exchange: bool = False


class GraphMapping(BaseModel):
    """Graph mapping configuration for a template."""

    on_complete: list[GraphMappingAction] = Field(default_factory=list)


class ThinkingTemplate(BaseModel):
    """Thinking template definition loaded from JSON."""

    id: str
    mode: TemplateMode
    name: str
    description: str | None = None
    sections: list[TemplateSection]
    graph_mapping: GraphMapping | None = None

