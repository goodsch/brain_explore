import { useCallback, useEffect, useRef } from 'react';
import type { Rendition, Contents } from 'epubjs';
import { useFlowStore, type EntityType } from '../store/flowStore';

/**
 * Entity type to CSS class mapping for highlighting
 */
const ENTITY_TYPE_CLASSES: Record<EntityType, string> = {
  Concept: 'entity-highlight-concept',
  Person: 'entity-highlight-person',
  Theory: 'entity-highlight-theory',
  Framework: 'entity-highlight-framework',
  Assessment: 'entity-highlight-assessment',
};

/**
 * CSS styles for entity highlighting in the epub content
 */
const ENTITY_HIGHLIGHT_STYLES = `
  .entity-highlight {
    cursor: pointer;
    border-radius: 2px;
    padding: 0 2px;
    transition: background-color 0.15s ease;
  }
  .entity-highlight:hover {
    opacity: 0.8;
  }
  .entity-highlight-concept {
    background-color: rgba(37, 99, 235, 0.15);
    color: inherit;
  }
  .entity-highlight-concept:hover {
    background-color: rgba(37, 99, 235, 0.25);
  }
  .entity-highlight-person {
    background-color: rgba(5, 150, 105, 0.15);
    color: inherit;
  }
  .entity-highlight-person:hover {
    background-color: rgba(5, 150, 105, 0.25);
  }
  .entity-highlight-theory {
    background-color: rgba(124, 58, 237, 0.15);
    color: inherit;
  }
  .entity-highlight-theory:hover {
    background-color: rgba(124, 58, 237, 0.25);
  }
  .entity-highlight-framework {
    background-color: rgba(234, 88, 12, 0.15);
    color: inherit;
  }
  .entity-highlight-framework:hover {
    background-color: rgba(234, 88, 12, 0.25);
  }
  .entity-highlight-assessment {
    background-color: rgba(220, 38, 38, 0.15);
    color: inherit;
  }
  .entity-highlight-assessment:hover {
    background-color: rgba(220, 38, 38, 0.25);
  }
`;

/**
 * Build a trie for efficient entity name matching
 */
interface TrieNode {
  children: Map<string, TrieNode>;
  entity: { name: string; type: EntityType } | null;
}

function buildEntityTrie(entities: Array<{ name: string; type: EntityType }>): TrieNode {
  const root: TrieNode = { children: new Map(), entity: null };

  for (const entity of entities) {
    let node = root;
    const words = entity.name.toLowerCase().split(/\s+/);

    for (const word of words) {
      if (!node.children.has(word)) {
        node.children.set(word, { children: new Map(), entity: null });
      }
      node = node.children.get(word)!;
    }
    node.entity = entity;
  }

  return root;
}

/**
 * Process text content to add entity highlights
 */
