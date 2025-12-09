"""Pass 3 LLM Enrichment Service.

Orchestrates multiple enrichment types for book entities:
1. Reframes - Metaphors and analogies via existing ReframeService
2. Mechanisms - Step-by-step process explanations
3. Patterns - Cross-domain structural templates
4. Rich Descriptions - Enhanced entity descriptions

Prioritizes high-value entities and includes comprehensive rate limiting.
"""

from __future__ import annotations

import asyncio
import json
import logging
import re
from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import uuid4

from anthropic import AsyncAnthropic

from ies_backend.config import settings
from ies_backend.services.neo4j_client import Neo4jClient
from ies_backend.services.reframe_service import reframe_service

logger = logging.getLogger(__name__)


# Entity types eligible for mechanism extraction
MECHANISM_ELIGIBLE_TYPES = {"Concept", "Theory", "Framework", "DynamicPattern"}

# Entity types eligible for pattern detection
PATTERN_ELIGIBLE_TYPES = {"Concept", "Theory", "Framework", "DynamicPattern"}


# LLM Prompts

MECHANISM_EXTRACTION_PROMPT = """Analyze this concept and extract a mechanistic explanation of how it works.

**Concept:** {concept_name}
**Type:** {concept_type}
**Current Description:** {concept_description}

**Context from book "{book_title}":**
{context_chunks}

**Instructions:**
1. Determine if this concept involves a process or mechanism (does it describe HOW something works?)
2. If yes, break down the mechanism into clear sequential steps
3. Identify triggers/inputs that initiate the mechanism
4. Identify outcomes/effects of the mechanism
5. Keep explanations ADHD-friendly:
   - Use short, concrete steps (3-7 steps ideal)
   - Avoid jargon where possible
   - Make progression clear and logical

**Return JSON:**
{{
  "has_mechanism": true/false,
  "mechanism": {{
    "name": "descriptive name for the mechanism",
    "description": "one-sentence overview",
    "steps": [
      "Step 1: [action/stage]",
      "Step 2: [action/stage]",
      ...
    ],
    "triggers": ["trigger 1", "trigger 2", ...],
    "outcomes": ["outcome 1", "outcome 2", ...],
    "confidence": 0.0-1.0
  }}
}}

If has_mechanism is false, set mechanism to null.
"""


PATTERN_DETECTION_PROMPT = """Analyze this concept to determine if it represents a recurring structural pattern.

**Concept:** {concept_name}
**Type:** {concept_type}
**Description:** {concept_description}

**Context from book:**
{context_chunks}

**Instructions:**
A pattern is a structural template that can appear across multiple domains. Examples:
- Feedback Loop (control systems, neuroscience, economics)
- Tipping Point (phase transitions, social movements, ecosystems)
- Emergence (complexity science, consciousness, culture)
- Oscillation (electrical circuits, mood cycles, market swings)

1. Determine if this concept describes a structural pattern (not just a domain-specific idea)
2. If yes, identify:
   - Core structural elements (what are the key components?)
   - Variants (how does the pattern manifest differently?)
   - Cross-domain examples (where else does this pattern appear?)

**Return JSON:**
{{
  "is_pattern": true/false,
  "pattern": {{
    "name": "pattern name",
    "description": "structural description (domain-agnostic)",
    "structural_elements": ["element 1", "element 2", ...],
    "variants": ["variant 1", "variant 2", ...],
    "examples_across_domains": [
      "domain 1: example",
      "domain 2: example",
      ...
    ],
    "confidence": 0.0-1.0
  }}
}}

If is_pattern is false, set pattern to null.
"""


DESCRIPTION_ENHANCEMENT_PROMPT = """Expand the description of this concept using context from the book.

**Concept:** {concept_name}
**Type:** {concept_type}
**Current Description:** {current_description}

**Context from book "{book_title}":**
{context_chunks}

**Instructions:**
1. Preserve the core meaning of the current description
2. Expand to 2-3 sentences (100-150 words)
3. Make it accessible to non-experts
4. Include key aspects: what it is, why it matters, how it relates to other concepts
5. Use concrete examples where possible

**Return JSON:**
{{
  "enhanced_description": "expanded description here",
  "key_aspects": ["aspect 1", "aspect 2", ...],
  "confidence": 0.0-1.0
}}
"""


