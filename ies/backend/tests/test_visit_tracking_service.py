"""Tests for visit tracking service."""

import pytest
from datetime import datetime, timedelta

from ies_backend.services.visit_tracking_service import VisitTrackingService
from ies_backend.services.question_service import QuestionService
from ies_backend.services.highlight_service import HighlightService
from ies_backend.services.context_crud_service import ContextCRUDService
from ies_backend.schemas.visit_tracking import (
    RecordVisitRequest,
    NewItemsDetailRequest,
    VisitScope,
)
from ies_backend.schemas.question import QuestionCreate, QuestionSource, QuestionStatus
from ies_backend.schemas.highlight import HighlightCreate, HighlightColor
from ies_backend.schemas.context import ContextCreate, ContextType


@pytest.fixture
def visit_service():
    """Create a visit tracking service."""
    return VisitTrackingService()


@pytest.fixture
def question_service():
    """Create a question service."""
    return QuestionService()


@pytest.fixture
def highlight_service():
    """Create a highlight service."""
    # Use the class directly since it's all static methods
    return HighlightService


@pytest.fixture
def context_service():
    """Create a context service."""
    return ContextCRUDService()


@pytest.mark.asyncio
async def test_record_visit_first_time(visit_service):
    """Test recording a first-time visit."""
    request = RecordVisitRequest(
        user_id="user1",
        scope=VisitScope.CONTEXT,
        scope_id="ctx_123",
    )

    response = await visit_service.record_visit(request)

    assert response.visit_record.user_id == "user1"
    assert response.visit_record.scope == VisitScope.CONTEXT
    assert response.visit_record.scope_id == "ctx_123"
    assert response.previous_visit is None  # First visit


@pytest.mark.asyncio
async def test_record_visit_update_existing(visit_service):
    """Test updating an existing visit record."""
    request = RecordVisitRequest(
        user_id="user1",
        scope=VisitScope.CONTEXT,
        scope_id="ctx_123",
    )

    # First visit
    first_response = await visit_service.record_visit(request)
    first_timestamp = first_response.visit_record.last_visited_at

    # Second visit (should update)
    second_response = await visit_service.record_visit(request)

    assert second_response.previous_visit == first_timestamp
    assert second_response.visit_record.last_visited_at > first_timestamp


@pytest.mark.asyncio
async def test_get_last_visit_never_visited(visit_service):
    """Test getting last visit for never-visited scope."""
    last_visit = await visit_service.get_last_visit(
        user_id="user1",
        scope=VisitScope.CONTEXT,
        scope_id="ctx_999",
    )

    assert last_visit is None


@pytest.mark.asyncio
async def test_get_last_visit_after_recording(visit_service):
    """Test getting last visit after recording a visit."""
    request = RecordVisitRequest(
        user_id="user1",
        scope=VisitScope.BOOK,
        scope_id="42",
    )

    response = await visit_service.record_visit(request)
    recorded_time = response.visit_record.last_visited_at

    last_visit = await visit_service.get_last_visit(
        user_id="user1",
        scope=VisitScope.BOOK,
        scope_id="42",
    )

    assert last_visit == recorded_time


@pytest.mark.asyncio
async def test_new_items_summary_never_visited(visit_service, question_service):
    """Test new items summary for never-visited context."""
    summary = await visit_service.get_new_items_summary(
        user_id="user1",
        scope=VisitScope.CONTEXT,
        scope_id="ctx_123",
        question_service=question_service,
    )

    assert summary.last_visited_at is None
    assert summary.new_questions == 0
    assert summary.new_highlights == 0


@pytest.mark.asyncio
async def test_new_items_summary_with_new_questions(
    visit_service, question_service
):
    """Test new items summary shows new questions."""
    context_id = "ctx_123"

    # Record initial visit
    await visit_service.record_visit(
        RecordVisitRequest(
            user_id="user1",
            scope=VisitScope.CONTEXT,
            scope_id=context_id,
        )
    )

    # Create a question after the visit
    await question_service.create(
        QuestionCreate(
            context_id=context_id,
            text="What is executive function?",
            source=QuestionSource.READER,
        )
    )

    # Get summary
    summary = await visit_service.get_new_items_summary(
        user_id="user1",
        scope=VisitScope.CONTEXT,
        scope_id=context_id,
        question_service=question_service,
    )

    assert summary.new_questions == 1


