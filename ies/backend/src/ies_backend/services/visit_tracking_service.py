"""Service for tracking user visits and surfacing new content.

Implements "New since last run" functionality by tracking when users
last visited contexts, books, and entities, then querying for items
created/modified since that timestamp.
"""

from datetime import datetime
from typing import Any

from ..schemas.visit_tracking import (
    VisitScope,
    VisitRecord,
    RecordVisitRequest,
    RecordVisitResponse,
    NewItemsSummary,
    NewItemsDetailRequest,
    NewItemsDetailResponse,
    NewEntity,
    NewHighlight,
    NewQuestion,
    NewRelationship,
    GlobalActivitySummary,
)
from ..schemas.question import QuestionStatus


class VisitTrackingService:
    """Service for tracking visits and finding new content.

    Uses in-memory storage (MVP). Will migrate to Neo4j/PostgreSQL later.
    """

    def __init__(self):
        # In-memory store: (user_id, scope, scope_id) -> VisitRecord
        self._visits: dict[tuple[str, str, str], VisitRecord] = {}

    async def record_visit(self, request: RecordVisitRequest) -> RecordVisitResponse:
        """Record that a user visited a scope.

        Args:
            request: Visit recording request

        Returns:
            Response with visit record and previous visit timestamp
        """
        key = (request.user_id, request.scope.value, request.scope_id)
        previous_visit = self._visits.get(key)

        now = datetime.utcnow()
        visit_record = VisitRecord(
            user_id=request.user_id,
            scope=request.scope,
            scope_id=request.scope_id,
            last_visited_at=now,
        )

        self._visits[key] = visit_record

        return RecordVisitResponse(
            visit_record=visit_record,
            previous_visit=previous_visit.last_visited_at if previous_visit else None,
        )

    async def get_last_visit(
        self,
        user_id: str,
        scope: VisitScope,
        scope_id: str,
    ) -> datetime | None:
        """Get the timestamp of the last visit to a scope.

        Args:
            user_id: User identifier
            scope: What was visited
            scope_id: ID of the visited item

        Returns:
            Last visit timestamp or None if never visited
        """
        key = (user_id, scope.value, scope_id)
        visit_record = self._visits.get(key)
        return visit_record.last_visited_at if visit_record else None

    async def get_new_items_summary(
        self,
        user_id: str,
        scope: VisitScope,
        scope_id: str,
        # Injected services for querying
        question_service: Any = None,
        highlight_service: Any = None,
        context_service: Any = None,
    ) -> NewItemsSummary:
        """Get summary of new items since last visit.

        Args:
            user_id: User identifier
            scope: What scope to check
            scope_id: ID of the scope
            question_service: QuestionService instance (optional)
            highlight_service: HighlightService instance (optional)
            context_service: ContextCRUDService instance (optional)

        Returns:
            Summary of new items counts
        """
        last_visit = await self.get_last_visit(user_id, scope, scope_id)

        summary = NewItemsSummary(
            scope=scope,
            scope_id=scope_id,
            last_visited_at=last_visit,
        )

        if last_visit is None:
            # First visit - don't count everything as "new"
            return summary

        # Count new questions (if context or global)
        if question_service and scope in [VisitScope.CONTEXT, VisitScope.GLOBAL]:
            questions = await question_service.list(
                context_id=scope_id if scope == VisitScope.CONTEXT else None
            )
            summary.new_questions = sum(
                1 for q in questions if q.created_at > last_visit
            )

        # Count new highlights (if book, context, or global)
        if highlight_service:
            if scope == VisitScope.BOOK:
                highlights = await highlight_service.list_highlights(book_id=scope_id)
                summary.new_highlights = sum(
                    1 for h in highlights if h.created_at > last_visit
                )
            elif scope == VisitScope.CONTEXT:
                highlights = await highlight_service.list_highlights(context_id=scope_id)
                summary.new_highlights = sum(
                    1 for h in highlights if h.created_at > last_visit
                )
            elif scope == VisitScope.GLOBAL:
                highlights = await highlight_service.list_highlights()
                summary.new_highlights = sum(
                    1 for h in highlights if h.created_at > last_visit
                )

        return summary

    async def get_new_items_detail(
        self,
        request: NewItemsDetailRequest,
        # Injected services
        question_service: Any = None,
        highlight_service: Any = None,
        context_service: Any = None,
    ) -> NewItemsDetailResponse:
        """Get detailed list of new items since last visit.

        Args:
            request: Request with scope and filters
            question_service: QuestionService instance (optional)
            highlight_service: HighlightService instance (optional)
            context_service: ContextCRUDService instance (optional)

        Returns:
            Detailed list of new items
        """
        last_visit = await self.get_last_visit(
            request.user_id, request.scope, request.scope_id
        )

        response = NewItemsDetailResponse(
            scope=request.scope,
            scope_id=request.scope_id,
            last_visited_at=last_visit,
            total_new_items=0,
        )

        if last_visit is None:
            # First visit - return empty
            return response

        # Get new questions
        if question_service and request.scope in [VisitScope.CONTEXT, VisitScope.GLOBAL]:
            questions = await question_service.list(
                context_id=request.scope_id if request.scope == VisitScope.CONTEXT else None,
                limit=request.limit,
            )
            new_questions = [
                NewQuestion(
                    id=q.id,
                    text=q.text,
                    context_id=q.context_id,
                    created_at=q.created_at,
                    status=q.status.value,
                )
                for q in questions
                if q.created_at > last_visit
            ]
            response.questions = new_questions[:request.limit]

        # Get new highlights
        if highlight_service:
            if request.scope == VisitScope.BOOK:
                highlights = await highlight_service.list_highlights(
                    book_id=request.scope_id, limit=request.limit
                )
            elif request.scope == VisitScope.CONTEXT:
                highlights = await highlight_service.list_highlights(
                    context_id=request.scope_id, limit=request.limit
                )
            else:  # GLOBAL or ENTITY
                highlights = await highlight_service.list_highlights(limit=request.limit)

            new_highlights = [
                NewHighlight(
                    id=h.id,
                    book_id=h.book_id,
                    text=h.text[:200] + "..." if len(h.text) > 200 else h.text,
                    created_at=h.created_at,
                    context_id=h.context_id,
                )
                for h in highlights
                if h.created_at > last_visit
            ]
            response.highlights = new_highlights[:request.limit]

        # Calculate total
        response.total_new_items = (
            len(response.questions)
            + len(response.highlights)
            + len(response.entities)
            + len(response.relationships)
        )

        return response

    async def get_global_activity_summary(
        self,
        user_id: str,
        # Injected services
        question_service: Any = None,
        highlight_service: Any = None,
        context_service: Any = None,
    ) -> GlobalActivitySummary:
        """Get summary of all new activity across the system.

        Args:
            user_id: User identifier
            question_service: QuestionService instance (optional)
            highlight_service: HighlightService instance (optional)
            context_service: ContextCRUDService instance (optional)

        Returns:
            Global activity summary
        """
        last_active = await self.get_last_visit(user_id, VisitScope.GLOBAL, "global")

        summary = GlobalActivitySummary(
            last_active_at=last_active,
        )

        if last_active is None:
            # First time user - don't count everything
            return summary

        # Count new questions
        if question_service:
            questions = await question_service.list()
            summary.new_questions_total = sum(
                1 for q in questions if q.created_at > last_active
            )

            # Find contexts with new questions
            contexts_with_questions = set(
                q.context_id for q in questions if q.created_at > last_active
            )
            summary.active_contexts.extend(contexts_with_questions)

        # Count new highlights
        if highlight_service:
            highlights = await highlight_service.list_highlights()
            summary.new_highlights_total = sum(
                1 for h in highlights if h.created_at > last_active
            )

        # Count new contexts
        if context_service:
            contexts = await context_service.list()
            summary.new_contexts_total = sum(
                1 for c in contexts if c.created_at > last_active
            )

        # Deduplicate active contexts
        summary.active_contexts = list(set(summary.active_contexts))

        return summary

    async def clear_visits(self, user_id: str | None = None) -> int:
        """Clear visit records (for testing).

        Args:
            user_id: User to clear visits for (None = all users)

        Returns:
            Number of visits cleared
        """
        if user_id is None:
            count = len(self._visits)
            self._visits.clear()
            return count

        # Clear visits for specific user
        keys_to_remove = [
            key for key in self._visits.keys() if key[0] == user_id
        ]
        for key in keys_to_remove:
            del self._visits[key]
        return len(keys_to_remove)
