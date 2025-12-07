"""
Pass 2: Cross-Domain Mapping ("ADHD Leap")

After Pass 1 extracts entities, this service finds non-obvious connections
between newly extracted patterns/stories and existing concepts in the graph.

The "resonance check" identifies structural similarities across domains,
creating RESONATES_WITH and METAPHOR_FOR relationships that enable the
ADHD-friendly exploration pattern of following conceptual rhymes rather
than hierarchical categories.
"""

import json
import logging
from dataclasses import dataclass
from typing import Literal

from openai import OpenAI

from library.graph.neo4j_client import KnowledgeGraph

logger = logging.getLogger(__name__)

# Entity types that can serve as reframe sources
REFRAME_SOURCE_TYPES = ["pattern", "dynamic_pattern", "story_insight", "schema_break"]

# Minimum confidence threshold for creating relationships
CONFIDENCE_THRESHOLD = 0.7


@dataclass
class ResonanceMatch:
    """A potential cross-domain connection."""
    source_entity: str
    target_concept: str
    relationship_type: Literal["RESONATES_WITH", "METAPHOR_FOR", "ANALOGOUS_TO"]
    confidence: float
    rationale: str


RESONANCE_PROMPT = """You are identifying cross-domain conceptual resonances for an ADHD-friendly knowledge graph.

Given a newly extracted entity (pattern, story, or schema break), identify which existing concepts it "resonates with" - meaning they share structural similarity even though they come from different domains.

**Newly Extracted Entity:**
- Name: {source_name}
- Type: {source_type}
- Description: {source_description}

**Existing Concepts to Consider:**
{concepts_list}

**Instructions:**
1. Look for STRUCTURAL similarity, not topic overlap
2. A pattern about "feedback loops" might resonate with concepts about "emotional regulation" or "habit formation"
3. A story about "unlearning" might connect to concepts about "neuroplasticity" or "cognitive flexibility"
4. Prefer non-obvious connections that reveal deeper structure

Return JSON with matches (0-3 per entity):
```json
{{
  "matches": [
    {{
      "target_concept": "concept name from list",
      "relationship_type": "RESONATES_WITH | METAPHOR_FOR | ANALOGOUS_TO",
      "confidence": 0.0-1.0,
      "rationale": "brief explanation of structural similarity"
    }}
  ]
}}
```

If no strong resonances exist, return empty matches array.
"""


