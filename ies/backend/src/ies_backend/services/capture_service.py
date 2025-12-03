"""Service for Quick Capture processing."""

import os
import re
from typing import Any

from ..schemas.capture import (
    CaptureProcessRequest,
    CaptureProcessResponse,
    CaptureType,
    ExtractedEntity,
    PlacementType,
    SuggestedPlacement,
)
from .graph_service import GraphService

# Check for Anthropic availability
ANTHROPIC_AVAILABLE = False
try:
    import anthropic

    ANTHROPIC_AVAILABLE = bool(os.getenv("ANTHROPIC_API_KEY"))
except ImportError:
    pass


class CaptureService:
    """Service for processing and routing captured content."""

    @staticmethod
    async def process_capture(
        request: CaptureProcessRequest,
    ) -> CaptureProcessResponse:
        """Process captured content to extract entities and suggest placements.

        Args:
            request: Capture processing request

        Returns:
            Processed response with entities and placement suggestions
        """
        content = request.content

        # Extract entities (AI-powered if available, otherwise simple extraction)
        if ANTHROPIC_AVAILABLE:
            entities, summary, tags = await CaptureService._ai_extract(content)
        else:
            entities = CaptureService._simple_extract(content)
            summary = content[:200] + "..." if len(content) > 200 else content
            tags = CaptureService._extract_tags(content)

        # Find related concepts in graph
        related_concepts = []
        for entity in entities:
            graph_matches = await GraphService.search_concepts(entity.name, limit=3)
            related_concepts.extend(graph_matches)

        # Generate placement suggestions
        placements = await CaptureService._suggest_placements(
            content, entities, related_concepts, request.context
        )

        return CaptureProcessResponse(
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

        prompt = f"""Analyze this captured thought/note and extract:
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
                CaptureService._simple_extract(content),
                content[:200],
                CaptureService._extract_tags(content),
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
