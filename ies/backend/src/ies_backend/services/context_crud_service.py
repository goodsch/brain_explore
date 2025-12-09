"""Context CRUD service with simplified interface.

This service provides a clean CRUD interface for context operations,
using in-memory storage for MVP (to be replaced with Neo4j later).
"""

import uuid
from datetime import datetime

from ies_backend.schemas.context import (
    Context,
    ContextCreate,
    ContextStatus,
    ContextType,
    ContextUpdate,
)


class ContextCRUDService:
    """Service for managing contexts with simplified CRUD operations.

    Uses in-memory storage for MVP; replace with Neo4j/DB later.
    """

    # In-memory store (shared across all instances)
    _contexts: dict[str, Context] = {}

    @classmethod
    async def create(cls, data: ContextCreate) -> Context:
        """Create a new context."""
        context_id = f"ctx_{uuid.uuid4().hex[:12]}"
        now = datetime.utcnow()

        context = Context(
            id=context_id,
            type=data.type,
            title=data.title,
            summary=data.summary,
            parent_context_id=data.parent_context_id,
            status=data.status,
            siyuan_block_id=data.siyuan_doc_id,
            key_questions=[],
            core_concepts=[],
            linked_sources=[],
            areas_of_exploration=[],
            created_at=now,
            updated_at=now,
        )

        cls._contexts[context_id] = context
        return context

    @classmethod
    async def get(cls, context_id: str) -> Context | None:
        """Get a context by ID."""
        return cls._contexts.get(context_id)

    @classmethod
    async def list(
        cls,
        context_type: ContextType | None = None,
        status: ContextStatus | None = None,
        limit: int = 100,
    ) -> list[Context]:
        """List contexts with optional filters."""
        contexts = list(cls._contexts.values())

        if context_type:
            contexts = [c for c in contexts if c.type == context_type]

        if status:
            contexts = [c for c in contexts if c.status == status]

        # Sort by updated_at descending
        contexts.sort(key=lambda c: c.updated_at, reverse=True)

        return contexts[:limit]

    @classmethod
    async def update(cls, context_id: str, data: ContextUpdate) -> Context | None:
        """Update a context."""
        context = cls._contexts.get(context_id)
        if not context:
            return None

        update_data = data.model_dump(exclude_unset=True)
        if not update_data:
            return context

        # Apply updates
        for field, value in update_data.items():
            if value is not None:
                setattr(context, field, value)

        context.updated_at = datetime.utcnow()
        cls._contexts[context_id] = context

        return context

    @classmethod
    async def delete(cls, context_id: str) -> bool:
        """Delete a context."""
        if context_id in cls._contexts:
            del cls._contexts[context_id]
            return True
        return False

    @classmethod
    async def add_question(cls, context_id: str, question_id: str) -> Context | None:
        """Add a question to a context."""
        context = cls._contexts.get(context_id)
        if not context:
            return None

        if question_id not in context.key_questions:
            context.key_questions.append(question_id)
            context.updated_at = datetime.utcnow()
            cls._contexts[context_id] = context

        return context

    @classmethod
    def clear_store(cls) -> None:
        """Clear in-memory store (for testing)."""
        cls._contexts.clear()
