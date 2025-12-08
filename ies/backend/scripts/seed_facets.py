#!/usr/bin/env python3
"""Seed example facets for testing Flow Mode Phase 2B.

This script creates facets for key entities in the knowledge graph,
enabling entity → facet → sub-entity drilling in Flow Mode.

Usage:
    uv run python scripts/seed_facets.py
"""

import asyncio
from ies_backend.services.graph_service import GraphService


# Facet templates from flow-mode-evolution.md
FACET_TEMPLATES = {
    "ADHD": [
        {
            "name": "Diagnosis & Assessment",
            "description": "Diagnostic criteria and assessment tools",
            "order": 0,
            "concepts": ["DSM-5", "assessment", "diagnosis"],
        },
        {
            "name": "Symptoms & Presentation",
            "description": "Observable symptoms and behavioral patterns",
            "order": 1,
            "concepts": ["inattention", "hyperactivity", "impulsivity"],
        },
        {
            "name": "Neurobiology",
            "description": "Brain mechanisms and neuroscience",
            "order": 2,
            "concepts": ["dopamine", "prefrontal cortex", "executive function"],
        },
        {
            "name": "Executive Function",
            "description": "EF deficits and impact",
            "order": 3,
            "concepts": ["working memory", "inhibition", "cognitive flexibility"],
        },
        {
            "name": "Time Perception",
            "description": "Temporal processing differences",
            "order": 4,
            "concepts": ["time blindness", "temporal discounting"],
        },
        {
            "name": "Treatment & Strategies",
            "description": "Interventions and management approaches",
            "order": 5,
            "concepts": ["medication", "therapy", "CBT", "coaching"],
        },
    ],
    "Executive Function": [
        {
            "name": "Components",
            "description": "Core EF components and processes",
            "order": 0,
            "concepts": ["working memory", "inhibition", "cognitive flexibility", "planning"],
        },
        {
            "name": "Development",
            "description": "EF development across lifespan",
            "order": 1,
            "concepts": ["childhood", "adolescence", "maturation"],
        },
        {
            "name": "Assessment",
            "description": "EF measurement and evaluation",
            "order": 2,
            "concepts": ["neuropsychological testing", "behavioral assessment"],
        },
        {
            "name": "Impairments",
            "description": "EF deficits and disorders",
            "order": 3,
            "concepts": ["ADHD", "autism", "traumatic brain injury"],
        },
        {
            "name": "Interventions",
            "description": "EF training and support",
            "order": 4,
            "concepts": ["cognitive training", "scaffolding", "compensation strategies"],
        },
    ],
}


async def seed_facets():
    """Create facets for entities in the knowledge graph."""
    print("Seeding facets for Flow Mode Phase 2B...")

    for entity_name, facets in FACET_TEMPLATES.items():
        print(f"\nProcessing entity: {entity_name}")

        for facet_data in facets:
            facet_name = facet_data["name"]
            description = facet_data["description"]
            order = facet_data["order"]

            print(f"  Creating facet: {facet_name}")
            success = await GraphService.create_facet(
                entity_name=entity_name,
                facet_name=facet_name,
                description=description,
                order=order,
            )

            if success:
                print(f"    ✓ Created {facet_name}")

                # Add concepts to facet (if they exist in graph)
                for concept_name in facet_data.get("concepts", []):
                    added = await GraphService.add_entity_to_facet(
                        facet_name=facet_name,
                        entity_name=entity_name,
                        concept_name=concept_name,
                    )
                    if added:
                        print(f"      + Added {concept_name}")
                    else:
                        print(f"      - Skipped {concept_name} (not found in graph)")
            else:
                print(f"    ✗ Failed to create {facet_name}")

    print("\n✓ Facet seeding complete!")


async def verify_facets():
    """Verify that facets were created successfully."""
    print("\nVerifying facets...")

    for entity_name in FACET_TEMPLATES.keys():
        result = await GraphService.get_entity_facets(entity_name)

        if result:
            facet_count = len(result["facets"])
            entity_count = sum(f["entity_count"] for f in result["facets"])
            print(f"  {entity_name}: {facet_count} facets, {entity_count} total entities")
        else:
            print(f"  {entity_name}: No facets found (entity may not exist in graph)")


async def main():
    """Main entry point."""
    await seed_facets()
    await verify_facets()


if __name__ == "__main__":
    asyncio.run(main())
