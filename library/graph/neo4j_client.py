"""
Neo4j knowledge graph client.

DEPRECATED: This module is maintained for backwards compatibility only.
Use UnifiedGraphClient from library.graph.unified_client instead.

The KnowledgeGraph class in this module is now an alias to UnifiedGraphClient,
which combines domain knowledge, personal knowledge, and query operations
into a single client with one connection pool.

Schema:
- (:Researcher {name, description})
- (:Concept {name, description, aliases})
- (:Theory {name, description, aliases})
- (:Assessment {name, description, aliases})
- (:Book {title, author, path})
- (:Chunk {id, content})

Relationships:
- (Researcher)-[:CITES]->(Researcher)
- (Researcher)-[:DEVELOPS]->(Theory|Concept)
- (Chunk)-[:SUPPORTS]->(Concept|Theory)
- (Chunk)-[:CONTRADICTS]->(Concept|Theory)
- (Assessment)-[:OPERATIONALIZES]->(Concept)
- (Concept)-[:COMPONENT_OF]->(Theory|Concept)
- (Chunk)-[:FROM_BOOK]->(Book)
- (Chunk)-[:MENTIONS]->(Entity)
"""

import warnings
from typing import Optional

from .entities import Entity, Relationship, ExtractionResult
from .unified_client import UnifiedGraphClient


# Backwards compatibility alias
# KnowledgeGraph is now just UnifiedGraphClient
class KnowledgeGraph(UnifiedGraphClient):
    """
    DEPRECATED: Use UnifiedGraphClient instead.

    This class is maintained for backwards compatibility.
    It inherits all functionality from UnifiedGraphClient.
    """

    def __init__(
        self,
        uri: str = "bolt://localhost:7687",
        user: str = "neo4j",
        password: str = "brainexplore"
    ):
        warnings.warn(
            "KnowledgeGraph is deprecated. Use UnifiedGraphClient instead. "
            "Note: UnifiedGraphClient uses a singleton driver, so uri/user/password "
            "parameters are only effective on first instantiation.",
            DeprecationWarning,
            stacklevel=2
        )
        # UnifiedGraphClient doesn't take parameters in __init__
        # It uses singleton driver from config
        super().__init__()


# Module-level __getattr__ for dynamic deprecation warnings
def __getattr__(name):
    if name == "KnowledgeGraph":
        warnings.warn(
            "Importing KnowledgeGraph from neo4j_client is deprecated. "
            "Use 'from library.graph.unified_client import UnifiedGraphClient' instead.",
            DeprecationWarning,
            stacklevel=2
        )
        return KnowledgeGraph
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")
