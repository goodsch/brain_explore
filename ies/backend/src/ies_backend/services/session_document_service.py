"""Session document service - creates structured session documents in SiYuan."""

from datetime import datetime, timezone

from ies_backend.schemas.entity import ExtractionResult, ExtractedEntity
from ies_backend.services.siyuan_client import SiYuanClient


class SessionDocumentService:
    """Service for creating session documents in SiYuan."""

    # Default notebook for sessions (IES notebook in SiYuan)
    DEFAULT_NOTEBOOK = "20251201113102-ctr4bco"

    def __init__(self, notebook_id: str | None = None):
        """Initialize with optional notebook override."""
        self.notebook_id = notebook_id or self.DEFAULT_NOTEBOOK

    async def create_session_document(
        self,
        user_id: str,
        extraction: ExtractionResult,
        session_title: str | None = None,
        session_date: str | None = None,
    ) -> str:
        """Create a session document in SiYuan.

        Args:
            user_id: User ID
            extraction: Extraction result with entities and summary
            session_title: Optional title (defaults to date-based)
            session_date: Optional date string (defaults to now)

        Returns:
            Document ID
        """
        date = session_date or datetime.now(timezone.utc).strftime("%Y-%m-%d")
        title = session_title or f"Session {date}"
        path = f"/Sessions/{user_id}/{date}-{title.replace(' ', '-').lower()}"

        markdown = self._render_session_document(
            title=title,
            date=date,
            extraction=extraction,
        )

        result = await SiYuanClient.create_doc(
            self.notebook_id,
            path,
            markdown,
        )

        # SiYuan returns the doc ID directly as a string
        return result if isinstance(result, str) else result.get("id", "")

    def _render_session_document(
        self,
        title: str,
        date: str,
        extraction: ExtractionResult,
    ) -> str:
        """Render session document as markdown."""
        lines = [
            f"# {title}",
            "",
            f"*Date: {date}*",
            "",
        ]

        # Key Insights
        if extraction.session_summary.key_insights:
            lines.extend([
                "## Key Insights",
                "",
            ])
            for insight in extraction.session_summary.key_insights:
                lines.append(f"- {insight}")
            lines.append("")

        # Entities Discussed
        if extraction.entities:
            lines.extend([
                "## Entities Discussed",
                "",
            ])
            for entity in extraction.entities:
                lines.extend(self._render_entity_section(entity))
            lines.append("")

        # Open Questions
        if extraction.session_summary.open_questions:
            lines.extend([
                "## Open Questions",
                "",
            ])
            for question in extraction.session_summary.open_questions:
                lines.append(f"- {question}")
            lines.append("")

        # Threads Explored
        if extraction.session_summary.threads_explored:
            lines.extend([
                "## Threads Explored",
                "",
            ])
            for thread in extraction.session_summary.threads_explored:
                lines.append(f"- {thread}")
            lines.append("")

        # Key Quotes (from all entities)
        all_quotes = []
        for entity in extraction.entities:
            for quote in entity.quotes:
                all_quotes.append((entity.name, quote))

        if all_quotes:
            lines.extend([
                "## Key Quotes",
                "",
            ])
            for entity_name, quote in all_quotes:
                lines.append(f"> {quote}")
                lines.append(f"> — *re: {entity_name}*")
                lines.append("")

        return "\n".join(lines)

    def _render_entity_section(self, entity: ExtractedEntity) -> list[str]:
        """Render a single entity as markdown section."""
        lines = [
            f"### {entity.name}",
            "",
            f"**Kind:** {entity.kind.value} | **Domain:** {entity.domain.value} | **Status:** {entity.status.value}",
            "",
            entity.description,
            "",
        ]

        if entity.connections:
            lines.append("**Connections:**")
            for conn in entity.connections:
                lines.append(f"- {conn.relationship.value} → {conn.to}")
            lines.append("")

        return lines
