"""API routes for generating and managing reframes."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from ies_backend.schemas.reframe import (
    FeedbackRequest,
    GenerateReframesRequest,
    ReframeListResponse,
)
from ies_backend.services.reframe_service import reframe_service

router = APIRouter()


@router.get("/concepts/{concept_id}/reframes", response_model=ReframeListResponse)
async def list_reframes(concept_id: str) -> ReframeListResponse:
    """Return reframes stored for a concept."""

    reframes = await reframe_service.get_reframes(concept_id)
    return ReframeListResponse(reframes=reframes)


@router.post(
    "/concepts/{concept_id}/reframes/generate",
    response_model=ReframeListResponse,
)
async def generate_reframes(
    concept_id: str,
    request: GenerateReframesRequest,
) -> ReframeListResponse:
    """Generate reframes for a concept and store them in Neo4j."""

    try:
        reframes = await reframe_service.generate_reframes(concept_id, request.count)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:  # pragma: no cover - unexpected
        raise HTTPException(status_code=500, detail=f"Failed to generate reframes: {exc}") from exc

    return ReframeListResponse(reframes=reframes)


@router.post("/{reframe_id}/feedback")
async def submit_feedback(reframe_id: str, request: FeedbackRequest) -> None:
    """Submit a helpful/confusing vote for a specific reframe."""

    try:
        await reframe_service.record_feedback(reframe_id, request.vote)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
