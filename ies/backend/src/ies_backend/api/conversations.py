"""API endpoints for AI conversation imports."""

from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse

from ies_backend.schemas.conversation import (
    ConversationImport,
    ConversationImportResponse,
    ConversationListResponse,
    ConversationSession,
)
from ies_backend.services.conversation_service import ConversationService
from ies_backend.services.rendering_service import RenderingService

router = APIRouter(tags=["conversations"])


@router.post("/conversations/import", response_model=ConversationImportResponse)
async def import_conversation(request: ConversationImport) -> ConversationImportResponse:
    """Import a conversation from Claude/ChatGPT/text/URL."""
    return await ConversationService.import_conversation(request)


@router.get("/conversations", response_model=ConversationListResponse)
async def list_conversations(user_id: str | None = None) -> ConversationListResponse:
    """List imported conversations."""
    return await ConversationService.list_conversations(user_id=user_id)


@router.get("/conversations/{conversation_id}", response_model=ConversationSession)
async def get_conversation(conversation_id: str) -> ConversationSession:
    """Get a single conversation."""
    session = await ConversationService.get_conversation(conversation_id)
    if not session:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return session


@router.delete("/conversations/{conversation_id}")
async def delete_conversation(conversation_id: str) -> dict[str, str]:
    """Delete a conversation."""
    deleted = await ConversationService.delete_conversation(conversation_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return {"message": "Conversation deleted"}


@router.get("/conversations/{conversation_id}/read", response_class=HTMLResponse)
async def read_conversation(conversation_id: str) -> HTMLResponse:
    """Render a conversation in reader view."""
    session = await ConversationService.get_conversation(conversation_id)
    if not session:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return RenderingService.render_reader_view(session)


@router.get("/conversations/{conversation_id}/epub")
async def epub_conversation(conversation_id: str):
    """Download conversation as EPUB."""
    session = await ConversationService.get_conversation(conversation_id)
    if not session:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return RenderingService.render_epub(session)
