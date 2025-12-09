"""Question service for CRUD operations."""

from __future__ import annotations

import uuid
from datetime import datetime

from ies_backend.schemas.question import (
    Question,
    QuestionCreate,
    QuestionSource,
    QuestionStatus,
    QuestionType,
    QuestionUpdate,
    AnswerBlock,
    AnswerBlockCreate,
)


class QuestionService:
    """Service for managing questions."""

    def __init__(self):
        # In-memory store for MVP; replace with Neo4j/DB later
        self._questions: dict[str, Question] = {}
        self._answers: dict[str, AnswerBlock] = {}

    async def create(self, data: QuestionCreate) -> Question:
        """Create a new question."""
        question_id = str(uuid.uuid4())
        now = datetime.utcnow()

        question = Question(
            id=question_id,
            context_id=data.context_id,
            text=data.text,
            question_type=data.question_type,
            parent_question_id=data.parent_question_id,
            parent_entity_id=data.parent_entity_id,
            status=data.status,
            source=data.source,
            siyuan_block_id=data.siyuan_block_id,
            evidence_count=data.evidence_count,
            confidence=data.confidence,
            prerequisite_questions=[],
            related_concepts=[],
            linked_sources=[],
            created_at=now,
            updated_at=now,
        )

        self._questions[question_id] = question
        return question

    async def get(self, question_id: str) -> Question | None:
        """Get a question by ID."""
        return self._questions.get(question_id)

    async def list_by_context(self, context_id: str) -> list[Question]:
        """List all questions for a context."""
        questions = [q for q in self._questions.values() if q.context_id == context_id]
        questions.sort(key=lambda q: q.created_at, reverse=True)
        return questions

    async def list_by_source(self, source: QuestionSource) -> list[Question]:
        """List questions by source."""
        questions = [q for q in self._questions.values() if q.source == source]
        questions.sort(key=lambda q: q.created_at, reverse=True)
        return questions

    async def list_by_entity(self, entity_id: str, status: QuestionStatus | None = None) -> list[Question]:
        """List questions for a specific entity."""
        questions = [q for q in self._questions.values() if q.parent_entity_id == entity_id]
        if status:
            questions = [q for q in questions if q.status == status]
        questions.sort(key=lambda q: q.created_at, reverse=True)
        return questions

    async def list(
        self,
        context_id: str | None = None,
        source: QuestionSource | None = None,
        status: QuestionStatus | None = None,
        parent_entity_id: str | None = None,
        limit: int = 100,
    ) -> list[Question]:
        """List questions with optional filters."""
        questions = list(self._questions.values())

        if context_id:
            questions = [q for q in questions if q.context_id == context_id]
        if source:
            questions = [q for q in questions if q.source == source]
        if status:
            questions = [q for q in questions if q.status == status]
        if parent_entity_id:
            questions = [q for q in questions if q.parent_entity_id == parent_entity_id]

        questions.sort(key=lambda q: q.updated_at, reverse=True)
        return questions[:limit]

    async def update(self, question_id: str, data: QuestionUpdate) -> Question | None:
        """Update a question."""
        question = self._questions.get(question_id)
        if not question:
            return None

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(question, field, value)

        question.updated_at = datetime.utcnow()
        self._questions[question_id] = question
        return question

    async def delete(self, question_id: str) -> bool:
        """Delete a question."""
        if question_id in self._questions:
            del self._questions[question_id]
            return True
        return False

    async def create_answer(self, data: AnswerBlockCreate) -> AnswerBlock:
        """Create an answer block for a question."""
        answer_id = str(uuid.uuid4())
        now = datetime.utcnow()

        answer = AnswerBlock(
            id=answer_id,
            question_id=data.question_id,
            content=data.content,
            quality=data.quality,
            created_at=now,
            updated_at=now,
        )

        self._answers[answer_id] = answer
        return answer

    async def get_answers(self, question_id: str) -> list[AnswerBlock]:
        """Get all answers for a question."""
        return [a for a in self._answers.values() if a.question_id == question_id]
