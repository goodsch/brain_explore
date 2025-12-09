"""Centralized journey event logging service.

Provides a simple interface for logging events to the journey timeline.
Used by various services (extraction, highlight sync, templates) to track
user activity for pattern analysis.
"""

import logging
import uuid
from datetime import datetime, timezone
from typing import Optional

from ..schemas.context import ContextJourneyEntry, JourneyClassification
from .neo4j_client import Neo4jClient

logger = logging.getLogger(__name__)


class JourneyLogger:
    """Centralized service for logging journey events.

    Provides a consistent way to log various event types to Neo4j
    for timeline visualization and pattern analysis.
    """

    @classmethod
    async def log_event(
        cls,
        context_id: str,
        classification: JourneyClassification,
        text: str,
        focus_id: Optional[str] = None,
        entity_links: Optional[list[str]] = None,
        source_links: Optional[list[str]] = None,
        source_action: Optional[str] = None,
    ) -> Optional[str]:
        """Log a journey event.

        Args:
            context_id: Context this event belongs to
            classification: Type of event (JourneyClassification enum)
            text: Human-readable description of the event
            focus_id: Optional focus (question_id) for this event
            entity_links: Optional list of entity IDs related to this event
            source_links: Optional list of source IDs (book IDs, etc.)
            source_action: Optional identifier for the originating action

        Returns:
            Journey entry ID if successful, None otherwise
        """
        try:
            entry_id = f"je_{uuid.uuid4().hex[:12]}"
            entry = ContextJourneyEntry(
                id=entry_id,
                timestamp=datetime.now(timezone.utc),
                context_id=context_id,
                focus_id=focus_id,
                text=text,
                classifications=[classification],
                entity_links=entity_links or [],
                source_links=source_links or [],
                source_action=source_action,
            )

            query = """
            CREATE (j:ContextJourneyEntry {
                id: $id,
                timestamp: datetime($timestamp),
                context_id: $context_id,
                focus_id: $focus_id,
                text: $text,
                classifications: $classifications,
                entity_links: $entity_links,
                source_links: $source_links,
                source_action: $source_action
            })
            RETURN j.id as id
            """
            await Neo4jClient.execute_query(
                query,
                {
                    "id": entry.id,
                    "timestamp": entry.timestamp.isoformat(),
                    "context_id": entry.context_id,
                    "focus_id": entry.focus_id,
                    "text": entry.text,
                    "classifications": [c.value for c in entry.classifications],
                    "entity_links": entry.entity_links,
                    "source_links": entry.source_links,
                    "source_action": entry.source_action,
                },
            )
            logger.debug(f"Logged journey event: {entry_id} ({classification.value})")
            return entry_id

        except Exception as e:
            logger.error(f"Failed to log journey event: {e}")
            return None

    @classmethod
    async def log_highlight_created(
        cls,
        context_id: str,
        highlight_text: str,
        book_id: str,
        question_id: Optional[str] = None,
    ) -> Optional[str]:
        """Log a highlight creation event.

        Args:
            context_id: Context this highlight belongs to
            highlight_text: The highlighted text (truncated for display)
            book_id: Calibre book ID
            question_id: Optional question this highlight relates to

        Returns:
            Journey entry ID if successful
        """
        # Truncate text for display
        display_text = highlight_text[:100] + "..." if len(highlight_text) > 100 else highlight_text
        return await cls.log_event(
            context_id=context_id,
            classification=JourneyClassification.HIGHLIGHT,
            text=f"Captured highlight: \"{display_text}\"",
            focus_id=question_id,
            source_links=[f"book_calibre_{book_id}"],
            source_action="highlight_sync",
        )

    @classmethod
    async def log_extraction_run(
        cls,
        context_id: str,
        segments_analyzed: int,
        concepts_found: list[str],
        question_id: Optional[str] = None,
    ) -> Optional[str]:
        """Log an extraction run event.

        Args:
            context_id: Context this extraction belongs to
            segments_analyzed: Number of text segments analyzed
            concepts_found: List of concept entity IDs found
            question_id: Optional question that triggered this extraction

        Returns:
            Journey entry ID if successful
        """
        return await cls.log_event(
            context_id=context_id,
            classification=JourneyClassification.EXTRACTION_RUN,
            text=f"Extraction run: {segments_analyzed} segments, {len(concepts_found)} concepts found",
            focus_id=question_id,
            entity_links=concepts_found[:10],  # Limit to first 10
            source_action="extraction_engine",
        )

    @classmethod
    async def log_template_session(
        cls,
        context_id: str,
        template_name: str,
        question_id: Optional[str] = None,
    ) -> Optional[str]:
        """Log a thinking template session start.

        Args:
            context_id: Context for this session
            template_name: Name of the template used
            question_id: Optional question this session explores

        Returns:
            Journey entry ID if successful
        """
        return await cls.log_event(
            context_id=context_id,
            classification=JourneyClassification.TEMPLATE_SESSION,
            text=f"Started thinking session: {template_name}",
            focus_id=question_id,
            source_action="template_service",
        )

    @classmethod
    async def log_note_taken(
        cls,
        context_id: str,
        note_text: str,
        question_id: Optional[str] = None,
        source_book_id: Optional[str] = None,
    ) -> Optional[str]:
        """Log a note creation event.

        Args:
            context_id: Context this note belongs to
            note_text: The note content (truncated for display)
            question_id: Optional question this note relates to
            source_book_id: Optional Calibre book ID if note is from a book

        Returns:
            Journey entry ID if successful
        """
        display_text = note_text[:100] + "..." if len(note_text) > 100 else note_text
        source_links = [f"book_calibre_{source_book_id}"] if source_book_id else []

        return await cls.log_event(
            context_id=context_id,
            classification=JourneyClassification.READING_NOTE,
            text=f"Note: \"{display_text}\"",
            focus_id=question_id,
            source_links=source_links,
            source_action="note_capture",
        )

    @classmethod
    async def log_question_clicked(
        cls,
        context_id: str,
        question_id: str,
        question_text: str,
    ) -> Optional[str]:
        """Log a question selection/click event.

        Args:
            context_id: Context for this question
            question_id: The question ID that was clicked
            question_text: The question text (truncated)

        Returns:
            Journey entry ID if successful
        """
        display_text = question_text[:80] + "..." if len(question_text) > 80 else question_text
        return await cls.log_event(
            context_id=context_id,
            classification=JourneyClassification.QUESTION_CLICK,
            text=f"Explored question: \"{display_text}\"",
            focus_id=question_id,
            source_action="question_navigation",
        )

    @classmethod
    async def log_entity_visit(
        cls,
        context_id: str,
        entity_id: str,
        entity_name: str,
        question_id: Optional[str] = None,
    ) -> Optional[str]:
        """Log an entity exploration event.

        Args:
            context_id: Context for this exploration
            entity_id: The entity that was visited
            entity_name: Human-readable entity name
            question_id: Optional related question

        Returns:
            Journey entry ID if successful
        """
        return await cls.log_event(
            context_id=context_id,
            classification=JourneyClassification.ENTITY_VISIT,
            text=f"Explored entity: {entity_name}",
            focus_id=question_id,
            entity_links=[entity_id],
            source_action="entity_navigation",
        )
