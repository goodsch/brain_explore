"""Visit tracking API for "New since last run" functionality.

Provides endpoints to:
- Record when users visit contexts/books/entities
- Query for new items created since last visit
- Get global activity summary
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import Annotated

from ..schemas.visit_tracking import (
    RecordVisitRequest,
    RecordVisitResponse,
    NewItemsSummary,
    NewItemsDetailRequest,
    NewItemsDetailResponse,
    GlobalActivitySummary,
    VisitScope,
)
from ..services.visit_tracking_service import VisitTrackingService
from ..services.question_service import QuestionService
from ..services.highlight_service import HighlightService
from ..services.context_crud_service import ContextCRUDService

router = APIRouter(prefix="/visits", tags=["visit_tracking"])

# Service instances
visit_tracking_service = VisitTrackingService()
question_service = QuestionService()
highlight_service = HighlightService()
context_service = ContextCRUDService()


@router.post("/record", response_model=RecordVisitResponse)
async def record_visit(request: RecordVisitRequest):
    """Record that a user visited a scope (context, book, entity, or global).

    This updates the "last visited" timestamp for the user/scope combination.
    Use this to track when users were last active so you can show them
    what's new since their last session.

    **Examples:**
    - Record visiting a context: `{"scope": "context", "scope_id": "ctx_123"}`
    - Record visiting a book: `{"scope": "book", "scope_id": "42"}`
    - Record global activity: `{"scope": "global", "scope_id": "global"}`
    """
    return await visit_tracking_service.record_visit(request)


@router.get("/new-items-summary/{scope}/{scope_id}", response_model=NewItemsSummary)
async def get_new_items_summary(
    scope: VisitScope,
    scope_id: str,
    user_id: str = "default_user",
):
    """Get a summary count of new items since last visit.

    Returns counts of:
    - New questions created
    - New highlights added
    - New entities extracted
    - New relationships formed
    - New journey entries logged

    **Examples:**
    - Get new items for context: `/visits/new-items-summary/context/ctx_123`
    - Get new items for book: `/visits/new-items-summary/book/42`
    - Get global new items: `/visits/new-items-summary/global/global`
    """
    return await visit_tracking_service.get_new_items_summary(
        user_id=user_id,
        scope=scope,
        scope_id=scope_id,
        question_service=question_service,
        highlight_service=highlight_service,
        context_service=context_service,
    )


@router.post("/new-items-detail", response_model=NewItemsDetailResponse)
async def get_new_items_detail(request: NewItemsDetailRequest):
    """Get detailed list of new items since last visit.

    Returns the actual items (questions, highlights, entities, etc.)
    that were created since the user's last visit to this scope.

    **Request body:**
    ```json
    {
      "user_id": "default_user",
      "scope": "context",
      "scope_id": "ctx_123",
      "limit": 50
    }
    ```

    **Use cases:**
    - Show "New in this context" panel
    - Populate "What's new" feed
    - Highlight unseen items in UI
    """
    return await visit_tracking_service.get_new_items_detail(
        request=request,
        question_service=question_service,
        highlight_service=highlight_service,
        context_service=context_service,
    )


@router.get("/global-activity", response_model=GlobalActivitySummary)
async def get_global_activity(user_id: str = "default_user"):
    """Get summary of all new activity across the entire system.

    Returns:
    - When user was last active globally
    - Total new entities, highlights, questions, contexts
    - List of context IDs with new activity

    **Use case:** Dashboard showing "What happened while you were away"
    """
    return await visit_tracking_service.get_global_activity_summary(
        user_id=user_id,
        question_service=question_service,
        highlight_service=highlight_service,
        context_service=context_service,
    )


@router.get("/last-visit/{scope}/{scope_id}")
async def get_last_visit(
    scope: VisitScope,
    scope_id: str,
    user_id: str = "default_user",
):
    """Get the timestamp of the user's last visit to a scope.

    Returns:
    - `last_visited_at`: ISO timestamp of last visit (or null if never visited)

    **Examples:**
    - Check last context visit: `/visits/last-visit/context/ctx_123`
    - Check last book visit: `/visits/last-visit/book/42`
    """
    last_visit = await visit_tracking_service.get_last_visit(
        user_id=user_id,
        scope=scope,
        scope_id=scope_id,
    )
    return {
        "scope": scope,
        "scope_id": scope_id,
        "user_id": user_id,
        "last_visited_at": last_visit.isoformat() if last_visit else None,
    }


@router.delete("/clear")
async def clear_visits(user_id: str | None = None):
    """Clear visit records (for testing/reset).

    **Query params:**
    - `user_id`: Clear visits for specific user (omit to clear all)

    **WARNING:** This is destructive and primarily for testing.
    """
    count = await visit_tracking_service.clear_visits(user_id)
    return {
        "cleared": count,
        "user_id": user_id or "all",
    }
