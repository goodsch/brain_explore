"""Question Feedback Service for storing and analyzing question effectiveness."""

import uuid
from datetime import datetime, timezone

from neo4j import AsyncGraphDatabase

from ies_backend.config import settings
from ies_backend.schemas.question_engine import (
    FeedbackType,
    QuestionClass,
    QuestionFeedbackRequest,
    QuestionFeedbackResponse,
)


class FeedbackService:
    """Service for recording and analyzing question feedback.

    Stores feedback in Neo4j with relationships to users, entities, and sessions.
    Enables analysis of which question types lead to insights.
    """

    def __init__(self):
        """Initialize the feedback service with Neo4j connection."""
        self._driver = None

    async def _get_driver(self):
        """Get or create Neo4j driver."""
        if self._driver is None:
            self._driver = AsyncGraphDatabase.driver(
                settings.neo4j_uri,
                auth=(settings.neo4j_user, settings.neo4j_password),
            )
        return self._driver

    async def record_feedback(
        self, request: QuestionFeedbackRequest
    ) -> QuestionFeedbackResponse:
        """Record question feedback in Neo4j.

        Creates a QuestionFeedback node with relationships to:
        - UserProfile (GIVEN_BY)
        - Entity (ABOUT_ENTITY) if entity_id provided
        - Session (IN_SESSION) if session_id provided

        Args:
            request: The feedback request with question and response details

        Returns:
            QuestionFeedbackResponse with generated feedback_id
        """
        driver = await self._get_driver()
        feedback_id = f"fb-{uuid.uuid4().hex[:12]}"
        timestamp = request.timestamp or datetime.now(timezone.utc).isoformat()

        async with driver.session() as session:
            # Create feedback node
            query = """
            CREATE (f:QuestionFeedback {
                id: $feedback_id,
                question_id: $question_id,
                question_text: $question_text,
                question_class: $question_class,
                feedback_type: $feedback_type,
                response_text: $response_text,
                created_at: datetime($timestamp)
            })
            WITH f

            // Link to user profile
            OPTIONAL MATCH (u:UserProfile {user_id: $user_id})
            FOREACH (_ IN CASE WHEN u IS NOT NULL THEN [1] ELSE [] END |
                MERGE (f)-[:GIVEN_BY]->(u)
            )

            // Create UserProfile if doesn't exist
            FOREACH (_ IN CASE WHEN u IS NULL THEN [1] ELSE [] END |
                CREATE (newUser:UserProfile {user_id: $user_id, created_at: datetime()})
                MERGE (f)-[:GIVEN_BY]->(newUser)
            )

            WITH f

            // Link to entity if provided
            OPTIONAL MATCH (e) WHERE elementId(e) = $entity_id OR e.id = $entity_id
            FOREACH (_ IN CASE WHEN e IS NOT NULL AND $entity_id IS NOT NULL THEN [1] ELSE [] END |
                MERGE (f)-[:ABOUT_ENTITY]->(e)
            )

            WITH f

            // Link to session if provided
            OPTIONAL MATCH (s:Session {id: $session_id})
            FOREACH (_ IN CASE WHEN s IS NOT NULL AND $session_id IS NOT NULL THEN [1] ELSE [] END |
                MERGE (f)-[:IN_SESSION]->(s)
            )

            RETURN f.id as feedback_id
            """

            result = await session.run(
                query,
                feedback_id=feedback_id,
                question_id=request.question_id,
                question_text=request.question_text,
                question_class=request.question_class.value if request.question_class else None,
                feedback_type=request.feedback_type.value,
                response_text=request.response_text,
                user_id=request.user_id,
                entity_id=request.entity_id,
                session_id=request.session_id,
                timestamp=timestamp,
            )

            record = await result.single()

            if record:
                return QuestionFeedbackResponse(
                    feedback_id=record["feedback_id"],
                    recorded=True,
                    message="Feedback recorded successfully",
                )

            return QuestionFeedbackResponse(
                feedback_id=feedback_id,
                recorded=True,
                message="Feedback recorded (no relationships created)",
            )

    async def get_feedback_stats(self, user_id: str | None = None) -> dict:
        """Get aggregated feedback statistics.

        Args:
            user_id: Optional filter by user

        Returns:
            Dictionary with feedback counts by type and class
        """
        driver = await self._get_driver()

        async with driver.session() as session:
            query = """
            MATCH (f:QuestionFeedback)
            WHERE $user_id IS NULL OR EXISTS {
                MATCH (f)-[:GIVEN_BY]->(u:UserProfile {user_id: $user_id})
            }
            RETURN
                f.feedback_type as feedback_type,
                f.question_class as question_class,
                count(f) as count
            """

            result = await session.run(query, user_id=user_id)
            records = await result.data()

            # Aggregate by feedback type
            by_type: dict[str, int] = {}
            by_class: dict[str, dict[str, int]] = {}

            for record in records:
                fb_type = record["feedback_type"]
                qc = record["question_class"] or "unknown"
                count = record["count"]

                by_type[fb_type] = by_type.get(fb_type, 0) + count

                if qc not in by_class:
                    by_class[qc] = {}
                by_class[qc][fb_type] = count

            return {
                "total": sum(by_type.values()),
                "by_type": by_type,
                "by_class": by_class,
                "insight_rate": by_type.get("led_to_insight", 0) / max(sum(by_type.values()), 1),
            }

    async def get_effective_question_classes(
        self, min_insight_rate: float = 0.2
    ) -> list[str]:
        """Get question classes that frequently lead to insights.

        Args:
            min_insight_rate: Minimum ratio of insights to total feedback

        Returns:
            List of question class names that meet the threshold
        """
        driver = await self._get_driver()

        async with driver.session() as session:
            query = """
            MATCH (f:QuestionFeedback)
            WHERE f.question_class IS NOT NULL
            WITH f.question_class as qc,
                 count(f) as total,
                 sum(CASE WHEN f.feedback_type = 'led_to_insight' THEN 1 ELSE 0 END) as insights
            WHERE toFloat(insights) / total >= $min_rate
            RETURN qc, total, insights, toFloat(insights) / total as rate
            ORDER BY rate DESC
            """

            result = await session.run(query, min_rate=min_insight_rate)
            records = await result.data()

            return [r["qc"] for r in records]

    async def get_user_effective_classes(
        self, user_id: str, min_sample: int = 5
    ) -> dict[str, float]:
        """Get user-specific question class effectiveness weights.

        Calculates effectiveness based on helpful + insight responses.
        Classes with fewer than min_sample responses are excluded.

        Args:
            user_id: The user to get preferences for
            min_sample: Minimum number of feedback samples required

        Returns:
            Dict mapping question class to effectiveness weight (0.0-1.0)
        """
        driver = await self._get_driver()

        async with driver.session() as session:
            query = """
            MATCH (f:QuestionFeedback)
            WHERE f.user_id = $user_id AND f.question_class IS NOT NULL
            WITH f.question_class as qc,
                 count(f) as total,
                 sum(CASE WHEN f.feedback_type IN ['helpful', 'led_to_insight'] THEN 1 ELSE 0 END) as helpful,
                 sum(CASE WHEN f.feedback_type = 'led_to_insight' THEN 1 ELSE 0 END) as insights
            WHERE total >= $min_sample
            RETURN qc, total, helpful, insights, 
                   toFloat(helpful + insights) / (total * 2) as effectiveness
            ORDER BY effectiveness DESC
            """

            result = await session.run(query, user_id=user_id, min_sample=min_sample)
            records = await result.data()

            return {r["qc"]: r["effectiveness"] for r in records}

    async def close(self):
        """Close the Neo4j driver connection."""
        if self._driver:
            await self._driver.close()
            self._driver = None