@pytest.mark.asyncio
async def test_new_items_summary_with_new_highlights(
    visit_service, highlight_service
):
    """Test new items summary shows new highlights."""
    book_id = "42"

    # Record initial visit
    await visit_service.record_visit(
        RecordVisitRequest(
            user_id="user1",
            scope=VisitScope.BOOK,
            scope_id=book_id,
        )
    )

    # Create a highlight after the visit
    await highlight_service.create_highlight(
        HighlightCreate(
            book_id=book_id,
            text="Executive function is critical for ADHD management",
            cfi="/6/4[chap01]!/4/2/1:0",
            color=HighlightColor.YELLOW,
        )
    )

    # Get summary
    summary = await visit_service.get_new_items_summary(
        user_id="user1",
        scope=VisitScope.BOOK,
        scope_id=book_id,
        highlight_service=highlight_service,
    )

    assert summary.new_highlights == 1


@pytest.mark.asyncio
async def test_new_items_detail_with_questions(
    visit_service, question_service
):
    """Test detailed new items includes question details."""
    context_id = "ctx_123"

    # Record visit
    await visit_service.record_visit(
        RecordVisitRequest(
            user_id="user1",
            scope=VisitScope.CONTEXT,
            scope_id=context_id,
        )
    )

    # Create question after visit
    question = await question_service.create(
        QuestionCreate(
            context_id=context_id,
            text="How does working memory affect ADHD?",
            source=QuestionSource.AI_SUGGESTED,
        )
    )

    # Get detailed items
    detail = await visit_service.get_new_items_detail(
        request=NewItemsDetailRequest(
            user_id="user1",
            scope=VisitScope.CONTEXT,
            scope_id=context_id,
        ),
        question_service=question_service,
    )

    assert len(detail.questions) == 1
    assert detail.questions[0].text == "How does working memory affect ADHD?"
    assert detail.questions[0].id == question.id


@pytest.mark.asyncio
async def test_new_items_detail_with_highlights(
    visit_service, highlight_service
):
    """Test detailed new items includes highlight details."""
    book_id = "42"

    # Record visit
    await visit_service.record_visit(
        RecordVisitRequest(
            user_id="user1",
            scope=VisitScope.BOOK,
            scope_id=book_id,
        )
    )

    # Create highlight after visit
    highlight = await highlight_service.create_highlight(
        HighlightCreate(
            book_id=book_id,
            text="Working memory is a core executive function",
            cfi="/6/4[chap01]!/4/2/2:0",
            color=HighlightColor.GREEN,
        )
    )

    # Get detailed items
    detail = await visit_service.get_new_items_detail(
        request=NewItemsDetailRequest(
            user_id="user1",
            scope=VisitScope.BOOK,
            scope_id=book_id,
        ),
        highlight_service=highlight_service,
    )

    assert len(detail.highlights) == 1
    assert highlight.text in detail.highlights[0].text
    assert detail.highlights[0].book_id == book_id


@pytest.mark.asyncio
async def test_global_activity_summary(
    visit_service, question_service, highlight_service, context_service
):
    """Test global activity summary across all content."""
    # Record global activity timestamp
    await visit_service.record_visit(
        RecordVisitRequest(
            user_id="user1",
            scope=VisitScope.GLOBAL,
            scope_id="global",
        )
    )

    # Create context
    context = await context_service.create(
        ContextCreate(
            type=ContextType.FEYNMAN_PROBLEM,
            title="Understanding ADHD",
        )
    )

    # Create question
    await question_service.create(
        QuestionCreate(
            context_id=context.id,
            text="What causes ADHD?",
            source=QuestionSource.READER,
        )
    )

    # Create highlight
    await highlight_service.create_highlight(
        HighlightCreate(
            book_id="42",
            text="ADHD has genetic components",
            cfi="/6/4[chap02]!/4/2/1:0",
            color=HighlightColor.BLUE,
        )
    )

    # Get global summary
    summary = await visit_service.get_global_activity_summary(
        user_id="user1",
        question_service=question_service,
        highlight_service=highlight_service,
        context_service=context_service,
    )

    assert summary.new_questions_total == 1
    assert summary.new_highlights_total == 1
    assert summary.new_contexts_total == 1
    assert context.id in summary.active_contexts


