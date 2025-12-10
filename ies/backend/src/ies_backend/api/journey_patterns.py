"""API routes for journey pattern analysis.

Provides endpoints for analyzing exploration patterns, getting recommendations,
and retrieving insights based on journey history.
"""

from fastapi import APIRouter, HTTPException, Query

from ..schemas.journey_patterns import (
    JourneyPatternAnalysis,
    JourneyPatternRequest,
)
from ..services.journey_pattern_service import JourneyPatternService

router = APIRouter(prefix="/journey-patterns", tags=["journey-patterns"])


@router.get("/user/{user_id}", response_model=JourneyPatternAnalysis)
async def get_user_patterns(
    user_id: str,
    context_id: str | None = Query(None, description="Optional context filter"),
    days_back: int = Query(30, ge=1, le=365, description="Days to analyze"),
    min_visits_for_frequent: int = Query(
        3, ge=1, description="Minimum visits for frequent entity"
    ),
    min_path_frequency: int = Query(
        2, ge=1, description="Minimum occurrences for common path"
    ),
    max_recommendations: int = Query(
        10, ge=1, le=50, description="Max recommendations to return"
    ),
) -> JourneyPatternAnalysis:
    """Analyze journey patterns for a user.

    Returns entity clusters, frequent entities, common paths,
    recommendations, and insights based on exploration history.
    """
    request = JourneyPatternRequest(
        user_id=user_id,
        context_id=context_id,
        days_back=days_back,
        min_visits_for_frequent=min_visits_for_frequent,
        min_path_frequency=min_path_frequency,
        max_recommendations=max_recommendations,
    )

    try:
        return await JourneyPatternService.analyze_patterns(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pattern analysis failed: {e}")


@router.get("/context/{context_id}", response_model=JourneyPatternAnalysis)
async def get_context_patterns(
    context_id: str,
    user_id: str = Query("default_user", description="User ID"),
    days_back: int = Query(30, ge=1, le=365),
) -> JourneyPatternAnalysis:
    """Analyze journey patterns within a specific context."""
    request = JourneyPatternRequest(
        user_id=user_id,
        context_id=context_id,
        days_back=days_back,
    )

    try:
        return await JourneyPatternService.analyze_patterns(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pattern analysis failed: {e}")


@router.post("/analyze", response_model=JourneyPatternAnalysis)
async def analyze_patterns(request: JourneyPatternRequest) -> JourneyPatternAnalysis:
    """Analyze journey patterns with full configuration.

    Accepts a JourneyPatternRequest body for complete control over
    analysis parameters.
    """
    try:
        return await JourneyPatternService.analyze_patterns(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pattern analysis failed: {e}")