class ReframeMapper:
    """Maps newly extracted patterns/stories to existing concepts via resonance."""

    def __init__(self, kg: KnowledgeGraph, model: str = "gpt-4o-mini"):
        self.kg = kg
        self.client = OpenAI()
        self.model = model

    def get_reframe_sources_for_book(self, calibre_id: int) -> list[dict]:
        """Get pattern/story entities from a specific book."""
        with self.kg.driver.session() as session:
            # Query by label (Pattern, StoryInsight, etc.) not type property
            result = session.run("""
                MATCH (b:Book {calibre_id: $calibre_id})-[:MENTIONS]->(e)
                WHERE e:Pattern OR e:DynamicPattern OR e:StoryInsight OR e:SchemaBreak
                RETURN e.name AS name,
                       CASE
                         WHEN e:Pattern THEN 'pattern'
                         WHEN e:DynamicPattern THEN 'dynamic_pattern'
                         WHEN e:StoryInsight THEN 'story_insight'
                         WHEN e:SchemaBreak THEN 'schema_break'
                       END AS type,
                       e.description AS description
            """, calibre_id=calibre_id)
            return [dict(r) for r in result]

    def get_concepts_without_reframes(self, limit: int = 50) -> list[dict]:
        """Get concepts that could benefit from reframe connections."""
        with self.kg.driver.session() as session:
            # Get concepts, prioritizing those with fewer incoming RESONATES_WITH edges
            result = session.run("""
                MATCH (c:Concept)
                OPTIONAL MATCH (c)<-[r:RESONATES_WITH|METAPHOR_FOR|ANALOGOUS_TO]-()
                WITH c, count(r) AS reframe_count
                ORDER BY reframe_count ASC
                LIMIT $limit
                RETURN c.name AS name, c.description AS description, reframe_count
            """, limit=limit)
            return [dict(r) for r in result]

    def find_resonances(self, source: dict, concepts: list[dict]) -> list[ResonanceMatch]:
        """Use LLM to find resonance connections between source and concepts."""
        if not concepts:
            return []

        # Format concepts for prompt
        concepts_text = "\n".join([
            f"- {c['name']}: {c.get('description', 'No description')}"
            for c in concepts
        ])

        prompt = RESONANCE_PROMPT.format(
            source_name=source['name'],
            source_type=source['type'],
            source_description=source.get('description', 'No description'),
            concepts_list=concepts_text
        )

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                response_format={"type": "json_object"}
            )

            content = response.choices[0].message.content
            data = json.loads(content)
            matches = []

            for m in data.get("matches", []):
                if m.get("confidence", 0) >= CONFIDENCE_THRESHOLD:
                    matches.append(ResonanceMatch(
                        source_entity=source['name'],
                        target_concept=m['target_concept'],
                        relationship_type=m['relationship_type'],
                        confidence=m['confidence'],
                        rationale=m['rationale']
                    ))

            return matches

        except Exception as e:
            logger.error(f"Failed to find resonances for {source['name']}: {e}")
            return []

    def create_resonance_relationships(self, matches: list[ResonanceMatch]) -> int:
        """Create relationships in the graph for validated matches."""
        created = 0
        with self.kg.driver.session() as session:
            for match in matches:
                try:
                    # Create the relationship with metadata
                    session.run(f"""
                        MATCH (source) WHERE source.name = $source_name
                        MATCH (target:Concept) WHERE target.name = $target_name
                        MERGE (source)-[r:{match.relationship_type}]->(target)
                        SET r.confidence = $confidence,
                            r.rationale = $rationale,
                            r.created_by = 'reframe_mapper'
                    """,
                        source_name=match.source_entity,
                        target_name=match.target_concept,
                        confidence=match.confidence,
                        rationale=match.rationale
                    )
                    created += 1
                    logger.info(
                        f"Created {match.relationship_type}: "
                        f"{match.source_entity} -> {match.target_concept} "
                        f"(confidence: {match.confidence:.2f})"
                    )
                except Exception as e:
                    logger.error(f"Failed to create relationship: {e}")

        return created

    def process_book(self, calibre_id: int) -> dict:
        """Run Pass 2 on a single book after Pass 1 completes."""
        # Get reframe source entities from this book
        sources = self.get_reframe_sources_for_book(calibre_id)
        if not sources:
            logger.info(f"No reframe sources found for book {calibre_id}")
            return {"sources": 0, "matches": 0, "relationships": 0}

        # Get concepts that could benefit from connections
        concepts = self.get_concepts_without_reframes(limit=50)
        if not concepts:
            logger.info("No concepts found in graph")
            return {"sources": len(sources), "matches": 0, "relationships": 0}

        # Find and create resonance relationships
        total_matches = 0
        total_relationships = 0

        for source in sources:
            matches = self.find_resonances(source, concepts)
            total_matches += len(matches)
            if matches:
                created = self.create_resonance_relationships(matches)
                total_relationships += created

        # Update book status if relationships were created
        if total_relationships > 0:
            self.kg.update_book_status(calibre_id, "relationships_mapped")

        result = {
            "sources": len(sources),
            "matches": total_matches,
            "relationships": total_relationships
        }
        logger.info(f"Pass 2 complete for book {calibre_id}: {result}")
        return result


def run_pass2_for_book(calibre_id: int) -> dict:
    """Convenience function to run Pass 2 on a specific book."""
    kg = KnowledgeGraph()
    mapper = ReframeMapper(kg)
    return mapper.process_book(calibre_id)


if __name__ == "__main__":
    import sys

    logging.basicConfig(level=logging.INFO)

    if len(sys.argv) < 2:
        print("Usage: python -m library.graph.reframe_mapper <calibre_id>")
        sys.exit(1)

    calibre_id = int(sys.argv[1])
    result = run_pass2_for_book(calibre_id)
    print(f"Result: {result}")