@pytest.mark.asyncio
async def test_clear_visits_all_users(visit_service):
    """Test clearing all visit records."""
    # Record visits for multiple users
    await visit_service.record_visit(
        RecordVisitRequest(
            user_id="user1",
            scope=VisitScope.CONTEXT,
            scope_id="ctx_123",
        )
    )
    await visit_service.record_visit(
        RecordVisitRequest(
            user_id="user2",
            scope=VisitScope.BOOK,
            scope_id="42",
        )
    )

    # Clear all visits
    count = await visit_service.clear_visits()

    assert count == 2

    # Verify all visits cleared
    last_visit_1 = await visit_service.get_last_visit(
        "user1", VisitScope.CONTEXT, "ctx_123"
    )
    last_visit_2 = await visit_service.get_last_visit(
        "user2", VisitScope.BOOK, "42"
    )

    assert last_visit_1 is None
    assert last_visit_2 is None


@pytest.mark.asyncio
async def test_clear_visits_specific_user(visit_service):
    """Test clearing visits for specific user."""
    # Record visits for multiple users
    await visit_service.record_visit(
        RecordVisitRequest(
            user_id="user1",
            scope=VisitScope.CONTEXT,
            scope_id="ctx_123",
        )
    )
    await visit_service.record_visit(
        RecordVisitRequest(
            user_id="user2",
            scope=VisitScope.BOOK,
            scope_id="42",
        )
    )

    # Clear only user1's visits
    count = await visit_service.clear_visits(user_id="user1")

    assert count == 1

    # Verify user1's visits cleared but user2's remain
    last_visit_1 = await visit_service.get_last_visit(
        "user1", VisitScope.CONTEXT, "ctx_123"
    )
    last_visit_2 = await visit_service.get_last_visit(
        "user2", VisitScope.BOOK, "42"
    )

    assert last_visit_1 is None
    assert last_visit_2 is not None


@pytest.mark.asyncio
async def test_multiple_scopes_independent(visit_service):
    """Test that different scopes are tracked independently."""
    user_id = "user1"

    # Record visits to different scopes
    await visit_service.record_visit(
        RecordVisitRequest(
            user_id=user_id,
            scope=VisitScope.CONTEXT,
            scope_id="ctx_123",
        )
    )
    await visit_service.record_visit(
        RecordVisitRequest(
            user_id=user_id,
            scope=VisitScope.BOOK,
            scope_id="42",
        )
    )
    await visit_service.record_visit(
        RecordVisitRequest(
            user_id=user_id,
            scope=VisitScope.GLOBAL,
            scope_id="global",
        )
    )

    # Verify all scopes have independent timestamps
    context_visit = await visit_service.get_last_visit(
        user_id, VisitScope.CONTEXT, "ctx_123"
    )
    book_visit = await visit_service.get_last_visit(
        user_id, VisitScope.BOOK, "42"
    )
    global_visit = await visit_service.get_last_visit(
        user_id, VisitScope.GLOBAL, "global"
    )

    assert context_visit is not None
    assert book_visit is not None
    assert global_visit is not None
    # All should be different timestamps (recorded sequentially)
    assert context_visit != book_visit
    assert book_visit != global_visit


@pytest.mark.asyncio
async def test_limit_parameter_in_detail_request(
    visit_service, question_service
):
    """Test that limit parameter correctly limits returned items."""
    context_id = "ctx_123"

    # Record visit
    await visit_service.record_visit(
        RecordVisitRequest(
            user_id="user1",
            scope=VisitScope.CONTEXT,
            scope_id=context_id,
        )
    )

    # Create multiple questions
    for i in range(5):
        await question_service.create(
            QuestionCreate(
                context_id=context_id,
                text=f"Question {i}?",
                source=QuestionSource.READER,
            )
        )

    # Get detailed items with limit=2
    detail = await visit_service.get_new_items_detail(
        request=NewItemsDetailRequest(
            user_id="user1",
            scope=VisitScope.CONTEXT,
            scope_id=context_id,
            limit=2,
        ),
        question_service=question_service,
    )

    assert len(detail.questions) == 2
    assert detail.total_new_items == 2
