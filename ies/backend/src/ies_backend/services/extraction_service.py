"""Entity extraction service using Claude API."""

import json
from anthropic import AsyncAnthropic

from ies_backend.config import settings
from ies_backend.schemas.entity import (
    EntityConnection,
    EntityDomain,
    EntityKind,
    EntityStatus,
    ExtractionResult,
    ExtractedEntity,
    SessionSummary,
)


EXTRACTION_PROMPT = """You are an expert at identifying and extracting knowledge entities from exploratory conversations.

Analyze the following transcript and extract:

1. **Entities** - Ideas, concepts, questions, tensions, people, or processes that emerged
2. **Connections** - How entities relate to each other
3. **Session Summary** - Key insights, open questions, and threads explored

For each entity, determine:
- **kind**: idea | person | process | question | tension
  - idea: A concept, belief, or insight
  - person: A theorist, author, or figure referenced
  - process: A method, technique, or way of doing something
  - question: An open question or inquiry
  - tension: A conflict, paradox, or unresolved opposition

- **domain**: therapy | personal | meta
  - therapy: Related to therapeutic approach, theory, or practice
  - personal: Related to the user's personal experience or context
  - meta: About the exploration process itself

- **status**: seed | developing | solid
  - seed: First mention, rough idea, needs more exploration
  - developing: Has been explored some, taking shape
  - solid: Well-developed, clearly articulated

- **connections**: How this entity relates to others
  - supports: This entity supports/strengthens another
  - tensions: This entity is in tension with another
  - develops: This entity develops/extends another

Extract exact quotes from the transcript that support each entity.

TRANSCRIPT:
{transcript}

Respond with valid JSON matching this schema:
{{
  "entities": [
    {{
      "name": "string",
      "kind": "idea | person | process | question | tension",
      "domain": "therapy | personal | meta",
      "status": "seed | developing | solid",
      "description": "string",
      "quotes": ["exact quotes from transcript"],
      "connections": [
        {{"to": "entity_name", "relationship": "supports | tensions | develops"}}
      ]
    }}
  ],
  "session_summary": {{
    "key_insights": ["string"],
    "open_questions": ["string"],
    "threads_explored": ["string"]
  }}
}}

Be selective - only extract meaningful entities that represent genuine insights, not every topic mentioned.
Prefer fewer, richer entities over many shallow ones."""


class ExtractionService:
    """Service for extracting entities from session transcripts using Claude."""

    def __init__(self) -> None:
        """Initialize with Anthropic client."""
        self.client = AsyncAnthropic(api_key=settings.anthropic_api_key)

    async def extract_entities(self, transcript: str) -> ExtractionResult:
        """Extract entities and summary from a transcript.

        Args:
            transcript: Raw session transcript

        Returns:
            ExtractionResult with entities and summary
        """
        prompt = EXTRACTION_PROMPT.format(transcript=transcript)

        message = await self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4096,
            messages=[
                {"role": "user", "content": prompt}
            ],
        )

        # Parse response
        response_text = message.content[0].text

        # Extract JSON from response (handle markdown code blocks)
        json_text = response_text
        if "```json" in json_text:
            json_text = json_text.split("```json")[1].split("```")[0]
        elif "```" in json_text:
            json_text = json_text.split("```")[1].split("```")[0]

        try:
            data = json.loads(json_text.strip())
        except json.JSONDecodeError as e:
            # If parsing fails, return empty result
            return ExtractionResult(
                entities=[],
                session_summary=SessionSummary(
                    key_insights=[f"Extraction failed: {str(e)}"],
                    open_questions=[],
                    threads_explored=[],
                ),
            )

        # Convert to Pydantic models
        entities = []
        for entity_data in data.get("entities", []):
            try:
                connections = [
                    EntityConnection(
                        to=conn["to"],
                        relationship=conn["relationship"],
                    )
                    for conn in entity_data.get("connections", [])
                ]

                entity = ExtractedEntity(
                    name=entity_data["name"],
                    kind=EntityKind(entity_data["kind"]),
                    domain=EntityDomain(entity_data["domain"]),
                    status=EntityStatus(entity_data["status"]),
                    description=entity_data["description"],
                    quotes=entity_data.get("quotes", []),
                    connections=connections,
                )
                entities.append(entity)
            except (KeyError, ValueError):
                # Skip malformed entities
                continue

        summary_data = data.get("session_summary", {})
        summary = SessionSummary(
            key_insights=summary_data.get("key_insights", []),
            open_questions=summary_data.get("open_questions", []),
            threads_explored=summary_data.get("threads_explored", []),
        )

        return ExtractionResult(entities=entities, session_summary=summary)
