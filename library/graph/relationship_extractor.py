"""
Relationship extraction between entities using LLM (Pass 2).

Extracts three core relationship types from entity-rich book chunks:
- CAUSES: Causal/enabling relationships
- PART_OF: Component/hierarchical relationships
- CONTRASTS_WITH: Distinction/comparison relationships

Part of the multi-pass ingestion pipeline:
- Pass 1 (entities.py): Extract entities from text
- Pass 2 (this module): Extract relationships between entities
- Pass 3 (future): LLM enrichment with reframes and mechanisms
"""

import json
import logging
from dataclasses import dataclass
from typing import Optional
from openai import OpenAI

from library.ingest.chunk import Chunk

logger = logging.getLogger(__name__)


@dataclass
class ExtractedRelationship:
    """A relationship extracted by LLM with evidence."""
    source: str           # Entity name
    target: str           # Entity name
    relation_type: str    # CAUSES | PART_OF | CONTRASTS_WITH
    evidence: str         # Text quote supporting relationship
    confidence: float     # 0.0-1.0
    chunk_id: str         # Source chunk for traceability


@dataclass
class RelationshipExtractionResult:
    """Result of relationship extraction for one chunk."""
    chunk_id: str
    relationships: list[ExtractedRelationship]
    entities_present: list[str]  # Entities that were in chunk


RELATIONSHIP_EXTRACTION_PROMPT = """Analyze this text and extract ONLY the following relationship types between entities:

ENTITY TYPES:
- Concept (core ideas, constructs)
- Theory (named theories/models)
- Framework (structured approaches)
- Person (authors, researchers)
- Assessment (instruments, scales)

RELATIONSHIP TYPES TO EXTRACT:

1) CAUSES (A→B): A causes, enables, produces, or leads to B
   - Causal mechanisms (e.g., "dopamine deficiency causes attention issues")
   - Prerequisites (e.g., "self-regulation requires executive function")
   - Temporal sequences (e.g., "shame blocks metabolization")

2) PART_OF (A→B): A is a component, aspect, module, or element of B
   - Hierarchical relationships (e.g., "working memory is part of executive function")
   - Taxonomic relationships (e.g., "ADHD is part of neurodevelopmental disorders")
   - Modular composition (e.g., "DBT includes mindfulness")

3) CONTRASTS_WITH (A↔B): A differs from, contrasts with, or is distinguished from B
   - Conceptual distinctions (e.g., "acceptance contrasts with resignation")
   - Comparison relationships (e.g., "ADHD differs from autism")
   - Theoretical opposites (e.g., "behaviorism contrasts with psychoanalysis")

INSTRUCTIONS:
- Only extract relationships that are EXPLICITLY stated or STRONGLY implied
- Include brief evidence quote (1-2 sentences) from the text
- If no clear relationships exist, return empty array
- Use exact entity names from the provided list
- Prefer precise relationships over vague connections

Return JSON in this exact format:
```json
{{
  "relationships": [
    {{
      "source": "exact entity name",
      "target": "exact entity name",
      "relation_type": "CAUSES | PART_OF | CONTRASTS_WITH",
      "evidence": "brief quote or paraphrase from text",
      "confidence": 0.0-1.0
    }}
  ]
}}
```

TEXT TO ANALYZE:
---
{chunk_text}
---

ENTITIES PRESENT:
{entity_list}

JSON output:"""


