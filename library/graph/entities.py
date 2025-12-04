"""
Entity extraction from text chunks using LLM.

Extracts:
- Researchers (who wrote it, who they cite)
- Concepts (emotion regulation, executive function, etc.)
- Theories/Models (Gross's process model, Barkley's EF theory)
- Relationships (supports, contradicts, operationalizes, etc.)
"""

import json
from dataclasses import dataclass, field
from typing import Iterator
from openai import OpenAI

from library.ingest.chunk import Chunk


@dataclass
class Entity:
    """An extracted entity."""
    name: str
    type: str  # researcher, concept, theory, assessment
    description: str | None = None
    aliases: list[str] = field(default_factory=list)


@dataclass
class Relationship:
    """A relationship between entities."""
    source: str
    target: str
    relation_type: str  # cites, supports, contradicts, operationalizes, develops
    evidence: str | None = None


@dataclass
class ExtractionResult:
    """Result of entity extraction from a chunk."""
    chunk_id: str
    entities: list[Entity]
    relationships: list[Relationship]


EXTRACTION_PROMPT = """Analyze this text from a therapy/psychology book and extract:

1. **Researchers** - People mentioned (researchers, theorists, clinicians)
2. **Concepts** - Key psychological concepts (e.g., "emotion regulation", "executive function", "psychological flexibility")
3. **Theories/Models** - Named theories or models (e.g., "Gross's process model", "ACT hexaflex")
4. **Assessments** - Any mentioned scales or instruments (e.g., "DERS", "AAQ-II")

Also identify relationships between entities:
- **cites** - Author A cites Author B's work
- **develops** - Author develops a theory/model
- **supports** - Evidence supports a concept/theory
- **contradicts** - Evidence contradicts a concept/theory
- **operationalizes** - Assessment operationalizes a concept
- **component_of** - Concept is part of larger concept/theory

Return JSON in this exact format:
```json
{{
  "entities": [
    {{"name": "string", "type": "researcher|concept|theory|assessment", "description": "brief description", "aliases": ["optional", "aliases"]}}
  ],
  "relationships": [
    {{"source": "entity name", "target": "entity name", "relation_type": "cites|develops|supports|contradicts|operationalizes|component_of", "evidence": "brief quote or paraphrase"}}
  ]
}}
```

Be selective - only extract clearly stated entities and relationships, not vague references.
If nothing clear to extract, return empty arrays.

TEXT TO ANALYZE:
---
{text}
---

JSON output:"""


class EntityExtractor:
    """Extract entities and relationships from chunks using OpenAI."""

    def __init__(self, model: str = "gpt-4o-mini"):
        self.client = OpenAI()
        self.model = model

    def extract_from_chunk(self, chunk: Chunk) -> ExtractionResult:
        """Extract entities and relationships from a single chunk."""
        prompt = EXTRACTION_PROMPT.format(text=chunk.content)

        response = self.client.chat.completions.create(
            model=self.model,
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}]
        )

        # Parse response
        content = response.choices[0].message.content

        # Extract JSON from response (handle markdown code blocks)
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0]
        elif "```" in content:
            content = content.split("```")[1].split("```")[0]

        # Try to find JSON object directly
        content = content.strip()
        if not content.startswith("{"):
            # Try to find JSON object in content
            start = content.find("{")
            if start != -1:
                # Find matching closing brace
                depth = 0
                for i, c in enumerate(content[start:]):
                    if c == "{":
                        depth += 1
                    elif c == "}":
                        depth -= 1
                        if depth == 0:
                            content = content[start:start+i+1]
                            break

        try:
            data = json.loads(content)
        except json.JSONDecodeError as e:
            # Return empty if parsing fails
            return ExtractionResult(
                chunk_id=chunk.id,
                entities=[],
                relationships=[]
            )

        entities = [
            Entity(
                name=e.get("name", ""),
                type=e.get("type", "concept"),
                description=e.get("description"),
                aliases=e.get("aliases", [])
            )
            for e in data.get("entities", [])
            if e.get("name")
        ]

        relationships = [
            Relationship(
                source=r.get("source", ""),
                target=r.get("target", ""),
                relation_type=r.get("relation_type", "relates_to"),
                evidence=r.get("evidence")
            )
            for r in data.get("relationships", [])
            if r.get("source") and r.get("target")
        ]

        return ExtractionResult(
            chunk_id=chunk.id,
            entities=entities,
            relationships=relationships
        )

    def extract_from_chunks(
        self,
        chunks: list[Chunk],
        progress_callback=None
    ) -> Iterator[ExtractionResult]:
        """Extract from multiple chunks."""
        for i, chunk in enumerate(chunks):
            if progress_callback:
                progress_callback(i, len(chunks), chunk.id)

            result = self.extract_from_chunk(chunk)
            if result.entities or result.relationships:
                yield result


def deduplicate_entities(results: list[ExtractionResult]) -> dict[str, Entity]:
    """Deduplicate entities across multiple extraction results."""
    entities = {}

    for result in results:
        for entity in result.entities:
            # Normalize name for deduplication
            key = entity.name.lower().strip()

            if key in entities:
                # Merge aliases
                existing = entities[key]
                existing.aliases = list(set(existing.aliases + entity.aliases))
                # Keep longer description
                if entity.description and (
                    not existing.description or
                    len(entity.description) > len(existing.description)
                ):
                    existing.description = entity.description
            else:
                entities[key] = entity

    return entities
