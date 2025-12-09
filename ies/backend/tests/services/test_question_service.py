"""Tests for question service."""

import pytest
from ies_backend.schemas.question import (
    QuestionCreate,
    QuestionSource,
    QuestionStatus,
    QuestionUpdate,
    AnswerBlockCreate,
)
from ies_backend.services.question_service import QuestionService


@pytest.fixture
def question_service():
    return QuestionService()


class TestQuestionService:
    @pytest.mark.asyncio
    async def test_create_question(self, question_service):
        question_data = QuestionCreate(
            context_id="ctx-123",
            text="How does ADHD affect time perception?",
            source=QuestionSource.READER,
        )
        question = await question_service.create(question_data)

        assert question.id is not None
        assert question.text == "How does ADHD affect time perception?"
        assert question.context_id == "ctx-123"
        assert question.status == QuestionStatus.OPEN

    @pytest.mark.asyncio
    async def test_get_question(self, question_service):
        created = await question_service.create(QuestionCreate(
            context_id="ctx-1",
            text="Test question",
        ))
        fetched = await question_service.get(created.id)

        assert fetched is not None
        assert fetched.id == created.id

    @pytest.mark.asyncio
    async def test_list_questions_by_context(self, question_service):
        await question_service.create(QuestionCreate(
            context_id="ctx-1",
            text="Question 1 for ctx-1",
        ))
        await question_service.create(QuestionCreate(
            context_id="ctx-1",
            text="Question 2 for ctx-1",
        ))
        await question_service.create(QuestionCreate(
            context_id="ctx-2",
            text="Question for ctx-2",
        ))

        ctx1_questions = await question_service.list_by_context("ctx-1")
        assert len(ctx1_questions) == 2
        assert all(q.context_id == "ctx-1" for q in ctx1_questions)

    @pytest.mark.asyncio
    async def test_update_question_status(self, question_service):
        question = await question_service.create(QuestionCreate(
            context_id="ctx-1",
            text="Test question",
        ))

        updated = await question_service.update(
            question.id,
            QuestionUpdate(status=QuestionStatus.ANSWERED)
        )

        assert updated.status == QuestionStatus.ANSWERED

    @pytest.mark.asyncio
    async def test_list_questions_by_source(self, question_service):
        await question_service.create(QuestionCreate(
            context_id="ctx-1",
            text="From reader",
            source=QuestionSource.READER,
        ))
        await question_service.create(QuestionCreate(
            context_id="ctx-1",
            text="From SiYuan",
            source=QuestionSource.SIYUAN,
        ))

        reader_questions = await question_service.list_by_source(QuestionSource.READER)
        assert all(q.source == QuestionSource.READER for q in reader_questions)

    @pytest.mark.asyncio
    async def test_delete_question(self, question_service):
        created = await question_service.create(QuestionCreate(
            context_id="ctx-1",
            text="To delete",
        ))

        result = await question_service.delete(created.id)
        assert result is True

        fetched = await question_service.get(created.id)
        assert fetched is None

    @pytest.mark.asyncio
    async def test_create_answer_block(self, question_service):
        question = await question_service.create(QuestionCreate(
            context_id="ctx-1",
            text="Test question",
        ))

        answer = await question_service.create_answer(AnswerBlockCreate(
            question_id=question.id,
            content="This is an answer.",
            quality="draft",
        ))

        assert answer.id is not None
        assert answer.question_id == question.id
        assert answer.content == "This is an answer."

    @pytest.mark.asyncio
    async def test_get_answers_for_question(self, question_service):
        question = await question_service.create(QuestionCreate(
            context_id="ctx-1",
            text="Test question",
        ))

        await question_service.create_answer(AnswerBlockCreate(
            question_id=question.id,
            content="Answer 1",
        ))
        await question_service.create_answer(AnswerBlockCreate(
            question_id=question.id,
            content="Answer 2",
        ))

        answers = await question_service.get_answers(question.id)
        assert len(answers) == 2