class RelationshipExtractor:
    """Extract typed relationships between entities using OpenAI."""

    def __init__(
        self,
        model: str = "gpt-4o-mini",
        confidence_threshold: float = 0.5
    ):
        """
        Initialize relationship extractor.

        Args:
            model: OpenAI model to use (default: gpt-4o-mini for cost efficiency)
            confidence_threshold: Minimum confidence to accept relationships (0.0-1.0)
        """
        self.client = OpenAI()
        self.model = model
        self.confidence_threshold = confidence_threshold

    def extract_relationships_from_chunks(
        self,
        chunks_with_entities: list[tuple[Chunk, list[str]]]
    ) -> list[RelationshipExtractionResult]:
        """
        Extract relationships from multiple chunks.

        Args:
            chunks_with_entities: List of (Chunk, entity_names) tuples

        Returns:
            List of extraction results, one per chunk
        """
        results = []

        for chunk, entities in chunks_with_entities:
            if len(entities) < 2:
                # Skip chunks with fewer than 2 entities
                logger.debug(f"Skipping chunk {chunk.id}: only {len(entities)} entities")
                continue

            try:
                result = self._extract_from_chunk(chunk, entities)
                if result.relationships:
                    results.append(result)
                    logger.info(
                        f"Extracted {len(result.relationships)} relationships "
                        f"from chunk {chunk.id}"
                    )
            except Exception as e:
                logger.error(f"Failed to extract from chunk {chunk.id}: {e}")
                continue

        return results

    def _extract_from_chunk(
        self,
        chunk: Chunk,
        entities: list[str]
    ) -> RelationshipExtractionResult:
        """
        Extract relationships from a single chunk.

        Args:
            chunk: Text chunk to analyze
            entities: List of entity names present in chunk

        Returns:
            RelationshipExtractionResult with extracted relationships
        """
        # Format entity list for prompt
        entity_list = "\n".join(f"- {entity}" for entity in entities)

        # Build prompt
        prompt = RELATIONSHIP_EXTRACTION_PROMPT.format(
            chunk_text=chunk.content,
            entity_list=entity_list
        )

        # Call OpenAI
        logger.debug(f"Extracting relationships from chunk {chunk.id}")
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1500,
            temperature=0.3  # Lower temperature for more precise extraction
        )

        # Parse response
        content = response.choices[0].message.content
        relationships = self._parse_relationships(content, chunk.id)

        # Filter by confidence threshold
        filtered = [
            rel for rel in relationships
            if rel.confidence >= self.confidence_threshold
        ]

        if len(filtered) < len(relationships):
            logger.debug(
                f"Filtered {len(relationships) - len(filtered)} "
                f"low-confidence relationships from chunk {chunk.id}"
            )

        return RelationshipExtractionResult(
            chunk_id=chunk.id,
            relationships=filtered,
            entities_present=entities
        )

    def _parse_relationships(
        self,
        content: str,
        chunk_id: str
    ) -> list[ExtractedRelationship]:
        """
        Parse LLM response into ExtractedRelationship objects.

        Args:
            content: Raw LLM response content
            chunk_id: ID of source chunk

        Returns:
            List of extracted relationships (may be empty if parsing fails)
        """
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

        # Parse JSON
        try:
            data = json.loads(content)
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse JSON from chunk {chunk_id}: {e}")
            return []

        # Extract relationships
        relationships = []
        for r in data.get("relationships", []):
            # Validate required fields
            if not r.get("source") or not r.get("target"):
                logger.warning(f"Skipping relationship with missing source/target: {r}")
                continue

            if not r.get("relation_type"):
                logger.warning(f"Skipping relationship with missing type: {r}")
                continue

            # Validate relationship type
            relation_type = r.get("relation_type", "").upper()
            if relation_type not in ["CAUSES", "PART_OF", "CONTRASTS_WITH"]:
                logger.warning(
                    f"Skipping relationship with invalid type '{relation_type}': "
                    f"{r.get('source')} -> {r.get('target')}"
                )
                continue

            # Extract confidence (default to 0.7 if not provided)
            confidence = float(r.get("confidence", 0.7))
            if confidence < 0.0 or confidence > 1.0:
                logger.warning(f"Invalid confidence {confidence}, clamping to [0,1]")
                confidence = max(0.0, min(1.0, confidence))

            relationships.append(ExtractedRelationship(
                source=r["source"].strip(),
                target=r["target"].strip(),
                relation_type=relation_type,
                evidence=r.get("evidence", "").strip(),
                confidence=confidence,
                chunk_id=chunk_id
            ))

        return relationships


def deduplicate_relationships(
    relationships: list[ExtractedRelationship]
) -> list[ExtractedRelationship]:
    """
    Merge duplicate relationships, keeping highest confidence.

    Relationships are considered duplicates if they have the same
    (source, target, relation_type) triple.

    Args:
        relationships: List of relationships to deduplicate

    Returns:
        Deduplicated list with merged evidence and highest confidence
    """
    seen = {}  # (source, target, type) → relationship

    for rel in relationships:
        # Create normalized key
        key = (
            rel.source.lower().strip(),
            rel.target.lower().strip(),
            rel.relation_type
        )

        if key not in seen:
            seen[key] = rel
        else:
            # Merge with existing relationship
            existing = seen[key]

            # Keep relationship with higher confidence
            if rel.confidence > existing.confidence:
                # Merge evidence (accumulate supporting quotes)
                if rel.evidence and existing.evidence:
                    existing.evidence = f"{existing.evidence}; {rel.evidence}"
                elif rel.evidence:
                    existing.evidence = rel.evidence

                existing.confidence = rel.confidence
                # Keep the original chunk_id from the higher-confidence extraction
                existing.chunk_id = rel.chunk_id
            elif rel.evidence and rel.evidence not in existing.evidence:
                # Add additional evidence even if confidence is lower
                existing.evidence = f"{existing.evidence}; {rel.evidence}"

    return list(seen.values())


def validate_relationship(
    rel: ExtractedRelationship,
    valid_entities: set[str]
) -> tuple[bool, str]:
    """
    Validate relationship against business rules.

    Args:
        rel: Relationship to validate
        valid_entities: Set of valid entity names (case-insensitive)

    Returns:
        (is_valid, reason) tuple
    """
    # Check confidence
    if rel.confidence < 0.5:
        return False, f"confidence too low ({rel.confidence})"

    # Check self-loop
    if rel.source.lower() == rel.target.lower():
        return False, "self-loop not allowed"

    # Check type
    if rel.relation_type not in ["CAUSES", "PART_OF", "CONTRASTS_WITH"]:
        return False, f"invalid type '{rel.relation_type}'"

    # Check entities exist (case-insensitive)
    valid_entities_lower = {e.lower() for e in valid_entities}

    if rel.source.lower() not in valid_entities_lower:
        return False, f"source entity not found: {rel.source}"

    if rel.target.lower() not in valid_entities_lower:
        return False, f"target entity not found: {rel.target}"

    # Check evidence
    if not rel.evidence or len(rel.evidence) < 10:
        return False, "insufficient evidence"

    return True, "valid"
