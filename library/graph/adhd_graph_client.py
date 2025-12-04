"""
ADHD-Friendly Knowledge Graph Client

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

from datetime import datetime
from typing import Optional
from uuid import uuid4

from neo4j import GraphDatabase

# Schema version - increment when making breaking changes
SCHEMA_VERSION = "0.1.0"

# Migration functions: version -> callable that takes session
# Add migrations here as schema evolves
MIGRATIONS: dict[str, callable] = {
    # "0.1.0 -> 0.2.0": lambda session: session.run("..."),
}

from library.graph.adhd_ontology import (
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


class ADHDKnowledgeGraph:
    """
    Neo4j knowledge graph operations for ADHD-friendly personal knowledge.

    This client handles personal knowledge artifacts (sparks, insights, threads)
    separately from domain knowledge (concepts, theories from books).
    """

    def __init__(
        self,
        uri: str = "bolt://localhost:7687",
        user: str = "neo4j",
        password: str = "brainexplore"
    ):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        self._ensure_adhd_schema()

    def close(self):
        self.driver.close()

    def _ensure_adhd_schema(self):
        """Create ADHD-friendly indexes and constraints."""
        with self.driver.session() as session:
            # =================================================================
            # Node Constraints (unique IDs)
            # =================================================================
            constraints = [
                # Personal artifacts
                "CREATE CONSTRAINT spark_id IF NOT EXISTS FOR (s:Spark) REQUIRE s.id IS UNIQUE",
                "CREATE CONSTRAINT insight_id IF NOT EXISTS FOR (i:Insight) REQUIRE i.id IS UNIQUE",
                "CREATE CONSTRAINT thread_id IF NOT EXISTS FOR (t:Thread) REQUIRE t.id IS UNIQUE",
                "CREATE CONSTRAINT favorite_problem_id IF NOT EXISTS FOR (fp:FavoriteProblem) REQUIRE fp.id IS UNIQUE",

                # Domain knowledge (extending existing)
                "CREATE CONSTRAINT concept_id IF NOT EXISTS FOR (c:Concept) REQUIRE c.id IS UNIQUE",
                "CREATE CONSTRAINT framework_id IF NOT EXISTS FOR (f:Framework) REQUIRE f.id IS UNIQUE",
                "CREATE CONSTRAINT theory_id IF NOT EXISTS FOR (t:Theory) REQUIRE t.id IS UNIQUE",
                "CREATE CONSTRAINT mechanism_id IF NOT EXISTS FOR (m:Mechanism) REQUIRE m.id IS UNIQUE",
                "CREATE CONSTRAINT phenomenon_id IF NOT EXISTS FOR (p:Phenomenon) REQUIRE p.id IS UNIQUE",
                "CREATE CONSTRAINT pattern_id IF NOT EXISTS FOR (p:Pattern) REQUIRE p.id IS UNIQUE",
                "CREATE CONSTRAINT distinction_id IF NOT EXISTS FOR (d:Distinction) REQUIRE d.id IS UNIQUE",
                "CREATE CONSTRAINT person_id IF NOT EXISTS FOR (p:Person) REQUIRE p.id IS UNIQUE",
            ]
            for constraint in constraints:
                try:
                    session.run(constraint)
                except Exception:
                    pass  # Constraint may already exist

            # =================================================================
            # Indexes for Navigation
            # =================================================================
            indexes = [
                # Status-based queries (find all captured sparks, etc.)
                "CREATE INDEX spark_status IF NOT EXISTS FOR (s:Spark) ON (s.status)",
                "CREATE INDEX insight_status IF NOT EXISTS FOR (i:Insight) ON (i.status)",
                "CREATE INDEX thread_status IF NOT EXISTS FOR (t:Thread) ON (t.status)",

                # Resonance-based navigation (find all things that made me curious)
                "CREATE INDEX spark_resonance IF NOT EXISTS FOR (s:Spark) ON (s.resonance_signal)",
                "CREATE INDEX insight_resonance IF NOT EXISTS FOR (i:Insight) ON (i.resonance_signal)",

                # Energy-appropriate navigation
                "CREATE INDEX spark_energy IF NOT EXISTS FOR (s:Spark) ON (s.energy_level)",
                "CREATE INDEX insight_energy IF NOT EXISTS FOR (i:Insight) ON (i.energy_level)",
                "CREATE INDEX concept_energy IF NOT EXISTS FOR (c:Concept) ON (c.energy_level)",

                # Title search
                "CREATE INDEX spark_title IF NOT EXISTS FOR (s:Spark) ON (s.title)",
                "CREATE INDEX insight_title IF NOT EXISTS FOR (i:Insight) ON (i.title)",
                "CREATE INDEX concept_title IF NOT EXISTS FOR (c:Concept) ON (c.title)",

                # Favorite problem queries
                "CREATE INDEX favorite_problem_active IF NOT EXISTS FOR (fp:FavoriteProblem) ON (fp.active)",

                # Recency queries
                "CREATE INDEX spark_created IF NOT EXISTS FOR (s:Spark) ON (s.created_at)",
                "CREATE INDEX spark_visited IF NOT EXISTS FOR (s:Spark) ON (s.last_visited)",
            ]
            for index in indexes:
                try:
                    session.run(index)
                except Exception:
                    pass

    # =========================================================================
    # Spark Operations (Raw Capture)
    # =========================================================================

    def capture_spark(
        self,
        title: str,
        content: str,
        resonance_signal: Optional[ResonanceSignal] = None,
        capture_context: Optional[str] = None,
        energy_level: EnergyLevel = EnergyLevel.MEDIUM,
        source_id: Optional[str] = None,
        source_location: Optional[str] = None,
        tags: Optional[list[str]] = None,
    ) -> str:
        """
        Capture a spark - a moment of resonance.

        Returns the spark ID for future reference.
        """
        spark_id = f"spark_{uuid4().hex[:12]}"
        now = datetime.now().isoformat()

        with self.driver.session() as session:
            session.run("""
                CREATE (s:Spark {
                    id: $id,
                    title: $title,
                    content: $content,
                    resonance_signal: $resonance,
                    capture_context: $context,
                    energy_level: $energy,
                    status: $status,
                    source_id: $source_id,
                    source_location: $source_location,
                    tags: $tags,
                    exploration_visits: 0,
                    created_at: $created_at,
                    schema_version: $schema_version
                })
            """,
                id=spark_id,
                title=title,
                content=content,
                resonance=resonance_signal.value if resonance_signal else None,
                context=capture_context,
                energy=energy_level.value,
                status=EntityStatus.CAPTURED.value,
                source_id=source_id,
                source_location=source_location,
                tags=tags or [],
                created_at=now,
                schema_version=SCHEMA_VERSION
            )

        return spark_id

    def get_spark(self, spark_id: str) -> Optional[dict]:
        """Get a spark by ID."""
        with self.driver.session() as session:
            result = session.run("""
                MATCH (s:Spark {id: $id})
                RETURN s
            """, id=spark_id)
            record = result.single()
            return dict(record["s"]) if record else None

    def visit_spark(self, spark_id: str) -> None:
        """Record an exploration visit to a spark."""
        now = datetime.now().isoformat()
        with self.driver.session() as session:
            session.run("""
                MATCH (s:Spark {id: $id})
                SET s.exploration_visits = s.exploration_visits + 1,
                    s.last_visited = $now
            """, id=spark_id, now=now)

    def promote_spark_to_insight(
        self,
        spark_id: str,
        insight_title: str,
        insight_content: str,
    ) -> str:
        """
        Promote a spark to an insight (it now has personal meaning).

        Creates the insight node and links it to the original spark.
        """
        insight_id = f"insight_{uuid4().hex[:12]}"
        now = datetime.now().isoformat()

        with self.driver.session() as session:
            # Create insight and link to spark
            session.run("""
                MATCH (s:Spark {id: $spark_id})
                CREATE (i:Insight {
                    id: $insight_id,
                    title: $title,
                    content: $content,
                    resonance_signal: s.resonance_signal,
                    capture_context: s.capture_context,
                    energy_level: s.energy_level,
                    status: $status,
                    tags: s.tags,
                    exploration_visits: 0,
                    created_at: $created_at,
                    schema_version: $schema_version
                })
                CREATE (i)-[:SPARKED_BY]->(s)
                SET s.status = $explored
            """,
                spark_id=spark_id,
                insight_id=insight_id,
                title=insight_title,
                content=insight_content,
                status=EntityStatus.EXPLORING.value,
                explored=EntityStatus.EXPLORING.value,
                created_at=now,
                schema_version=SCHEMA_VERSION
            )

        return insight_id

    # =========================================================================
    # Favorite Problem Operations
    # =========================================================================

    def create_favorite_problem(
        self,
        question: str,
        why_matters: str,
    ) -> str:
        """
        Create a favorite problem (Feynman's 12 problems).

        These serve as navigation anchors - persistent questions you carry.
        """
        fp_id = f"fp_{uuid4().hex[:12]}"
        now = datetime.now().isoformat()

        with self.driver.session() as session:
            session.run("""
                CREATE (fp:FavoriteProblem {
                    id: $id,
                    question: $question,
                    why_matters: $why_matters,
                    active: true,
                    created_at: $created_at,
                    schema_version: $schema_version
                })
            """,
                id=fp_id,
                question=question,
                why_matters=why_matters,
                created_at=now,
                schema_version=SCHEMA_VERSION
            )

        return fp_id

    def link_to_favorite_problem(
        self,
        entity_id: str,
        problem_id: str,
    ) -> None:
        """Link any entity to a favorite problem it addresses."""
        now = datetime.now().isoformat()
        with self.driver.session() as session:
            # Find the entity regardless of label
            session.run("""
                MATCH (e {id: $entity_id})
                MATCH (fp:FavoriteProblem {id: $problem_id})
                MERGE (e)-[:ADDRESSES_PROBLEM]->(fp)
                SET fp.last_discovery = $now
            """,
                entity_id=entity_id,
                problem_id=problem_id,
                now=now
            )

    def get_favorite_problems(self, active_only: bool = True) -> list[dict]:
        """Get all favorite problems."""
        with self.driver.session() as session:
            if active_only:
                result = session.run("""
                    MATCH (fp:FavoriteProblem {active: true})
                    OPTIONAL MATCH (e)-[:ADDRESSES_PROBLEM]->(fp)
                    RETURN fp, count(e) as discovery_count
                    ORDER BY fp.created_at DESC
                """)
            else:
                result = session.run("""
                    MATCH (fp:FavoriteProblem)
                    OPTIONAL MATCH (e)-[:ADDRESSES_PROBLEM]->(fp)
                    RETURN fp, count(e) as discovery_count
                    ORDER BY fp.created_at DESC
                """)
            return [
                {**dict(r["fp"]), "discovery_count": r["discovery_count"]}
                for r in result
            ]

    def get_discoveries_for_problem(self, problem_id: str) -> list[dict]:
        """Get all entities that address a favorite problem."""
        with self.driver.session() as session:
            result = session.run("""
                MATCH (e)-[:ADDRESSES_PROBLEM]->(fp:FavoriteProblem {id: $id})
                RETURN e, labels(e) as labels
                ORDER BY e.created_at DESC
            """, id=problem_id)
            return [
                {**dict(r["e"]), "type": r["labels"][0]}
                for r in result
            ]

    # =========================================================================
    # Thread Operations (Exploration Journeys)
    # =========================================================================

    def start_thread(
        self,
        title: str,
        starting_context: Optional[str] = None,
        current_question: Optional[str] = None,
    ) -> str:
        """Start a new exploration thread."""
        thread_id = f"thread_{uuid4().hex[:12]}"
        now = datetime.now().isoformat()

        with self.driver.session() as session:
            session.run("""
                CREATE (t:Thread {
                    id: $id,
                    title: $title,
                    starting_context: $context,
                    current_question: $question,
                    status: $status,
                    created_at: $created_at,
                    last_extended: $created_at,
                    schema_version: $schema_version
                })
            """,
                id=thread_id,
                title=title,
                context=starting_context,
                question=current_question,
                status=EntityStatus.EXPLORING.value,
                created_at=now,
                schema_version=SCHEMA_VERSION
            )

        return thread_id

    def add_breadcrumb_to_thread(
        self,
        thread_id: str,
        entity_id: str,
    ) -> None:
        """Add an entity to a thread's exploration path."""
        now = datetime.now().isoformat()
        with self.driver.session() as session:
            # Get current breadcrumb count for ordering
            result = session.run("""
                MATCH (t:Thread {id: $thread_id})
                OPTIONAL MATCH (t)-[b:HAS_BREADCRUMB]->()
                RETURN count(b) as count
            """, thread_id=thread_id)
            count = result.single()["count"]

            # Add breadcrumb relationship
            session.run("""
                MATCH (t:Thread {id: $thread_id})
                MATCH (e {id: $entity_id})
                CREATE (t)-[:HAS_BREADCRUMB {order: $order, added_at: $now}]->(e)
                SET t.last_extended = $now
            """,
                thread_id=thread_id,
                entity_id=entity_id,
                order=count,
                now=now
            )

    def get_thread_journey(self, thread_id: str) -> list[dict]:
        """Get the ordered breadcrumb journey of a thread."""
        with self.driver.session() as session:
            result = session.run("""
                MATCH (t:Thread {id: $thread_id})-[b:HAS_BREADCRUMB]->(e)
                RETURN e, labels(e) as labels, b.order as order
                ORDER BY b.order
            """, thread_id=thread_id)
            return [
                {**dict(r["e"]), "type": r["labels"][0], "order": r["order"]}
                for r in result
            ]

    # =========================================================================
    # Navigation Queries
    # =========================================================================

    def find_by_resonance(
        self,
        resonance: ResonanceSignal,
        limit: int = 20,
    ) -> list[dict]:
        """Find entities by resonance signal (emotional retrieval)."""
        with self.driver.session() as session:
            result = session.run("""
                MATCH (e)
                WHERE e.resonance_signal = $resonance
                RETURN e, labels(e) as labels
                ORDER BY e.created_at DESC
                LIMIT $limit
            """, resonance=resonance.value, limit=limit)
            return [
                {**dict(r["e"]), "type": r["labels"][0]}
                for r in result
            ]

    def find_by_energy_level(
        self,
        energy: EnergyLevel,
        limit: int = 20,
    ) -> list[dict]:
        """Find entities appropriate for current energy level."""
        with self.driver.session() as session:
            result = session.run("""
                MATCH (e)
                WHERE e.energy_level = $energy
                RETURN e, labels(e) as labels
                ORDER BY e.last_visited DESC NULLS LAST
                LIMIT $limit
            """, energy=energy.value, limit=limit)
            return [
                {**dict(r["e"]), "type": r["labels"][0]}
                for r in result
            ]

    def find_unvisited_sparks(self, limit: int = 10) -> list[dict]:
        """Find captured sparks that haven't been explored yet."""
        with self.driver.session() as session:
            result = session.run("""
                MATCH (s:Spark {status: 'captured'})
                WHERE s.exploration_visits = 0
                RETURN s
                ORDER BY s.created_at DESC
                LIMIT $limit
            """, limit=limit)
            return [dict(r["s"]) for r in result]

    def find_stale_explorations(self, days_since: int = 7, limit: int = 10) -> list[dict]:
        """Find things that were being explored but haven't been visited recently."""
        with self.driver.session() as session:
            result = session.run("""
                MATCH (e)
                WHERE e.status = 'exploring'
                AND (e.last_visited IS NULL OR
                     datetime(e.last_visited) < datetime() - duration({days: $days}))
                RETURN e, labels(e) as labels
                ORDER BY e.last_visited ASC NULLS FIRST
                LIMIT $limit
            """, days=days_since, limit=limit)
            return [
                {**dict(r["e"]), "type": r["labels"][0]}
                for r in result
            ]

    # =========================================================================
    # Relationship Operations
    # =========================================================================

    def create_relationship(
        self,
        source_id: str,
        target_id: str,
        relation_type: RelationshipType,
        evidence: Optional[str] = None,
        discovery_context: Optional[str] = None,
    ) -> str:
        """Create a relationship between any two entities."""
        rel_id = f"rel_{uuid4().hex[:12]}"
        now = datetime.now().isoformat()

        # Convert relation type to Neo4j format
        rel_type = relation_type.value.upper()

        with self.driver.session() as session:
            session.run(f"""
                MATCH (source {{id: $source_id}})
                MATCH (target {{id: $target_id}})
                CREATE (source)-[r:{rel_type} {{
                    id: $rel_id,
                    evidence: $evidence,
                    discovery_context: $context,
                    created_at: $created_at
                }}]->(target)
            """,
                source_id=source_id,
                target_id=target_id,
                rel_id=rel_id,
                evidence=evidence,
                context=discovery_context,
                created_at=now
            )

        return rel_id

    def find_connected(
        self,
        entity_id: str,
        depth: int = 2,
    ) -> dict:
        """Find all entities connected to a given entity."""
        with self.driver.session() as session:
            result = session.run("""
                MATCH (start {id: $id})
                CALL apoc.path.subgraphAll(start, {maxLevel: $depth})
                YIELD nodes, relationships
                RETURN nodes, relationships
            """, id=entity_id, depth=depth)

            record = result.single()
            if record:
                return {
                    "nodes": [
                        {**dict(n), "type": list(n.labels)[0]}
                        for n in record["nodes"]
                    ],
                    "relationships": [
                        {
                            "type": r.type,
                            "source": r.start_node["id"],
                            "target": r.end_node["id"],
                        }
                        for r in record["relationships"]
                    ]
                }
            return {"nodes": [], "relationships": []}

    # =========================================================================
    # Stats and Health
    # =========================================================================

    def get_adhd_stats(self) -> dict:
        """Get statistics relevant to ADHD-friendly usage."""
        with self.driver.session() as session:
            # Count by status
            status_result = session.run("""
                MATCH (e)
                WHERE e.status IS NOT NULL
                RETURN e.status as status, count(*) as count
            """)
            status_counts = {r["status"]: r["count"] for r in status_result}

            # Count by resonance
            resonance_result = session.run("""
                MATCH (e)
                WHERE e.resonance_signal IS NOT NULL
                RETURN e.resonance_signal as resonance, count(*) as count
            """)
            resonance_counts = {r["resonance"]: r["count"] for r in resonance_result}

            # Recent activity
            recent_result = session.run("""
                MATCH (e)
                WHERE e.created_at IS NOT NULL
                AND datetime(e.created_at) > datetime() - duration({days: 7})
                RETURN count(*) as recent_captures
            """)
            recent = recent_result.single()["recent_captures"]

            # Favorite problems
            fp_result = session.run("""
                MATCH (fp:FavoriteProblem {active: true})
                RETURN count(*) as active_problems
            """)
            active_problems = fp_result.single()["active_problems"]

            return {
                "by_status": status_counts,
                "by_resonance": resonance_counts,
                "captures_last_7_days": recent,
                "active_favorite_problems": active_problems,
            }

    # =========================================================================
    # Schema Management
    # =========================================================================

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
