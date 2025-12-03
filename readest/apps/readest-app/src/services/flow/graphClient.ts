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
} from '@/store/flowModeStore';

// Configuration
const DEFAULT_API_BASE = 'http://localhost:8081/api/v1';

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

interface ThinkingPartnerResponse {
  questions: ThinkingPartnerQuestion[];
}

interface JourneyResponse {
  id: string;
  siyuanNoteId?: string;
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

    try {
      const response = await fetch(`${this.baseUrl}${endpoint}`, {
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
   * Get entity details by ID
   */
  async getEntity(entityId: string): Promise<EntityResponse> {
    return this.fetch<EntityResponse>(`/graph/entity/${entityId}`);
  }

  /**
   * Search for entities by name or term
   */
  async searchEntities(query: string, limit = 10): Promise<GraphEntity[]> {
    const params = new URLSearchParams({ query, limit: String(limit) });
    return this.fetch<GraphEntity[]>(`/graph/search?${params}`);
  }

  /**
   * Get neighborhood exploration (related entities)
   */
  async exploreNeighborhood(entityId: string, depth = 1, limit = 20): Promise<ExploreResponse> {
    const params = new URLSearchParams({
      depth: String(depth),
      limit: String(limit),
    });
    return this.fetch<ExploreResponse>(`/graph/explore/${entityId}?${params}`);
  }

  /**
   * Get book sources that discuss an entity
   */
  async getEntitySources(entityId: string): Promise<BookSource[]> {
    return this.fetch<BookSource[]>(`/graph/sources/${entityId}`);
  }

  /**
   * Get thinking partner questions for an entity
   */
  async getThinkingPartnerQuestions(
    entityId: string,
    context?: {
      currentPassage?: string;
      recentPath?: string[];
      userProfileId?: string;
    }
  ): Promise<ThinkingPartnerQuestion[]> {
    const response = await this.fetch<ThinkingPartnerResponse>('/question-engine/question', {
      method: 'POST',
      body: JSON.stringify({
        entity_id: entityId,
        context: {
          current_passage: context?.currentPassage,
          recent_path: context?.recentPath || [],
          user_profile_id: context?.userProfileId || 'default',
        },
      }),
    });
    return response.questions;
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

// Singleton instance
let graphClient: GraphAPIClient | null = null;

export function getGraphClient(config?: GraphClientConfig): GraphAPIClient {
  if (!graphClient) {
    graphClient = new GraphAPIClient(config);
  }
  return graphClient;
}

export function resetGraphClient(): void {
  graphClient = null;
}

export { GraphAPIClient };
export type { GraphClientConfig, EntityResponse, ExploreResponse, ThinkingPartnerResponse };
