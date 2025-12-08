"""Context + Question Layer service.

Manages contexts, questions, and context-aware operations:
- Parsing Context Notes from SiYuan markdown
- CRUD for contexts and questions
- Context-aware keyword search
- Journey entry logging
"""

import json
import re
import uuid
from datetime import datetime, timezone

from ies_backend.schemas.context import (
    AreaOfExploration,
    Context,
    ContextCreateRequest,
    ContextCreateResponse,
    ContextJourneyEntry,
    ContextListResponse,
    ContextNoteParseRequest,
    ContextNoteParseResponse,
    ContextSearchRequest,
    ContextSearchResponse,
    ContextSearchResult,
    ContextStatus,
    ContextType,
    JourneyClassification,
    JourneyEntryCreateRequest,
    JourneyListResponse,
    Question,
    QuestionCreateRequest,
    QuestionListResponse,
    QuestionStatus,
)
from ies_backend.services.neo4j_client import Neo4jClient


class ContextService:
    """Manage Context + Question layer operations."""

    # ------------------------------------------------------------------
    # Context Note Parsing
    # ------------------------------------------------------------------

    @classmethod
    def parse_context_note(cls, request: ContextNoteParseRequest) -> ContextNoteParseResponse:
        """Parse a SiYuan Context Note into structured data.

        Expected format:
        ```
        # [Type]: Title

        ## Summary / Intent
        Brief description...

        ## Key Questions
        - Question 1?
        - Question 2?

        ## Areas of Exploration
        - Area 1
        - Area 2

        ## Core Concepts
        - Concept 1
        - Concept 2
        ```
        """
        markdown = request.markdown_content
        siyuan_block_id = request.siyuan_block_id

        # Parse title and type from first heading
        title, context_type = cls._parse_title_line(markdown)

        # Parse sections
        sections = cls._parse_sections(markdown)

        # Extract summary
        summary = sections.get("summary / intent", [""])[0] if sections.get("summary / intent") else None

        # Build Context
        context = Context(
            id=f"ctx_{uuid.uuid4().hex[:12]}",
            type=context_type,
            title=title,
            summary=summary,
            status=ContextStatus.ACTIVE,
            siyuan_block_id=siyuan_block_id,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )

        # Build Questions from "Key Questions" section
        questions: list[Question] = []
        for q_text in sections.get("key questions", []):
            if q_text.strip():
                questions.append(
                    Question(
                        id=f"q_{uuid.uuid4().hex[:12]}",
                        context_id=context.id,
                        text=q_text.strip(),
                        status=QuestionStatus.OPEN,
                        created_at=datetime.now(timezone.utc),
                        updated_at=datetime.now(timezone.utc),
                    )
                )

        # Build Areas from "Areas of Exploration" section
        areas: list[AreaOfExploration] = []
        for area_text in sections.get("areas of exploration", []):
            if area_text.strip():
                areas.append(
                    AreaOfExploration(
                        id=f"area_{uuid.uuid4().hex[:12]}",
                        context_id=context.id,
                        title=area_text.strip(),
                        created_at=datetime.now(timezone.utc),
                    )
                )

        # Link question IDs to context
        context.key_questions = [q.id for q in questions]
        context.areas_of_exploration = [a.id for a in areas]
        context.core_concepts = sections.get("core concepts", [])

        return ContextNoteParseResponse(
            context=context,
            questions=questions,
            areas=areas,
            raw_sections=sections,
        )

    @classmethod
    def _parse_title_line(cls, markdown: str) -> tuple[str, ContextType]:
        """Extract title and context type from first heading."""
        lines = markdown.strip().split("\n")
        for line in lines:
            if line.startswith("# "):
                title_line = line[2:].strip()
                # Check for type prefix like "Feynman: ..." or "Project: ..."
                type_map = {
                    "feynman": ContextType.FEYNMAN_PROBLEM,
                    "project": ContextType.PROJECT,
                    "theory": ContextType.THEORY,
                    "concept": ContextType.CONCEPT_CLUSTER,
                    "life": ContextType.LIFE_AREA,
                }
                for prefix, ctx_type in type_map.items():
                    if title_line.lower().startswith(f"{prefix}:"):
                        title = title_line.split(":", 1)[1].strip()
                        return title, ctx_type
                return title_line, ContextType.FEYNMAN_PROBLEM
        return "Untitled Context", ContextType.FEYNMAN_PROBLEM

    @classmethod
    def _parse_sections(cls, markdown: str) -> dict[str, list[str]]:
        """Parse markdown into sections by ## headings."""
        sections: dict[str, list[str]] = {}
        current_section: str | None = None
        current_items: list[str] = []

        for line in markdown.split("\n"):
            if line.startswith("## "):
                # Save previous section
                if current_section:
                    sections[current_section] = current_items
                # Start new section
                current_section = line[3:].strip().lower()
                current_items = []
            elif current_section:
                # Parse list items
                stripped = line.strip()
                if stripped.startswith("- "):
                    current_items.append(stripped[2:].strip())
                elif stripped.startswith("* "):
                    current_items.append(stripped[2:].strip())
                elif stripped and not stripped.startswith("#"):
                    # Paragraph text (for summary)
                    if current_items:
                        current_items[-1] += " " + stripped
                    else:
                        current_items.append(stripped)

        # Save last section
        if current_section:
            sections[current_section] = current_items

        return sections

    # ------------------------------------------------------------------
    # Context CRUD
    # ------------------------------------------------------------------

    @classmethod
    async def create_context(cls, request: ContextCreateRequest) -> ContextCreateResponse:
        """Create a new context."""
        await cls._ensure_schema()

        context = Context(
            id=f"ctx_{uuid.uuid4().hex[:12]}",
            type=request.type,
            title=request.title,
            summary=request.summary,
            status=ContextStatus.ACTIVE,
            siyuan_block_id=request.siyuan_block_id,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )

        await Neo4jClient.execute_write(
            """
            CREATE (c:Context {
                id: $id,
                type: $type,
                title: $title,
                summary: $summary,
                status: $status,
                siyuan_block_id: $siyuan_block_id,
                key_questions: $key_questions,
                core_concepts: $core_concepts,
                areas_of_exploration: $areas_of_exploration,
                created_at: $created_at,
                updated_at: $updated_at
            })
            """,
            {
                "id": context.id,
                "type": context.type.value,
                "title": context.title,
                "summary": context.summary,
                "status": context.status.value,
                "siyuan_block_id": context.siyuan_block_id,
                "key_questions": context.key_questions,
                "core_concepts": context.core_concepts,
                "areas_of_exploration": context.areas_of_exploration,
                "created_at": context.created_at.isoformat(),
                "updated_at": context.updated_at.isoformat(),
            },
        )

        return ContextCreateResponse(context=context, questions_created=0)

    @classmethod
    async def save_parsed_context(cls, parsed: ContextNoteParseResponse) -> Context:
        """Save a parsed context note (context + questions + areas) to Neo4j."""
        await cls._ensure_schema()

        context = parsed.context

        # Save context
        await Neo4jClient.execute_write(
            """
            MERGE (c:Context {id: $id})
            SET c.type = $type,
                c.title = $title,
                c.summary = $summary,
                c.status = $status,
                c.siyuan_block_id = $siyuan_block_id,
                c.key_questions = $key_questions,
                c.core_concepts = $core_concepts,
                c.areas_of_exploration = $areas_of_exploration,
                c.created_at = $created_at,
                c.updated_at = $updated_at
            """,
            {
                "id": context.id,
                "type": context.type.value,
                "title": context.title,
                "summary": context.summary,
                "status": context.status.value,
                "siyuan_block_id": context.siyuan_block_id,
                "key_questions": context.key_questions,
                "core_concepts": context.core_concepts,
                "areas_of_exploration": context.areas_of_exploration,
                "created_at": context.created_at.isoformat(),
                "updated_at": context.updated_at.isoformat(),
            },
        )

        # Save questions
        for question in parsed.questions:
            await Neo4jClient.execute_write(
                """
                MERGE (q:ContextQuestion {id: $id})
                SET q.context_id = $context_id,
                    q.text = $text,
                    q.status = $status,
                    q.created_at = $created_at,
                    q.updated_at = $updated_at
                WITH q
                MATCH (c:Context {id: $context_id})
                MERGE (q)-[:BELONGS_TO]->(c)
                """,
                {
                    "id": question.id,
                    "context_id": question.context_id,
                    "text": question.text,
                    "status": question.status.value,
                    "created_at": question.created_at.isoformat(),
                    "updated_at": question.updated_at.isoformat(),
                },
            )

        # Save areas
        for area in parsed.areas:
            await Neo4jClient.execute_write(
                """
                MERGE (a:ContextArea {id: $id})
                SET a.context_id = $context_id,
                    a.title = $title,
                    a.created_at = $created_at
                WITH a
                MATCH (c:Context {id: $context_id})
                MERGE (a)-[:BELONGS_TO]->(c)
                """,
                {
                    "id": area.id,
                    "context_id": area.context_id,
                    "title": area.title,
                    "created_at": area.created_at.isoformat(),
                },
            )

        return context

    @classmethod
    async def get_context(cls, context_id: str) -> Context | None:
        """Get a context by ID."""
        results = await Neo4jClient.execute_query(
            "MATCH (c:Context {id: $id}) RETURN c",
            {"id": context_id},
        )
        if not results:
            return None
        return cls._record_to_context(results[0])

    @classmethod
    async def list_contexts(cls, status: ContextStatus | None = None) -> ContextListResponse:
        """List all contexts, optionally filtered by status."""
        if status:
            results = await Neo4jClient.execute_query(
                "MATCH (c:Context {status: $status}) RETURN c ORDER BY c.updated_at DESC",
                {"status": status.value},
            )
        else:
            results = await Neo4jClient.execute_query(
                "MATCH (c:Context) RETURN c ORDER BY c.updated_at DESC",
            )

        contexts = [cls._record_to_context(r) for r in (results or [])]
        return ContextListResponse(contexts=contexts, total=len(contexts))

    # ------------------------------------------------------------------
    # Question CRUD
    # ------------------------------------------------------------------

    @classmethod
    async def create_question(cls, request: QuestionCreateRequest) -> Question:
        """Create a new question."""
        await cls._ensure_schema()

        question = Question(
            id=f"q_{uuid.uuid4().hex[:12]}",
            context_id=request.context_id,
            text=request.text,
            parent_question_id=request.parent_question_id,
            status=QuestionStatus.OPEN,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )

        await Neo4jClient.execute_write(
            """
            CREATE (q:ContextQuestion {
                id: $id,
                context_id: $context_id,
                text: $text,
                parent_question_id: $parent_question_id,
                status: $status,
                created_at: $created_at,
                updated_at: $updated_at
            })
            WITH q
            MATCH (c:Context {id: $context_id})
            MERGE (q)-[:BELONGS_TO]->(c)
            """,
            {
                "id": question.id,
                "context_id": question.context_id,
                "text": question.text,
                "parent_question_id": question.parent_question_id,
                "status": question.status.value,
                "created_at": question.created_at.isoformat(),
                "updated_at": question.updated_at.isoformat(),
            },
        )

        # Update context's key_questions list
        await Neo4jClient.execute_write(
            """
            MATCH (c:Context {id: $context_id})
            SET c.key_questions = c.key_questions + $question_id
            """,
            {"context_id": request.context_id, "question_id": question.id},
        )

        return question

    @classmethod
    async def get_questions(cls, context_id: str) -> QuestionListResponse:
        """Get all questions for a context."""
        results = await Neo4jClient.execute_query(
            """
            MATCH (q:ContextQuestion {context_id: $context_id})
            RETURN q ORDER BY q.created_at
            """,
            {"context_id": context_id},
        )

        questions = [cls._record_to_question(r) for r in (results or [])]
        return QuestionListResponse(questions=questions, total=len(questions))

    @classmethod
    async def get_question(cls, question_id: str) -> Question | None:
        """Get a question by ID."""
        results = await Neo4jClient.execute_query(
            "MATCH (q:ContextQuestion {id: $id}) RETURN q",
            {"id": question_id},
        )
        if not results:
            return None
        return cls._record_to_question(results[0])

    # ------------------------------------------------------------------
    # Context-Aware Search
    # ------------------------------------------------------------------

    @classmethod
    async def search_for_context(cls, request: ContextSearchRequest) -> ContextSearchResponse:
        """Perform keyword search within a context/question.

        For MVP: simple keyword search across book segments using
        concepts from the context and question text.
        """
        # Get context and focus (question/area)
        context = await cls.get_context(request.context_id)
        if not context:
            return ContextSearchResponse(results=[], concepts_found=[], suggested_subquestions=[])

        # Build keywords from context + question
        keywords = list(request.keywords) if request.keywords else []

        # Add context's core concepts
        keywords.extend(context.core_concepts)

        # If focusing on a question, add its text as keywords
        if request.focus_id:
            question = await cls.get_question(request.focus_id)
            if question:
                # Extract key terms from question text
                question_words = re.findall(r'\b\w+\b', question.text.lower())
                stop_words = {"what", "how", "why", "is", "the", "a", "an", "in", "of", "to", "and", "or", "for"}
                keywords.extend([w for w in question_words if w not in stop_words and len(w) > 3])

        # Deduplicate
        keywords = list(set(k.lower() for k in keywords if k))

        if not keywords:
            return ContextSearchResponse(results=[], concepts_found=[], suggested_subquestions=[])

        # Search for snippets in book segments using keywords
        results = await cls._keyword_search(keywords)

        # Log journey entry
        journey_entry = await cls.log_journey_entry(
            JourneyEntryCreateRequest(
                context_id=request.context_id,
                focus_id=request.focus_id,
                text=f"Searched for: {', '.join(keywords[:5])}",
                classifications=[JourneyClassification.QUESTION_CLICK],
                source_action="context_search",
            )
        )

        # Find concepts that were found in results
        concepts_found = cls._extract_concepts_from_results(results, context.core_concepts)

        return ContextSearchResponse(
            results=results,
            concepts_found=concepts_found,
            suggested_subquestions=[],  # TODO: AI-generated suggestions
            journey_entry_id=journey_entry.id if journey_entry else None,
        )

    @classmethod
    async def _keyword_search(cls, keywords: list[str], limit: int = 20) -> list[ContextSearchResult]:
        """Search book segments for keywords.

        MVP: Simple text matching against entity descriptions and book segments.
        Uses CONTAINS for robustness instead of regex.
        """
        results: list[ContextSearchResult] = []

        if not keywords:
            return results

        # Search for entities (concepts) that match any keyword
        # Use CONTAINS for each keyword (more robust than regex)
        for keyword in keywords[:5]:  # Limit to first 5 keywords to avoid huge queries
            try:
                entity_results = await Neo4jClient.execute_query(
                    """
                    MATCH (e:Entity)
                    WHERE toLower(e.name) CONTAINS toLower($keyword)
                       OR (e.description IS NOT NULL AND toLower(e.description) CONTAINS toLower($keyword))
                    RETURN e.name as name, e.description as description, e.id as id
                    LIMIT $limit
                    """,
                    {"keyword": keyword, "limit": limit // len(keywords[:5]) + 1},
                )

                for record in entity_results or []:
                    if isinstance(record, dict):
                        name = record.get("name", "")
                        description = record.get("description", "")
                        # Avoid duplicates
                        if not any(r.source_title == name for r in results):
                            results.append(
                                ContextSearchResult(
                                    source_id=record.get("id", name),
                                    source_title=name,
                                    snippet=description[:500] if description else name,
                                    relevance_score=0.8,
                                    concepts_found=[name],
                                )
                            )
            except Exception:
                # Continue with other keywords if one fails
                continue

        # Search for book entities with matching text
        for keyword in keywords[:5]:
            try:
                book_entity_results = await Neo4jClient.execute_query(
                    """
                    MATCH (be:BookEntity)-[:MENTIONED_IN]->(b:Book)
                    WHERE toLower(be.text) CONTAINS toLower($keyword)
                    RETURN be.text as text, be.type as type, b.title as book_title, b.calibre_id as calibre_id
                    LIMIT $limit
                    """,
                    {"keyword": keyword, "limit": limit // len(keywords[:5]) + 1},
                )

                for record in book_entity_results or []:
                    if isinstance(record, dict):
                        text = record.get("text", "")
                        book_title = record.get("book_title", "Unknown")
                        calibre_id = str(record.get("calibre_id", ""))
                        # Avoid duplicates
                        if not any(r.source_id == calibre_id and r.snippet == text[:500] for r in results):
                            results.append(
                                ContextSearchResult(
                                    source_id=calibre_id,
                                    source_title=book_title,
                                    snippet=text[:500] if text else "",
                                    relevance_score=0.7,
                                    concepts_found=[record.get("type", "")],
                                )
                            )
            except Exception:
                continue

        return results[:limit]

    @classmethod
    def _extract_concepts_from_results(
        cls, results: list[ContextSearchResult], core_concepts: list[str]
    ) -> list[str]:
        """Extract which core concepts appear in results."""
        found = set()
        core_lower = {c.lower() for c in core_concepts}

        for result in results:
            for concept in result.concepts_found:
                if concept.lower() in core_lower:
                    found.add(concept)
            # Also check snippet
            snippet_lower = result.snippet.lower()
            for core in core_concepts:
                if core.lower() in snippet_lower:
                    found.add(core)

        return list(found)

    # ------------------------------------------------------------------
    # Journey Logging
    # ------------------------------------------------------------------

    @classmethod
    async def log_journey_entry(cls, request: JourneyEntryCreateRequest) -> ContextJourneyEntry:
        """Log a journey entry."""
        await cls._ensure_schema()

        entry = ContextJourneyEntry(
            id=f"je_{uuid.uuid4().hex[:12]}",
            timestamp=datetime.now(timezone.utc),
            context_id=request.context_id,
            focus_id=request.focus_id,
            text=request.text,
            classifications=request.classifications,
            source_action=request.source_action,
        )

        await Neo4jClient.execute_write(
            """
            CREATE (j:ContextJourneyEntry {
                id: $id,
                timestamp: $timestamp,
                context_id: $context_id,
                focus_id: $focus_id,
                text: $text,
                classifications: $classifications,
                source_action: $source_action
            })
            """,
            {
                "id": entry.id,
                "timestamp": entry.timestamp.isoformat(),
                "context_id": entry.context_id,
                "focus_id": entry.focus_id,
                "text": entry.text,
                "classifications": [c.value for c in entry.classifications],
                "source_action": entry.source_action,
            },
        )

        # Link to context if provided
        if entry.context_id:
            await Neo4jClient.execute_write(
                """
                MATCH (j:ContextJourneyEntry {id: $id})
                MATCH (c:Context {id: $context_id})
                MERGE (j)-[:IN_CONTEXT]->(c)
                """,
                {"id": entry.id, "context_id": entry.context_id},
            )

        return entry

    @classmethod
    async def get_journey_entries(
        cls, context_id: str, focus_id: str | None = None, limit: int = 50
    ) -> JourneyListResponse:
        """Get journey entries for a context, optionally filtered by focus."""
        if focus_id:
            results = await Neo4jClient.execute_query(
                """
                MATCH (j:ContextJourneyEntry {context_id: $context_id, focus_id: $focus_id})
                RETURN j ORDER BY j.timestamp DESC LIMIT $limit
                """,
                {"context_id": context_id, "focus_id": focus_id, "limit": limit},
            )
        else:
            results = await Neo4jClient.execute_query(
                """
                MATCH (j:ContextJourneyEntry {context_id: $context_id})
                RETURN j ORDER BY j.timestamp DESC LIMIT $limit
                """,
                {"context_id": context_id, "limit": limit},
            )

        entries = [cls._record_to_journey_entry(r) for r in (results or [])]
        return JourneyListResponse(entries=entries, total=len(entries))

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @classmethod
    async def _ensure_schema(cls) -> None:
        """Ensure Neo4j schema exists for context layer."""
        constraints = [
            "CREATE CONSTRAINT context_id IF NOT EXISTS FOR (c:Context) REQUIRE c.id IS UNIQUE",
            "CREATE CONSTRAINT question_id IF NOT EXISTS FOR (q:ContextQuestion) REQUIRE q.id IS UNIQUE",
            "CREATE CONSTRAINT area_id IF NOT EXISTS FOR (a:ContextArea) REQUIRE a.id IS UNIQUE",
            "CREATE CONSTRAINT journey_entry_id IF NOT EXISTS FOR (j:ContextJourneyEntry) REQUIRE j.id IS UNIQUE",
            "CREATE INDEX context_status IF NOT EXISTS FOR (c:Context) ON (c.status)",
            "CREATE INDEX question_context IF NOT EXISTS FOR (q:ContextQuestion) ON (q.context_id)",
            "CREATE INDEX journey_context IF NOT EXISTS FOR (j:ContextJourneyEntry) ON (j.context_id)",
        ]
        for query in constraints:
            try:
                await Neo4jClient.execute_write(query)
            except Exception:
                continue

    @classmethod
    def _record_to_context(cls, record: dict) -> Context:
        """Convert Neo4j record to Context."""
        data = record.get("c") if isinstance(record, dict) else record
        if hasattr(data, "__getitem__"):
            data = dict(data)

        return Context(
            id=data.get("id"),
            type=ContextType(data.get("type", "feynman_problem")),
            title=data.get("title", ""),
            summary=data.get("summary"),
            status=ContextStatus(data.get("status", "active")),
            siyuan_block_id=data.get("siyuan_block_id"),
            key_questions=data.get("key_questions", []),
            core_concepts=data.get("core_concepts", []),
            areas_of_exploration=data.get("areas_of_exploration", []),
            created_at=datetime.fromisoformat(data.get("created_at", datetime.now(timezone.utc).isoformat())),
            updated_at=datetime.fromisoformat(data.get("updated_at", datetime.now(timezone.utc).isoformat())),
        )

    @classmethod
    def _record_to_question(cls, record: dict) -> Question:
        """Convert Neo4j record to Question."""
        data = record.get("q") if isinstance(record, dict) else record
        if hasattr(data, "__getitem__"):
            data = dict(data)

        return Question(
            id=data.get("id"),
            context_id=data.get("context_id", ""),
            text=data.get("text", ""),
            parent_question_id=data.get("parent_question_id"),
            status=QuestionStatus(data.get("status", "open")),
            created_at=datetime.fromisoformat(data.get("created_at", datetime.now(timezone.utc).isoformat())),
            updated_at=datetime.fromisoformat(data.get("updated_at", datetime.now(timezone.utc).isoformat())),
        )

    @classmethod
    def _record_to_journey_entry(cls, record: dict) -> ContextJourneyEntry:
        """Convert Neo4j record to ContextJourneyEntry."""
        data = record.get("j") if isinstance(record, dict) else record
        if hasattr(data, "__getitem__"):
            data = dict(data)

        classifications = []
        for c in data.get("classifications", []):
            try:
                classifications.append(JourneyClassification(c))
            except ValueError:
                pass

        return ContextJourneyEntry(
            id=data.get("id"),
            timestamp=datetime.fromisoformat(data.get("timestamp", datetime.now(timezone.utc).isoformat())),
            context_id=data.get("context_id"),
            focus_id=data.get("focus_id"),
            text=data.get("text"),
            classifications=classifications,
            source_action=data.get("source_action"),
        )