function processTextNode(
  node: Text,
  trie: TrieNode,
  enabledTypes: Record<EntityType, boolean>,
  onEntityClick: (name: string, type: EntityType) => void
): Node[] {
  const text = node.textContent || '';
  const words = text.split(/(\s+)/); // Split but keep whitespace
  const result: Node[] = [];
  let i = 0;

  while (i < words.length) {
    const word = words[i];

    // Skip whitespace
    if (/^\s*$/.test(word)) {
      result.push(document.createTextNode(word));
      i++;
      continue;
    }

    // Try to match entity starting from this word
    let trieNode = trie;
    let matchEnd = i;
    let matchedEntity: { name: string; type: EntityType } | null = null;

    for (let j = i; j < words.length; j++) {
      const currentWord = words[j].toLowerCase().replace(/[.,!?;:'"]/g, '');

      if (/^\s*$/.test(words[j])) {
        // Skip whitespace in matching
        continue;
      }

      if (trieNode.children.has(currentWord)) {
        trieNode = trieNode.children.get(currentWord)!;
        if (trieNode.entity && enabledTypes[trieNode.entity.type]) {
          matchedEntity = trieNode.entity;
          matchEnd = j;
        }
      } else {
        break;
      }
    }

    if (matchedEntity) {
      // Create highlight span for matched entity
      const span = document.createElement('span');
      span.className = `entity-highlight ${ENTITY_TYPE_CLASSES[matchedEntity.type]}`;
      span.dataset.entityName = matchedEntity.name;
      span.dataset.entityType = matchedEntity.type;

      // Collect all words and whitespace in the match
      const matchedText = words.slice(i, matchEnd + 1).join('');
      span.textContent = matchedText;

      // Add click handler
      span.addEventListener('click', (e) => {
        e.preventDefault();
        e.stopPropagation();
        onEntityClick(matchedEntity!.name, matchedEntity!.type);
      });

      result.push(span);
      i = matchEnd + 1;
    } else {
      result.push(document.createTextNode(word));
      i++;
    }
  }

  return result;
}

/**
 * Process a DOM element to highlight entities
 */
function processElement(
  element: Element,
  trie: TrieNode,
  enabledTypes: Record<EntityType, boolean>,
  onEntityClick: (name: string, type: EntityType) => void
): void {
  // Skip script, style, and already highlighted elements
  if (
    element.tagName === 'SCRIPT' ||
    element.tagName === 'STYLE' ||
    element.classList.contains('entity-highlight')
  ) {
    return;
  }

  const childNodes = Array.from(element.childNodes);

  for (const child of childNodes) {
    if (child.nodeType === Node.TEXT_NODE) {
      const textNode = child as Text;
      if (textNode.textContent && textNode.textContent.trim()) {
        const newNodes = processTextNode(textNode, trie, enabledTypes, onEntityClick);
        if (newNodes.length > 1 || (newNodes.length === 1 && newNodes[0] !== textNode)) {
          // Replace text node with highlighted nodes
          const fragment = document.createDocumentFragment();
          newNodes.forEach(n => fragment.appendChild(n));
          textNode.replaceWith(fragment);
        }
      }
    } else if (child.nodeType === Node.ELEMENT_NODE) {
      processElement(child as Element, trie, enabledTypes, onEntityClick);
    }
  }
}

/**
 * Hook to apply entity highlighting to epub rendition
 */
export function useEntityHighlighter(rendition: Rendition | null) {
  const {
    isOverlayEnabled,
    overlayEntities,
    overlayEntityTypes,
    setFlowPanelOpen,
    setCurrentEntity,
    setIsLoadingEntity,
  } = useFlowStore();

  const trieRef = useRef<TrieNode | null>(null);
  const contentsRef = useRef<Set<Contents>>(new Set());

  // Build trie when entities change
  useEffect(() => {
    if (overlayEntities.length > 0) {
      trieRef.current = buildEntityTrie(
        overlayEntities.map(e => ({ name: e.name, type: e.type }))
      );
    } else {
      trieRef.current = null;
    }
  }, [overlayEntities]);

  // Handle entity click
  const handleEntityClick = useCallback(
    (name: string, type: EntityType) => {
      setFlowPanelOpen(true);
      setIsLoadingEntity(true);

      // Set temporary entity display while loading
      setCurrentEntity({
        id: `temp-${name}`,
        name,
        type,
        summary: 'Loading entity details...',
      });

      // The actual entity lookup will be triggered by the panel
    },
    [setFlowPanelOpen, setCurrentEntity, setIsLoadingEntity]
  );

  // Apply highlighting to a contents object
  const applyHighlighting = useCallback(
    (contents: Contents) => {
      if (!isOverlayEnabled || !trieRef.current) return;

      const doc = contents.document;
      if (!doc) return;

      // Inject styles
      const existingStyle = doc.getElementById('entity-highlight-styles');
      if (!existingStyle) {
        const style = doc.createElement('style');
        style.id = 'entity-highlight-styles';
        style.textContent = ENTITY_HIGHLIGHT_STYLES;
        doc.head.appendChild(style);
      }

      // Process body content
      processElement(doc.body, trieRef.current, overlayEntityTypes, handleEntityClick);
    },
    [isOverlayEnabled, overlayEntityTypes, handleEntityClick]
  );

  // Remove highlighting from a contents object
  const removeHighlighting = useCallback((contents: Contents) => {
    const doc = contents.document;
    if (!doc) return;

    // Remove all highlight spans and restore original text
    const highlights = doc.querySelectorAll('.entity-highlight');
    highlights.forEach(span => {
      const text = document.createTextNode(span.textContent || '');
      span.replaceWith(text);
    });

    // Remove injected styles
    const style = doc.getElementById('entity-highlight-styles');
    if (style) {
      style.remove();
    }
  }, []);

  // Set up rendition hooks
  useEffect(() => {
    if (!rendition) return;

    const handleContentLoaded = (contents: Contents) => {
      contentsRef.current.add(contents);
      if (isOverlayEnabled && trieRef.current) {
        applyHighlighting(contents);
      }
    };

    // Listen for content ready events
    rendition.on('rendered', (_section: any, view: any) => {
      if (view.contents) {
        handleContentLoaded(view.contents);
      }
    });

    return () => {
      contentsRef.current.forEach(contents => {
        removeHighlighting(contents);
      });
      contentsRef.current.clear();
    };
  }, [rendition, isOverlayEnabled, applyHighlighting, removeHighlighting]);

  // Re-apply highlighting when overlay state changes
  useEffect(() => {
    if (!rendition) return;

    contentsRef.current.forEach(contents => {
      if (isOverlayEnabled && trieRef.current) {
        applyHighlighting(contents);
      } else {
        removeHighlighting(contents);
      }
    });
  }, [rendition, isOverlayEnabled, overlayEntityTypes, applyHighlighting, removeHighlighting]);

  return { applyHighlighting, removeHighlighting };
}
