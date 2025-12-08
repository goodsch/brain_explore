"""Service for personal knowledge graph operations (ADHD-friendly ontology).

Uses the backend's Neo4jClient directly for ADHD entity operations.
"""

import uuid
from datetime import datetime

from ies_backend.services.neo4j_client import Neo4jClient

from ..schemas.personal import (
    CreateSparkRequest,
    SparkResponse,
    PromoteSparkRequest,
    InsightResponse,
    SparkListResponse,
    PersonalStatsResponse,
    ResonanceSignal,
    EnergyLevel,
    EntityStatus,
)

# Schema version for ADHD ontology nodes
SCHEMA_VERSION = "0.1.0"


def _generate_id(prefix: str) -> str:
    """Generate a unique ID with prefix."""
    return f"{prefix}_{uuid.uuid4().hex[:12]}"


def _parse_datetime(value: str | datetime | None) -> datetime:
    """Parse datetime from string or return current time."""
    if value is None:
        return datetime.now()
    if isinstance(value, datetime):
        return value
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (ValueError, AttributeError):
        return datetime.now()


def _node_to_spark_response(node: dict) -> SparkResponse:
    """Convert Neo4j node dict to SparkResponse."""
    resonance = node.get("resonance_signal")
    if resonance:
        try:
            resonance = ResonanceSignal(resonance)
        except ValueError:
            resonance = None

    energy = node.get("energy_level", "medium")
    status = node.get("status", "captured")

    return SparkResponse(
        id=node.get("id", ""),
        title=node.get("title", ""),
        content=node.get("content", ""),
        resonance_signal=resonance,
        energy_level=EnergyLevel(energy),
        status=EntityStatus(status),
        source_id=node.get("source_id"),
        concept_ids=node.get("concept_ids") or [],
        siyuan_block_id=node.get("siyuan_block_id"),
        visit_count=node.get("visit_count", 0),
        created_at=_parse_datetime(node.get("created_at")),
        updated_at=_parse_datetime(node.get("updated_at")) if node.get("updated_at") else None,
    )


