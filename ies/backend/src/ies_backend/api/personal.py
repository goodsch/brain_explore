"""API endpoints for personal knowledge graph (ADHD-friendly ontology)."""

from fastapi import APIRouter, HTTPException

from ..schemas.personal import (
    CreateSparkRequest,
    SparkResponse,
    PromoteSparkRequest,
    InsightResponse,
    SparkListResponse,
    PersonalStatsResponse,
    ResonanceSignal,
    EnergyLevel,
)
from ..services.personal_graph_service import PersonalGraphService

router = APIRouter(prefix="/personal", tags=["personal"])


@router.post("/sparks", response_model=SparkResponse)
async def create_spark(request: CreateSparkRequest) -> SparkResponse:
    """Create a new spark (raw resonance capture).

    Sparks are low-friction captures of ideas, insights, or moments of
    resonance. They can later be promoted to insights when they prove
    valuable.

    The `siyuan_block_id` field allows linking the spark to a SiYuan
    document block for bidirectional sync.
    """
    return await PersonalGraphService.create_spark(request)


@router.get("/sparks/{spark_id}", response_model=SparkResponse)
async def get_spark(spark_id: str) -> SparkResponse:
    """Get a spark by ID."""
    spark = await PersonalGraphService.get_spark(spark_id)
    if not spark:
        raise HTTPException(status_code=404, detail="Spark not found")
    return spark


@router.post("/sparks/{spark_id}/visit")
async def visit_spark(spark_id: str) -> dict:
    """Record a visit to a spark.

    This updates the visit count and last_visited timestamp,
    supporting recency-based navigation in the ADHD-friendly ontology.
    """
    success = await PersonalGraphService.visit_spark(spark_id)
    return {"success": success, "spark_id": spark_id}


@router.post("/sparks/{spark_id}/promote", response_model=InsightResponse)
async def promote_spark(spark_id: str, request: PromoteSparkRequest) -> InsightResponse:
    """Promote a spark to an insight.

    This transitions a spark from 'captured' status to 'anchored' as an
    insight. The original spark is preserved with a reference to the
    new insight.

    Optionally provide a new title and additional context for the insight.
    """
    try:
        return await PersonalGraphService.promote_to_insight(spark_id, request)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/sparks/by-resonance/{signal}", response_model=SparkListResponse)
async def find_by_resonance(signal: ResonanceSignal, limit: int = 20) -> SparkListResponse:
    """Find sparks by emotional resonance signal.

    ADHD-friendly retrieval: emotional states serve as better memory
    cues than taxonomic categories. Use this to find sparks captured
    during similar emotional states.
    """
    return await PersonalGraphService.find_sparks_by_resonance(signal, limit)


@router.get("/sparks/by-energy/{level}", response_model=SparkListResponse)
async def find_by_energy(level: EnergyLevel, limit: int = 20) -> SparkListResponse:
    """Find sparks by energy level.

    Mood-appropriate navigation: find content suitable for current
    energy state. Low energy → simpler content, high energy → complex
    exploration.
    """
    return await PersonalGraphService.find_sparks_by_energy(level, limit)


@router.get("/sparks/unvisited", response_model=SparkListResponse)
async def find_unvisited(limit: int = 20) -> SparkListResponse:
    """Find sparks that haven't been visited.

    Surface forgotten captures that may still hold value.
    """
    return await PersonalGraphService.find_unvisited_sparks(limit)


@router.get("/stats", response_model=PersonalStatsResponse)
async def get_personal_stats() -> PersonalStatsResponse:
    """Get statistics for the personal knowledge graph.

    Returns counts of sparks, insights, threads, and favorite problems,
    plus breakdowns by status and resonance signal.
    """
    return await PersonalGraphService.get_stats()
