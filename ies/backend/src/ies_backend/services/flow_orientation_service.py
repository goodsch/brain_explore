"""Service for generating Flow orientation phase content.

Analyzes spark context to extract entities and suggest exploration strands.
"""

import uuid
from typing import List, Tuple

from ies_backend.schemas.flow_session import (
    OrientationRequest,
    OrientationResponse,
    EntitySummary,
    Strand,
)
from ies_backend.services.graph_service import GraphService


class FlowOrientationService:
    """Generates orientation content for Flow initiation."""

    @classmethod
    async def generate_orientation(cls, request: OrientationRequest) -> OrientationResponse:
        """Generate strand proposals from spark context.

        Steps:
        1. Extract text content from the request
        2. Search knowledge graph for matching entities
        3. For each matched entity, find related entities
        4. Generate strands based on relationship patterns
        """
        # Get text to analyze
        text = cls._get_text_from_request(request)

        if not text:
            # No text context - return empty orientation
            return OrientationResponse(
                extracted_entities=[],
                suggested_strands=cls._generate_default_strands()
            )

        # Search for entities matching the text
        graph_service = GraphService()
        matched_entities, strands = await cls._analyze_context(graph_service, text)

        return OrientationResponse(
            extracted_entities=matched_entities,
            suggested_strands=strands
        )

    @classmethod
    def _get_text_from_request(cls, request: OrientationRequest) -> str:
        """Extract text content to analyze from the request."""
        # Priority: selected text > note title > empty
        if request.text:
            return request.text
        if request.note_title:
            return request.note_title
        return ""

    @classmethod
    async def _analyze_context(
        cls,
        graph_service: GraphService,
        text: str
    ) -> Tuple[List[EntitySummary], List[Strand]]:
        """Analyze text and generate entities and strands."""
        # Search for concepts matching the text
        search_results = await graph_service.search_concepts(text, limit=10)

        if not search_results:
            # No matches - try with individual words for longer text
            if len(text.split()) > 3:
                words = text.split()
                for word in words[:5]:
                    if len(word) > 3:
                        results = await graph_service.search_concepts(word, limit=3)
                        search_results.extend(results)

        if not search_results:
            # Still no matches - return defaults
            return [], cls._generate_default_strands()

        # Convert to EntitySummary
        entities = []
        seen_ids = set()
        for result in search_results[:8]:  # Limit to 8 entities
            if result.get("id") in seen_ids:
                continue
            seen_ids.add(result.get("id"))

            entities.append(EntitySummary(
                id=result.get("id", str(uuid.uuid4())),
                name=result.get("name", result.get("label", "Unknown")),
                type=result.get("type", result.get("labels", ["Unknown"])[0] if result.get("labels") else "Unknown"),
                summary=result.get("description", result.get("summary", None)),
                connection_count=result.get("connection_count", 0)
            ))

        # Generate strands based on entities
        strands = await cls._generate_strands_from_entities(graph_service, entities)

        return entities, strands

    @classmethod
    async def _generate_strands_from_entities(
        cls,
        graph_service: GraphService,
        entities: List[EntitySummary]
    ) -> List[Strand]:
        """Generate exploration strands based on found entities."""
        strands = []

        if not entities:
            return cls._generate_default_strands()

        # Group entities by type for strand generation
        entities_by_type = {}
        for entity in entities:
            entity_type = entity.type or "concept"
            if entity_type not in entities_by_type:
                entities_by_type[entity_type] = []
            entities_by_type[entity_type].append(entity)

        # Strand 1: Main concept exploration
        if entities:
            primary = entities[0]
            strands.append(Strand(
                id=str(uuid.uuid4()),
                name=f"Understanding {primary.name}",
                description=f"Deep dive into {primary.name} and its connections",
                starting_entities=[e.id for e in entities[:3]]
            ))

        # Strand 2: Connections and relationships
        if len(entities) > 1:
            strands.append(Strand(
                id=str(uuid.uuid4()),
                name="Connecting the Dots",
                description=f"Explore relationships between {entities[0].name} and related concepts",
                starting_entities=[e.id for e in entities[:4]]
            ))

        # Strand 3: Type-specific strand (if multiple types)
        for entity_type, type_entities in entities_by_type.items():
            if entity_type.lower() in ["person", "framework", "theory"]:
                strands.append(Strand(
                    id=str(uuid.uuid4()),
                    name=f"{entity_type.title()} Perspective",
                    description=f"Explore through the lens of {type_entities[0].name}",
                    starting_entities=[e.id for e in type_entities[:3]]
                ))
                break

        # Strand 4: Practical application (if we have mechanisms/patterns)
        mechanisms = entities_by_type.get("mechanism", []) + entities_by_type.get("pattern", [])
        if mechanisms:
            strands.append(Strand(
                id=str(uuid.uuid4()),
                name="Practical Application",
                description="Understanding how these concepts work in practice",
                starting_entities=[e.id for e in mechanisms[:3]]
            ))

        # Ensure we have at least 3 strands
        while len(strands) < 3:
            strands.extend(cls._generate_default_strands())
            strands = strands[:5]  # Max 5 strands

        return strands[:5]

    @classmethod
    def _generate_default_strands(cls) -> List[Strand]:
        """Generate default exploration strands when no entities found."""
        return [
            Strand(
                id=str(uuid.uuid4()),
                name="Free Exploration",
                description="Browse the knowledge graph to discover interesting connections",
                starting_entities=[]
            ),
            Strand(
                id=str(uuid.uuid4()),
                name="Recent Discoveries",
                description="Explore concepts from your recent reading and thinking sessions",
                starting_entities=[]
            ),
            Strand(
                id=str(uuid.uuid4()),
                name="Core Frameworks",
                description="Explore fundamental frameworks and theories",
                starting_entities=[]
            )
        ]
