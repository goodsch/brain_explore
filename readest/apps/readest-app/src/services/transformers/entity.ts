/**
 * Entity transformer for overlay flow mode.
 *
 * Wraps known entity names in styled <span> elements for highlighting
 * and interaction in the reader view.
 */

import type { Transformer, TransformContext, EntityOverlay } from './types';

const ENTITY_TYPE_CLASSES: Record<string, string> = {
  Concept: 'entity-concept',
  Person: 'entity-person',
  Theory: 'entity-theory',
  Framework: 'entity-framework',
  Assessment: 'entity-assessment',
  Model: 'entity-theory',
  Researcher: 'entity-person',
};

/**
 * Escape special regex characters in entity name.
 */
function escapeRegex(str: string): string {
  return str.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

/**
 * Build regex pattern for entity matching.
 * Matches whole words only, case-insensitive.
 */
function buildEntityPattern(entities: EntityOverlay[]): RegExp | null {
  if (entities.length === 0) return null;

  // Sort by length descending to match longer phrases first
  const sorted = [...entities].sort((a, b) => b.name.length - a.name.length);

  const patterns = sorted.map(e => escapeRegex(e.name));
  // Word boundary matching, case-insensitive
  return new RegExp(`\\b(${patterns.join('|')})\\b`, 'gi');
}

/**
 * Create entity name to data lookup map.
 */
function buildEntityMap(entities: EntityOverlay[]): Map<string, EntityOverlay> {
  const map = new Map<string, EntityOverlay>();
  for (const entity of entities) {
    map.set(entity.name.toLowerCase(), entity);
  }
  return map;
}

/**
 * Transform HTML content to wrap entity mentions in styled spans.
 */
export const entityTransformer: Transformer = {
  name: 'entity',

  transform: async (ctx: TransformContext): Promise<string> => {
    const { entityOverlay, content } = ctx;

    // Skip if not enabled or no entities
    if (!entityOverlay?.enabled || !entityOverlay.entities?.length) {
      return content;
    }

    // Filter to visible types only
    const visibleEntities = entityOverlay.entities.filter(
      e => entityOverlay.visibleTypes.includes(e.type)
    );

    if (visibleEntities.length === 0) {
      return content;
    }

    const pattern = buildEntityPattern(visibleEntities);
    if (!pattern) return content;

    const entityMap = buildEntityMap(visibleEntities);

    // Parse HTML and process text nodes only (avoid matching in tags/attributes)
    // Simple approach: split on HTML tags, process text parts
    const parts = content.split(/(<[^>]+>)/);

    const transformed = parts.map(part => {
      // Skip HTML tags
      if (part.startsWith('<')) return part;

      // Replace entity mentions in text
      return part.replace(pattern, (match) => {
        const entity = entityMap.get(match.toLowerCase());
        if (!entity) return match;

        const typeClass = ENTITY_TYPE_CLASSES[entity.type] || 'entity-default';

        return `<span class="entity-link ${typeClass}" data-entity-name="${entity.name}" data-entity-type="${entity.type}">${match}</span>`;
      });
    });

    return transformed.join('');
  },
};
