"""API endpoints for Quick Inbox and Flow inbox queue."""

from fastapi import APIRouter, HTTPException, Query

from ..schemas.inbox import (
    DialogueMessageRequest,
    DialogueResponse,
    InboxCreateRequest,
    InboxItem,
    InboxListResponse,
    InboxProcessRequest,
    InboxProcessResponse,
    InboxStatus,
    InboxUpdateRequest,
    ResolveRequest,
    ResolveResponse,
)
from ..services.inbox_service import InboxService

router = APIRouter(tags=["inbox"])


@router.post("", response_model=InboxItem)
async def create_inbox(request: InboxCreateRequest) -> InboxItem:
    """Create an inbox queue item."""
    return await InboxService.create_inbox(request)


@router.get("", response_model=InboxListResponse)
async def list_inbox(
    status: InboxStatus | None = Query(
        default=InboxStatus.QUEUED,
        description="Filter by status; defaults to queued items",
    )
) -> InboxListResponse:
    """List inbox queue items."""
    return await InboxService.list_inbox(status)


@router.get("/{inbox_id}", response_model=InboxItem)
async def get_inbox(inbox_id: str) -> InboxItem:
    """Get a single inbox item."""
    inbox = await InboxService.get_inbox(inbox_id)
    if not inbox:
        raise HTTPException(status_code=404, detail="Inbox item not found")
    return inbox


@router.patch("/{inbox_id}", response_model=InboxItem)
async def update_inbox(
    inbox_id: str, request: InboxUpdateRequest
) -> InboxItem:
    """Update inbox status or metadata."""
    inbox = await InboxService.update_inbox(inbox_id, request)
    if not inbox:
        raise HTTPException(status_code=404, detail="Inbox item not found")
    return inbox


@router.delete("/{inbox_id}")
async def delete_inbox(inbox_id: str) -> dict:
    """Delete an inbox item."""
    success = await InboxService.delete_inbox(inbox_id)
    if not success:
        raise HTTPException(status_code=404, detail="Inbox item not found")
    return {"message": "Inbox item deleted"}


# Legacy quick-capture processing endpoint (preserved)
@router.post("/process", response_model=InboxProcessResponse)
async def process_inbox(request: InboxProcessRequest) -> InboxProcessResponse:
    """Process inbox content for intelligent routing."""
    return await InboxService.process_inbox(request)


@router.post("/{inbox_id}/message", response_model=DialogueResponse)
async def add_dialogue_message(
    inbox_id: str, request: DialogueMessageRequest
) -> DialogueResponse:
    """Add a user message to inbox dialogue and get AI response.

    The AI analyzes the inbox content and user message to:
    1. Understand what the capture is about
    2. Identify relevant concepts and connections
    3. Suggest placement options with confidence scores
    """
    response = await InboxService.add_dialogue_message(inbox_id, request)
    if not response:
        raise HTTPException(status_code=404, detail="Inbox item not found")
    return response


@router.post("/{inbox_id}/resolve", response_model=ResolveResponse)
async def resolve_inbox(
    inbox_id: str, request: ResolveRequest
) -> ResolveResponse:
    """Resolve an inbox item by routing to a destination.

    Actions:
    - link_to_concept: Link to existing knowledge graph concept
    - create_note: Create new SiYuan note with content
    - add_to_existing_note: Append to existing note
    - explore_in_flow: Escalate to FlowMode for deeper exploration
    - link_to_journey: Associate with active journey
    """
    response = await InboxService.resolve_inbox(inbox_id, request)
    if not response:
        raise HTTPException(status_code=404, detail="Inbox item not found")
    return response
