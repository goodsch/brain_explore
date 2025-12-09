"""Enhanced Context Note Parser for SiYuan markdown documents.

Parses Context Notes with support for:
- YAML frontmatter with context_id, context_type, status
- Question bullet parsing with checkbox status and existing IDs
- Core concepts extraction
- Areas of exploration
- Robust regex patterns for flexible markdown formats
"""

import re
import uuid
from datetime import datetime, timezone

import yaml
from pydantic import BaseModel, Field

from ies_backend.schemas.context import (
    AreaOfExploration,
    Context,
    ContextStatus,
    ContextType,
    Question,
    QuestionStatus,
)


# -----------------------------------------------------------------------------
# Parsing Result Schemas
# -----------------------------------------------------------------------------


class ParsedQuestion(BaseModel):
    """Parsed question from markdown with metadata."""

    text: str
    existing_id: str | None = None  # From <!-- q_xxx --> comment
    is_completed: bool = False  # [x] vs [ ]
    prefix: str | None = None  # Q1:, Q2:, etc.
    siyuan_block_id: str | None = None


class ParsedArea(BaseModel):
    """Parsed area of exploration."""

    title: str
    description: str | None = None
    existing_id: str | None = None


class ParsedConcept(BaseModel):
    """Parsed concept from core concepts list."""

    name: str
    existing_id: str | None = None  # Future: resolve from KG


class ContextNoteFrontmatter(BaseModel):
    """Parsed YAML frontmatter from Context Note."""

    context_id: str | None = None
    context_type: str | None = None
    status: str | None = None
    created: str | None = None
    parent_context_id: str | None = None
    siyuan_doc_id: str | None = None


class ContextNoteParseResult(BaseModel):
    """Complete parse result from Context Note."""

    context: Context
    questions: list[ParsedQuestion]
    areas: list[ParsedArea]
    concepts: list[ParsedConcept]
    raw_sections: dict[str, list[str]] = Field(default_factory=dict)


# -----------------------------------------------------------------------------
# Context Note Parser
# -----------------------------------------------------------------------------


