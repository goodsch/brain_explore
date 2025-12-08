/**
 * Graph API Client for Flow Mode
 *
 * Connects to the brain_explore backend to fetch entity data,
 * relationships, sources, and thinking partner questions.
 */

import {
  GraphEntity,
  EntityRelationship,
  BookSource,
  ThinkingPartnerQuestion,
  BreadcrumbJourney,
  EvidencePassage,
} from '@/store/flowModeStore';

// Configuration - use same host as the web app (backend runs on same server)
const DEFAULT_API_BASE =
  typeof window !== 'undefined' && window.location.hostname !== 'localhost'
    ? `http://${window.location.hostname}:8081`
    : 'http://localhost:8081';

interface GraphClientConfig {
  baseUrl?: string;
  timeout?: number;
}

interface EntityResponse {
  entity: GraphEntity;
  relationships: EntityRelationship[];
  sources: BookSource[];
}

interface ExploreResponse {
  center: GraphEntity;
  neighbors: Array<{
    entity: GraphEntity;
    relationship: string;
    distance: number;
  }>;
}

interface JourneyResponse {
  id: string;
  siyuanNoteId?: string;
}

// Raw API response types
interface RawExploreResponse {
  concept: string;
  nodes: Array<{
    name: string;
    type: string;
    labels: string[];
  }>;
  relationships: Array<{
    start: string;
    type: string;
    end: string;
  }>;
}

interface RawSourcesResponse {
  concept: string;
  sources: Array<{
    text: string;
    book: string;
    author: string;
    chapter: string | null;
  }>;
}

interface RawSearchResponse {
  query: string;
  results: Array<{
    name: string;
    type: string;
    score: number;
  }>;
}

interface RawEvidenceResponse {
  entity_name: string;
  evidence: Array<{
    id: string;
    text: string;
    source_title: string;
    source_author: string | null;
    location: {
      chapter?: string;
      page?: number;
      cfi?: string;
    } | null;
    confidence: number;
    source_type: 'chunk' | 'book';
  }>;
  total_count: number;
  sources_searched: number;
}

class GraphAPIClient {
  private baseUrl: string;
  private timeout: number;

  constructor(config: GraphClientConfig = {}) {
    this.baseUrl = config.baseUrl || DEFAULT_API_BASE;
    this.timeout = config.timeout || 10000;
  }

