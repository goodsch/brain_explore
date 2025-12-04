# Graph modules

# Original entity extraction (for book ingestion - Layer 1)
from library.graph.entities import (
    Entity,
    EntityExtractor,
    ExtractionResult,
    Relationship,
    deduplicate_entities,
)

# Original Neo4j client (for book knowledge graph)
from library.graph.neo4j_client import KnowledgeGraph

# ADHD-friendly ontology (for personal knowledge - Layers 3/4)
from library.graph.adhd_ontology import (
    ADHDEntity,
    ADHDRelationship,
    EnergyLevel,
    EntityStatus,
    EntityType,
    FavoriteProblem,
    RelationshipType,
    ResonanceSignal,
    Thread,
)

# ADHD-friendly Neo4j client (for personal knowledge graph)
from library.graph.adhd_graph_client import ADHDKnowledgeGraph, SCHEMA_VERSION

__all__ = [
    # Original (book ingestion)
    "Entity",
    "Relationship",
    "ExtractionResult",
    "EntityExtractor",
    "deduplicate_entities",
    "KnowledgeGraph",
    # ADHD-friendly (personal knowledge)
    "EntityType",
    "ResonanceSignal",
    "EnergyLevel",
    "EntityStatus",
    "ADHDEntity",
    "ADHDRelationship",
    "RelationshipType",
    "FavoriteProblem",
    "Thread",
    "ADHDKnowledgeGraph",
    "SCHEMA_VERSION",
]
