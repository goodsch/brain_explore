"""API endpoints for standalone Question operations.

Provides CRUD for questions independent of context nesting.
"""

from fastapi import APIRouter, HTTPException, Query

from ies_backend.schemas.question import (
    AnswerBlock,
    AnswerBlockCreate,
    Question,
    QuestionCreate,
    QuestionSource,
    QuestionStatus,
    QuestionUpdate,
)
from ies_backend.services.question_service import QuestionService

router = APIRouter(prefix="/questions", tags=["questions"])

# Global service instance
_question_service = QuestionService()


@router.post("/", response_model=Question)
async def create_question(data: QuestionCreate) -> Question:
    """Create a new question."""
    return await _question_service.create(data)


@router.get("/", response_model=list[Question])
async def list_questions(
    context_id: str | None = Query(None, description="Filter by context ID"),
    source: QuestionSource | None = Query(None, description="Filter by source"),
    status: QuestionStatus | None = Query(None, description="Filter by status"),
    limit: int = Query(100, ge=1, le=500, description="Maximum results"),
) -> list[Question]:
    """List questions with optional filters."""
    return await _question_service.list(
        context_id=context_id,
        source=source,
        status=status,
        limit=limit,
    )


@router.get("/{question_id}", response_model=Question)
async def get_question(question_id: str) -> Question:
    """Get a question by ID."""
    question = await _question_service.get(question_id)
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    return question


@router.patch("/{question_id}", response_model=Question)
async def update_question(question_id: str, data: QuestionUpdate) -> Question:
    """Update a question."""
    question = await _question_service.update(question_id, data)
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    return question


@router.delete("/{question_id}")
async def delete_question(question_id: str) -> dict:
    """Delete a question."""
    deleted = await _question_service.delete(question_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Question not found")
    return {"deleted": True}


@router.get("/{question_id}/answers", response_model=list[AnswerBlock])
async def list_answers(question_id: str) -> list[AnswerBlock]:
    """Get all answers for a question."""
    # Verify question exists
    question = await _question_service.get(question_id)
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    return await _question_service.get_answers(question_id)


@router.post("/{question_id}/answers", response_model=AnswerBlock)
async def create_answer(question_id: str, data: AnswerBlockCreate) -> AnswerBlock:
    """Create an answer block for a question."""
    # Verify question exists
    question = await _question_service.get(question_id)
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")

    # Ensure question_id matches
    if data.question_id != question_id:
        data = AnswerBlockCreate(
            question_id=question_id,
            content=data.content,
            quality=data.quality,
        )

    return await _question_service.create_answer(data)
