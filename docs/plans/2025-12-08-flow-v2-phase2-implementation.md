# Flow v2 Phase 2 — Context & Question API Integration

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build backend persistence for Contexts and Questions, enable SiYuan sync, and connect to the IES Reader.

**Background:** Phase 1 built the frontend infrastructure (useFlowLayout hook, question state in Zustand, QuestionSelector component, FlowPage standalone, FlowPanel integration). Phase 2 connects this to the backend and SiYuan.

**Architecture Source:** `redux/` folder contains the full Context + Question Layer spec:
- `redux/docs/IES_Context_and_Question_Layer.md` — Data model
- `redux/docs/IES_Flow_Reader_Journey_v2.md` — UI/UX behavior
- `redux/docs/IES_Integration_Checklist.md` — Implementation tasks

---

## Phase 2 Scope

Phase 2 focuses on **backend schemas + CRUD APIs** for Context and Question, plus basic SiYuan integration. Advanced features (Extraction Engine, Journey trace, Answer synthesis) are Phase 3+.

**What Phase 2 delivers:**
1. Backend schemas for `Context`, `Question`, `AnswerBlock`
2. REST APIs for CRUD operations
3. SiYuan plugin can read/write questions
4. IES Reader syncs questions with backend
5. Basic journey logging for question events

**What Phase 2 defers:**
- Extraction Engine integration (context-aware extraction)
- AI-generated subquestions
- Context Note parsing from SiYuan markdown
- Question/Journey Reader mode
- Dynamic source acquisition

---

## Data Model (from redux/docs/IES_Context_and_Question_Layer.md)

### Context

```python
class Context(BaseModel):
    id: str  # UUID
    type: Literal["feynman_problem", "project", "theory", "concept_cluster", "life_area"]
    title: str
    parent_context_id: str | None = None
    status: Literal["idea", "active", "paused", "archived"] = "active"

    key_questions: list[str] = []  # Question IDs
    core_concepts: list[str] = []  # Concept IDs in KG
    linked_sources: list[str] = []  # Source IDs
    artifacts: list[str] = []  # Note IDs, diagrams, etc.

    siyuan_doc_id: str | None = None  # Link to SiYuan Context Note

    created_at: datetime
    updated_at: datetime
```

### Question

```python
class Question(BaseModel):
    id: str  # UUID
    context_id: str
    parent_question_id: str | None = None  # For subquestions

    text: str  # The question itself
    status: Literal["open", "partial", "answered", "modeled"] = "open"
    source: Literal["siyuan", "reader", "ai-suggested", "dialogue"] = "reader"

    prerequisite_questions: list[str] = []  # Question IDs
    related_concepts: list[str] = []  # Concept IDs in KG
    linked_sources: list[str] = []  # Source IDs

    siyuan_block_id: str | None = None  # Link to SiYuan block

    created_at: datetime
    updated_at: datetime
```

### AnswerBlock

```python
class AnswerBlock(BaseModel):
    id: str
    question_id: str
    content: str  # Markdown
    quality: Literal["draft", "good_enough", "polished"] = "draft"

    created_at: datetime
    updated_at: datetime
```

---

## Task 1: Create Backend Schemas

**Files:**
- Create: `ies/backend/src/ies_backend/schemas/context.py`
- Create: `ies/backend/src/ies_backend/schemas/question.py`

**Step 1: Create context schema**

```python
# ies/backend/src/ies_backend/schemas/context.py
"""Context schemas for the Context + Question layer."""

from datetime import datetime
from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field


class ContextType(str, Enum):
    """Types of contexts."""
    FEYNMAN_PROBLEM = "feynman_problem"
    PROJECT = "project"
    THEORY = "theory"
    CONCEPT_CLUSTER = "concept_cluster"
    LIFE_AREA = "life_area"


class ContextStatus(str, Enum):
    """Context lifecycle status."""
    IDEA = "idea"
    ACTIVE = "active"
    PAUSED = "paused"
    ARCHIVED = "archived"


class ContextBase(BaseModel):
    """Base context fields for creation."""
    type: ContextType
    title: str = Field(..., min_length=1, max_length=500)
    parent_context_id: str | None = None
    status: ContextStatus = ContextStatus.ACTIVE
    siyuan_doc_id: str | None = None


class ContextCreate(ContextBase):
    """Schema for creating a context."""
    pass


class ContextUpdate(BaseModel):
    """Schema for updating a context."""
    type: ContextType | None = None
    title: str | None = Field(None, min_length=1, max_length=500)
    status: ContextStatus | None = None
    key_questions: list[str] | None = None
    core_concepts: list[str] | None = None
    linked_sources: list[str] | None = None
    artifacts: list[str] | None = None
    siyuan_doc_id: str | None = None


class Context(ContextBase):
    """Full context with all fields."""
    id: str
    key_questions: list[str] = []
    core_concepts: list[str] = []
    linked_sources: list[str] = []
    artifacts: list[str] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
```

