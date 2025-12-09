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

# Pass 2: Relationship extraction
from library.graph.relationship_extractor import (
    RelationshipExtractor,
    ExtractedRelationship,
    RelationshipExtractionResult,
    deduplicate_relationships,
    validate_relationship,
)

# ADHD-friendly ontology (for personal knowledge - Layers 3/4)
from library.graph.adhd_ontology import (
    ADHDEntity,
    ADHDRelationship,
    EnergyLevel,
    EntityStatus,
    EntityType,
    FavoriteProblem,
    Reframe,
    ReframeType,
    RelationshipType,
    ResonanceSignal,
    Thread,
)

# ADHD-friendly Neo4j client (for personal knowledge graph)
from library.graph.adhd_graph_client import ADHDKnowledgeGraph, SCHEMA_VERSION

# Reframe Layer (Pass 2 cross-domain mapping)
from library.graph.reframe_mapper import ReframeMapper, ResonanceMatch

# Reframe Layer (Pass 3 generative reframe creation)
from library.graph.reframe_generator import ReframeGenerator, GeneratedReframe

__all__ = [
    # Original (book ingestion)
    "Entity",
    "Relationship",
    "ExtractionResult",
    "EntityExtractor",
    "deduplicate_entities",
    "KnowledgeGraph",
    # Pass 2: Relationship extraction
    "RelationshipExtractor",
    "ExtractedRelationship",
    "RelationshipExtractionResult",
    "deduplicate_relationships",
    "validate_relationship",
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
    "ReframeType",
    "Reframe",
    "ADHDKnowledgeGraph",
    "SCHEMA_VERSION",
    # Reframe Layer
    "ReframeMapper",
    "ResonanceMatch",
    "ReframeGenerator",
    "GeneratedReframe",
]
