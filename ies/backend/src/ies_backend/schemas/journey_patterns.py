"""Schemas for journey pattern analysis.

Defines data structures for pattern detection, entity clustering,
and personalized recommendations based on exploration history.
"""

from datetime import datetime
from pydantic import BaseModel, Field


class EntityCluster(BaseModel):
    """A cluster of entities that are frequently explored together."""

    cluster_id: str
    entity_ids: list[str]
    entity_names: list[str]
    cohesion_score: float = Field(
        ge=0.0, le=1.0, description="How tightly grouped the entities are (0-1)"
    )
    visit_count: int = Field(description="Total visits to entities in this cluster")
    description: str | None = None


class FrequentEntity(BaseModel):
    """An entity that is frequently visited."""

    entity_id: str
    entity_name: str
    entity_type: str | None = None
    visit_count: int
    total_dwell_seconds: float = 0.0
    avg_dwell_seconds: float = 0.0
    last_visited: datetime | None = None


class ExplorationPath(BaseModel):
    """A common sequence of entity visits."""

    path_id: str
    sequence: list[str] = Field(description="Entity IDs in order")
    sequence_names: list[str] = Field(description="Entity names in order")
    frequency: int = Field(description="How often this path occurs")
    avg_duration_seconds: float = 0.0


class EntityRecommendation(BaseModel):
    """A recommended entity to explore based on journey patterns."""

    entity_id: str
    entity_name: str
    entity_type: str | None = None
    reason: str
    confidence: float = Field(ge=0.0, le=1.0)
    source_pattern: str = Field(
        description="Pattern type that generated this recommendation"
    )


class JourneyInsight(BaseModel):
    """A natural language insight derived from journey patterns."""

    insight_type: str = Field(
        description="Type: exploration_habit, knowledge_gap, emerging_interest"
    )
    message: str
    supporting_data: dict | None = None


class JourneyPatternAnalysis(BaseModel):
    """Complete journey pattern analysis response."""

    # Analysis metadata
    user_id: str
    context_id: str | None = None
    analysis_period_start: datetime
    analysis_period_end: datetime
    total_entries_analyzed: int

    # Pattern results
    discovered_clusters: list[EntityCluster] = Field(default_factory=list)
    frequent_entities: list[FrequentEntity] = Field(default_factory=list)
    common_paths: list[ExplorationPath] = Field(default_factory=list)

    # Recommendations
    recommendations: list[EntityRecommendation] = Field(default_factory=list)
    insights: list[JourneyInsight] = Field(default_factory=list)

    # Summary stats
    unique_entities_visited: int = 0
    total_sessions: int = 0
    avg_session_duration_minutes: float = 0.0
    exploration_breadth_score: float = Field(
        default=0.0, ge=0.0, le=1.0, description="How diverse the exploration is (0-1)"
    )
    exploration_depth_score: float = Field(
        default=0.0, ge=0.0, le=1.0, description="How deep the exploration goes (0-1)"
    )


class JourneyPatternRequest(BaseModel):
    """Request for journey pattern analysis."""

    user_id: str
    context_id: str | None = None
    days_back: int = Field(default=30, ge=1, le=365)
    min_visits_for_frequent: int = Field(default=3, ge=1)
    min_path_frequency: int = Field(default=2, ge=1)
    max_recommendations: int = Field(default=10, ge=1, le=50)
