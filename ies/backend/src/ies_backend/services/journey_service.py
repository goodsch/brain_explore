"""Service for breadcrumb journey storage and retrieval."""

import uuid
from datetime import datetime, timezone
from typing import Any

import os

import anthropic

from ..schemas.journey import (
    BreadcrumbJourney,
    JourneyCreateRequest,
    JourneySynthesisResponse,
    JourneyUpdateRequest,
)
from .neo4j_client import Neo4jClient


class JourneyService:
    """Service for managing exploration journeys in Neo4j."""

    @staticmethod
    async def create_journey(request: JourneyCreateRequest) -> BreadcrumbJourney:
        """Create a new journey.

        Args:
            request: Journey creation request

        Returns:
            Created journey with assigned ID
        """
        journey_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc)

        # Create Journey node
        query = """
        CREATE (j:Journey {
            id: $id,
            user_id: $user_id,
            started_at: $started_at,
            ended_at: $ended_at,
            entry_point_type: $entry_point_type,
            entry_point_reference: $entry_point_reference,
            entry_point_context: $entry_point_context,
            title: $title,
            tags: $tags,
            notes: $notes,
            processed: false,
            created_at: $created_at
        })
        RETURN j
        """

        await Neo4jClient.execute_write(
            query,
            {
                "id": journey_id,
                "user_id": request.user_id,
                "started_at": now.isoformat(),
                "ended_at": None,
                "entry_point_type": request.entry_point.type.value,
                "entry_point_reference": request.entry_point.reference,
                "entry_point_context": request.entry_point.context,
                "title": request.title,
                "tags": request.tags,
                "notes": request.notes,
                "created_at": now.isoformat(),
            },
        )

        # Store path steps
        for i, step in enumerate(request.path):
            await JourneyService._add_step(journey_id, i, step.model_dump())

        # Store marks
        for mark in request.marks:
            await JourneyService._add_mark(journey_id, mark.model_dump())

        # Store thinking partner exchanges
        for exchange in request.thinking_partner_exchanges:
            await JourneyService._add_exchange(journey_id, exchange.model_dump())

        # Return full journey
        return await JourneyService.get_journey(journey_id)

    @staticmethod
    async def _add_step(journey_id: str, order: int, step: dict) -> None:
        """Add a step to a journey."""
        query = """
        MATCH (j:Journey {id: $journey_id})
        CREATE (s:JourneyStep {
            entity_id: $entity_id,
            entity_name: $entity_name,
            timestamp: $timestamp,
            source_passage: $source_passage,
            source_book_id: $source_book_id,
            dwell_time_seconds: $dwell_time_seconds,
            step_order: $order
        })
        CREATE (j)-[:HAS_STEP]->(s)
        """
        await Neo4jClient.execute_write(
            query,
            {
                "journey_id": journey_id,
                "entity_id": step.get("entity_id"),
                "entity_name": step.get("entity_name"),
                "timestamp": step.get("timestamp", datetime.now(timezone.utc)).isoformat()
                if isinstance(step.get("timestamp"), datetime)
                else step.get("timestamp"),
                "source_passage": step.get("source_passage"),
                "source_book_id": step.get("source_book_id"),
                "dwell_time_seconds": step.get("dwell_time_seconds", 0),
                "order": order,
            },
        )

    @staticmethod
    async def _add_mark(journey_id: str, mark: dict) -> None:
        """Add a mark to a journey."""
        query = """
        MATCH (j:Journey {id: $journey_id})
        CREATE (m:JourneyMark {
            type: $type,
            entity_id: $entity_id,
            content: $content,
            timestamp: $timestamp,
            source_location: $source_location
        })
        CREATE (j)-[:HAS_MARK]->(m)
        """
        await Neo4jClient.execute_write(
            query,
            {
                "journey_id": journey_id,
                "type": mark.get("type").value
                if hasattr(mark.get("type"), "value")
                else mark.get("type"),
                "entity_id": mark.get("entity_id"),
                "content": mark.get("content"),
                "timestamp": mark.get("timestamp", datetime.now(timezone.utc)).isoformat()
                if isinstance(mark.get("timestamp"), datetime)
                else mark.get("timestamp"),
                "source_location": mark.get("source_location"),
            },
        )

    @staticmethod
    async def _add_exchange(journey_id: str, exchange: dict) -> None:
        """Add a thinking partner exchange to a journey."""
        query = """
        MATCH (j:Journey {id: $journey_id})
        CREATE (e:ThinkingPartnerExchange {
            question: $question,
            response: $response,
            timestamp: $timestamp,
            entity_context: $entity_context
        })
        CREATE (j)-[:HAS_EXCHANGE]->(e)
        """
        await Neo4jClient.execute_write(
            query,
            {
                "journey_id": journey_id,
                "question": exchange.get("question"),
                "response": exchange.get("response"),
                "timestamp": exchange.get("timestamp", datetime.now(timezone.utc)).isoformat()
                if isinstance(exchange.get("timestamp"), datetime)
                else exchange.get("timestamp"),
                "entity_context": exchange.get("entity_context"),
            },
        )

    @staticmethod
    async def get_journey(journey_id: str) -> BreadcrumbJourney | None:
        """Get a journey by ID with all its components."""
        # Get journey node
        journey_query = """
        MATCH (j:Journey {id: $id})
        RETURN j
        """
        journey_results = await Neo4jClient.execute_query(
            journey_query, {"id": journey_id}
        )

        if not journey_results:
            return None

        j = journey_results[0]["j"]

        # Get steps
        steps_query = """
        MATCH (j:Journey {id: $id})-[:HAS_STEP]->(s:JourneyStep)
        RETURN s
        ORDER BY s.step_order
        """
        steps_results = await Neo4jClient.execute_query(
            steps_query, {"id": journey_id}
        )
        steps = [dict(r["s"]) for r in steps_results]

        # Get marks
        marks_query = """
        MATCH (j:Journey {id: $id})-[:HAS_MARK]->(m:JourneyMark)
        RETURN m
        ORDER BY m.timestamp
        """
        marks_results = await Neo4jClient.execute_query(
            marks_query, {"id": journey_id}
        )
        marks = [dict(r["m"]) for r in marks_results]

        # Get exchanges
        exchanges_query = """
        MATCH (j:Journey {id: $id})-[:HAS_EXCHANGE]->(e:ThinkingPartnerExchange)
        RETURN e
        ORDER BY e.timestamp
        """
        exchanges_results = await Neo4jClient.execute_query(
            exchanges_query, {"id": journey_id}
        )
        exchanges = [dict(r["e"]) for r in exchanges_results]

        # Construct journey
        return BreadcrumbJourney(
            id=j["id"],
            user_id=j["user_id"],
            started_at=j["started_at"],
            ended_at=j.get("ended_at"),
            entry_point={
                "type": j["entry_point_type"],
                "reference": j["entry_point_reference"],
                "context": j.get("entry_point_context"),
            },
            path=steps,
            marks=marks,
            thinking_partner_exchanges=exchanges,
            title=j.get("title"),
            tags=j.get("tags", []),
            notes=j.get("notes"),
            processed=j.get("processed", False),
            siyuan_note_id=j.get("siyuan_note_id"),
        )

    @staticmethod
    async def list_journeys(
        user_id: str, page: int = 1, page_size: int = 20
    ) -> tuple[list[BreadcrumbJourney], int]:
        """List journeys for a user with pagination.

        Returns:
            Tuple of (journeys, total_count)
        """
        # Get total count
        count_query = """
        MATCH (j:Journey {user_id: $user_id})
        RETURN count(j) as total
        """
        count_results = await Neo4jClient.execute_query(
            count_query, {"user_id": user_id}
        )
        total = count_results[0]["total"] if count_results else 0

        # Get paginated journeys
        skip = (page - 1) * page_size
        list_query = """
        MATCH (j:Journey {user_id: $user_id})
        RETURN j.id as id
        ORDER BY j.started_at DESC
        SKIP $skip
        LIMIT $limit
        """
        list_results = await Neo4jClient.execute_query(
            list_query, {"user_id": user_id, "skip": skip, "limit": page_size}
        )

        # Fetch full journeys
        journeys = []
        for r in list_results:
            journey = await JourneyService.get_journey(r["id"])
            if journey:
                journeys.append(journey)

        return journeys, total

    @staticmethod
    async def update_journey(
        journey_id: str, request: JourneyUpdateRequest
    ) -> BreadcrumbJourney | None:
        """Update a journey (append steps, marks, etc.)."""
        # Check journey exists
        existing = await JourneyService.get_journey(journey_id)
        if not existing:
            return None

        # Update journey properties
        updates = []
        params: dict[str, Any] = {"id": journey_id}

        if request.ended_at:
            updates.append("j.ended_at = $ended_at")
            params["ended_at"] = request.ended_at.isoformat()

        if request.title is not None:
            updates.append("j.title = $title")
            params["title"] = request.title

        if request.tags is not None:
            updates.append("j.tags = $tags")
            params["tags"] = request.tags

        if request.notes is not None:
            updates.append("j.notes = $notes")
            params["notes"] = request.notes

        if updates:
            update_query = f"""
            MATCH (j:Journey {{id: $id}})
            SET {", ".join(updates)}
            """
            await Neo4jClient.execute_write(update_query, params)

        # Append new steps
        if request.path:
            # Get current step count
            count_query = """
            MATCH (j:Journey {id: $id})-[:HAS_STEP]->(s:JourneyStep)
            RETURN count(s) as count
            """
            count_result = await Neo4jClient.execute_query(
                count_query, {"id": journey_id}
            )
            current_count = count_result[0]["count"] if count_result else 0

            for i, step in enumerate(request.path):
                await JourneyService._add_step(
                    journey_id, current_count + i, step.model_dump()
                )

        # Append new marks
        if request.marks:
            for mark in request.marks:
                await JourneyService._add_mark(journey_id, mark.model_dump())

        # Append new exchanges
        if request.thinking_partner_exchanges:
            for exchange in request.thinking_partner_exchanges:
                await JourneyService._add_exchange(journey_id, exchange.model_dump())

        return await JourneyService.get_journey(journey_id)

    @staticmethod
    async def delete_journey(journey_id: str) -> bool:
        """Delete a journey and all its components."""
        query = """
        MATCH (j:Journey {id: $id})
        OPTIONAL MATCH (j)-[:HAS_STEP]->(s:JourneyStep)
        OPTIONAL MATCH (j)-[:HAS_MARK]->(m:JourneyMark)
        OPTIONAL MATCH (j)-[:HAS_EXCHANGE]->(e:ThinkingPartnerExchange)
        DETACH DELETE j, s, m, e
        RETURN count(j) as deleted
        """
        result = await Neo4jClient.execute_write(query, {"id": journey_id})
        return result is not None

    @staticmethod
    def _get_anthropic_client() -> anthropic.AsyncAnthropic | None:
        """Get Anthropic client if API key is available."""
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            return None
        return anthropic.AsyncAnthropic(api_key=api_key)

    @staticmethod
    async def generate_synthesis(journey_id: str) -> JourneySynthesisResponse | None:
        """Generate an AI-powered synthesis of the journey's insights.

        Analyzes the exploration path, marks, and thinking partner exchanges
        to produce a coherent narrative of what was discovered.
        """
        journey = await JourneyService.get_journey(journey_id)
        if not journey:
            return None

        # Build journey narrative from steps
        path_summary = []
        for step in journey.path:
            entry = f"- {step.entity_name}"
            if step.dwell_time_seconds > 60:
                entry += f" (explored for {int(step.dwell_time_seconds / 60)} min)"
            if step.source_passage:
                entry += f": \"{step.source_passage[:100]}...\""
            path_summary.append(entry)

        # Gather marks (highlights, annotations)
        marks_summary = []
        for mark in journey.marks:
            marks_summary.append(f"- [{mark.type.value}] {mark.content}")

        # Gather thinking partner exchanges
        exchanges_summary = []
        for exchange in journey.thinking_partner_exchanges:
            q = exchange.question[:100] + "..." if len(exchange.question) > 100 else exchange.question
            exchanges_summary.append(f"- Q: {q}")
            if exchange.response:
                r = exchange.response[:100] + "..." if len(exchange.response) > 100 else exchange.response
                exchanges_summary.append(f"  A: {r}")

        # Construct prompt
        entry_type = journey.entry_point.type.value
        entry_ref = journey.entry_point.reference

        prompt = f"""Analyze this exploration journey and provide insights.

Entry point: Started from {entry_type} - "{entry_ref}"

Exploration path ({len(journey.path)} steps):
{chr(10).join(path_summary) or "No steps recorded"}

Marks made ({len(journey.marks)}):
{chr(10).join(marks_summary) or "No marks"}

Thinking partner exchanges ({len(journey.thinking_partner_exchanges)}):
{chr(10).join(exchanges_summary) or "No exchanges"}

Provide:
1. A 2-3 sentence synthesis of what was discovered
2. 3-5 key insights as bullet points
3. Count of meaningful connections discovered between concepts

Format your response as:
SYNTHESIS: [your synthesis]
INSIGHTS:
- [insight 1]
- [insight 2]
...
CONNECTIONS: [number]"""

        client = JourneyService._get_anthropic_client()
        if not client:
            # Fallback without AI
            return JourneySynthesisResponse(
                synthesis=f"Explored {len(journey.path)} concepts starting from {entry_ref}",
                journey=journey,
                insights=[f"Visited: {', '.join(s.entity_name for s in journey.path[:5])}"],
                connections_discovered=max(0, len(journey.path) - 1),
            )

        try:
            message = await client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=600,
                messages=[{"role": "user", "content": prompt}],
            )
            response_text = message.content[0].text if message and message.content else ""

            # Parse response
            synthesis = ""
            insights = []
            connections = 0

            lines = response_text.split("\n")
            current_section = None
            for line in lines:
                line = line.strip()
                if line.startswith("SYNTHESIS:"):
                    synthesis = line[10:].strip()
                    current_section = "synthesis"
                elif line.startswith("INSIGHTS:"):
                    current_section = "insights"
                elif line.startswith("CONNECTIONS:"):
                    try:
                        connections = int(line[12:].strip())
                    except ValueError:
                        connections = len(journey.path) - 1
                elif current_section == "insights" and line.startswith("-"):
                    insights.append(line[1:].strip())
                elif current_section == "synthesis" and line:
                    synthesis += " " + line

            return JourneySynthesisResponse(
                synthesis=synthesis or f"Explored {len(journey.path)} concepts",
                journey=journey,
                insights=insights or [f"Visited {len(journey.path)} concepts"],
                connections_discovered=connections or max(0, len(journey.path) - 1),
            )

        except Exception:
            # Fallback on error
            return JourneySynthesisResponse(
                synthesis=f"Explored {len(journey.path)} concepts starting from {entry_ref}",
                journey=journey,
                insights=[f"Visited: {', '.join(s.entity_name for s in journey.path[:5])}"],
                connections_discovered=max(0, len(journey.path) - 1),
            )
