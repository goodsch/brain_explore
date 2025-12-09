"""Tests for context CRUD service."""

import pytest

from ies_backend.schemas.context import (
    ContextCreate,
    ContextStatus,
    ContextType,
    ContextUpdate,
)
from ies_backend.services.context_crud_service import ContextCRUDService


@pytest.fixture(autouse=True)
def clear_context_store():
    """Clear the in-memory context store before each test."""
    ContextCRUDService.clear_store()
    yield
    ContextCRUDService.clear_store()


class TestContextCRUDService:
    """Test suite for ContextCRUDService."""

    @pytest.mark.asyncio
    async def test_create_context(self):
        """Test creating a context with minimal data."""
        context_data = ContextCreate(
            type=ContextType.FEYNMAN_PROBLEM,
            title="What is ADHD time perception?",
        )
        context = await ContextCRUDService.create(context_data)

        assert context.id is not None
        assert context.id.startswith("ctx_")
        assert context.title == "What is ADHD time perception?"
        assert context.type == ContextType.FEYNMAN_PROBLEM
        assert context.status == ContextStatus.ACTIVE
        assert context.summary is None
        assert context.key_questions == []
        assert context.created_at is not None
        assert context.updated_at is not None

    @pytest.mark.asyncio
    async def test_create_context_with_full_data(self):
        """Test creating a context with all fields populated."""
        context_data = ContextCreate(
            type=ContextType.PROJECT,
            title="IES Flow Mode v2",
            summary="Implement question-driven exploration UI",
            status=ContextStatus.ACTIVE,
            parent_context_id="ctx_parent123",
            siyuan_doc_id="20231208-123456",
        )
        context = await ContextCRUDService.create(context_data)

        assert context.id is not None
        assert context.title == "IES Flow Mode v2"
        assert context.type == ContextType.PROJECT
        assert context.summary == "Implement question-driven exploration UI"
        assert context.status == ContextStatus.ACTIVE
        assert context.parent_context_id == "ctx_parent123"
        assert context.siyuan_block_id == "20231208-123456"

    @pytest.mark.asyncio
    async def test_get_context(self):
        """Test retrieving a context by ID."""
        # Create a context first
        context_data = ContextCreate(
            type=ContextType.PROJECT,
            title="Test Project",
        )
        created = await ContextCRUDService.create(context_data)

        # Retrieve it
        fetched = await ContextCRUDService.get(created.id)

        assert fetched is not None
        assert fetched.id == created.id
        assert fetched.title == "Test Project"
        assert fetched.type == ContextType.PROJECT

    @pytest.mark.asyncio
    async def test_get_nonexistent_context(self):
        """Test retrieving a context that doesn't exist."""
        result = await ContextCRUDService.get("nonexistent-id")
        assert result is None

    @pytest.mark.asyncio
    async def test_list_contexts(self):
        """Test listing all contexts."""
        # Create multiple contexts
        await ContextCRUDService.create(
            ContextCreate(type=ContextType.PROJECT, title="Project 1")
        )
        await ContextCRUDService.create(
            ContextCreate(type=ContextType.THEORY, title="Theory 1")
        )

        contexts = await ContextCRUDService.list()
        assert len(contexts) >= 2

    @pytest.mark.asyncio
    async def test_list_contexts_by_type(self):
        """Test listing contexts filtered by type."""
        # Create contexts of different types
        await ContextCRUDService.create(
            ContextCreate(type=ContextType.PROJECT, title="Project A")
        )
        await ContextCRUDService.create(
            ContextCreate(type=ContextType.THEORY, title="Theory A")
        )
        await ContextCRUDService.create(
            ContextCreate(type=ContextType.PROJECT, title="Project B")
        )

        projects = await ContextCRUDService.list(context_type=ContextType.PROJECT)
        assert all(c.type == ContextType.PROJECT for c in projects)
        assert len([c for c in projects if c.title in ["Project A", "Project B"]]) == 2

    @pytest.mark.asyncio
    async def test_list_contexts_by_status(self):
        """Test listing contexts filtered by status."""
        # Create contexts with different statuses
        await ContextCRUDService.create(
            ContextCreate(
                type=ContextType.PROJECT, title="Active Project", status=ContextStatus.ACTIVE
            )
        )
        await ContextCRUDService.create(
            ContextCreate(
                type=ContextType.PROJECT, title="Paused Project", status=ContextStatus.PAUSED
            )
        )

        active_contexts = await ContextCRUDService.list(status=ContextStatus.ACTIVE)
        assert all(c.status == ContextStatus.ACTIVE for c in active_contexts)

    @pytest.mark.asyncio
    async def test_list_contexts_with_combined_filters(self):
        """Test listing contexts with both type and status filters."""
        # Create test data
        await ContextCRUDService.create(
            ContextCreate(
                type=ContextType.PROJECT,
                title="Active Project",
                status=ContextStatus.ACTIVE,
            )
        )
        await ContextCRUDService.create(
            ContextCreate(
                type=ContextType.PROJECT,
                title="Paused Project",
                status=ContextStatus.PAUSED,
            )
        )
        await ContextCRUDService.create(
            ContextCreate(
                type=ContextType.THEORY, title="Active Theory", status=ContextStatus.ACTIVE
            )
        )

        # Filter for active projects
        active_projects = await ContextCRUDService.list(
            context_type=ContextType.PROJECT, status=ContextStatus.ACTIVE
        )
        assert all(
            c.type == ContextType.PROJECT and c.status == ContextStatus.ACTIVE
            for c in active_projects
        )

    @pytest.mark.asyncio
    async def test_list_contexts_limit(self):
        """Test that the limit parameter works correctly."""
        # Create multiple contexts
        for i in range(5):
            await ContextCRUDService.create(
                ContextCreate(type=ContextType.PROJECT, title=f"Project {i}")
            )

        limited_contexts = await ContextCRUDService.list(limit=3)
        assert len(limited_contexts) <= 3

    @pytest.mark.asyncio
    async def test_update_context_title(self):
        """Test updating a context's title."""
        created = await ContextCRUDService.create(
            ContextCreate(
                type=ContextType.PROJECT,
                title="Original Title",
            )
        )

        updated = await ContextCRUDService.update(
            created.id, ContextUpdate(title="New Title")
        )

        assert updated is not None
        assert updated.title == "New Title"
        assert updated.id == created.id

    @pytest.mark.asyncio
    async def test_update_context_status(self):
        """Test updating a context's status."""
        created = await ContextCRUDService.create(
            ContextCreate(type=ContextType.PROJECT, title="Test Project")
        )

        updated = await ContextCRUDService.update(
            created.id, ContextUpdate(status=ContextStatus.PAUSED)
        )

        assert updated is not None
        assert updated.status == ContextStatus.PAUSED

    @pytest.mark.asyncio
    async def test_update_context_multiple_fields(self):
        """Test updating multiple fields at once."""
        created = await ContextCRUDService.create(
            ContextCreate(
                type=ContextType.PROJECT,
                title="Original",
                summary="Original summary",
            )
        )

        updated = await ContextCRUDService.update(
            created.id,
            ContextUpdate(
                title="Updated Title",
                summary="Updated summary",
                status=ContextStatus.ARCHIVED,
            ),
        )

        assert updated is not None
        assert updated.title == "Updated Title"
        assert updated.summary == "Updated summary"
        assert updated.status == ContextStatus.ARCHIVED

    @pytest.mark.asyncio
    async def test_update_nonexistent_context(self):
        """Test updating a context that doesn't exist."""
        result = await ContextCRUDService.update(
            "nonexistent-id", ContextUpdate(title="New Title")
        )
        assert result is None

    @pytest.mark.asyncio
    async def test_update_with_no_changes(self):
        """Test update with empty update data."""
        created = await ContextCRUDService.create(
            ContextCreate(type=ContextType.PROJECT, title="Test")
        )

        updated = await ContextCRUDService.update(created.id, ContextUpdate())

        assert updated is not None
        assert updated.title == created.title

    @pytest.mark.asyncio
    async def test_delete_context(self):
        """Test deleting a context."""
        created = await ContextCRUDService.create(
            ContextCreate(
                type=ContextType.PROJECT,
                title="To Delete",
            )
        )

        result = await ContextCRUDService.delete(created.id)
        assert result is True

        # Verify it's gone
        fetched = await ContextCRUDService.get(created.id)
        assert fetched is None

    @pytest.mark.asyncio
    async def test_delete_nonexistent_context(self):
        """Test deleting a context that doesn't exist."""
        result = await ContextCRUDService.delete("nonexistent-id")
        assert result is False

    @pytest.mark.asyncio
    async def test_add_question_to_context(self):
        """Test adding a question ID to a context."""
        created = await ContextCRUDService.create(
            ContextCreate(
                type=ContextType.FEYNMAN_PROBLEM,
                title="Test Context",
            )
        )

        updated = await ContextCRUDService.add_question(created.id, "q-123")

        assert updated is not None
        assert "q-123" in updated.key_questions

    @pytest.mark.asyncio
    async def test_add_duplicate_question(self):
        """Test that adding the same question twice doesn't create duplicates."""
        created = await ContextCRUDService.create(
            ContextCreate(type=ContextType.FEYNMAN_PROBLEM, title="Test Context")
        )

        # Add question twice
        await ContextCRUDService.add_question(created.id, "q-123")
        updated = await ContextCRUDService.add_question(created.id, "q-123")

        assert updated is not None
        # Count occurrences
        assert updated.key_questions.count("q-123") == 1

    @pytest.mark.asyncio
    async def test_add_question_to_nonexistent_context(self):
        """Test adding a question to a context that doesn't exist."""
        result = await ContextCRUDService.add_question("nonexistent-id", "q-123")
        assert result is None

    @pytest.mark.asyncio
    async def test_context_timestamps(self):
        """Test that created_at and updated_at are properly set."""
        created = await ContextCRUDService.create(
            ContextCreate(type=ContextType.PROJECT, title="Test")
        )

        assert created.created_at is not None
        assert created.updated_at is not None
        assert created.created_at == created.updated_at

        # Update and verify timestamp changes
        import asyncio

        await asyncio.sleep(0.1)  # Small delay to ensure timestamp difference

        updated = await ContextCRUDService.update(
            created.id, ContextUpdate(title="Updated")
        )

        assert updated is not None
        assert updated.updated_at >= created.updated_at

    @pytest.mark.asyncio
    async def test_list_contexts_ordered_by_updated_at(self):
        """Test that contexts are returned in descending order by updated_at."""
        import asyncio

        # Create contexts with small delays
        ctx1 = await ContextCRUDService.create(
            ContextCreate(type=ContextType.PROJECT, title="First")
        )
        await asyncio.sleep(0.1)

        ctx2 = await ContextCRUDService.create(
            ContextCreate(type=ContextType.PROJECT, title="Second")
        )
        await asyncio.sleep(0.1)

        ctx3 = await ContextCRUDService.create(
            ContextCreate(type=ContextType.PROJECT, title="Third")
        )

        contexts = await ContextCRUDService.list(context_type=ContextType.PROJECT)

        # Find our test contexts in the list
        test_contexts = [c for c in contexts if c.id in [ctx1.id, ctx2.id, ctx3.id]]

        # Most recent should be first
        assert len(test_contexts) >= 2
        # Verify ordering (newer contexts first)
        for i in range(len(test_contexts) - 1):
            assert test_contexts[i].updated_at >= test_contexts[i + 1].updated_at
