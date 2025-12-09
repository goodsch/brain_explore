"""
Unified Neo4j Graph Client

Combines functionality from three previous clients:
- KnowledgeGraph (domain knowledge)
- ADHDKnowledgeGraph (personal knowledge)
- GraphService (query operations)

This unified client:
1. Maintains a single connection pool (singleton driver)
2. Preserves all 14 entity types (no collapse to generic Concept)
3. Protects against Cypher injection via type validation
4. Provides personal-domain bridge methods (SPARKED_BY relationships)

Schema Version: 0.1.0
"""

from datetime import datetime
from typing import Optional
from uuid import uuid4

from neo4j import GraphDatabase, Driver

from library.graph.entities import Entity, Relationship, ExtractionResult
from library.graph.adhd_ontology import (
    ResonanceSignal,
    EnergyLevel,
    EntityStatus,
    RelationshipType,
)

# Module-level singleton driver with lazy initialization
_driver: Driver | None = None

# All allowed entity types (prevents Cypher injection)
ALLOWED_TYPES = {
    # Domain knowledge types
    "Concept",
    "Person",
    "Theory",
    "Framework",
    "Assessment",
    # Personal knowledge types
    "Spark",
    "Insight",
    "Thread",
    "FavoriteProblem",
    # Reframe Layer types (cross-domain conceptual reframing)
    "Reframe",           # Metaphor/analogy/story linking concepts across domains
    "Pattern",           # Reusable conceptual schemas (Feedback Loop, Tipping Point)
    "DynamicPattern",    # Temporal/process structures (Oscillation, Emergence)
    "StoryInsight",      # Narrative vignettes that embody concepts
    "SchemaBreak",       # Moments where intuitive models fail
    # Other enrichment types
    "Mechanism",
    "Method",
    # Content types
    "Book",
    "Chunk",
    # Legacy (keep for backward compatibility)
    "Researcher",
}

# Schema version - increment when making breaking changes
SCHEMA_VERSION = "0.2.0"


def get_driver() -> Driver:
    """Get singleton Neo4j driver with connection pooling.

    Creates driver on first call, returns cached instance on subsequent calls.
    Uses optimal connection pool settings for production use.
    """
    global _driver
    if _driver is None:
        # Use settings from config if available
        try:
            from ies_backend.config import settings
            uri = settings.neo4j_uri
            user = settings.neo4j_user
            password = settings.neo4j_password
        except ImportError:
            # Fallback to defaults if not in backend context
            uri = "bolt://localhost:7687"
            user = "neo4j"
            password = "brainexplore"

        _driver = GraphDatabase.driver(
            uri,
            auth=(user, password),
            max_connection_lifetime=3600,  # 1 hour
            max_connection_pool_size=50,
        )
    return _driver