class RateLimiter:
    """Rate limiter for API calls."""

    def __init__(self, calls_per_minute: int = 60) -> None:
        self.calls_per_minute = calls_per_minute
        self.call_times: list[datetime] = []

    async def wait_if_needed(self) -> None:
        """Sleep if approaching rate limit."""
        now = datetime.now()
        minute_ago = now - timedelta(minutes=1)

        # Remove old calls
        self.call_times = [t for t in self.call_times if t > minute_ago]

        if len(self.call_times) >= self.calls_per_minute:
            # Calculate sleep time needed
            sleep_time = (self.call_times[0] - minute_ago).total_seconds()
            if sleep_time > 0:
                logger.debug(f"Rate limit approached, sleeping {sleep_time:.2f}s")
                await asyncio.sleep(sleep_time)

        self.call_times.append(now)


def calculate_enrichment_priority(entity: dict[str, Any]) -> float:
    """Calculate priority score for entity enrichment (0-1).

    Higher scores = higher priority for enrichment.

    Factors:
    - Mention count (max 0.3)
    - Entity type priority (0.2 for central types)
    - Missing description (0.3)
    - No reframes yet (0.2)
    """
    score = 0.0

    # High mention count = high value
    mentions = entity.get("mention_count", 0)
    score += min(mentions / 50, 0.3)  # Max 0.3 from mentions

    # Central entity types get priority
    priority_types = {"Concept", "Theory", "Framework", "Mechanism"}
    if entity.get("type") in priority_types:
        score += 0.2

    # Missing description = needs enrichment
    desc = entity.get("description", "")
    if not desc or len(desc) < 50:
        score += 0.3

    # No reframes yet
    if not entity.get("has_reframes", False):
        score += 0.2

    return min(score, 1.0)


def should_extract_mechanism(entity: dict[str, Any]) -> bool:
    """Determine if entity is eligible for mechanism extraction."""
    if entity.get("type") not in MECHANISM_ELIGIBLE_TYPES:
        return False

    # Skip if already has mechanism
    if entity.get("has_mechanism", False):
        return False

    # Require minimum description length
    desc = entity.get("description", "")
    if len(desc) < 30:
        return False

    return True