  private async fetch<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), this.timeout);
    const fullUrl = `${this.baseUrl}${endpoint}`;

    try {
      const response = await fetch(fullUrl, {
        ...options,
        signal: controller.signal,
        headers: {
          'Content-Type': 'application/json',
          ...options.headers,
        },
      });

      if (!response.ok) {
        throw new Error(`API error: ${response.status} ${response.statusText}`);
      }

      return await response.json();
    } finally {
      clearTimeout(timeoutId);
    }
  }

  /**
   * Get entity details by name (uses explore endpoint)
   */
  async getEntity(entityName: string): Promise<EntityResponse> {
    // Use explore to get entity and relationships
    const exploreData = await this.fetch<RawExploreResponse>(
      `/graph/explore/${encodeURIComponent(entityName)}?depth=1&limit=20`
    );

    // Get sources separately
    let sources: BookSource[] = [];
    try {
      const sourcesData = await this.fetch<RawSourcesResponse>(
        `/graph/sources/${encodeURIComponent(entityName)}`
      );
      sources = sourcesData.sources.map((s) => ({
        bookId: `${s.book}-${s.chapter || 'main'}`,
        bookTitle: `${s.book} by ${s.author}`,
        chapter: s.chapter || undefined,
      }));
    } catch {
      // Sources may not exist for all entities
    }

    // Transform to expected format
    const entity: GraphEntity = {
      id: entityName,
      name: entityName,
      type: 'Concept',
      summary: `Concept from knowledge graph with ${exploreData.nodes.length} related entities`,
    };

    const relationships: EntityRelationship[] = exploreData.relationships.map((r) => ({
      type: r.type,
      target: {
        id: r.end,
        name: r.end,
        type: exploreData.nodes.find((n) => n.name === r.end)?.type || 'Unknown',
        summary: '',
      },
    }));

    return { entity, relationships, sources };
  }

  /**
   * Search for entities by name or term
   */
  async searchEntities(query: string, limit = 10): Promise<GraphEntity[]> {
    const params = new URLSearchParams({ q: query, limit: String(limit) });
    const response = await this.fetch<RawSearchResponse>(`/graph/search?${params}`);
    return response.results.map((r) => ({
      id: r.name,
      name: r.name,
      type: r.type,
      summary: '',
    }));
  }

  /**
   * Get neighborhood exploration (related entities)
   */
  async exploreNeighborhood(entityName: string, depth = 1, limit = 20): Promise<ExploreResponse> {
    const params = new URLSearchParams({
      depth: String(depth),
      limit: String(limit),
    });
    const raw = await this.fetch<RawExploreResponse>(
      `/graph/explore/${encodeURIComponent(entityName)}?${params}`
    );

    const center: GraphEntity = {
      id: raw.concept,
      name: raw.concept,
      type: 'Concept',
      summary: '',
    };

    const neighbors = raw.nodes.map((node) => {
      const rel = raw.relationships.find((r) => r.end === node.name || r.start === node.name);
      return {
        entity: {
          id: node.name,
          name: node.name,
          type: node.type,
          summary: '',
        },
        relationship: rel?.type || 'RELATED_TO',
        distance: 1,
      };
    });

    return { center, neighbors };
  }

  /**
   * Get book sources that discuss an entity
   */
  async getEntitySources(entityName: string): Promise<BookSource[]> {
    const response = await this.fetch<RawSourcesResponse>(
      `/graph/sources/${encodeURIComponent(entityName)}`
    );
    return response.sources.map((s) => ({
      bookId: `${s.book}-${s.chapter || 'main'}`,
      bookTitle: `${s.book} by ${s.author}`,
      chapter: s.chapter || undefined,
    }));
  }

  /**
   * Get evidence passages for an entity (Sprint 2)
   * Returns text snippets from books that mention/discuss the entity
   */
  async getEntityEvidence(entityName: string, limit = 10): Promise<EvidencePassage[]> {
    try {
      const params = new URLSearchParams({
        limit: String(limit),
        include_book_mentions: 'true',
      });
      const response = await this.fetch<RawEvidenceResponse>(
        `/graph/entity/${encodeURIComponent(entityName)}/evidence?${params}`
      );
      return response.evidence.map((e) => ({
        id: e.id,
        text: e.text,
        sourceTitle: e.source_title,
        sourceAuthor: e.source_author || undefined,
        location: e.location || undefined,
        confidence: e.confidence,
        sourceType: e.source_type,
      }));
    } catch {
      // Evidence may not exist for all entities
      return [];
    }
  }

  /**
   * Get thinking partner question for an entity
   */
  async getThinkingPartnerQuestions(
    entityName: string,
    _context?: {
      currentPassage?: string;
      recentPath?: string[];
      userProfileId?: string;
    }
  ): Promise<ThinkingPartnerQuestion[]> {
    const response = await this.fetch<{ question: string }>('/graph/thinking-partner', {
      method: 'POST',
      body: JSON.stringify({ concept: entityName }),
    });
    return [
      {
        text: response.question,
        type: 'clarifying',
      },
    ];
  }

  /**
   * Save a breadcrumb journey
   */
  async saveJourney(journey: BreadcrumbJourney): Promise<JourneyResponse> {
    return this.fetch<JourneyResponse>('/journeys', {
      method: 'POST',
      body: JSON.stringify(journey),
    });
  }

  /**
   * Get a journey by ID
   */
  async getJourney(journeyId: string): Promise<BreadcrumbJourney> {
    return this.fetch<BreadcrumbJourney>(`/journeys/${journeyId}`);
  }

  /**
   * List user's journeys
   */
  async listUserJourneys(userId: string, limit = 20): Promise<BreadcrumbJourney[]> {
    const params = new URLSearchParams({ limit: String(limit) });
    return this.fetch<BreadcrumbJourney[]>(`/journeys/user/${userId}?${params}`);
  }

  /**
   * Update a journey
   */
  async updateJourney(journeyId: string, updates: Partial<BreadcrumbJourney>): Promise<void> {
    await this.fetch(`/journeys/${journeyId}`, {
      method: 'PATCH',
      body: JSON.stringify(updates),
    });
  }

  /**
   * Delete a journey
   */
  async deleteJourney(journeyId: string): Promise<void> {
    await this.fetch(`/journeys/${journeyId}`, {
      method: 'DELETE',
    });
  }
}

// Singleton instance with config tracking
let graphClient: GraphAPIClient | null = null;
let clientConfigHash: string | null = null;

function hashConfig(config?: GraphClientConfig): string {
  return JSON.stringify({
    baseUrl: config?.baseUrl || DEFAULT_API_BASE,
    timeout: config?.timeout || 10000,
  });
}

export function getGraphClient(config?: GraphClientConfig): GraphAPIClient {
  const newConfigHash = hashConfig(config);

  // Recreate client if config has changed
  if (!graphClient || clientConfigHash !== newConfigHash) {
    graphClient = new GraphAPIClient(config);
    clientConfigHash = newConfigHash;
  }
  return graphClient;
}

export function resetGraphClient(): void {
  graphClient = null;
  clientConfigHash = null;
}

export { GraphAPIClient };
export type { GraphClientConfig, EntityResponse, ExploreResponse };