class ContextNoteParser:
    """Enhanced parser for SiYuan Context Notes with frontmatter and IDs."""

    # Regex patterns
    FRONTMATTER_PATTERN = re.compile(r"^---\n(.*?)\n---", re.DOTALL | re.MULTILINE)
    TITLE_TYPE_PATTERN = re.compile(r"^(feynman|project|theory|concept|life):\s*(.+)$", re.IGNORECASE)
    QUESTION_BULLET_PATTERN = re.compile(
        r"^[-*]\s*"  # Bullet marker
        r"(\[[ xX]\])?\s*"  # Optional checkbox
        r"(?:([A-Z]\d+):\s*)?"  # Optional prefix Q1:
        r"(.+?)"  # Question text
        r"(?:\s*<!--\s*([a-zA-Z0-9_]+)\s*-->)?"  # Optional ID comment (any ID format)
        r"\s*$",
        re.IGNORECASE,
    )
    AREA_BULLET_PATTERN = re.compile(
        r"^[-*]\s*"  # Bullet marker
        r"(.+?)"  # Area title
        r"(?:\s*<!--\s*([a-zA-Z0-9_]+)\s*-->)?"  # Optional ID comment
        r"\s*$",
        re.IGNORECASE,
    )
    CONCEPT_BULLET_PATTERN = re.compile(
        r"^[-*]\s*"  # Bullet marker
        r"(.+?)"  # Concept name
        r"(?:\s*<!--\s*([a-zA-Z0-9_]+)\s*-->)?"  # Optional ID comment
        r"\s*$",
        re.IGNORECASE,
    )

    @classmethod
    def parse(cls, markdown_content: str, siyuan_block_id: str | None = None) -> ContextNoteParseResult:
        """Parse a SiYuan Context Note into structured data.

        Args:
            markdown_content: Full markdown content of the note
            siyuan_block_id: Optional SiYuan block ID for the document

        Returns:
            ContextNoteParseResult with parsed context, questions, areas, concepts

        Example markdown format:
        ```
        ---
        context_id: ctx_abc123
        context_type: feynman_problem
        status: active
        created: 2025-12-09T12:00:00Z
        ---

        # Feynman: Understanding Executive Function

        ## Summary / Intent
        Exploring how executive function works in ADHD brains...

        ## Key Questions
        - [ ] What are the core components of executive function? <!-- q_abc123 -->
        - [x] How does working memory affect EF?
        - Q1: Why is task initiation so difficult? <!-- q_def456 -->

        ## Areas of Exploration
        - Neural mechanisms of attention <!-- area_xyz789 -->
        - Working memory capacity

        ## Core Concepts
        - Executive Function
        - Working Memory
        - Dopamine
        ```
        """
        # Extract frontmatter and body
        frontmatter, body = cls._extract_frontmatter(markdown_content)

        # Parse title and type from first heading
        title, context_type = cls._parse_title_line(body)

        # Override type from frontmatter if present
        if frontmatter.context_type:
            try:
                context_type = ContextType(frontmatter.context_type)
            except ValueError:
                pass  # Keep parsed type from title

        # Parse status from frontmatter
        status = ContextStatus.ACTIVE
        if frontmatter.status:
            try:
                status = ContextStatus(frontmatter.status)
            except ValueError:
                pass

        # Parse sections
        sections = cls._parse_sections(body)

        # Extract summary
        summary = None
        summary_section = sections.get("summary / intent") or sections.get("summary") or sections.get("intent")
        if summary_section:
            summary = " ".join(summary_section)

        # Build Context ID (use frontmatter or generate new)
        context_id = frontmatter.context_id or f"ctx_{uuid.uuid4().hex[:12]}"

        # Build Context
        context = Context(
            id=context_id,
            type=context_type,
            title=title,
            summary=summary,
            status=status,
            parent_context_id=frontmatter.parent_context_id,
            siyuan_block_id=siyuan_block_id or frontmatter.siyuan_doc_id,
            created_at=cls._parse_datetime(frontmatter.created) if frontmatter.created else datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )

        # Parse questions
        questions = cls._parse_questions(sections.get("key questions", []), context.id)

        # Parse areas
        areas = cls._parse_areas(sections.get("areas of exploration", []), context.id)

        # Parse concepts
        concepts = cls._parse_concepts(sections.get("core concepts", []))

        # Link IDs to context
        context.key_questions = [q.existing_id or f"q_{uuid.uuid4().hex[:12]}" for q in questions]
        context.areas_of_exploration = [a.existing_id or f"area_{uuid.uuid4().hex[:12]}" for a in areas]
        context.core_concepts = [c.name for c in concepts]

        return ContextNoteParseResult(
            context=context,
            questions=questions,
            areas=areas,
            concepts=concepts,
            raw_sections=sections,
        )

    @classmethod
    def _extract_frontmatter(cls, markdown: str) -> tuple[ContextNoteFrontmatter, str]:
        """Extract YAML frontmatter and return (frontmatter, body).

        Args:
            markdown: Full markdown content

        Returns:
            Tuple of (parsed frontmatter, markdown body without frontmatter)
        """
        match = cls.FRONTMATTER_PATTERN.match(markdown.strip())
        if not match:
            # No frontmatter, return empty and full content
            return ContextNoteFrontmatter(), markdown

        frontmatter_text = match.group(1)
        body = markdown[match.end() :].lstrip()

        # Parse YAML
        try:
            data = yaml.safe_load(frontmatter_text) or {}

            # Convert datetime to string if present
            created_str = data.get("created")
            if created_str and not isinstance(created_str, str):
                # YAML parsed it as datetime, convert to ISO string
                created_str = created_str.isoformat()

            frontmatter = ContextNoteFrontmatter(
                context_id=data.get("context_id"),
                context_type=data.get("context_type"),
                status=data.get("status"),
                created=created_str,
                parent_context_id=data.get("parent_context_id"),
                siyuan_doc_id=data.get("siyuan_doc_id"),
            )
            return frontmatter, body
        except yaml.YAMLError:
            # Invalid YAML, treat as no frontmatter
            return ContextNoteFrontmatter(), markdown

    @classmethod
    def _parse_title_line(cls, markdown: str) -> tuple[str, ContextType]:
        """Extract title and context type from first heading.

        Args:
            markdown: Markdown body (without frontmatter)

        Returns:
            Tuple of (title, context_type)

        Examples:
            "# Feynman: Understanding EF" -> ("Understanding EF", FEYNMAN_PROBLEM)
            "# Project: Build IES Reader" -> ("Build IES Reader", PROJECT)
            "# My Exploration" -> ("My Exploration", FEYNMAN_PROBLEM)
        """
        lines = markdown.strip().split("\n")
        for line in lines:
            if line.startswith("# "):
                title_line = line[2:].strip()

                # Check for type prefix with regex
                match = cls.TITLE_TYPE_PATTERN.match(title_line)
                if match:
                    type_str = match.group(1).lower()
                    title = match.group(2).strip()

                    # Map to ContextType
                    type_map = {
                        "feynman": ContextType.FEYNMAN_PROBLEM,
                        "project": ContextType.PROJECT,
                        "theory": ContextType.THEORY,
                        "concept": ContextType.CONCEPT_CLUSTER,
                        "life": ContextType.LIFE_AREA,
                    }
                    context_type = type_map.get(type_str, ContextType.FEYNMAN_PROBLEM)
                    return title, context_type

                # No type prefix, return full title
                return title_line, ContextType.FEYNMAN_PROBLEM

        # No heading found
        return "Untitled Context", ContextType.FEYNMAN_PROBLEM

    @classmethod
    def _parse_sections(cls, markdown: str) -> dict[str, list[str]]:
        """Parse markdown into sections by ## headings.

        Args:
            markdown: Markdown body

        Returns:
            Dict mapping section names (lowercase) to list of content lines
        """
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
                # Collect lines for current section
                stripped = line.strip()
                if stripped:
                    current_items.append(stripped)

        # Save last section
        if current_section:
            sections[current_section] = current_items

        return sections

    @classmethod
    def _parse_questions(cls, lines: list[str], context_id: str) -> list[ParsedQuestion]:
        """Parse question lines into ParsedQuestion objects.

        Args:
            lines: Lines from "Key Questions" section
            context_id: Parent context ID

        Returns:
            List of ParsedQuestion objects

        Example lines:
            "- [ ] What is executive function? <!-- q_abc123 -->"
            "- [x] How does ADHD affect EF?"
            "Q1: Why is task initiation hard? <!-- q_def456 -->"
        """
        questions: list[ParsedQuestion] = []

        for line in lines:
            match = cls.QUESTION_BULLET_PATTERN.match(line)
            if match:
                checkbox = match.group(1)  # [x] or [ ] or None
                prefix = match.group(2)  # Q1: or None
                text = match.group(3).strip()
                existing_id = match.group(4)  # q_abc123 or None

                # Determine completion status
                is_completed = bool(checkbox and checkbox.strip().lower() in ["[x]", "[X]"])

                questions.append(
                    ParsedQuestion(
                        text=text,
                        existing_id=existing_id,
                        is_completed=is_completed,
                        prefix=prefix,
                    )
                )
            else:
                # Fallback: treat as plain question text
                text = line.strip().lstrip("-*").strip()
                if text and not text.startswith("#"):
                    questions.append(ParsedQuestion(text=text))

        return questions

    @classmethod
    def _parse_areas(cls, lines: list[str], context_id: str) -> list[ParsedArea]:
        """Parse area lines into ParsedArea objects.

        Args:
            lines: Lines from "Areas of Exploration" section
            context_id: Parent context ID

        Returns:
            List of ParsedArea objects
        """
        areas: list[ParsedArea] = []

        for line in lines:
            match = cls.AREA_BULLET_PATTERN.match(line)
            if match:
                title = match.group(1).strip()
                existing_id = match.group(2)  # area_xyz789 or None

                areas.append(
                    ParsedArea(
                        title=title,
                        existing_id=existing_id,
                    )
                )
            else:
                # Fallback: treat as plain area title
                title = line.strip().lstrip("-*").strip()
                if title and not title.startswith("#"):
                    areas.append(ParsedArea(title=title))

        return areas

    @classmethod
    def _parse_concepts(cls, lines: list[str]) -> list[ParsedConcept]:
        """Parse concept lines into ParsedConcept objects.

        Args:
            lines: Lines from "Core Concepts" section

        Returns:
            List of ParsedConcept objects
        """
        concepts: list[ParsedConcept] = []

        for line in lines:
            match = cls.CONCEPT_BULLET_PATTERN.match(line)
            if match:
                name = match.group(1).strip()
                existing_id = match.group(2)  # concept_abc123 or None

                concepts.append(
                    ParsedConcept(
                        name=name,
                        existing_id=existing_id,
                    )
                )
            else:
                # Fallback: treat as plain concept name
                name = line.strip().lstrip("-*").strip()
                if name and not name.startswith("#"):
                    concepts.append(ParsedConcept(name=name))

        return concepts

    @classmethod
    def _parse_datetime(cls, dt_str: str) -> datetime:
        """Parse ISO datetime string or return current time.

        Args:
            dt_str: ISO format datetime string

        Returns:
            Parsed datetime or current UTC time
        """
        try:
            return datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
        except (ValueError, AttributeError):
            return datetime.now(timezone.utc)