**Step 2: Create question schema**

```python
# ies/backend/src/ies_backend/schemas/question.py
"""Question schemas for the Context + Question layer."""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class QuestionStatus(str, Enum):
    """Question resolution status."""
    OPEN = "open"
    PARTIAL = "partial"
    ANSWERED = "answered"
    MODELED = "modeled"


class QuestionSource(str, Enum):
    """Where the question originated."""
    SIYUAN = "siyuan"
    READER = "reader"
    AI_SUGGESTED = "ai-suggested"
    DIALOGUE = "dialogue"


class QuestionBase(BaseModel):
    """Base question fields."""
    context_id: str
    text: str = Field(..., min_length=1, max_length=2000)
    parent_question_id: str | None = None
    status: QuestionStatus = QuestionStatus.OPEN
    source: QuestionSource = QuestionSource.READER
    siyuan_block_id: str | None = None


class QuestionCreate(QuestionBase):
    """Schema for creating a question."""
    pass


class QuestionUpdate(BaseModel):
    """Schema for updating a question."""
    text: str | None = Field(None, min_length=1, max_length=2000)
    status: QuestionStatus | None = None
    parent_question_id: str | None = None
    prerequisite_questions: list[str] | None = None
    related_concepts: list[str] | None = None
    linked_sources: list[str] | None = None
    siyuan_block_id: str | None = None


class Question(QuestionBase):
    """Full question with all fields."""
    id: str
    prerequisite_questions: list[str] = []
    related_concepts: list[str] = []
    linked_sources: list[str] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AnswerBlockBase(BaseModel):
    """Base answer block fields."""
    question_id: str
    content: str = Field(..., min_length=1)
    quality: str = "draft"  # draft, good_enough, polished


class AnswerBlockCreate(AnswerBlockBase):
    """Schema for creating an answer block."""
    pass


class AnswerBlock(AnswerBlockBase):
    """Full answer block."""
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
```

**Step 3: Commit**

```bash
git add ies/backend/src/ies_backend/schemas/context.py ies/backend/src/ies_backend/schemas/question.py
git commit -m "feat(backend): add Context and Question schemas for Flow v2"
```

---

## Task 2: Create Context Service

**Files:**
- Create: `ies/backend/src/ies_backend/services/context_service.py`
- Test: `ies/backend/tests/services/test_context_service.py`

**Step 1: Write failing test**

```python
# ies/backend/tests/services/test_context_service.py
"""Tests for context service."""

import pytest
from ies_backend.schemas.context import ContextCreate, ContextType, ContextStatus
from ies_backend.services.context_service import ContextService


@pytest.fixture
def context_service():
    return ContextService()


class TestContextService:
    async def test_create_context(self, context_service):
        context_data = ContextCreate(
            type=ContextType.FEYNMAN_PROBLEM,
            title="What is ADHD time perception?",
        )
        context = await context_service.create(context_data)

        assert context.id is not None
        assert context.title == "What is ADHD time perception?"
        assert context.type == ContextType.FEYNMAN_PROBLEM
        assert context.status == ContextStatus.ACTIVE

    async def test_get_context(self, context_service):
        context_data = ContextCreate(
            type=ContextType.PROJECT,
            title="IES Flow Mode v2",
        )
        created = await context_service.create(context_data)
        fetched = await context_service.get(created.id)

        assert fetched is not None
        assert fetched.id == created.id
        assert fetched.title == "IES Flow Mode v2"

    async def test_list_contexts(self, context_service):
        # Create multiple contexts
        await context_service.create(ContextCreate(type=ContextType.PROJECT, title="Project 1"))
        await context_service.create(ContextCreate(type=ContextType.THEORY, title="Theory 1"))

        contexts = await context_service.list()
        assert len(contexts) >= 2

    async def test_list_contexts_by_type(self, context_service):
        await context_service.create(ContextCreate(type=ContextType.PROJECT, title="Project A"))
        await context_service.create(ContextCreate(type=ContextType.THEORY, title="Theory A"))

        projects = await context_service.list(context_type=ContextType.PROJECT)
        assert all(c.type == ContextType.PROJECT for c in projects)
```

