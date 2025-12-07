"""
Pass 3: Generative Reframe Creation

Proactively generates reframes for concepts that lack accessible metaphors/analogies.
Uses extracted StoryInsights and Patterns from the graph to create contextual reframes
that connect abstract concepts to concrete, relatable narratives.

This complements the on-demand ReframeService by background-filling gaps in the graph.
"""

import json
import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Literal
from uuid import uuid4

from openai import OpenAI

from library.graph.neo4j_client import KnowledgeGraph

logger = logging.getLogger(__name__)

# Minimum number of relationships a concept should have to be considered "dense"
DENSE_CONCEPT_THRESHOLD = 3


@dataclass
class GeneratedReframe:
    """A reframe generated from story/pattern + concept pairing."""
    concept_name: str
    source_entity: str  # The story/pattern used
    source_type: str
    reframe_type: Literal["Metaphor", "Analogy", "Story", "Pattern", "Contrast"]
    domain: str
    text: str
    structural_connection: str


GENERATION_PROMPT = """You are creating an ADHD-friendly reframe that connects an abstract concept to a concrete story or pattern.

**Concept to Reframe:**
- Name: {concept_name}
- Description: {concept_description}

**Source Material (use this to create the reframe):**
- Name: {source_name}
- Type: {source_type}
- Description: {source_description}

**Instructions:**
1. Identify the STRUCTURAL similarity between the concept and source
2. Create a reframe that makes the abstract concept visceral and memorable
3. Use vivid, concrete language from the source material
4. The reframe should feel like an "aha!" moment, not a dry explanation

**Examples of good reframes:**
- "Working Memory Load is like the Backwards Bicycle: your internal model keeps snapping back to the old path"
- "Emotional Regulation works like a thermostat: it doesn't eliminate temperature swings, it responds to them"

Return JSON:
```json
{{
  "reframe_type": "Metaphor | Analogy | Story | Pattern | Contrast",
  "domain": "source domain (e.g., Physics, Nature, Sports, Music)",
  "text": "Your {concept} is like [vivid reframe]. [Brief structural connection].",
  "structural_connection": "Brief explanation of the structural parallel"
}}
```
"""


