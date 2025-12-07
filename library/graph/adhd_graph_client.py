"""
ADHD-Friendly Knowledge Graph Client

DEPRECATED: This module is maintained for backwards compatibility only.
Use UnifiedGraphClient from library.graph.unified_client instead.

The ADHDKnowledgeGraph class in this module is now an alias to UnifiedGraphClient,
which combines domain knowledge, personal knowledge, and query operations
into a single client with one connection pool.

Extends the base Neo4j operations with ADHD-specific schema and operations:
- Spark capture with resonance signals
- Favorite problem tracking
- Thread/journey management
- Energy-appropriate navigation
- Exploration visit tracking

Designed to work WITH the ADHD brain, not against it.

Schema Versioning:
- All nodes get a `schema_version` property on creation
- Use `get_schema_info()` to check current version and node counts
- Use `migrate_schema()` when upgrading (migrations defined in MIGRATIONS dict)
"""

import warnings
from datetime import datetime
from typing import Optional
from uuid import uuid4

from .unified_client import UnifiedGraphClient, SCHEMA_VERSION
from .adhd_ontology import (
    ADHDEntity,
    ADHDRelationship,
    EntityStatus,
    EntityType,
    EnergyLevel,
    FavoriteProblem,
    RelationshipType,
    ResonanceSignal,
    Thread,
)

# Migration functions: version -> callable that takes session
# Add migrations here as schema evolves
MIGRATIONS: dict[str, callable] = {
    # "0.1.0 -> 0.2.0": lambda session: session.run("..."),
}


# Backwards compatibility alias
# ADHDKnowledgeGraph is now just UnifiedGraphClient
class ADHDKnowledgeGraph(UnifiedGraphClient):
    """
    DEPRECATED: Use UnifiedGraphClient instead.

    This class is maintained for backwards compatibility.
    It inherits all functionality from UnifiedGraphClient.

    Note: UnifiedGraphClient combines both domain knowledge (from KnowledgeGraph)
    and personal knowledge (from ADHDKnowledgeGraph) operations.
    """

    def __init__(
        self,
        uri: str = "bolt://localhost:7687",
        user: str = "neo4j",
        password: str = "brainexplore"
    ):
        warnings.warn(
            "ADHDKnowledgeGraph is deprecated. Use UnifiedGraphClient instead. "
            "Note: UnifiedGraphClient uses a singleton driver, so uri/user/password "
            "parameters are only effective on first instantiation.",
            DeprecationWarning,
            stacklevel=2
        )
        # UnifiedGraphClient doesn't take parameters in __init__
        # It uses singleton driver from config
        super().__init__()

    def _ensure_adhd_schema(self):
        """
        DEPRECATED: Schema creation is now handled by UnifiedGraphClient._ensure_schema()

        This method is kept for backwards compatibility but does nothing.
        """
        warnings.warn(
            "_ensure_adhd_schema is deprecated. Schema management is now handled "
            "by UnifiedGraphClient._ensure_schema() automatically.",
            DeprecationWarning,
            stacklevel=2
        )
        pass

    def get_schema_info(self) -> dict:
        """
        Get schema version info and node counts by version.

        Use this to understand what data exists and what migrations may be needed.
        """
        with self.driver.session() as session:
            # Current code version
            current_version = SCHEMA_VERSION

            # Count nodes by schema version
            version_result = session.run("""
                MATCH (n)
                WHERE n.schema_version IS NOT NULL
                RETURN n.schema_version as version, labels(n)[0] as label, count(*) as count
                ORDER BY version, label
            """)
            by_version = {}
            for r in version_result:
                v = r["version"]
                if v not in by_version:
                    by_version[v] = {}
                by_version[v][r["label"]] = r["count"]

            # Count nodes without schema version (legacy or from other systems)
            legacy_result = session.run("""
                MATCH (n)
                WHERE n.schema_version IS NULL
                RETURN labels(n)[0] as label, count(*) as count
            """)
            legacy = {r["label"]: r["count"] for r in legacy_result}

            return {
                "current_code_version": current_version,
                "nodes_by_version": by_version,
                "nodes_without_version": legacy,
                "available_migrations": list(MIGRATIONS.keys()),
            }

    def migrate_schema(self, from_version: str, to_version: str) -> dict:
        """
        Run a schema migration.

        Returns migration result with counts of affected nodes.
        """
        migration_key = f"{from_version} -> {to_version}"

        if migration_key not in MIGRATIONS:
            return {
                "success": False,
                "error": f"No migration defined for {migration_key}",
                "available": list(MIGRATIONS.keys()),
            }

        with self.driver.session() as session:
            # Run the migration
            migration_fn = MIGRATIONS[migration_key]
            try:
                result = migration_fn(session)

                # Update schema versions on migrated nodes
                session.run("""
                    MATCH (n {schema_version: $from_version})
                    SET n.schema_version = $to_version
                """, from_version=from_version, to_version=to_version)

                return {
                    "success": True,
                    "migration": migration_key,
                    "result": str(result) if result else "completed",
                }
            except Exception as e:
                return {
                    "success": False,
                    "migration": migration_key,
                    "error": str(e),
                }

    def backfill_schema_version(self, node_labels: Optional[list[str]] = None) -> dict:
        """
        Add schema_version to existing nodes that don't have it.

        Useful for migrating legacy data into the versioned system.
        """
        labels = node_labels or ["Spark", "Insight", "Thread", "FavoriteProblem"]

        with self.driver.session() as session:
            counts = {}
            for label in labels:
                result = session.run(f"""
                    MATCH (n:{label})
                    WHERE n.schema_version IS NULL
                    SET n.schema_version = $version
                    RETURN count(n) as updated
                """, version=SCHEMA_VERSION)
                counts[label] = result.single()["updated"]

            return {
                "backfilled_to_version": SCHEMA_VERSION,
                "updated_counts": counts,
            }


# Module-level __getattr__ for dynamic deprecation warnings
def __getattr__(name):
    if name == "ADHDKnowledgeGraph":
        warnings.warn(
            "Importing ADHDKnowledgeGraph from adhd_graph_client is deprecated. "
            "Use 'from library.graph.unified_client import UnifiedGraphClient' instead.",
            DeprecationWarning,
            stacklevel=2
        )
        return ADHDKnowledgeGraph
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")
