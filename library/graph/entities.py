"""
Entity extraction from text chunks using LLM.

Extracts entities for a domain-agnostic knowledge graph with "Reframe Layer"
support for cross-domain conceptual reframing (ADHD-friendly pattern detection).

Entity Types:
- Researcher: People (authors, theorists, experimenters)
- Concept: Core ideas, constructs, phenomena
- Theory: Named theories/models/frameworks
- Assessment: Instruments/scales/protocols
- Pattern: Reusable conceptual schemas (Feedback Loop, Tipping Point)
- DynamicPattern: Temporal/process structures (Oscillation, Emergence)
- StoryInsight: Narrative vignettes that embody concepts
- SchemaBreak: Moments where intuitive models fail
- Reframe: Metaphor/analogy/story linking concepts across domains

Relationships:
- cites, develops, supports, contradicts, operationalizes, component_of
- METAPHOR_FOR, ANALOGOUS_TO, DEMONSTRATES, EMBODIES, RESONATES_WITH
"""

import json
from dataclasses import dataclass, field
from typing import Iterator, Literal
from openai import OpenAI

from library.ingest.chunk import Chunk


# Valid entity types
EntityType = Literal[
    "researcher", "concept", "theory", "assessment",
    "pattern", "dynamic_pattern", "story_insight", "schema_break", "reframe"
]

# Valid reframe types (for reframe entities)
ReframeType = Literal["Metaphor", "Analogy", "Story", "Pattern", "Contrast"]

# Valid relationship types
RelationType = Literal[
    "cites", "develops", "supports", "contradicts", "operationalizes", "component_of",
    "METAPHOR_FOR", "ANALOGOUS_TO", "DEMONSTRATES", "EMBODIES", "RESONATES_WITH"
]


@dataclass
class Entity:
    """An extracted entity."""
    name: str
    type: str  # EntityType
    description: str | None = None
    aliases: list[str] = field(default_factory=list)
    # Reframe-specific fields
    reframe_type: str | None = None  # ReframeType - for type="reframe"
    source_domain: str | None = None  # e.g., "Physics", "Jazz", "Gardening"


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


EXTRACTION_PROMPT = """Analyze this text (any domain) and extract entities/relationships that capture cross-domain conceptual reframing. Prioritize structural patterns (shapes, dynamics, analogies) over surface semantics.

Entities to extract (use only these types):
1) researcher — people (authors, theorists, experimenters).
2) concept — core ideas, constructs, phenomena.
3) theory — named theories/models/frameworks.
4) assessment — instruments/scales/protocols.
5) pattern — reusable conceptual schemas (e.g., feedback loop, tragedy of the commons, tipping point).
6) dynamic_pattern — temporal/process shapes (e.g., oscillation, emergence, cascading failure).
7) story_insight — specific narrative vignette/experiment/story beat that embodies an idea (e.g., Backwards Bicycle experiment).
8) schema_break — moments where an intuitive model fails or reveals deeper structure (paradox, surprise, reversal).
9) reframe — an analogy/metaphor/story/pattern/contrast that explains one concept using another domain.
   - reframe_type: Metaphor | Analogy | Story | Pattern | Contrast
   - source_domain: originating domain of the reframe (e.g., Physics, Jazz, Gardening).

Relationships to extract (use only these):
- cites — author/person references another.
- develops — researcher develops a theory/model.
- supports — evidence supports a concept/theory.
- contradicts — evidence counters a concept/theory.
- operationalizes — assessment measures/operationalizes a concept.
- component_of — entity is a part/module of a larger concept/theory/pattern.
- METAPHOR_FOR — X is used as a metaphor/reframe for Y (often reframe -> concept).
- ANALOGOUS_TO — X and Y share structural similarity across domains.
- DEMONSTRATES — an experiment/story_insight shows a concept/theory/pattern.
- EMBODIES — a narrative/experiment instantiates a schema_break or pattern.
- RESONATES_WITH — non-obvious cross-domain connection (structural rhyme rather than topic match).

Guidance:
- Be concise and selective; prefer explicit or strongly implied structures over vague hints.
- Look for shape words (cycle, cascade, threshold, feedback, oscillate), surprise/violation cues (unexpected, paradox, fails), and analogy markers ("like", "as", "works the way", "reminds").
- Keep domain-agnostic language; do not assume psychology/therapy.
- If nothing clear, return empty arrays.

Return JSON exactly in this shape:
```json
{{
  "entities": [
    {{
      "name": "string",
      "type": "researcher|concept|theory|assessment|pattern|dynamic_pattern|story_insight|schema_break|reframe",
      "description": "brief description",
      "aliases": ["optional", "aliases"],
      "reframe_type": "Metaphor|Analogy|Story|Pattern|Contrast|null",
      "source_domain": "string|null"
    }}
  ],
  "relationships": [
    {{
      "source": "entity name",
      "target": "entity name",
      "relation_type": "cites|develops|supports|contradicts|operationalizes|component_of|METAPHOR_FOR|ANALOGOUS_TO|DEMONSTRATES|EMBODIES|RESONATES_WITH",
      "evidence": "short quote or paraphrase"
    }}
  ]
}}
```

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
                aliases=e.get("aliases", []),
                reframe_type=e.get("reframe_type"),
                source_domain=e.get("source_domain")
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
