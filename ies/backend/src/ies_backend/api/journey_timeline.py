"""API endpoints for journey timeline visualization."""

from fastapi import APIRouter, HTTPException, Query

from ies_backend.schemas.journey_timeline import (
    JourneyTimelineRequest,
    JourneyTimelineResponse,
    TimelineEntryType,
    TimelineGrouping,
    TimelineStatsResponse,
)
from ies_backend.services.journey_timeline_service import JourneyTimelineService

router = APIRouter(prefix="/journey-timeline", tags=["journey-timeline"])


@router.post("", response_model=JourneyTimelineResponse)
async def get_timeline(request: JourneyTimelineRequest) -> JourneyTimelineResponse:
    """Get a timeline view of journey entries.

    This endpoint aggregates journey data from multiple sources:
    - ContextJourneyEntry records (Flow Mode interactions)
    - BreadcrumbJourney steps (Reader exploration paths)
    - Highlights, notes, and other captured artifacts

    The timeline can be filtered by context, user, date range, and entry type.
    Entries can be grouped by day, week, session, or context.

    Args:
        request: Timeline request with filters and grouping options

    Returns:
        Timeline response with grouped entries and statistics

    Example:
        ```
        POST /journey-timeline
        {
          "context_id": "ctx_abc123",
          "grouping": "by_day",
          "entry_types": ["entity_visit", "highlight_created"],
          "limit": 50
        }
        ```
    """
    try:
        return await JourneyTimelineService.build_timeline(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to build timeline: {str(e)}")


@router.get("/context/{context_id}", response_model=JourneyTimelineResponse)
async def get_context_timeline(
    context_id: str,
    focus_id: str | None = None,
    grouping: TimelineGrouping = TimelineGrouping.BY_DAY,
    entry_types: list[TimelineEntryType] | None = Query(None),
    limit: int = 100,
) -> JourneyTimelineResponse:
    """Get timeline for a specific context.

    Convenience endpoint for fetching timeline filtered by context.

    Args:
        context_id: Context to filter by
        focus_id: Optional question/area to filter by
        grouping: How to group entries (by_day, by_week, by_session, etc.)
        entry_types: Optional list of entry types to include
        limit: Maximum number of entries to return

    Returns:
        Timeline response

    Example:
        ```
        GET /journey-timeline/context/ctx_abc123?grouping=by_day&limit=50
        ```
    """
    request = JourneyTimelineRequest(
        context_id=context_id,
        focus_id=focus_id,
        grouping=grouping,
        entry_types=entry_types,
        limit=limit,
    )
    return await JourneyTimelineService.build_timeline(request)


@router.get("/user/{user_id}", response_model=JourneyTimelineResponse)
async def get_user_timeline(
    user_id: str,
    context_id: str | None = None,
    grouping: TimelineGrouping = TimelineGrouping.BY_DAY,
    entry_types: list[TimelineEntryType] | None = Query(None),
    limit: int = 100,
) -> JourneyTimelineResponse:
    """Get timeline for a specific user.

    Convenience endpoint for fetching timeline filtered by user.

    Args:
        user_id: User to filter by
        context_id: Optional context to filter by
        grouping: How to group entries
        entry_types: Optional list of entry types to include
        limit: Maximum number of entries

    Returns:
        Timeline response

    Example:
        ```
        GET /journey-timeline/user/chris?grouping=by_week&limit=100
        ```
    """
    request = JourneyTimelineRequest(
        user_id=user_id,
        context_id=context_id,
        grouping=grouping,
        entry_types=entry_types,
        limit=limit,
    )
    return await JourneyTimelineService.build_timeline(request)


@router.get("/stats/context/{context_id}", response_model=TimelineStatsResponse)
async def get_context_stats(context_id: str) -> TimelineStatsResponse:
    """Get summary statistics for a context's timeline.

    Returns aggregated stats about exploration activity within a context:
    - Total counts by entry type
    - Activity distribution over time
    - Most visited entities
    - Total exploration time

    Args:
        context_id: Context to analyze

    Returns:
        Timeline statistics

    Example:
        ```
        GET /journey-timeline/stats/context/ctx_abc123
        ```
    """
    try:
        return await JourneyTimelineService.get_timeline_stats(context_id=context_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to calculate stats: {str(e)}")


@router.get("/stats/user/{user_id}", response_model=TimelineStatsResponse)
async def get_user_stats(user_id: str) -> TimelineStatsResponse:
    """Get summary statistics for a user's timeline.

    Returns aggregated stats about all exploration activity for a user.

    Args:
        user_id: User to analyze

    Returns:
        Timeline statistics

    Example:
        ```
        GET /journey-timeline/stats/user/chris
        ```
    """
    try:
        return await JourneyTimelineService.get_timeline_stats(user_id=user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to calculate stats: {str(e)}")
