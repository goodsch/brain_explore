"""Service for Quick Inbox processing and Flow inbox queue."""

import json
import os
import re
import uuid
from datetime import datetime, timezone
from typing import Any

from ..schemas.inbox import (
    AutoExtracted,
    DialogueMessage,
    DialogueMessageRequest,
    DialogueResponse,
    DialogueRole,
    DialogueSuggestion,
    ExtractedEntity,
    InboxCreateRequest,
    InboxItem,
    InboxListResponse,
    InboxProcessRequest,
    InboxProcessResponse,
    InboxSource,
    InboxStatus,
    InboxType,
    InboxUpdateRequest,
    PlacementType,
    ResolutionAction,
    ResolveRequest,
    ResolveResponse,
    Spark,
    SuggestedPlacement,
)
from .graph_service import GraphService
from .neo4j_client import Neo4jClient

# Check for Anthropic availability
ANTHROPIC_AVAILABLE = False
try:
    import anthropic

    ANTHROPIC_AVAILABLE = bool(os.getenv("ANTHROPIC_API_KEY"))
except ImportError:
    pass


class InboxService:
    """Service for processing and routing inbox content."""

    @staticmethod
    async def process_inbox(
        request: InboxProcessRequest,
    ) -> InboxProcessResponse:
        """Process inbox content to extract entities and suggest placements.

        Args:
            request: Inbox processing request

        Returns:
            Processed response with entities and placement suggestions
        """
        content = request.content

        # Extract entities (AI-powered if available, otherwise simple extraction)
        if ANTHROPIC_AVAILABLE:
            entities, summary, tags = await InboxService._ai_extract(content)
        else:
            entities = InboxService._simple_extract(content)
            summary = content[:200] + "..." if len(content) > 200 else content
            tags = InboxService._extract_tags(content)

        # Find related concepts in graph and mark entities that match
        related_concepts = []
        for entity in entities:
            graph_matches = await GraphService.search_concepts(entity.name, limit=3)
            # Check if any graph match closely matches this entity
            if graph_matches:
                for match in graph_matches:
                    match_name = match.get("name", "").lower()
                    if match_name == entity.name.lower() or entity.name.lower() in match_name:
                        entity.graph_match = True
                        break
                related_concepts.extend(graph_matches)

        # Generate placement suggestions
        placements = await InboxService._suggest_placements(
            content, entities, related_concepts, request.context
        )

        return InboxProcessResponse(
            extracted_entities=entities,
            suggested_placements=placements,
            summary=summary,
            tags=tags,
        )

    @staticmethod
    async def _ai_extract(
        content: str,
    ) -> tuple[list[ExtractedEntity], str, list[str]]:
        """Use AI to extract entities, summary, and tags."""
        client = anthropic.Anthropic()

        prompt = f"""Analyze this inbox thought/note and extract:
1. Key concepts/entities mentioned (with type: concept, person, theory, framework, practice)
2. A one-sentence summary
3. Relevant tags (3-5 short words)

Content:
{content}

Respond in this exact format:
ENTITIES:
- [name]: [type] ([confidence 0-1])
- [name]: [type] ([confidence 0-1])
...

SUMMARY: [one sentence]

TAGS: [tag1, tag2, tag3, ...]"""

        try:
            response = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=500,
                messages=[{"role": "user", "content": prompt}],
            )

            text = response.content[0].text

            # Parse entities
            entities = []
            entity_section = re.search(r"ENTITIES:\n(.*?)(?=\nSUMMARY:)", text, re.DOTALL)
            if entity_section:
                for line in entity_section.group(1).strip().split("\n"):
                    match = re.match(r"- (.+?): (.+?) \(([0-9.]+)\)", line)
                    if match:
                        entities.append(
                            ExtractedEntity(
                                name=match.group(1).strip(),
                                type=match.group(2).strip().lower(),
                                confidence=float(match.group(3)),
                            )
                        )

            # Parse summary
            summary_match = re.search(r"SUMMARY: (.+?)(?=\nTAGS:|$)", text, re.DOTALL)
            summary = summary_match.group(1).strip() if summary_match else content[:200]

            # Parse tags
            tags_match = re.search(r"TAGS: (.+?)$", text)
            tags = []
            if tags_match:
                tags = [t.strip().lower() for t in tags_match.group(1).split(",")]

            return entities, summary, tags

        except Exception:
            # Fallback to simple extraction
            return (
                InboxService._simple_extract(content),
                content[:200],
                InboxService._extract_tags(content),
            )

    @staticmethod
    def _simple_extract(content: str) -> list[ExtractedEntity]:
        """Simple entity extraction without AI."""
        entities = []

        # Look for capitalized phrases (potential concepts)
        # Match 1-4 consecutive capitalized words
        pattern = r"\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,3})\b"
        matches = re.findall(pattern, content)

        seen = set()
        for match in matches:
            # Skip common words
            if match.lower() in {"the", "this", "that", "just", "about", "with"}:
                continue
            if match not in seen:
                seen.add(match)
                entities.append(
                    ExtractedEntity(
                        name=match,
                        type="concept",
                        confidence=0.5,
                    )
                )

        return entities[:10]  # Limit to 10

    @staticmethod
    def _extract_tags(content: str) -> list[str]:
        """Extract potential tags from content."""
        # Common therapy/psychology concepts to look for
        keywords = [
            "acceptance",
            "grief",
            "shame",
            "trauma",
            "healing",
            "insight",
            "awareness",
            "presence",
            "metabolization",
            "regulation",
            "nervous system",
            "capacity",
            "window",
        ]

        content_lower = content.lower()
        return [kw for kw in keywords if kw in content_lower][:5]

    @staticmethod
    async def _suggest_placements(
        content: str,
        entities: list[ExtractedEntity],
        related_concepts: list[dict],
        context: dict | None,
    ) -> list[SuggestedPlacement]:
        """Generate placement suggestions based on content and context."""
        placements = []

        # If we have context with a current note, suggest appending there
        if context and context.get("current_note_id"):
            placements.append(
                SuggestedPlacement(
                    target_type=PlacementType.NOTE,
                    target_id=context["current_note_id"],
                    target_name="Current Note",
                    confidence=0.7,
                    preview=f"[Append to current note]\n\n{content[:100]}...",
                    rationale="You were viewing this note when capturing",
                )
            )

        # If we have context with a current journey, suggest linking
        if context and context.get("current_journey_id"):
            placements.append(
                SuggestedPlacement(
                    target_type=PlacementType.JOURNEY,
                    target_id=context["current_journey_id"],
                    target_name="Current Journey",
                    confidence=0.6,
                    preview=f"[Link to journey as mark]\n\n{content[:100]}...",
                    rationale="You were on this exploration journey when capturing",
                )
            )

        # Suggest linking to related concepts
        for concept in related_concepts[:3]:
            confidence = 0.5 + (0.2 if concept.get("type") == "concept" else 0.0)
            placements.append(
                SuggestedPlacement(
                    target_type=PlacementType.CONCEPT,
                    target_id=concept.get("name"),
                    target_name=concept.get("name"),
                    confidence=confidence,
                    preview=f"[Link to concept: {concept.get('name')}]\n\n{content[:100]}...",
                    rationale=f"Content mentions or relates to {concept.get('name')}",
                )
            )

        # Always offer creating a new note
        placements.append(
            SuggestedPlacement(
                target_type=PlacementType.NEW_NOTE,
                target_id=None,
                target_name="New Note",
                confidence=0.3,
                preview=f"[Create new note]\n\n{content}",
                rationale="Create a standalone note for this thought",
            )
        )

        # Sort by confidence
        placements.sort(key=lambda p: p.confidence, reverse=True)

        return placements[:5]  # Return top 5

    # =========================================================================
    # Flow Mode Inbox Queue
    # =========================================================================

    @staticmethod
    async def create_inbox(request: InboxCreateRequest) -> InboxItem:
        """Create an inbox queue item and persist to Neo4j."""
        await InboxService._ensure_inbox_schema()

        inbox_id = f"inbox_{uuid.uuid4().hex[:12]}"
        captured_at = datetime.now(timezone.utc)
        auto_extracted = request.auto_extracted or InboxService._auto_extract(request.raw_text)
        spark_payload = request.spark.model_dump(by_alias=True) if request.spark else None

        params = {
            "id": inbox_id,
            "raw_text": request.raw_text,
            "source": request.source.value,
            "captured_at": captured_at.isoformat(),
            "status": InboxStatus.QUEUED.value,
            "context_snippet": request.context_snippet,
            "entities": auto_extracted.entities if auto_extracted else [],
            "topics": auto_extracted.topics if auto_extracted else [],
            "spark": json.dumps(spark_payload) if spark_payload else None,
        }

        create_query = """
        MERGE (c:InboxItem {id: $id})
        SET c.raw_text = $raw_text,
            c.source = $source,
            c.captured_at = $captured_at,
            c.status = $status,
            c.context_snippet = $context_snippet,
            c.entities = $entities,
            c.topics = $topics,
            c.spark = $spark
        """
        await Neo4jClient.execute_write(create_query, params)

        if auto_extracted and auto_extracted.entities:
            rel_query = """
            MATCH (c:InboxItem {id: $id})
            UNWIND $entities AS entity_name
            MERGE (e:Concept {name: entity_name})
            MERGE (c)-[:MENTIONS]->(e)
            """
            await Neo4jClient.execute_write(rel_query, {"id": inbox_id, "entities": auto_extracted.entities})

        return await InboxService.get_inbox(inbox_id)

    @staticmethod
    async def list_inbox(status: InboxStatus | None = None) -> InboxListResponse:
        """List inbox queue items, optionally filtered by status."""
        await InboxService._ensure_inbox_schema()

        list_query = """
        MATCH (c:InboxItem)
        WHERE $status IS NULL OR c.status = $status
        OPTIONAL MATCH (c)-[:MENTIONS]->(e:Concept)
        RETURN c AS inbox, collect(DISTINCT e.name) AS entities
        ORDER BY c.captured_at DESC
        """
        params = {"status": status.value if status else None}
        results = await Neo4jClient.execute_query(list_query, params)
        items: list[InboxItem] = []
        for record in results:
            inbox = InboxService._record_to_inbox(record)
            if inbox:
                items.append(inbox)

        return InboxListResponse(items=items, total=len(items))

    @staticmethod
    async def get_inbox(inbox_id: str) -> InboxItem | None:
        """Get a single inbox item."""
        await InboxService._ensure_inbox_schema()

        query = """
        MATCH (c:InboxItem {id: $id})
        OPTIONAL MATCH (c)-[:MENTIONS]->(e:Concept)
        RETURN c AS inbox, collect(DISTINCT e.name) AS entities
        """
        results = await Neo4jClient.execute_query(query, {"id": inbox_id})
        if not results:
            return None
        return InboxService._record_to_inbox(results[0])

    @staticmethod
    async def update_inbox(inbox_id: str, request: InboxUpdateRequest) -> InboxItem | None:
        """Update inbox status or auto-extracted metadata."""
        await InboxService._ensure_inbox_schema()

        auto = request.auto_extracted
        params = {
            "id": inbox_id,
            "status": request.status.value if request.status else None,
            "entities": auto.entities if auto and auto.entities is not None else None,
            "topics": auto.topics if auto and auto.topics is not None else None,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }

        update_query = """
        MATCH (c:InboxItem {id: $id})
        SET c.status = COALESCE($status, c.status),
            c.entities = CASE WHEN $entities IS NULL THEN c.entities ELSE $entities END,
            c.topics = CASE WHEN $topics IS NULL THEN c.topics ELSE $topics END,
            c.updated_at = $updated_at
        """
        await Neo4jClient.execute_write(update_query, params)

        # Refresh mention relationships if entities provided
        if auto and auto.entities is not None:
            await Neo4jClient.execute_write(
                """
                MATCH (c:InboxItem {id: $id})-[r:MENTIONS]->(e)
                DELETE r
                """,
                {"id": inbox_id},
            )
            if auto.entities:
                await Neo4jClient.execute_write(
                    """
                    MATCH (c:InboxItem {id: $id})
                    UNWIND $entities AS entity_name
                    MERGE (e:Concept {name: entity_name})
                    MERGE (c)-[:MENTIONS]->(e)
                    """,
                    {"id": inbox_id, "entities": auto.entities},
                )

        return await InboxService.get_inbox(inbox_id)

    @staticmethod
    async def delete_inbox(inbox_id: str) -> bool:
        """Delete an inbox item."""
        await InboxService._ensure_inbox_schema()

        query = """
        MATCH (c:InboxItem {id: $id})
        DETACH DELETE c
        RETURN count(c) as deleted
        """
        results = await Neo4jClient.execute_write(query, {"id": inbox_id})
        if not results:
            return False
        deleted = results[0].get("deleted")
        if isinstance(deleted, list):
            # Neo4j driver can return lists for aggregates in mocks
            deleted = deleted[0] if deleted else 0
        return bool(deleted)


    @staticmethod
    async def add_dialogue_message(
        inbox_id: str, request: DialogueMessageRequest
    ) -> DialogueResponse | None:
        """Add a user message and generate AI response with suggestions.

        The AI analyzes the inbox content and conversation to understand context
        and suggest placement options (link to concept, create note, etc.).
        """
        # Get the existing inbox item
        inbox = await InboxService.get_inbox(inbox_id)
        if not inbox:
            return None

        # Create user message
        user_message = DialogueMessage(
            role=DialogueRole.USER,
            content=request.content,
            timestamp=datetime.now(timezone.utc),
        )

        # Generate AI response with suggestions
        assistant_message = await InboxService._generate_dialogue_response(
            inbox, request.content
        )

        # Update inbox with new dialogue messages
        updated_dialogue = inbox.dialogue + [user_message, assistant_message]
        
        # Update in Neo4j
        query = """
        MATCH (c:InboxItem {id: $id})
        SET c.dialogue = $dialogue
        RETURN c
        """
        dialogue_json = json.dumps(
            [msg.model_dump(mode="json", by_alias=True) for msg in updated_dialogue]
        )
        await Neo4jClient.execute_write(
            query, {"id": inbox_id, "dialogue": dialogue_json}
        )

        # Get updated inbox item
        updated_inbox = await InboxService.get_inbox(inbox_id)
        if not updated_inbox:
            return None

        return DialogueResponse(
            user_message=user_message,
            assistant_message=assistant_message,
            inbox_item=updated_inbox,
        )

    @staticmethod
    async def _generate_dialogue_response(
        inbox: InboxItem, user_message: str
    ) -> DialogueMessage:
        """Generate AI response with contextual suggestions."""
        if not ANTHROPIC_AVAILABLE:
            return InboxService._fallback_dialogue_response(inbox, user_message)

        client = anthropic.Anthropic()

        # Build conversation context
        conversation_history = "\n".join(
            f"{msg.role.value}: {msg.content}" for msg in inbox.dialogue
        )

        prompt = f"""You are helping process an inbox capture. Analyze the content and conversation to:
1. Understand what this capture is about
2. Identify relevant concepts/connections in the knowledge graph
3. Suggest clear actions the user can take

Captured content:
{inbox.raw_text}

Context snippet (if any):
{inbox.context_snippet or 'None provided'}

Previous conversation:
{conversation_history if conversation_history else 'This is the start of the conversation'}

User's latest message:
{user_message}

Respond conversationally and helpfully. At the end, provide 2-4 suggestions in this format:
SUGGESTIONS:
- [label]: [action_type] -> [target_name] (confidence: 0.0-1.0)

Action types: link_to_concept, create_note, explore_in_flow, link_to_journey, add_to_existing_note

Example suggestions:
- Link to "Acceptance": link_to_concept -> Acceptance (confidence: 0.85)
- Create new note: create_note -> Acceptance Insights (confidence: 0.7)
- Explore deeper: explore_in_flow -> null (confidence: 0.6)
"""

        try:
            response = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=800,
                messages=[{"role": "user", "content": prompt}],
            )

            text = response.content[0].text

            # Parse suggestions from response
            suggestions = InboxService._parse_suggestions(text)

            # Extract the conversational part (before SUGGESTIONS:)
            content_parts = text.split("SUGGESTIONS:")
            content = content_parts[0].strip()

            return DialogueMessage(
                role=DialogueRole.ASSISTANT,
                content=content,
                timestamp=datetime.now(timezone.utc),
                suggestions=suggestions,
            )

        except Exception:
            return InboxService._fallback_dialogue_response(inbox, user_message)

    @staticmethod
    def _parse_suggestions(text: str) -> list[DialogueSuggestion]:
        """Parse suggestions from AI response text."""
        suggestions = []
        suggestion_section = re.search(r"SUGGESTIONS:\n(.*)", text, re.DOTALL)
        
        if suggestion_section:
            for line in suggestion_section.group(1).strip().split("\n"):
                # Match: - [label]: [action] -> [target] (confidence: X.X)
                match = re.match(
                    r"- (.+?): (\w+) -> (.+?) \(confidence: ([0-9.]+)\)",
                    line.strip()
                )
                if match:
                    target_name = match.group(3).strip()
                    suggestions.append(
                        DialogueSuggestion(
                            label=match.group(1).strip(),
                            action=match.group(2).strip(),
                            target_name=None if target_name.lower() == "null" else target_name,
                            confidence=float(match.group(4)),
                        )
                    )
        
        return suggestions

    @staticmethod
    def _fallback_dialogue_response(
        inbox: InboxItem, user_message: str
    ) -> DialogueMessage:
        """Generate a simple response when AI is unavailable."""
        # Extract entities from auto_extracted if available
        entities = inbox.auto_extracted.entities if inbox.auto_extracted else []
        topics = inbox.auto_extracted.topics if inbox.auto_extracted else []

        suggestions = []
        
        # Suggest linking to extracted entities
        for entity in entities[:2]:
            suggestions.append(
                DialogueSuggestion(
                    label=f"Link to \"{entity}\"",
                    action="link_to_concept",
                    target_name=entity,
                    confidence=0.5,
                )
            )

        # Always offer to create a new note
        suggestions.append(
            DialogueSuggestion(
                label="Create new note",
                action="create_note",
                target_name=f"Note: {inbox.raw_text[:30]}...",
                confidence=0.4,
            )
        )

        content = "I've analyzed your capture. "
        if entities:
            content += f"I found these potential concepts: {', '.join(entities[:3])}. "
        if topics:
            content += f"Topics: {', '.join(topics[:3])}. "
        content += "Here are some options for what to do with it:"

        return DialogueMessage(
            role=DialogueRole.ASSISTANT,
            content=content,
            timestamp=datetime.now(timezone.utc),
            suggestions=suggestions,
        )


    @staticmethod
    async def resolve_inbox(
        inbox_id: str, request: ResolveRequest
    ) -> ResolveResponse | None:
        """Resolve an inbox item by routing to a destination.

        Handles different resolution actions and updates inbox status.
        """
        # Get the inbox item
        inbox = await InboxService.get_inbox(inbox_id)
        if not inbox:
            return None

        action = request.action
        target_id = request.target_id
        target_name = request.target_name

        # Handle each action type
        if action == ResolutionAction.LINK_TO_CONCEPT:
            return await InboxService._resolve_link_to_concept(
                inbox, target_id, target_name
            )

        elif action == ResolutionAction.CREATE_NOTE:
            return await InboxService._resolve_create_note(inbox, target_name)

        elif action == ResolutionAction.ADD_TO_NOTE:
            return await InboxService._resolve_add_to_note(
                inbox, target_id, target_name
            )

        elif action == ResolutionAction.EXPLORE_IN_FLOW:
            return await InboxService._resolve_explore_in_flow(inbox)

        elif action == ResolutionAction.LINK_TO_JOURNEY:
            return await InboxService._resolve_link_to_journey(
                inbox, target_id, target_name
            )

        return ResolveResponse(
            success=False,
            action=action,
            message=f"Unknown action: {action}",
        )

    @staticmethod
    async def _resolve_link_to_concept(
        inbox: InboxItem, concept_id: str | None, concept_name: str | None
    ) -> ResolveResponse:
        """Link inbox item to an existing concept in the knowledge graph."""
        if not concept_id and not concept_name:
            return ResolveResponse(
                success=False,
                action=ResolutionAction.LINK_TO_CONCEPT,
                message="No concept specified",
            )

        # Search for concept if only name provided
        if not concept_id and concept_name:
            matches = await GraphService.search_concepts(concept_name, limit=1)
            if matches:
                concept_id = matches[0].get("id")
                concept_name = matches[0].get("name", concept_name)

        if not concept_id:
            return ResolveResponse(
                success=False,
                action=ResolutionAction.LINK_TO_CONCEPT,
                message=f"Concept '{concept_name}' not found in knowledge graph",
            )

        # Create relationship between inbox content and concept
        query = """
        MATCH (i:InboxItem {id: $inbox_id})
        MATCH (c) WHERE c.id = $concept_id OR c.name = $concept_name
        MERGE (i)-[r:LINKED_TO]->(c)
        SET r.linked_at = datetime(),
            r.raw_text = $raw_text
        SET i.status = $status
        RETURN c.id as concept_id, c.name as concept_name
        """
        results = await Neo4jClient.execute_write(
            query,
            {
                "inbox_id": inbox.id,
                "concept_id": concept_id,
                "concept_name": concept_name,
                "raw_text": inbox.raw_text,
                "status": InboxStatus.INTEGRATED.value,
            },
        )

        if results:
            return ResolveResponse(
                success=True,
                action=ResolutionAction.LINK_TO_CONCEPT,
                message=f"Linked to concept: {concept_name}",
                target_id=concept_id,
                target_name=concept_name,
            )

        return ResolveResponse(
            success=False,
            action=ResolutionAction.LINK_TO_CONCEPT,
            message="Failed to create link",
        )

    @staticmethod
    async def _resolve_create_note(
        inbox: InboxItem, note_title: str | None
    ) -> ResolveResponse:
        """Prepare data for creating a new SiYuan note.

        Note: Actual note creation happens in SiYuan via its API.
        This marks the inbox item as integrated and returns the content.
        """
        title = note_title or f"Inbox: {inbox.raw_text[:40]}..."

        # Build note content from dialogue
        content_parts = [f"# {title}", "", inbox.raw_text]

        if inbox.dialogue:
            content_parts.extend(["", "## Processing Notes", ""])
            for msg in inbox.dialogue:
                role_label = "Me" if msg.role == DialogueRole.USER else "AI"
                content_parts.append(f"**{role_label}:** {msg.content}")

        if inbox.auto_extracted:
            if inbox.auto_extracted.entities:
                content_parts.extend([
                    "", "## Related Concepts",
                    ", ".join(inbox.auto_extracted.entities)
                ])
            if inbox.auto_extracted.topics:
                content_parts.extend([
                    "", "## Topics",
                    ", ".join(inbox.auto_extracted.topics)
                ])

        # Mark as integrated
        await InboxService._update_status(inbox.id, InboxStatus.INTEGRATED)

        return ResolveResponse(
            success=True,
            action=ResolutionAction.CREATE_NOTE,
            message=f"Ready to create note: {title}",
            target_name=title,
            note_id=None,  # SiYuan will create and return the ID
        )

    @staticmethod
    async def _resolve_add_to_note(
        inbox: InboxItem, note_id: str | None, note_name: str | None
    ) -> ResolveResponse:
        """Prepare content to append to an existing note.

        Note: Actual appending happens in SiYuan via its API.
        """
        if not note_id:
            return ResolveResponse(
                success=False,
                action=ResolutionAction.ADD_TO_NOTE,
                message="No note ID specified",
            )

        # Mark as integrated
        await InboxService._update_status(inbox.id, InboxStatus.INTEGRATED)

        return ResolveResponse(
            success=True,
            action=ResolutionAction.ADD_TO_NOTE,
            message=f"Ready to append to: {note_name or note_id}",
            target_id=note_id,
            target_name=note_name,
        )

    @staticmethod
    async def _resolve_explore_in_flow(inbox: InboxItem) -> ResolveResponse:
        """Create a thinking session from the inbox item for FlowMode exploration."""
        # Import here to avoid circular imports
        from .thinking_service import ThinkingService

        try:
            # Start a thinking session from this inbox item
            session = await ThinkingService.start_session(inbox.id)

            # Update inbox status to in_thinking
            await InboxService._update_status(inbox.id, InboxStatus.IN_THINKING)

            return ResolveResponse(
                success=True,
                action=ResolutionAction.EXPLORE_IN_FLOW,
                message="Opened in FlowMode for deeper exploration",
                target_id=session.get("session_id"),
                target_name=inbox.raw_text[:50],
            )

        except Exception as e:
            return ResolveResponse(
                success=False,
                action=ResolutionAction.EXPLORE_IN_FLOW,
                message=f"Failed to start FlowMode session: {str(e)}",
            )

    @staticmethod
    async def _resolve_link_to_journey(
        inbox: InboxItem, journey_id: str | None, journey_name: str | None
    ) -> ResolveResponse:
        """Link inbox item to an existing journey."""
        if not journey_id:
            return ResolveResponse(
                success=False,
                action=ResolutionAction.LINK_TO_JOURNEY,
                message="No journey ID specified",
            )

        # Create relationship between inbox and journey
        query = """
        MATCH (i:InboxItem {id: $inbox_id})
        MATCH (j:Journey {id: $journey_id})
        MERGE (i)-[r:PART_OF]->(j)
        SET r.linked_at = datetime()
        SET i.status = $status
        RETURN j.id as journey_id
        """
        results = await Neo4jClient.execute_write(
            query,
            {
                "inbox_id": inbox.id,
                "journey_id": journey_id,
                "status": InboxStatus.INTEGRATED.value,
            },
        )

        if results:
            return ResolveResponse(
                success=True,
                action=ResolutionAction.LINK_TO_JOURNEY,
                message=f"Linked to journey: {journey_name or journey_id}",
                target_id=journey_id,
                target_name=journey_name,
            )

        return ResolveResponse(
            success=False,
            action=ResolutionAction.LINK_TO_JOURNEY,
            message="Journey not found or link failed",
        )

    @staticmethod
    async def _update_status(inbox_id: str, status: InboxStatus) -> None:
        """Update the status of an inbox item."""
        query = """
        MATCH (i:InboxItem {id: $id})
        SET i.status = $status
        """
        await Neo4jClient.execute_write(
            query, {"id": inbox_id, "status": status.value}
        )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    async def _ensure_inbox_schema() -> None:
        """Ensure constraints/indexes for inbox nodes."""
        constraints = [
            "CREATE CONSTRAINT inbox_id IF NOT EXISTS FOR (c:InboxItem) REQUIRE c.id IS UNIQUE",
            "CREATE INDEX inbox_status IF NOT EXISTS FOR (c:InboxItem) ON (c.status)",
            "CREATE INDEX inbox_captured_at IF NOT EXISTS FOR (c:InboxItem) ON (c.captured_at)",
        ]
        for query in constraints:
            try:
                await Neo4jClient.execute_write(query)
            except Exception:
                continue

    @staticmethod
    def _auto_extract(raw_text: str) -> AutoExtracted:
        """Lightweight auto extraction when LLM not explicitly provided."""
        entities = [entity.name for entity in InboxService._simple_extract(raw_text)]
        topics = InboxService._extract_tags(raw_text)
        return AutoExtracted(entities=entities, topics=topics)

    @staticmethod
    def _record_to_inbox(record: dict) -> InboxItem | None:
        """Convert Neo4j record to InboxItem."""
        node = record.get("inbox") or record.get("c")
        if node is None:
            return None

        data = dict(node)
        status_value = data.get("status", InboxStatus.QUEUED.value)
        try:
            status = InboxStatus(status_value)
        except ValueError:
            status = InboxStatus.QUEUED

        captured_at_raw = data.get("captured_at") or data.get("capturedAt")
        captured_at = InboxService._parse_datetime(captured_at_raw)

        entities = record.get("entities") or data.get("entities") or []
        topics = record.get("topics") or data.get("topics") or []

        spark = None
        spark_raw = data.get("spark")
        if spark_raw:
            try:
                spark_payload = spark_raw if isinstance(spark_raw, dict) else json.loads(str(spark_raw))
                spark = Spark.model_validate(spark_payload)
            except Exception:
                spark = None

        auto = None
        if entities or topics:
            auto = AutoExtracted(entities=list(entities), topics=list(topics))

        # Parse dialogue from JSON
        dialogue: list[DialogueMessage] = []
        dialogue_raw = data.get("dialogue")
        if dialogue_raw:
            try:
                dialogue_data = dialogue_raw if isinstance(dialogue_raw, list) else json.loads(str(dialogue_raw))
                dialogue = [DialogueMessage.model_validate(msg) for msg in dialogue_data]
            except Exception:
                dialogue = []

        return InboxItem(
            id=data.get("id", ""),
            raw_text=data.get("raw_text") or data.get("rawText", ""),
            source=data.get("source", InboxSource.ASSISTANT_INTERRUPTION.value),
            captured_at=captured_at,
            status=status,
            context_snippet=data.get("context_snippet"),
            auto_extracted=auto,
            spark=spark,
            dialogue=dialogue,
        )

    @staticmethod
    def _parse_datetime(value: Any) -> datetime:
        """Parse ISO datetime strings safely."""
        if isinstance(value, datetime):
            return value
        if isinstance(value, str):
            try:
                return datetime.fromisoformat(value.replace("Z", "+00:00"))
            except ValueError:
                pass
        return datetime.now(timezone.utc)
