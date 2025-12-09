"""Concept schemas for knowledge graph formalization."""

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class ConceptType(str, Enum):
    """Type of concept in the knowledge graph."""

    CONCEPT = "concept"
    THEORY = "theory"
    FRAMEWORK = "framework"
    MECHANISM = "mechanism"
    PATTERN = "pattern"
    DISTINCTION = "distinction"


class RelationshipType(str, Enum):
    """Type of relationship between concepts."""

    SUPPORTS = "supports"
    CONTRADICTS = "contradicts"
    COMPONENT_OF = "component_of"
    OPERATIONALIZES = "operationalizes"
    DEVELOPS = "develops"
    ENABLES = "enables"
    CONTRASTS_WITH = "contrasts_with"


class ConceptRelationship(BaseModel):
    """A relationship to another concept."""

    target_name: str = Field(description="Name of the target concept")
    relationship_type: RelationshipType
    evidence: Optional[str] = Field(default=None, description="Supporting evidence or explanation")


class CreateConceptRequest(BaseModel):
    """Request to create a new concept."""

    name: str = Field(description="Concept name", min_length=1, max_length=200)
    concept_type: ConceptType = Field(default=ConceptType.CONCEPT)
    description: str = Field(description="Concept definition/description", min_length=10)
    aliases: list[str] = Field(default_factory=list, description="Alternative names")
    relationships: list[ConceptRelationship] = Field(default_factory=list)
    source_session_id: Optional[str] = Field(default=None, description="Session where concept emerged")
    source_quotes: list[str] = Field(default_factory=list, description="Supporting quotes from session")
    user_id: str = Field(description="User creating the concept")


class ConceptResponse(BaseModel):
    """Response from concept creation."""

    concept_id: str = Field(description="Graph node ID")
    name: str
    concept_type: ConceptType
    description: str
    relationships_created: int = 0
    message: str = "Concept created successfully"


class ConceptListResponse(BaseModel):
    """Response with list of concepts."""

    concepts: list[dict] = Field(default_factory=list)
    total: int = 0