class PersonalGraphService:
    """Service for managing personal knowledge entities."""

    @classmethod
    async def _ensure_schema(cls) -> None:
        """Ensure ADHD ontology constraints and indexes exist."""
        queries = [
            "CREATE CONSTRAINT spark_id IF NOT EXISTS FOR (s:Spark) REQUIRE s.id IS UNIQUE",
            "CREATE CONSTRAINT insight_id IF NOT EXISTS FOR (i:Insight) REQUIRE i.id IS UNIQUE",
            "CREATE INDEX spark_status IF NOT EXISTS FOR (s:Spark) ON (s.status)",
            "CREATE INDEX spark_resonance IF NOT EXISTS FOR (s:Spark) ON (s.resonance_signal)",
            "CREATE INDEX spark_energy IF NOT EXISTS FOR (s:Spark) ON (s.energy_level)",
        ]
        for query in queries:
            try:
                await Neo4jClient.execute_write(query)
            except Exception:
                pass  # Constraints may already exist

    @classmethod
    async def create_spark(cls, request: CreateSparkRequest) -> SparkResponse:
        """Create a new spark entity."""
        await cls._ensure_schema()

        spark_id = _generate_id("spark")
        now = datetime.now().isoformat()

        query = """
        CREATE (s:Spark:ADHDEntity {
            id: $id,
            title: $title,
            content: $content,
            resonance_signal: $resonance_signal,
            energy_level: $energy_level,
            status: 'captured',
            source_id: $source_id,
            concept_ids: $concept_ids,
            siyuan_block_id: $siyuan_block_id,
            visit_count: 0,
            created_at: $created_at,
            schema_version: $schema_version
        })
        RETURN s
        """

        params = {
            "id": spark_id,
            "title": request.title,
            "content": request.content,
            "resonance_signal": request.resonance_signal.value if request.resonance_signal else None,
            "energy_level": request.energy_level.value,
            "source_id": request.source_id,
            "concept_ids": request.concept_ids,
            "siyuan_block_id": request.siyuan_block_id,
            "created_at": now,
            "schema_version": SCHEMA_VERSION,
        }

        results = await Neo4jClient.execute_write(query, params)

        if not results:
            raise ValueError("Failed to create spark")

        node = results[0].get("s", {})
        return _node_to_spark_response(node)

    @classmethod
    async def get_spark(cls, spark_id: str) -> SparkResponse | None:
        """Get a spark by ID."""
        query = """
        MATCH (s:Spark {id: $id})
        RETURN s
        """
        results = await Neo4jClient.execute_query(query, {"id": spark_id})

        if not results:
            return None

        node = results[0].get("s", {})
        return _node_to_spark_response(node)

    @classmethod
    async def visit_spark(cls, spark_id: str) -> bool:
        """Record a visit to a spark."""
        query = """
        MATCH (s:Spark {id: $id})
        SET s.visit_count = COALESCE(s.visit_count, 0) + 1,
            s.last_visited = $now
        RETURN s.id as id
        """
        results = await Neo4jClient.execute_write(
            query, {"id": spark_id, "now": datetime.now().isoformat()}
        )
        return len(results) > 0

    @classmethod
    async def promote_to_insight(
        cls, spark_id: str, request: PromoteSparkRequest
    ) -> InsightResponse:
        """Promote a spark to an insight."""
        await cls._ensure_schema()

        # First get the spark
        spark = await cls.get_spark(spark_id)
        if not spark:
            raise ValueError(f"Spark not found: {spark_id}")

        insight_id = _generate_id("insight")
        now = datetime.now().isoformat()
        title = request.insight_title or spark.title

        # Create insight and update spark
        query = """
        MATCH (s:Spark {id: $spark_id})
        SET s.status = 'anchored',
            s.promoted_to = $insight_id,
            s.promoted_at = $now
        CREATE (i:Insight:ADHDEntity {
            id: $insight_id,
            title: $title,
            content: $content,
            original_spark_id: $spark_id,
            resonance_signal: s.resonance_signal,
            energy_level: s.energy_level,
            status: 'anchored',
            concept_ids: s.concept_ids,
            thread_id: $thread_id,
            siyuan_block_id: s.siyuan_block_id,
            additional_context: $additional_context,
            created_at: $now,
            schema_version: $schema_version
        })
        CREATE (s)-[:PROMOTED_TO]->(i)
        RETURN i
        """

        params = {
            "spark_id": spark_id,
            "insight_id": insight_id,
            "title": title,
            "content": spark.content,
            "thread_id": request.thread_id,
            "additional_context": request.additional_context,
            "now": now,
            "schema_version": SCHEMA_VERSION,
        }

        results = await Neo4jClient.execute_write(query, params)

        if not results:
            raise ValueError("Failed to create insight")

        return InsightResponse(
            id=insight_id,
            title=title,
            content=spark.content,
            original_spark_id=spark_id,
            resonance_signal=spark.resonance_signal,
            energy_level=spark.energy_level,
            status=EntityStatus.ANCHORED,
            concept_ids=spark.concept_ids,
            thread_id=request.thread_id,
            siyuan_block_id=spark.siyuan_block_id,
            created_at=datetime.now(),
        )

    @classmethod
    async def find_sparks_by_resonance(
        cls, signal: ResonanceSignal, limit: int = 20
    ) -> SparkListResponse:
        """Find sparks by resonance signal."""
        query = """
        MATCH (s:Spark {resonance_signal: $signal})
        RETURN s
        ORDER BY s.created_at DESC
        LIMIT $limit
        """
        results = await Neo4jClient.execute_query(
            query, {"signal": signal.value, "limit": limit}
        )
        sparks = [_node_to_spark_response(r.get("s", {})) for r in results]
        return SparkListResponse(sparks=sparks, total=len(sparks))

    @classmethod
    async def find_sparks_by_energy(
        cls, level: EnergyLevel, limit: int = 20
    ) -> SparkListResponse:
        """Find sparks by energy level."""
        query = """
        MATCH (s:Spark {energy_level: $level})
        RETURN s
        ORDER BY s.created_at DESC
        LIMIT $limit
        """
        results = await Neo4jClient.execute_query(
            query, {"level": level.value, "limit": limit}
        )
        sparks = [_node_to_spark_response(r.get("s", {})) for r in results]
        return SparkListResponse(sparks=sparks, total=len(sparks))

    @classmethod
    async def find_unvisited_sparks(cls, limit: int = 20) -> SparkListResponse:
        """Find sparks that haven't been visited."""
        query = """
        MATCH (s:Spark)
        WHERE s.visit_count IS NULL OR s.visit_count = 0
        RETURN s
        ORDER BY s.created_at DESC
        LIMIT $limit
        """
        results = await Neo4jClient.execute_query(query, {"limit": limit})
        sparks = [_node_to_spark_response(r.get("s", {})) for r in results]
        return SparkListResponse(sparks=sparks, total=len(sparks))

    @classmethod
    async def list_sparks(cls, limit: int = 20, offset: int = 0) -> SparkListResponse:
        """List all sparks with pagination."""
        query = """
        MATCH (s:Spark)
        RETURN s
        ORDER BY s.created_at DESC
        SKIP $offset
        LIMIT $limit
        """
        results = await Neo4jClient.execute_query(query, {"limit": limit, "offset": offset})
        sparks = [_node_to_spark_response(r.get("s", {})) for r in results]
        
        # Get total count
        count_query = "MATCH (s:Spark) RETURN count(s) as total"
        count_result = await Neo4jClient.execute_query(count_query)
        total = count_result[0].get("total", 0) if count_result else len(sparks)
        
        return SparkListResponse(sparks=sparks, total=total)

    @classmethod
    async def get_stats(cls) -> PersonalStatsResponse:
        """Get statistics for the personal knowledge graph."""
        query = """
        MATCH (s:Spark)
        WITH count(s) as total_sparks,
             count(CASE WHEN s.status = 'captured' THEN 1 END) as captured,
             count(CASE WHEN s.status = 'exploring' THEN 1 END) as exploring,
             count(CASE WHEN s.status = 'anchored' THEN 1 END) as anchored
        OPTIONAL MATCH (i:Insight)
        WITH total_sparks, captured, exploring, anchored, count(i) as total_insights
        OPTIONAL MATCH (t:Thread)
        WITH total_sparks, captured, exploring, anchored, total_insights, count(t) as total_threads
        OPTIONAL MATCH (fp:FavoriteProblem)
        RETURN total_sparks, captured, exploring, anchored, total_insights, total_threads, count(fp) as total_favorite_problems
        """
        results = await Neo4jClient.execute_query(query)

        if not results:
            return PersonalStatsResponse(
                total_sparks=0,
                total_insights=0,
                total_threads=0,
                total_favorite_problems=0,
                sparks_by_status={},
                sparks_by_resonance={},
                recent_activity_count=0,
            )

        r = results[0]
        sparks_by_status = {
            "captured": r.get("captured", 0),
            "exploring": r.get("exploring", 0),
            "anchored": r.get("anchored", 0),
        }

        # Get resonance breakdown
        resonance_query = """
        MATCH (s:Spark)
        WHERE s.resonance_signal IS NOT NULL
        RETURN s.resonance_signal as signal, count(*) as count
        """
        resonance_results = await Neo4jClient.execute_query(resonance_query)
        sparks_by_resonance = {
            row.get("signal"): row.get("count", 0)
            for row in resonance_results
            if row.get("signal")
        }

        return PersonalStatsResponse(
            total_sparks=r.get("total_sparks", 0),
            total_insights=r.get("total_insights", 0),
            total_threads=r.get("total_threads", 0),
            total_favorite_problems=r.get("total_favorite_problems", 0),
            sparks_by_status=sparks_by_status,
            sparks_by_resonance=sparks_by_resonance,
            recent_activity_count=0,  # TODO: Calculate from timestamps
        )