class ReframeGenerator:
    """Generates reframes by pairing concepts with stories/patterns."""

    def __init__(self, kg: KnowledgeGraph, model: str = "gpt-4o-mini"):
        self.kg = kg
        self.client = OpenAI()
        self.model = model

    def get_concepts_needing_reframes(self, limit: int = 20) -> list[dict]:
        """Get dense concepts (high connectivity) with few or no reframes."""
        with self.kg.driver.session() as session:
            result = session.run("""
                MATCH (c:Concept)
                // Count incoming relationships (measure of "density")
                OPTIONAL MATCH (c)<-[in]-()
                WITH c, count(DISTINCT in) AS in_degree
                WHERE in_degree >= $threshold

                // Count existing reframes
                OPTIONAL MATCH (c)-[:HAS_REFRAME]->(r:Reframe)
                WITH c, in_degree, count(r) AS reframe_count
                WHERE reframe_count < 2  // Few or no reframes

                RETURN c.name AS name, c.description AS description,
                       in_degree, reframe_count
                ORDER BY in_degree DESC, reframe_count ASC
                LIMIT $limit
            """, threshold=DENSE_CONCEPT_THRESHOLD, limit=limit)
            return [dict(r) for r in result]

    def get_story_insights_and_patterns(self, limit: int = 30) -> list[dict]:
        """Get available StoryInsights and Patterns for reframe generation."""
        with self.kg.driver.session() as session:
            result = session.run("""
                MATCH (e)
                WHERE e.type IN ['story_insight', 'pattern', 'dynamic_pattern', 'schema_break']
                RETURN e.name AS name, e.type AS type, e.description AS description,
                       e.source_domain AS source_domain
                LIMIT $limit
            """, limit=limit)
            return [dict(r) for r in result]

    def find_best_source_for_concept(
        self,
        concept: dict,
        sources: list[dict]
    ) -> dict | None:
        """Find a source that could provide a good reframe for this concept.

        Looks for sources not yet used for this concept that might share structure.
        """
        # Get existing reframe sources for this concept to avoid duplicates
        with self.kg.driver.session() as session:
            result = session.run("""
                MATCH (c:Concept {name: $name})-[:HAS_REFRAME]->(r:Reframe)
                WHERE r.source_entity IS NOT NULL
                RETURN collect(r.source_entity) AS used_sources
            """, name=concept['name'])
            record = result.single()
            used_sources = set(record['used_sources']) if record else set()

        # Filter to unused sources
        available = [s for s in sources if s['name'] not in used_sources]
        if not available:
            return None

        # Return first available (could add smarter matching later)
        return available[0]

    def generate_reframe(
        self,
        concept: dict,
        source: dict
    ) -> GeneratedReframe | None:
        """Generate a reframe connecting concept to source."""
        prompt = GENERATION_PROMPT.format(
            concept_name=concept['name'],
            concept_description=concept.get('description', 'No description'),
            source_name=source['name'],
            source_type=source['type'],
            source_description=source.get('description', 'No description')
        )

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,  # Slightly higher for creativity
                response_format={"type": "json_object"}
            )

            content = response.choices[0].message.content
            data = json.loads(content)

            return GeneratedReframe(
                concept_name=concept['name'],
                source_entity=source['name'],
                source_type=source['type'],
                reframe_type=data.get('reframe_type', 'Metaphor'),
                domain=data.get('domain', source.get('source_domain', 'general')),
                text=data['text'],
                structural_connection=data.get('structural_connection', '')
            )

        except Exception as e:
            logger.error(f"Failed to generate reframe for {concept['name']}: {e}")
            return None

    def store_generated_reframe(self, reframe: GeneratedReframe) -> bool:
        """Store a generated reframe in Neo4j."""
        reframe_id = str(uuid4())
        created_at = datetime.now(timezone.utc)

        with self.kg.driver.session() as session:
            try:
                session.run("""
                    MATCH (c:Concept {name: $concept_name})
                    CREATE (r:Reframe {
                        id: $reframe_id,
                        concept_id: c.name,
                        type: $type,
                        domain: $domain,
                        text: $text,
                        strength: 0.5,
                        helpful_votes: 0,
                        confusing_votes: 0,
                        created_at: $created_at,
                        source: 'generated_pass3',
                        source_entity: $source_entity,
                        structural_connection: $structural_connection
                    })
                    MERGE (c)-[:HAS_REFRAME]->(r)
                """,
                    concept_name=reframe.concept_name,
                    reframe_id=reframe_id,
                    type=reframe.reframe_type.lower(),
                    domain=reframe.domain,
                    text=reframe.text,
                    created_at=created_at.isoformat(),
                    source_entity=reframe.source_entity,
                    structural_connection=reframe.structural_connection
                )
                logger.info(f"Stored reframe for {reframe.concept_name}: {reframe.text[:50]}...")
                return True
            except Exception as e:
                logger.error(f"Failed to store reframe: {e}")
                return False

    def run_batch_generation(self, max_concepts: int = 10) -> dict:
        """Run Pass 3 batch generation for concepts needing reframes."""
        # Get concepts and sources
        concepts = self.get_concepts_needing_reframes(limit=max_concepts)
        if not concepts:
            logger.info("No concepts found needing reframes")
            return {"concepts": 0, "generated": 0, "stored": 0}

        sources = self.get_story_insights_and_patterns(limit=50)
        if not sources:
            logger.info("No story/pattern sources found in graph")
            return {"concepts": len(concepts), "generated": 0, "stored": 0}

        generated = 0
        stored = 0

        for concept in concepts:
            source = self.find_best_source_for_concept(concept, sources)
            if not source:
                logger.debug(f"No unused source for {concept['name']}")
                continue

            reframe = self.generate_reframe(concept, source)
            if reframe:
                generated += 1
                if self.store_generated_reframe(reframe):
                    stored += 1

        result = {
            "concepts": len(concepts),
            "sources_available": len(sources),
            "generated": generated,
            "stored": stored
        }
        logger.info(f"Pass 3 complete: {result}")
        return result


def run_pass3_batch(max_concepts: int = 10) -> dict:
    """Convenience function to run Pass 3 batch generation."""
    kg = KnowledgeGraph()
    generator = ReframeGenerator(kg)
    return generator.run_batch_generation(max_concepts)


if __name__ == "__main__":
    import sys

    logging.basicConfig(level=logging.INFO)

    max_concepts = int(sys.argv[1]) if len(sys.argv) > 1 else 10
    result = run_pass3_batch(max_concepts)
    print(f"Result: {result}")
