"""API endpoints for Quick Capture processing."""

from fastapi import APIRouter

from ..schemas.capture import (
    CaptureProcessRequest,
    CaptureProcessResponse,
)
from ..services.capture_service import CaptureService

router = APIRouter(prefix="/capture", tags=["capture"])


@router.post("/process", response_model=CaptureProcessResponse)
async def process_capture(request: CaptureProcessRequest) -> CaptureProcessResponse:
    """Process captured content for intelligent routing.

    This endpoint analyzes unstructured content (text, voice transcription,
    image OCR, or fetched URL) and:
    1. Extracts entities/concepts mentioned
    2. Generates a summary
    3. Suggests tags
    4. Recommends placements (existing notes, concepts, journeys, or new note)

    The response provides placement suggestions ranked by confidence.
    Use the top suggestion or let the user choose.
    """
    return await CaptureService.process_capture(request)
