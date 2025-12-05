"""API endpoints for Quick Capture and Flow capture queue."""

from fastapi import APIRouter, HTTPException, Query

from ..schemas.capture import (
    CaptureCreateRequest,
    CaptureItem,
    CaptureListResponse,
    CaptureProcessRequest,
    CaptureProcessResponse,
    CaptureStatus,
    CaptureUpdateRequest,
)
from ..services.capture_service import CaptureService

router = APIRouter(prefix="/capture", tags=["capture"])


@router.post("", response_model=CaptureItem)
async def create_capture(request: CaptureCreateRequest) -> CaptureItem:
    """Create a capture queue item."""
    return await CaptureService.create_capture(request)


@router.get("", response_model=CaptureListResponse)
async def list_captures(
    status: CaptureStatus | None = Query(
        default=CaptureStatus.QUEUED,
        description="Filter by status; defaults to queued items",
    )
) -> CaptureListResponse:
    """List capture queue items."""
    return await CaptureService.list_captures(status)


@router.get("/{capture_id}", response_model=CaptureItem)
async def get_capture(capture_id: str) -> CaptureItem:
    """Get a single capture item."""
    capture = await CaptureService.get_capture(capture_id)
    if not capture:
        raise HTTPException(status_code=404, detail="Capture not found")
    return capture


@router.patch("/{capture_id}", response_model=CaptureItem)
async def update_capture(
    capture_id: str, request: CaptureUpdateRequest
) -> CaptureItem:
    """Update capture status or metadata."""
    capture = await CaptureService.update_capture(capture_id, request)
    if not capture:
        raise HTTPException(status_code=404, detail="Capture not found")
    return capture


@router.delete("/{capture_id}")
async def delete_capture(capture_id: str) -> dict:
    """Delete a capture item."""
    success = await CaptureService.delete_capture(capture_id)
    if not success:
        raise HTTPException(status_code=404, detail="Capture not found")
    return {"message": "Capture deleted"}


# Legacy quick-capture processing endpoint (preserved)
@router.post("/process", response_model=CaptureProcessResponse)
async def process_capture(request: CaptureProcessRequest) -> CaptureProcessResponse:
    """Process captured content for intelligent routing."""
    return await CaptureService.process_capture(request)
