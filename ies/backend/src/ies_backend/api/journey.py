"""API endpoints for breadcrumb journey management."""

from fastapi import APIRouter, HTTPException

from ..schemas.journey import (
    BreadcrumbJourney,
    JourneyCreateRequest,
    JourneyCreateResponse,
    JourneyListResponse,
    JourneyUpdateRequest,
)
from ..services.journey_service import JourneyService

router = APIRouter(prefix="/journeys", tags=["journeys"])


@router.post("", response_model=JourneyCreateResponse)
async def create_journey(request: JourneyCreateRequest) -> JourneyCreateResponse:
    """Create a new exploration journey.

    This endpoint saves a breadcrumb journey from Readest or other exploration
    interfaces. Journeys capture the path, marks, and thinking partner exchanges
    during exploration.
    """
    journey = await JourneyService.create_journey(request)
    return JourneyCreateResponse(
        id=journey.id,
        siyuan_note_id=journey.siyuan_note_id,
        message="Journey saved successfully",
    )


@router.get("/{journey_id}", response_model=BreadcrumbJourney)
async def get_journey(journey_id: str) -> BreadcrumbJourney:
    """Get a journey by ID.

    Returns the complete journey including path, marks, and thinking partner
    exchanges.
    """
    journey = await JourneyService.get_journey(journey_id)
    if not journey:
        raise HTTPException(status_code=404, detail="Journey not found")
    return journey


@router.get("/user/{user_id}", response_model=JourneyListResponse)
async def list_user_journeys(
    user_id: str, page: int = 1, page_size: int = 20
) -> JourneyListResponse:
    """List journeys for a user.

    Returns paginated list of journeys ordered by start time (newest first).
    """
    journeys, total = await JourneyService.list_journeys(user_id, page, page_size)
    return JourneyListResponse(
        journeys=journeys,
        total=total,
        page=page,
        page_size=page_size,
    )


@router.patch("/{journey_id}", response_model=BreadcrumbJourney)
async def update_journey(
    journey_id: str, request: JourneyUpdateRequest
) -> BreadcrumbJourney:
    """Update a journey.

    Use this to:
    - Append new steps to the path (continuing exploration)
    - Add marks (highlights, annotations)
    - Add thinking partner exchanges
    - Set end time when exploration completes
    - Update title, tags, or notes
    """
    journey = await JourneyService.update_journey(journey_id, request)
    if not journey:
        raise HTTPException(status_code=404, detail="Journey not found")
    return journey


@router.delete("/{journey_id}")
async def delete_journey(journey_id: str) -> dict:
    """Delete a journey.

    Removes the journey and all associated steps, marks, and exchanges.
    """
    success = await JourneyService.delete_journey(journey_id)
    if not success:
        raise HTTPException(status_code=404, detail="Journey not found")
    return {"message": "Journey deleted successfully"}