class UnifiedGraphClient:
    """
    Unified Neo4j knowledge graph client.

    Combines domain knowledge, personal knowledge, and query operations
    into a single client with one connection pool.

    Key features:
    - Preserves all 14 entity types (no schema collapse)
    - Single connection pool for efficiency
    - Cypher injection protection via type validation
    - Personal-domain bridge methods
    """

    def __init__(self):
        """Initialize client with singleton driver."""
        self.driver = get_driver()
        self._ensure_schema()

    def close(self):
        """Close driver (affects all instances - use with caution)."""
        global _driver
        if _driver:
            _driver.close()
            _driver = None

    # =========================================================================
    # Schema Management
    # =========================================================================

    def _ensure_schema(self):
        """Create indexes and constraints for all entity types."""
        with self.driver.session() as session:
            # =================================================================
            # Node Constraints (unique identifiers)
            # =================================================================
            constraints = [
                # Domain knowledge
                "CREATE CONSTRAINT researcher_name IF NOT EXISTS FOR (r:Researcher) REQUIRE r.name IS UNIQUE",
                "CREATE CONSTRAINT concept_name IF NOT EXISTS FOR (c:Concept) REQUIRE c.name IS UNIQUE",
                "CREATE CONSTRAINT theory_name IF NOT EXISTS FOR (t:Theory) REQUIRE t.name IS UNIQUE",
                "CREATE CONSTRAINT assessment_name IF NOT EXISTS FOR (a:Assessment) REQUIRE a.name IS UNIQUE",
                "CREATE CONSTRAINT framework_name IF NOT EXISTS FOR (f:Framework) REQUIRE f.name IS UNIQUE",
                "CREATE CONSTRAINT person_name IF NOT EXISTS FOR (p:Person) REQUIRE p.name IS UNIQUE",

                # Content
                "CREATE CONSTRAINT book_path IF NOT EXISTS FOR (b:Book) REQUIRE b.path IS UNIQUE",
                "CREATE CONSTRAINT chunk_id IF NOT EXISTS FOR (c:Chunk) REQUIRE c.id IS UNIQUE",

                # Personal knowledge (use ID not name)
                "CREATE CONSTRAINT spark_id IF NOT EXISTS FOR (s:Spark) REQUIRE s.id IS UNIQUE",
                "CREATE CONSTRAINT insight_id IF NOT EXISTS FOR (i:Insight) REQUIRE i.id IS UNIQUE",
                "CREATE CONSTRAINT thread_id IF NOT EXISTS FOR (t:Thread) REQUIRE t.id IS UNIQUE",
                "CREATE CONSTRAINT favorite_problem_id IF NOT EXISTS FOR (fp:FavoriteProblem) REQUIRE fp.id IS UNIQUE",

                # Enrichment types
                "CREATE CONSTRAINT mechanism_id IF NOT EXISTS FOR (m:Mechanism) REQUIRE m.id IS UNIQUE",
                "CREATE CONSTRAINT pattern_id IF NOT EXISTS FOR (p:Pattern) REQUIRE p.id IS UNIQUE",
                "CREATE CONSTRAINT method_id IF NOT EXISTS FOR (m:Method) REQUIRE m.id IS UNIQUE",
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
                # Status-based queries
                "CREATE INDEX spark_status IF NOT EXISTS FOR (s:Spark) ON (s.status)",
                "CREATE INDEX insight_status IF NOT EXISTS FOR (i:Insight) ON (i.status)",
                "CREATE INDEX thread_status IF NOT EXISTS FOR (t:Thread) ON (t.status)",

                # Resonance-based navigation
                "CREATE INDEX spark_resonance IF NOT EXISTS FOR (s:Spark) ON (s.resonance_signal)",
                "CREATE INDEX insight_resonance IF NOT EXISTS FOR (i:Insight) ON (i.resonance_signal)",

                # Energy-appropriate navigation
                "CREATE INDEX spark_energy IF NOT EXISTS FOR (s:Spark) ON (s.energy_level)",
                "CREATE INDEX insight_energy IF NOT EXISTS FOR (i:Insight) ON (s.energy_level)",
                "CREATE INDEX concept_energy IF NOT EXISTS FOR (c:Concept) ON (c.energy_level)",

                # Title/name search
                "CREATE INDEX spark_title IF NOT EXISTS FOR (s:Spark) ON (s.title)",
                "CREATE INDEX insight_title IF NOT EXISTS FOR (i:Insight) ON (i.title)",
                "CREATE INDEX concept_title IF NOT EXISTS FOR (c:Concept) ON (c.title)",
                "CREATE INDEX researcher_name_idx IF NOT EXISTS FOR (r:Researcher) ON (r.name)",
                "CREATE INDEX concept_name_idx IF NOT EXISTS FOR (c:Concept) ON (c.name)",
                "CREATE INDEX theory_name_idx IF NOT EXISTS FOR (t:Theory) ON (t.name)",

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
    # Entity Operations (Unified with Type Preservation)
    # =========================================================================

    def add_entity_with_type(
        self,
        name: str,
        entity_type: str,
        description: Optional[str] = None,
        aliases: Optional[list[str]] = None,
        **kwargs
    ) -> str:
        """
        Add an entity with explicit type preservation.

        Args:
            name: Entity name
            entity_type: One of ALLOWED_TYPES (validated to prevent injection)
            description: Optional description
            aliases: Optional list of alternative names
            **kwargs: Additional properties

        Returns:
            The entity type used (for confirmation)

        Raises:
            ValueError: If entity_type not in ALLOWED_TYPES
        """
        # CRITICAL: Validate entity type to prevent Cypher injection
        if entity_type not in ALLOWED_TYPES:
            raise ValueError(
                f"Invalid entity type: {entity_type}. "
                f"Must be one of: {', '.join(sorted(ALLOWED_TYPES))}"
            )

        with self.driver.session() as session:
            # Now safe to use entity_type in query (validated above)
            query = f"""
                MERGE (e:{entity_type} {{name: $name}})
                SET e.description = $description,
                    e.aliases = $aliases,
                    e.schema_version = $schema_version
            """

            # Add any additional properties
            for key, value in kwargs.items():
                if value is not None:
                    query += f", e.{key} = ${key}"

            params = {
                "name": name,
                "description": description,
                "aliases": aliases or [],
                "schema_version": SCHEMA_VERSION,
                **kwargs
            }

            session.run(query, **params)

        return entity_type

    def add_entity(self, entity: Entity) -> str:
        """Add an entity from Entity object (legacy compatibility)."""
        # Map entity type to proper Neo4j label
        type_mapping = {
            # Original types
            "researcher": "Person",
            "concept": "Concept",
            "theory": "Theory",
            "assessment": "Assessment",
            "framework": "Framework",
            "person": "Person",
            # Reframe Layer types
            "pattern": "Pattern",
            "dynamic_pattern": "DynamicPattern",
            "story_insight": "StoryInsight",
            "schema_break": "SchemaBreak",
            "reframe": "Reframe",
        }

        entity_type = type_mapping.get(entity.type.lower(), "Concept")

        # Build additional properties for Reframe entities
        extra_props = {}
        if entity.reframe_type:
            extra_props["reframe_type"] = entity.reframe_type
        if entity.source_domain:
            extra_props["source_domain"] = entity.source_domain

        return self.add_entity_with_type(
            name=entity.name,
            entity_type=entity_type,
            description=entity.description,
            aliases=entity.aliases,
            **extra_props
        )

    # =========================================================================
    # Book Operations (from KnowledgeGraph)
    # =========================================================================

    def add_book(
        self,
        title: str,
        author: Optional[str],
        path: str,
        calibre_id: Optional[int] = None,
        processing_status: str = "pending",
        pattern_type: Optional[str] = None,
        pattern_type_confidence: Optional[float] = None,
        pattern_type_rationale: Optional[str] = None,
    ):
        """Add a book node with optional calibre_id."""
        with self.driver.session() as session:
            if calibre_id is not None:
                session.run("""
                    MERGE (b:Book {calibre_id: $calibre_id})
                    SET b.title = $title, b.author = $author, b.path = $path,
                        b.processing_status = $status, b.schema_version = $schema_version,
                        b.pattern_type = $pattern_type,
                        b.pattern_type_confidence = $pattern_type_confidence,
                        b.pattern_type_rationale = $pattern_type_rationale
                """, calibre_id=calibre_id, title=title, author=author,
                    path=path, status=processing_status, schema_version=SCHEMA_VERSION,
                    pattern_type=pattern_type,
                    pattern_type_confidence=pattern_type_confidence,
                    pattern_type_rationale=pattern_type_rationale)
            else:
                session.run("""
                    MERGE (b:Book {path: $path})
                    SET b.title = $title, b.author = $author,
                        b.processing_status = $status, b.schema_version = $schema_version,
                        b.pattern_type = $pattern_type,
                        b.pattern_type_confidence = $pattern_type_confidence,
                        b.pattern_type_rationale = $pattern_type_rationale
                """, title=title, author=author, path=path,
                    status=processing_status, schema_version=SCHEMA_VERSION,
                    pattern_type=pattern_type,
                    pattern_type_confidence=pattern_type_confidence,
                    pattern_type_rationale=pattern_type_rationale)

    def book_exists(self, calibre_id: int) -> bool:
        """Check if a book with calibre_id already exists."""
        with self.driver.session() as session:
            result = session.run("""
                MATCH (b:Book {calibre_id: $calibre_id})
                RETURN count(b) > 0 as exists
            """, calibre_id=calibre_id)
            record = result.single()
            return record["exists"] if record else False

    def update_book_status(self, calibre_id: int, status: str):
        """Update the processing status of a book."""
        with self.driver.session() as session:
            session.run("""
                MATCH (b:Book {calibre_id: $calibre_id})
                SET b.processing_status = $status
            """, calibre_id=calibre_id, status=status)

    def update_book_pattern_type(
        self,
        calibre_id: int,
        pattern_type: Optional[str],
        confidence: Optional[float] = None,
        rationale: Optional[str] = None,
    ):
        """Attach pattern type classification metadata to a book."""
        with self.driver.session() as session:
            session.run("""
                MATCH (b:Book {calibre_id: $calibre_id})
                SET b.pattern_type = $pattern_type,
                    b.pattern_type_confidence = $confidence,
                    b.pattern_type_rationale = $rationale
            """,
                calibre_id=calibre_id,
                pattern_type=pattern_type,
                confidence=confidence,
                rationale=rationale
            )

    def add_chunk(self, chunk_id: str, content: str, book_path: str):
        """Add a chunk and link to its book."""
        with self.driver.session() as session:
            session.run("""
                MERGE (c:Chunk {id: $chunk_id})
                SET c.content = $content, c.schema_version = $schema_version
                WITH c
                MATCH (b:Book {path: $book_path})
                MERGE (c)-[:FROM_BOOK]->(b)
            """, chunk_id=chunk_id, content=content[:500], book_path=book_path,
                schema_version=SCHEMA_VERSION)

    def link_chunk_to_entity(self, chunk_id: str, entity_name: str):
        """Create MENTIONS relationship from chunk to entity."""
        with self.driver.session() as session:
            session.run("""
                MATCH (c:Chunk {id: $chunk_id})
                MATCH (e) WHERE e.name = $entity_name
                MERGE (c)-[:MENTIONS]->(e)
            """, chunk_id=chunk_id, entity_name=entity_name)

    def add_relationship(self, rel: Relationship):
        """Add a relationship between entities."""
        import re
        rel_type = rel.relation_type.upper()
        rel_type = rel_type.replace(" ", "_").replace("-", "_")
        rel_type = re.sub(r'[^A-Z0-9_]', '', rel_type)
        if not rel_type:
            rel_type = "RELATED_TO"

        with self.driver.session() as session:
            session.run(f"""
                MATCH (source) WHERE source.name = $source_name
                MATCH (target) WHERE target.name = $target_name
                MERGE (source)-[r:{rel_type}]->(target)
                SET r.evidence = $evidence
            """,
                source_name=rel.source,
                target_name=rel.target,
                evidence=rel.evidence
            )

    def add_typed_relationship(
        self,
        source_name: str,
        target_name: str,
        relation_type: str,
        evidence: str,
        confidence: float,
        source_book: Optional[int] = None,
        source_chunk: Optional[str] = None
    ):
        """Add a Pass 2 typed relationship with metadata.

        Args:
            source_name: Source entity name
            target_name: Target entity name
            relation_type: CAUSES | PART_OF | CONTRASTS_WITH
            evidence: Text evidence supporting the relationship
            confidence: Confidence score (0.0-1.0)
            source_book: Optional calibre_id of source book
            source_chunk: Optional chunk ID where relationship was found

        Raises:
            ValueError: If relation_type is not one of the allowed types
        """
        # Validate relationship type to prevent Cypher injection
        allowed_types = ["CAUSES", "PART_OF", "CONTRASTS_WITH"]
        if relation_type not in allowed_types:
            raise ValueError(
                f"Invalid relation_type: {relation_type}. "
                f"Must be one of: {', '.join(allowed_types)}"
            )

        now = datetime.now().isoformat()

        with self.driver.session() as session:
            # For CONTRASTS_WITH, create bidirectional relationship
            if relation_type == "CONTRASTS_WITH":
                session.run(f"""
                    MATCH (a) WHERE a.name = $source
                    MATCH (b) WHERE b.name = $target
                    MERGE (a)-[r1:CONTRASTS_WITH]->(b)
                    MERGE (a)<-[r2:CONTRASTS_WITH]-(b)
                    SET r1.evidence = $evidence,
                        r1.confidence = $confidence,
                        r1.extracted_by = 'pass2',
                        r1.extracted_at = $now,
                        r1.source_book = $book,
                        r1.source_chunk = $chunk,
                        r2.evidence = $evidence,
                        r2.confidence = $confidence,
                        r2.extracted_by = 'pass2',
                        r2.extracted_at = $now,
                        r2.source_book = $book,
                        r2.source_chunk = $chunk
                """, source=source_name, target=target_name,
                     evidence=evidence, confidence=confidence,
                     now=now, book=source_book, chunk=source_chunk)
            else:
                # Unidirectional (CAUSES, PART_OF)
                session.run(f"""
                    MATCH (a) WHERE a.name = $source
                    MATCH (b) WHERE b.name = $target
                    MERGE (a)-[r:{relation_type}]->(b)
                    SET r.evidence = $evidence,
                        r.confidence = $confidence,
                        r.extracted_by = 'pass2',
                        r.extracted_at = $now,
                        r.source_book = $book,
                        r.source_chunk = $chunk
                """, source=source_name, target=target_name,
                     evidence=evidence, confidence=confidence,
                     now=now, book=source_book, chunk=source_chunk)

    def add_extraction_result(self, result: ExtractionResult, book_path: str):
        """Add all entities and relationships from an extraction result."""
        self.add_chunk(result.chunk_id, "", book_path)

        for entity in result.entities:
            self.add_entity(entity)
            self.link_chunk_to_entity(result.chunk_id, entity.name)

        for rel in result.relationships:
            self.add_relationship(rel)

    def find_related_concepts(self, concept_name: str, depth: int = 2) -> dict:
        """Find concepts related to a given concept."""
        with self.driver.session() as session:
            result = session.run("""
                MATCH (c:Concept {name: $name})
                CALL apoc.path.subgraphAll(c, {
                    maxLevel: $depth,
                    relationshipFilter: "COMPONENT_OF|SUPPORTS|OPERATIONALIZES"
                })
                YIELD nodes, relationships
                RETURN nodes, relationships
            """, name=concept_name, depth=depth)

            record = result.single()
            if record:
                return {
                    "nodes": [dict(n) for n in record["nodes"]],
                    "relationships": [
                        {
                            "type": r.type,
                            "start": r.start_node["name"],
                            "end": r.end_node["name"]
                        }
                        for r in record["relationships"]
                    ]
                }
            return {"nodes": [], "relationships": []}

    def find_researchers_for_concept(self, concept_name: str) -> list[dict]:
        """Find researchers who have written about a concept."""
        with self.driver.session() as session:
            result = session.run("""
                MATCH (r:Researcher)-[:DEVELOPS]->(c:Concept {name: $name})
                RETURN DISTINCT r.name as researcher, r.description as description
                UNION
                MATCH (r:Researcher)-[:DEVELOPS]->()<-[:COMPONENT_OF]-(c:Concept {name: $name})
                RETURN DISTINCT r.name as researcher, r.description as description
            """, name=concept_name)
            return [dict(r) for r in result]

    def find_supporting_chunks(self, entity_name: str, limit: int = 10) -> list[dict]:
        """Find chunks that mention an entity."""
        with self.driver.session() as session:
            result = session.run("""
                MATCH (c:Chunk)-[:MENTIONS]->(e {name: $name})
                MATCH (c)-[:FROM_BOOK]->(b:Book)
                RETURN c.id as chunk_id, c.content as content,
                       b.title as book_title, b.author as book_author
                LIMIT $limit
            """, name=entity_name, limit=limit)
            return [dict(r) for r in result]

    def get_stats(self) -> dict:
        """Get graph statistics."""
        with self.driver.session() as session:
            result = session.run("""
                MATCH (n)
                RETURN labels(n)[0] as label, count(*) as count
                ORDER BY count DESC
            """)
            node_counts = {r["label"]: r["count"] for r in result}

            result = session.run("""
                MATCH ()-[r]->()
                RETURN type(r) as type, count(*) as count
                ORDER BY count DESC
            """)
            rel_counts = {r["type"]: r["count"] for r in result}

            return {
                "nodes": node_counts,
                "relationships": rel_counts
            }

    def clear_all(self):
        """Clear all data (use with caution!)."""
        with self.driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")

    # =========================================================================
    # Personal Knowledge Operations (from ADHDKnowledgeGraph)
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
        """Capture a spark - a moment of resonance."""
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
        """Promote a spark to an insight."""
        insight_id = f"insight_{uuid4().hex[:12]}"
        now = datetime.now().isoformat()

        with self.driver.session() as session:
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

    def create_favorite_problem(
        self,
        question: str,
        why_matters: str,
    ) -> str:
        """Create a favorite problem (Feynman's 12 problems)."""
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
            # Get current breadcrumb count
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

    def find_by_resonance(
        self,
        resonance: ResonanceSignal,
        limit: int = 20,
    ) -> list[dict]:
        """Find entities by resonance signal."""
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
        """Find things being explored but not visited recently."""
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
    # Query Operations (from GraphService)
    # =========================================================================

    def search_concepts(self, query: str, limit: int = 10) -> list[dict]:
        """Search for concepts by name (case-insensitive substring match)."""
        with self.driver.session() as session:
            result = session.run("""
                MATCH (n)
                WHERE n.name IS NOT NULL AND toLower(n.name) CONTAINS toLower($query)
                RETURN DISTINCT n.name as name, labels(n) as labels
                ORDER BY size(n.name)
                LIMIT $limit
            """, query=query, limit=limit)
            return [
                {
                    "name": r["name"],
                    "type": r["labels"][0] if r.get("labels") else "Unknown",
                    "labels": r.get("labels", []),
                }
                for r in result
            ]

    def get_most_connected(self, limit: int = 10) -> list[dict]:
        """Get the most connected concepts in the graph."""
        with self.driver.session() as session:
            result = session.run("""
                MATCH (n)-[r]-()
                WHERE n.name IS NOT NULL
                WITH n, count(r) as connections
                ORDER BY connections DESC
                LIMIT $limit
                RETURN n.name as name, labels(n) as labels, connections
            """, limit=limit)
            return [
                {
                    "name": r["name"],
                    "type": r["labels"][0] if r.get("labels") else "Unknown",
                    "connections": r["connections"],
                }
                for r in result
            ]

    def get_entities_by_book(
        self,
        book_hash: str,
        title: str | None = None,
        types: list[str] | None = None,
        limit: int = 500
    ) -> list[dict]:
        """Get all entities mentioned in a book."""
        # Build type filter
        type_filter = ""
        if types:
            type_labels = " OR ".join([f"e:{t}" for t in types])
            type_filter = f"AND ({type_labels})"

        title_match = "OR toLower(b.title) CONTAINS toLower($title)" if title else ""

        with self.driver.session() as session:
            result = session.run(f"""
                MATCH (b:Book)
                WHERE b.hash = $book_hash
                   OR b.path CONTAINS $book_hash
                   OR b.file_hash = $book_hash
                   {title_match}
                WITH b
                MATCH (b)-[:MENTIONS]->(e)
                WHERE e.name IS NOT NULL {type_filter}
                WITH e, count(*) as mention_count
                RETURN DISTINCT e.name as name, labels(e)[0] as type, mention_count
                ORDER BY mention_count DESC
                LIMIT $limit
            """, book_hash=book_hash, title=title or "", limit=limit)

            return [
                {
                    "name": r["name"],
                    "type": r["type"] or "Concept",
                    "mention_count": r["mention_count"],
                }
                for r in result
            ]

    def get_entities_by_calibre_id(
        self,
        calibre_id: int,
        types: list[str] | None = None,
        limit: int = 500
    ) -> list[dict]:
        """Get all entities mentioned in a book by its Calibre ID."""
        # Build type filter
        type_filter = ""
        if types:
            type_labels = " OR ".join([f"e:{t}" for t in types])
            type_filter = f"AND ({type_labels})"

        with self.driver.session() as session:
            result = session.run(f"""
                MATCH (b:Book)
                WHERE b.calibre_id = $calibre_id
                WITH b
                MATCH (b)-[:MENTIONS]->(e)
                WHERE e.name IS NOT NULL {type_filter}
                WITH e, count(*) as mention_count
                RETURN DISTINCT e.name as name, labels(e)[0] as type, mention_count
                ORDER BY mention_count DESC
                LIMIT $limit
            """, calibre_id=calibre_id, limit=limit)

            return [
                {
                    "name": r["name"],
                    "type": r["type"] or "Concept",
                    "mention_count": r["mention_count"],
                }
                for r in result
            ]

    # =========================================================================
    # Personal-Domain Bridge Methods (NEW)
    # =========================================================================

    def link_spark_to_entity(
        self,
        spark_id: str,
        entity_name: str,
        context: Optional[str] = None
    ) -> None:
        """
        Link a personal spark to a domain entity.

        Creates a SPARKED_BY relationship from the spark to the entity,
        bridging personal knowledge with domain knowledge.

        Args:
            spark_id: ID of the spark node
            entity_name: Name of the domain entity
            context: Optional context about why this spark relates to this entity
        """
        now = datetime.now().isoformat()

        with self.driver.session() as session:
            session.run("""
                MATCH (s:Spark {id: $spark_id})
                MATCH (e) WHERE e.name = $entity_name
                MERGE (s)-[r:SPARKED_BY]->(e)
                SET r.context = $context,
                    r.created_at = $created_at
            """, spark_id=spark_id, entity_name=entity_name,
                context=context, created_at=now)

    def find_sparks_for_entity(
        self,
        entity_name: str,
        limit: int = 20
    ) -> list[dict]:
        """
        Find all user sparks linked to a domain entity.

        Useful for seeing personal insights about a concept from reading/learning.

        Args:
            entity_name: Name of the domain entity
            limit: Maximum sparks to return

        Returns:
            List of spark dictionaries with id, title, content, resonance
        """
        with self.driver.session() as session:
            result = session.run("""
                MATCH (s:Spark)-[:SPARKED_BY]->(e)
                WHERE e.name = $entity_name
                RETURN s.id as spark_id, s.title as title, s.content as content,
                       s.resonance_signal as resonance, s.created_at as created_at
                ORDER BY s.created_at DESC
                LIMIT $limit
            """, entity_name=entity_name, limit=limit)

            return [dict(r) for r in result]

    def find_entities_for_spark(
        self,
        spark_id: str
    ) -> list[dict]:
        """
        Find all domain entities linked to a spark.

        Shows what concepts/frameworks/theories a spark connects to.

        Args:
            spark_id: ID of the spark

        Returns:
            List of entity dictionaries with name and type
        """
        with self.driver.session() as session:
            result = session.run("""
                MATCH (s:Spark {id: $spark_id})-[:SPARKED_BY]->(e)
                RETURN e.name as name, labels(e)[0] as type
            """, spark_id=spark_id)

            return [dict(r) for r in result]

    def enrich_entity_from_sparks(
        self,
        entity_name: str,
        user_insights: Optional[str] = None,
        **enrichment_fields
    ) -> None:
        """
        Enrich a domain entity with user insights from sparks.

        Updates the entity node with personalized annotations.

        Args:
            entity_name: Name of the entity to enrich
            user_insights: Aggregated user insights text
            **enrichment_fields: Additional fields to add (e.g., user_examples, personal_questions)
        """
        with self.driver.session() as session:
            # Build SET clause dynamically
            set_clause = "SET e.user_insights = $user_insights, e.enriched_at = $now"
            for field in enrichment_fields.keys():
                set_clause += f", e.{field} = ${field}"

            params = {
                "entity_name": entity_name,
                "user_insights": user_insights,
                "now": datetime.now().isoformat(),
                **enrichment_fields
            }

            session.run(f"""
                MATCH (e) WHERE e.name = $entity_name
                {set_clause}
            """, **params)