class EnrichmentService:
    """Orchestrates Pass 3 LLM enrichment for book entities."""

    def __init__(self, anthropic_client: AsyncAnthropic | None = None) -> None:
        self._anthropic_client = anthropic_client
        self.rate_limiter = RateLimiter(calls_per_minute=30)  # Conservative limit

    @property
    def anthropic_client(self) -> AsyncAnthropic:
        """Return or create the Anthropic client lazily."""
        if self._anthropic_client is None:
            if not settings.anthropic_api_key:
                raise RuntimeError("Anthropic API key is not configured")
            self._anthropic_client = AsyncAnthropic(api_key=settings.anthropic_api_key)
        return self._anthropic_client

    async def enrich_book_entities(
        self,
        calibre_id: int,
        enable_reframes: bool = True,
        enable_mechanisms: bool = True,
        enable_patterns: bool = True,
        enable_descriptions: bool = True,
        max_entities: int = 10,
    ) -> dict[str, Any]:
        """Run Pass 3 enrichment for all high-value entities in a book.

        Args:
            calibre_id: Book ID from Calibre
            enable_reframes: Generate reframes (default True)
            enable_mechanisms: Extract mechanisms (default True)
            enable_patterns: Detect patterns (default True)
            enable_descriptions: Enhance descriptions (default True)
            max_entities: Max entities to enrich (default 10)

        Returns:
            Statistics dict with counts of enrichments
        """
        logger.info(f"Starting Pass 3 enrichment for book {calibre_id}")

        stats = {
            "calibre_id": calibre_id,
            "reframes_generated": 0,
            "mechanisms_extracted": 0,
            "patterns_detected": 0,
            "descriptions_enriched": 0,
            "entities_processed": 0,
            "errors": 0,
        }

        # Load book context
        book_context = await self._get_book_context(calibre_id)
        if not book_context:
            logger.error(f"Book {calibre_id} not found in graph")
            return stats

        # Get prioritized entities
        entities = await self._get_prioritized_entities(calibre_id, limit=max_entities)
        logger.info(f"Enriching {len(entities)} high-priority entities")

        # Process each entity
        for entity in entities:
            stats["entities_processed"] += 1
            logger.info(
                f"Enriching entity {stats['entities_processed']}/{len(entities)}: "
                f"{entity['name']} ({entity['type']})"
            )

            try:
                # 1. Reframes (cheapest, always useful)
                if enable_reframes and not entity.get("has_reframes"):
                    reframe_count = await self._generate_reframes_for_entity(
                        entity, book_context
                    )
                    stats["reframes_generated"] += reframe_count

                # 2. Mechanisms (expensive, selective)
                if enable_mechanisms and should_extract_mechanism(entity):
                    if await self._extract_mechanism_for_entity(entity, book_context):
                        stats["mechanisms_extracted"] += 1

                # 3. Patterns (expensive, high value)
                if enable_patterns and entity["type"] in PATTERN_ELIGIBLE_TYPES:
                    if await self._detect_pattern_for_entity(entity, book_context):
                        stats["patterns_detected"] += 1

                # 4. Descriptions (cheap, fill gaps)
                if enable_descriptions and len(entity.get("description", "")) < 50:
                    if await self._enhance_description_for_entity(entity, book_context):
                        stats["descriptions_enriched"] += 1

            except Exception as e:
                logger.error(f"Enrichment failed for {entity['name']}: {e}")
                stats["errors"] += 1
                continue

        # Update book status to "enriched"
        await self._update_book_status(calibre_id, "enriched")

        logger.info(f"Pass 3 complete: {stats}")
        return stats

    async def _generate_reframes_for_entity(
        self, entity: dict[str, Any], book_context: dict[str, Any]
    ) -> int:
        """Generate reframes for entity using existing ReframeService."""
        await self.rate_limiter.wait_if_needed()

        try:
            # Get entity ID for reframe service
            entity_id = entity.get("id") or entity.get("name")

            reframes = await reframe_service.generate_reframes(
                concept_id=entity_id, count=3
            )
            logger.info(f"Generated {len(reframes)} reframes for {entity['name']}")
            return len(reframes)
        except Exception as e:
            logger.error(f"Reframe generation failed for {entity['name']}: {e}")
            return 0

    async def _extract_mechanism_for_entity(
        self, entity: dict[str, Any], book_context: dict[str, Any]
    ) -> bool:
        """Extract mechanism explanation for entity."""
        await self.rate_limiter.wait_if_needed()

        try:
            # Get relevant chunks mentioning this entity
            chunks = await self._get_entity_chunks(
                entity_name=entity["name"],
                calibre_id=book_context["calibre_id"],
                limit=5,
            )

            if not chunks:
                logger.debug(f"No chunks found for {entity['name']}, skipping mechanism extraction")
                return False

            context_text = "\n\n---\n\n".join([c["content"] for c in chunks])

            prompt = MECHANISM_EXTRACTION_PROMPT.format(
                concept_name=entity["name"],
                concept_type=entity.get("type", "Unknown"),
                concept_description=entity.get("description", "No description available"),
                book_title=book_context["title"],
                context_chunks=context_text[:3000],  # Limit token usage
            )

            message = await self.anthropic_client.messages.create(
                model="claude-3-5-haiku-20241022",
                max_tokens=1024,
                messages=[{"role": "user", "content": prompt}],
            )

            result = self._parse_json_response(message.content[0].text)

            if (
                result
                and result.get("has_mechanism")
                and result.get("mechanism")
                and result["mechanism"].get("confidence", 0) >= 0.7
            ):
                # Store in Neo4j
                await self._create_mechanism_node(
                    mechanism_data=result["mechanism"],
                    entity_id=entity.get("id") or entity["name"],
                    book_calibre_id=book_context["calibre_id"],
                    source_chunks=[c["id"] for c in chunks],
                )
                logger.info(f"Extracted mechanism for {entity['name']}")
                return True

            return False

        except Exception as e:
            logger.error(f"Mechanism extraction failed for {entity['name']}: {e}")
            return False

    async def _detect_pattern_for_entity(
        self, entity: dict[str, Any], book_context: dict[str, Any]
    ) -> bool:
        """Detect if entity represents a structural pattern."""
        await self.rate_limiter.wait_if_needed()

        try:
            # Get context
            chunks = await self._get_entity_chunks(
                entity_name=entity["name"],
                calibre_id=book_context["calibre_id"],
                limit=3,
            )

            if not chunks:
                logger.debug(f"No chunks found for {entity['name']}, skipping pattern detection")
                return False

            context_text = "\n\n---\n\n".join([c["content"] for c in chunks])

            prompt = PATTERN_DETECTION_PROMPT.format(
                concept_name=entity["name"],
                concept_type=entity.get("type", "Unknown"),
                concept_description=entity.get("description", "No description"),
                context_chunks=context_text[:2000],
            )

            message = await self.anthropic_client.messages.create(
                model="claude-3-5-haiku-20241022",
                max_tokens=1024,
                messages=[{"role": "user", "content": prompt}],
            )

            result = self._parse_json_response(message.content[0].text)

            if (
                result
                and result.get("is_pattern")
                and result.get("pattern")
                and result["pattern"].get("confidence", 0) >= 0.75
            ):
                # Create Pattern node if new, or link existing pattern
                await self._create_or_link_pattern(
                    pattern_data=result["pattern"],
                    entity_id=entity.get("id") or entity["name"],
                    book_calibre_id=book_context["calibre_id"],
                )
                logger.info(f"Detected pattern for {entity['name']}")
                return True

            return False

        except Exception as e:
            logger.error(f"Pattern detection failed for {entity['name']}: {e}")
            return False

    async def _enhance_description_for_entity(
        self, entity: dict[str, Any], book_context: dict[str, Any]
    ) -> bool:
        """Enhance entity description with richer content."""
        await self.rate_limiter.wait_if_needed()

        current_desc = entity.get("description", "")

        # Only enhance if description is too short
        if len(current_desc) >= 50:
            return False

        try:
            # Get context chunks
            chunks = await self._get_entity_chunks(
                entity_name=entity["name"],
                calibre_id=book_context["calibre_id"],
                limit=3,
            )

            if not chunks:
                logger.debug(f"No chunks found for {entity['name']}, skipping description enhancement")
                return False

            context_text = "\n\n---\n\n".join([c["content"] for c in chunks])

            prompt = DESCRIPTION_ENHANCEMENT_PROMPT.format(
                concept_name=entity["name"],
                concept_type=entity.get("type", "Unknown"),
                current_description=current_desc or "No description available",
                book_title=book_context["title"],
                context_chunks=context_text[:2000],
            )

            message = await self.anthropic_client.messages.create(
                model="claude-3-5-haiku-20241022",
                max_tokens=512,
                messages=[{"role": "user", "content": prompt}],
            )

            result = self._parse_json_response(message.content[0].text)

            if result and result.get("confidence", 0) >= 0.7:
                # Update entity description
                await self._update_entity_description(
                    entity_id=entity.get("id") or entity["name"],
                    description=result["enhanced_description"],
                    key_aspects=result.get("key_aspects", []),
                )
                logger.info(f"Enhanced description for {entity['name']}")
                return True

            return False

        except Exception as e:
            logger.error(f"Description enhancement failed for {entity['name']}: {e}")
            return False

    async def _get_book_context(self, calibre_id: int) -> dict[str, Any] | None:
        """Load book metadata for context."""
        try:
            results = await Neo4jClient.execute_query(
                """
                MATCH (b:Book {calibre_id: $calibre_id})
                RETURN b.title as title, b.author as author,
                       b.genres as genres, b.description as description
                """,
                {"calibre_id": calibre_id},
            )

            if not results:
                return None

            record = results[0]
            return {
                "calibre_id": calibre_id,
                "title": record["title"],
                "author": record.get("author", "Unknown"),
                "genres": record.get("genres", []),
                "description": record.get("description", ""),
            }
        except Exception as e:
            logger.error(f"Failed to load book context for {calibre_id}: {e}")
            return None

    async def _get_prioritized_entities(
        self, calibre_id: int, limit: int = 20
    ) -> list[dict[str, Any]]:
        """Get high-value entities for enrichment."""
        try:
            results = await Neo4jClient.execute_query(
                """
                MATCH (b:Book {calibre_id: $calibre_id})-[:MENTIONS]->(e)
                WITH e, count(*) as mention_count
                RETURN e.id as id, e.name as name, e.type as type,
                       e.description as description, mention_count,
                       exists((e)-[:HAS_REFRAME]->()) as has_reframes,
                       exists((e)<-[:EXPLAINS]-()) as has_mechanism
                ORDER BY mention_count DESC
                LIMIT $limit
                """,
                {"calibre_id": calibre_id, "limit": limit},
            )

            entities = []
            for record in results:
                entity = dict(record)
                entity["priority"] = calculate_enrichment_priority(entity)
                entities.append(entity)

            # Sort by calculated priority
            entities.sort(key=lambda e: e["priority"], reverse=True)
            return entities

        except Exception as e:
            logger.error(f"Failed to get prioritized entities for {calibre_id}: {e}")
            return []

    async def _get_entity_chunks(
        self, entity_name: str, calibre_id: int, limit: int = 5
    ) -> list[dict[str, Any]]:
        """Get text chunks mentioning an entity from a specific book."""
        try:
            results = await Neo4jClient.execute_query(
                """
                MATCH (b:Book {calibre_id: $calibre_id})-[:HAS_CHUNK]->(c:Chunk)
                WHERE toLower(c.text) CONTAINS toLower($entity_name)
                   OR toLower(c.content) CONTAINS toLower($entity_name)
                RETURN c.id as id, coalesce(c.text, c.content) as content
                LIMIT $limit
                """,
                {"calibre_id": calibre_id, "entity_name": entity_name, "limit": limit},
            )

            return [{"id": r["id"], "content": r["content"]} for r in results]

        except Exception as e:
            logger.error(f"Failed to get chunks for {entity_name}: {e}")
            return []

    async def _create_mechanism_node(
        self,
        mechanism_data: dict[str, Any],
        entity_id: str,
        book_calibre_id: int,
        source_chunks: list[str],
    ) -> str:
        """Create Mechanism node and relationships."""
        mechanism_id = str(uuid4())

        try:
            query = """
            MATCH (e) WHERE e.id = $entity_id OR e.name = $entity_id
            MATCH (b:Book {calibre_id: $calibre_id})
            CREATE (m:Mechanism {
              id: $mechanism_id,
              name: $name,
              description: $description,
              steps: $steps,
              triggers: $triggers,
              outcomes: $outcomes,
              confidence: $confidence,
              source_book_calibre_id: $calibre_id,
              source_chunks: $source_chunks,
              created_at: datetime()
            })
            MERGE (m)-[:EXPLAINS]->(e)
            MERGE (b)-[:DESCRIBES]->(m)
            RETURN m.id as id
            """

            results = await Neo4jClient.execute_write(
                query,
                {
                    "mechanism_id": mechanism_id,
                    "entity_id": entity_id,
                    "calibre_id": book_calibre_id,
                    "name": mechanism_data["name"],
                    "description": mechanism_data["description"],
                    "steps": mechanism_data["steps"],
                    "triggers": mechanism_data["triggers"],
                    "outcomes": mechanism_data["outcomes"],
                    "confidence": mechanism_data["confidence"],
                    "source_chunks": source_chunks,
                },
            )

            if results:
                logger.debug(f"Created Mechanism node: {mechanism_id}")
                return mechanism_id
            else:
                logger.warning(f"Failed to create Mechanism node for entity {entity_id}")
                return mechanism_id

        except Exception as e:
            logger.error(f"Failed to create mechanism node: {e}")
            raise

    async def _create_or_link_pattern(
        self, pattern_data: dict[str, Any], entity_id: str, book_calibre_id: int
    ) -> str:
        """Create new Pattern node or link to existing one."""
        # Check if pattern already exists (by name similarity)
        existing = await self._find_similar_pattern(pattern_data["name"])

        if existing:
            # Link entity to existing pattern
            pattern_id = existing["id"]
            await self._link_entity_to_pattern(entity_id, pattern_id, book_calibre_id)
            return pattern_id
        else:
            # Create new Pattern node
            pattern_id = str(uuid4())

            try:
                query = """
                MATCH (e) WHERE e.id = $entity_id OR e.name = $entity_id
                MATCH (b:Book {calibre_id: $calibre_id})
                CREATE (p:Pattern {
                  id: $pattern_id,
                  name: $name,
                  description: $description,
                  structural_elements: $structural_elements,
                  variants: $variants,
                  examples_across_domains: $examples,
                  source_books: [$calibre_id],
                  created_at: datetime()
                })
                MERGE (p)-[:APPEARS_IN]->(e)
                MERGE (b)-[:DEMONSTRATES]->(p)
                RETURN p.id as id
                """

                results = await Neo4jClient.execute_write(
                    query,
                    {
                        "pattern_id": pattern_id,
                        "entity_id": entity_id,
                        "calibre_id": book_calibre_id,
                        "name": pattern_data["name"],
                        "description": pattern_data["description"],
                        "structural_elements": pattern_data["structural_elements"],
                        "variants": pattern_data["variants"],
                        "examples": pattern_data["examples_across_domains"],
                    },
                )

                if results:
                    logger.debug(f"Created Pattern node: {pattern_id}")
                else:
                    logger.warning(f"Failed to create Pattern node for entity {entity_id}")

                return pattern_id

            except Exception as e:
                logger.error(f"Failed to create pattern node: {e}")
                raise

    async def _find_similar_pattern(
        self, pattern_name: str
    ) -> dict[str, Any] | None:
        """Find existing pattern by name similarity."""
        try:
            results = await Neo4jClient.execute_query(
                """
                MATCH (p:Pattern)
                WHERE toLower(p.name) = toLower($pattern_name)
                RETURN p.id as id, p.name as name
                LIMIT 1
                """,
                {"pattern_name": pattern_name},
            )

            return dict(results[0]) if results else None

        except Exception as e:
            logger.error(f"Failed to find similar pattern: {e}")
            return None

    async def _link_entity_to_pattern(
        self, entity_id: str, pattern_id: str, book_calibre_id: int
    ) -> None:
        """Link entity to existing pattern and update source_books."""
        try:
            query = """
            MATCH (e) WHERE e.id = $entity_id OR e.name = $entity_id
            MATCH (p:Pattern {id: $pattern_id})
            MATCH (b:Book {calibre_id: $calibre_id})
            MERGE (p)-[:APPEARS_IN]->(e)
            MERGE (b)-[:DEMONSTRATES]->(p)
            WITH p
            SET p.source_books = CASE
                WHEN NOT $calibre_id IN p.source_books
                THEN p.source_books + $calibre_id
                ELSE p.source_books
            END
            """

            await Neo4jClient.execute_write(
                query,
                {
                    "entity_id": entity_id,
                    "pattern_id": pattern_id,
                    "calibre_id": book_calibre_id,
                },
            )

            logger.debug(f"Linked entity {entity_id} to pattern {pattern_id}")

        except Exception as e:
            logger.error(f"Failed to link entity to pattern: {e}")
            raise

    async def _update_entity_description(
        self, entity_id: str, description: str, key_aspects: list[str]
    ) -> None:
        """Update entity description in Neo4j."""
        try:
            query = """
            MATCH (e) WHERE e.id = $entity_id OR e.name = $entity_id
            SET e.description = $description,
                e.key_aspects = $key_aspects,
                e.description_enriched_at = datetime()
            """

            await Neo4jClient.execute_write(
                query,
                {
                    "entity_id": entity_id,
                    "description": description,
                    "key_aspects": key_aspects,
                },
            )

            logger.debug(f"Updated description for entity {entity_id}")

        except Exception as e:
            logger.error(f"Failed to update entity description: {e}")
            raise

    async def _update_book_status(self, calibre_id: int, status: str) -> None:
        """Update book processing status."""
        try:
            query = """
            MATCH (b:Book {calibre_id: $calibre_id})
            SET b.processing_status = $status,
                b.enriched_at = datetime()
            """

            await Neo4jClient.execute_write(
                query, {"calibre_id": calibre_id, "status": status}
            )

            logger.info(f"Updated book {calibre_id} status to: {status}")

        except Exception as e:
            logger.error(f"Failed to update book status: {e}")

    @staticmethod
    def _parse_json_response(text: str) -> dict[str, Any] | None:
        """Parse LLM JSON response, handling markdown code blocks."""
        cleaned = text.strip()

        # Remove markdown code blocks
        if "```json" in cleaned:
            cleaned = cleaned.split("```json", 1)[1].split("```", 1)[0]
        elif cleaned.startswith("```"):
            cleaned = cleaned.strip("`")

        # Find JSON object in text
        start = cleaned.find("{")
        end = cleaned.rfind("}") + 1

        if start >= 0 and end > start:
            try:
                return json.loads(cleaned[start:end])
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON response: {e}")
                return None

        return None


# Singleton-style access
enrichment_service = EnrichmentService()
