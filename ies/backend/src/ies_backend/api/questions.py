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
from ies_backend.schemas.passage import (
    PassageRankingRequest,
    PassageRankingResponse,
)
from ies_backend.services.question_service import QuestionService
from ies_backend.services.passage_ranking_service import PassageRankingService

router = APIRouter(tags=["questions"])

# Global service instances
_question_service = QuestionService()
_passage_ranking_service = PassageRankingService()


@router.post("/", response_model=Question)
async def create_question(data: QuestionCreate) -> Question:
    """Create a new question."""
    return await _question_service.create(data)


@router.get("/", response_model=list[Question])
async def list_questions(
    context_id: str | None = Query(None, description="Filter by context ID"),
    source: QuestionSource | None = Query(None, description="Filter by source"),
    status: QuestionStatus | None = Query(None, description="Filter by status"),
    parent_entity_id: str | None = Query(None, description="Filter by parent entity ID"),
    limit: int = Query(100, ge=1, le=500, description="Maximum results"),
) -> list[Question]:
    """List questions with optional filters."""
    return await _question_service.list(
        context_id=context_id,
        source=source,
        status=status,
        parent_entity_id=parent_entity_id,
        limit=limit,
    )


@router.get("/by-entity/{entity_id}", response_model=list[Question])
async def list_questions_by_entity(
    entity_id: str,
    status: QuestionStatus | None = Query(None, description="Filter by status"),
) -> list[Question]:
    """List all questions about a specific entity."""
    return await _question_service.list_by_entity(entity_id, status=status)


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


@router.get("/{question_id}/relevant-passages", response_model=PassageRankingResponse)
async def get_relevant_passages(
    question_id: str,
    max_passages: int = Query(10, ge=1, le=100, description="Maximum passages to return"),
    min_score: float = Query(0.1, ge=0.0, le=1.0, description="Minimum relevance score"),
    source_ids: list[str] | None = Query(None, description="Optional: limit to specific sources"),
) -> PassageRankingResponse:
    """Get passages ranked by relevance to the question.

    This endpoint helps answer questions by finding the most relevant
    text passages from indexed books. The ranking algorithm uses:
    - Keyword extraction from question text
    - Related concepts from the question
    - TF-IDF-like scoring with length normalization
    - Concept match bonuses

    Returns passages sorted by relevance score (0-1), with source
    attribution and matching details.
    """
    try:
        request = PassageRankingRequest(
            max_passages=max_passages,
            min_score=min_score,
            source_ids=source_ids,
        )
        return await _passage_ranking_service.rank_passages_for_question(
            question_id=question_id,
            request=request,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to rank passages: {str(e)}")