**Step 2: Implement service**

```python
# ies/backend/src/ies_backend/services/context_service.py
"""Context service for CRUD operations."""

import uuid
from datetime import datetime

from ies_backend.schemas.context import (
    Context,
    ContextCreate,
    ContextStatus,
    ContextType,
    ContextUpdate,
)


class ContextService:
    """Service for managing contexts."""

    def __init__(self):
        # In-memory store for MVP; replace with Neo4j/DB later
        self._contexts: dict[str, Context] = {}

    async def create(self, data: ContextCreate) -> Context:
        """Create a new context."""
        context_id = str(uuid.uuid4())
        now = datetime.utcnow()

        context = Context(
            id=context_id,
            type=data.type,
            title=data.title,
            parent_context_id=data.parent_context_id,
            status=data.status,
            siyuan_doc_id=data.siyuan_doc_id,
            key_questions=[],
            core_concepts=[],
            linked_sources=[],
            artifacts=[],
            created_at=now,
            updated_at=now,
        )

        self._contexts[context_id] = context
        return context

    async def get(self, context_id: str) -> Context | None:
        """Get a context by ID."""
        return self._contexts.get(context_id)

    async def list(
        self,
        context_type: ContextType | None = None,
        status: ContextStatus | None = None,
        limit: int = 100,
    ) -> list[Context]:
        """List contexts with optional filters."""
        contexts = list(self._contexts.values())

        if context_type:
            contexts = [c for c in contexts if c.type == context_type]
        if status:
            contexts = [c for c in contexts if c.status == status]

        # Sort by updated_at descending
        contexts.sort(key=lambda c: c.updated_at, reverse=True)
        return contexts[:limit]

    async def update(self, context_id: str, data: ContextUpdate) -> Context | None:
        """Update a context."""
        context = self._contexts.get(context_id)
        if not context:
            return None

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(context, field, value)

        context.updated_at = datetime.utcnow()
        self._contexts[context_id] = context
        return context

    async def delete(self, context_id: str) -> bool:
        """Delete a context."""
        if context_id in self._contexts:
            del self._contexts[context_id]
            return True
        return False

    async def add_question(self, context_id: str, question_id: str) -> Context | None:
        """Add a question to a context."""
        context = self._contexts.get(context_id)
        if not context:
            return None

        if question_id not in context.key_questions:
            context.key_questions.append(question_id)
            context.updated_at = datetime.utcnow()

        return context
```

**Step 3: Run tests and commit**

```bash
cd ies/backend
uv run pytest tests/services/test_context_service.py -v
git add .
git commit -m "feat(backend): add ContextService with CRUD operations"
```

---

## Task 3: Create Question Service

**Files:**
- Create: `ies/backend/src/ies_backend/services/question_service.py`
- Test: `ies/backend/tests/services/test_question_service.py`

**Step 1: Write failing test**

```python
# ies/backend/tests/services/test_question_service.py
"""Tests for question service."""

import pytest
from ies_backend.schemas.question import QuestionCreate, QuestionSource, QuestionStatus
from ies_backend.services.question_service import QuestionService


@pytest.fixture
def question_service():
    return QuestionService()


class TestQuestionService:
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

    async def test_list_questions_by_context(self, question_service):
        # Create questions for different contexts
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

    async def test_update_question_status(self, question_service):
        question = await question_service.create(QuestionCreate(
            context_id="ctx-1",
            text="Test question",
        ))

        from ies_backend.schemas.question import QuestionUpdate
        updated = await question_service.update(
            question.id,
            QuestionUpdate(status=QuestionStatus.ANSWERED)
        )

        assert updated.status == QuestionStatus.ANSWERED

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
```

**Step 2: Implement service** (similar pattern to ContextService)

**Step 3: Run tests and commit**

---

## Task 4: Create REST API Endpoints

**Files:**
- Create: `ies/backend/src/ies_backend/api/contexts.py`
- Create: `ies/backend/src/ies_backend/api/questions.py`
- Modify: `ies/backend/src/ies_backend/main.py`

**Step 1: Create contexts API**

```python
# ies/backend/src/ies_backend/api/contexts.py
"""Context API endpoints."""

from fastapi import APIRouter, HTTPException, Query

from ies_backend.schemas.context import (
    Context,
    ContextCreate,
    ContextStatus,
    ContextType,
    ContextUpdate,
)
from ies_backend.services.context_service import ContextService

router = APIRouter()
context_service = ContextService()


@router.post("/", response_model=Context)
async def create_context(data: ContextCreate) -> Context:
    """Create a new context."""
    return await context_service.create(data)


@router.get("/", response_model=list[Context])
async def list_contexts(
    type: ContextType | None = Query(None),
    status: ContextStatus | None = Query(None),
    limit: int = Query(100, ge=1, le=500),
) -> list[Context]:
    """List contexts with optional filters."""
    return await context_service.list(context_type=type, status=status, limit=limit)


@router.get("/{context_id}", response_model=Context)
async def get_context(context_id: str) -> Context:
    """Get a context by ID."""
    context = await context_service.get(context_id)
    if not context:
        raise HTTPException(status_code=404, detail="Context not found")
    return context


@router.patch("/{context_id}", response_model=Context)
async def update_context(context_id: str, data: ContextUpdate) -> Context:
    """Update a context."""
    context = await context_service.update(context_id, data)
    if not context:
        raise HTTPException(status_code=404, detail="Context not found")
    return context


@router.delete("/{context_id}")
async def delete_context(context_id: str) -> dict:
    """Delete a context."""
    deleted = await context_service.delete(context_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Context not found")
    return {"deleted": True}
```

**Step 2: Create questions API** (similar pattern)

**Step 3: Register routers in main.py**

```python
# Add to ies/backend/src/ies_backend/main.py
from ies_backend.api import contexts, questions

app.include_router(contexts.router, prefix="/contexts", tags=["contexts"])
app.include_router(questions.router, prefix="/questions", tags=["questions"])
```

**Step 4: Run tests and commit**

---

## Task 5: Connect IES Reader to Backend

**Files:**
- Modify: `.worktrees/ies-reader/ies/reader/src/store/flowStore.ts`
- Create: `.worktrees/ies-reader/ies/reader/src/services/questionApi.ts`

**Step 1: Create API service**

```typescript
// src/services/questionApi.ts
const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8081';

export interface Question {
  id: string;
  context_id: string;
  text: string;
  status: 'open' | 'partial' | 'answered' | 'modeled';
  source: 'siyuan' | 'reader' | 'ai-suggested' | 'dialogue';
  parent_question_id?: string;
  siyuan_block_id?: string;
  created_at: string;
  updated_at: string;
}

export interface QuestionCreate {
  context_id: string;
  text: string;
  source?: 'reader';
}

export const questionApi = {
  async list(contextId?: string): Promise<Question[]> {
    const url = contextId
      ? `${API_BASE}/questions/?context_id=${contextId}`
      : `${API_BASE}/questions/`;
    const res = await fetch(url);
    if (!res.ok) throw new Error('Failed to fetch questions');
    return res.json();
  },

  async create(data: QuestionCreate): Promise<Question> {
    const res = await fetch(`${API_BASE}/questions/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    if (!res.ok) throw new Error('Failed to create question');
    return res.json();
  },

  async update(id: string, data: Partial<Question>): Promise<Question> {
    const res = await fetch(`${API_BASE}/questions/${id}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    if (!res.ok) throw new Error('Failed to update question');
    return res.json();
  },

  async delete(id: string): Promise<void> {
    const res = await fetch(`${API_BASE}/questions/${id}`, { method: 'DELETE' });
    if (!res.ok) throw new Error('Failed to delete question');
  },
};
```

**Step 2: Update flowStore to sync with backend**

Add async actions that call the API and update local state.

**Step 3: Test and commit**

---

## Task 6: Basic SiYuan Sync

**Files:**
- Modify: `.worktrees/siyuan/ies/plugin/src/api/questions.ts`

**Step 1: Create SiYuan plugin API client**

Mirror the Reader's `questionApi.ts` for the SiYuan plugin, enabling:
- Fetch questions from backend
- Create questions from SiYuan (with `source: 'siyuan'` and `siyuan_block_id`)
- Sync status changes

**Step 2: Wire into plugin UI**

Add question list/create UI to the SiYuan plugin's Flow panel.

---

## Summary

**Phase 2 delivers:**
1. ✅ Backend schemas: `Context`, `Question`, `AnswerBlock`
2. ✅ Services: `ContextService`, `QuestionService` with CRUD
3. ✅ REST APIs: `/contexts/*`, `/questions/*`
4. ✅ IES Reader integration: sync questions with backend
5. ✅ Basic SiYuan sync: read/write questions

**Total: 6 tasks**

**Next Phase (3):** Extraction Engine integration, Journey logging, AI subquestions, Context Note parsing
