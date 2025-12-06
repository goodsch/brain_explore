import type {
  GraphEntity,
  EntityRelationship,
  BookSource,
  ThinkingPartnerQuestion,
  BreadcrumbJourney,
} from '../store/flowStore';
import { offlineQueue } from './offlineQueue';

const API_BASE = 'http://localhost:8081';

// Device ID for anonymous users (persisted in localStorage)
function getDeviceId(): string {
  const key = 'ies-reader-device-id';
  let deviceId = localStorage.getItem(key);
  if (!deviceId) {
    deviceId = `device-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    localStorage.setItem(key, deviceId);
  }
  return deviceId;
}

interface UserProfile {
  user_id: string;
  display_name: string | null;
}

interface EntitySearchResult {
  entities: GraphEntity[];
  total: number;
}

interface EntityDetailsResult {
  entity: GraphEntity;
  relationships: EntityRelationship[];
  sources: BookSource[];
}

class GraphClient {
  private async fetch<T>(path: string, options?: RequestInit): Promise<T> {
    const response = await fetch(`${API_BASE}${path}`, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options?.headers,
      },
    });

    if (!response.ok) {
      throw new Error(`API error: ${response.status} ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * Check if backend is available
   */
  async isBackendAvailable(): Promise<boolean> {
    try {
      const response = await fetch(`${API_BASE}/health`, {
        method: 'GET',
        signal: AbortSignal.timeout(5000), // 5 second timeout
      });
      return response.ok;
    } catch (error) {
      return false;
    }
  }

  /**
   * Login or create user profile. Returns user_id for all subsequent calls.
   */
  async login(userId?: string): Promise<UserProfile> {
    const id = userId || getDeviceId();
    return this.fetch<UserProfile>(`/profile/login?user_id=${encodeURIComponent(id)}`, {
      method: 'POST',
    });
  }

  /**
   * Search for entities by text (e.g., selected text from reader)
   */
  async searchEntities(query: string): Promise<EntitySearchResult> {
    return this.fetch<EntitySearchResult>(
      `/graph/search?q=${encodeURIComponent(query)}&limit=10`
    );
  }

  /**
   * Get entity details by ID
   */
  async getEntity(entityId: string): Promise<GraphEntity> {
    return this.fetch<GraphEntity>(`/graph/entity/${entityId}`);
  }

  /**
   * Get entity with relationships and sources
   */
  async exploreEntity(entityId: string): Promise<EntityDetailsResult> {
    return this.fetch<EntityDetailsResult>(`/graph/explore/${entityId}`);
  }

  /**
   * Get entities for a specific book by calibre ID
   */
  async getEntitiesByBook(calibreId: number): Promise<EntitySearchResult> {
    return this.fetch<EntitySearchResult>(
      `/graph/entities/by-calibre-id/${calibreId}`
    );
  }

  /**
   * Get thinking partner questions for an entity
   */
  async getThinkingPartnerQuestions(
    entityId: string,
    context?: string
  ): Promise<ThinkingPartnerQuestion[]> {
    const body = {
      entity_id: entityId,
      context: context || '',
    };

    const result = await this.fetch<{ questions: ThinkingPartnerQuestion[] }>(
      '/question-engine/questions',
      {
        method: 'POST',
        body: JSON.stringify(body),
      }
    );

    return result.questions;
  }

  /**
   * Save a completed journey to backend.
   * Transforms frontend camelCase schema to backend snake_case.
   * Falls back to offline queue if backend is unavailable.
   */
  async saveJourney(journey: BreadcrumbJourney, userId: string): Promise<{ id: string; queued?: boolean }> {
    // Transform frontend schema to backend schema
    const backendJourney = {
      user_id: userId,
      entry_point: {
        type: journey.entryPoint.type,
        reference: journey.entryPoint.reference,
      },
      path: journey.path.map((step) => ({
        entity_id: step.entityId,
        entity_name: step.entityName,
        timestamp: step.timestamp,
        source_passage: step.sourcePassage || null,
        dwell_time_seconds: step.dwellTimeSeconds,
      })),
      // Optional fields
      marks: [],
      thinking_partner_exchanges: [],
      title: null,
      tags: [],
      notes: null,
    };

    try {
      // Try direct save first
      const result = await this.fetch<{ id: string }>('/journeys', {
        method: 'POST',
        body: JSON.stringify(backendJourney),
      });

      // Success: process any pending queue operations
      offlineQueue.processQueue().catch((error) => {
        console.error('Background queue processing failed:', error);
      });

      return result;

    } catch (error) {
      // Backend unreachable: queue the operation
      console.warn('Backend unavailable, queueing journey save:', error);

      const operationId = offlineQueue.enqueue({
        userId,
        operationType: 'journey',
        payload: backendJourney,
        endpoint: '/journeys',
      });

      // Return synthetic ID to indicate queued state
      return { id: operationId, queued: true };
    }
  }

  /**
   * Fetch journey history for a user
   */
  async getJourneyHistory(
    userId: string,
    page: number = 1
  ): Promise<{ journeys: unknown[]; total: number }> {
    return this.fetch(`/journeys/user/${encodeURIComponent(userId)}?page=${page}`);
  }

  /**
   * Manually trigger offline queue processing
   * Useful for "retry sync" buttons in UI
   */
  async processOfflineQueue(): Promise<{ succeeded: number; failed: number }> {
    return offlineQueue.processQueue();
  }

  /**
   * Get offline queue status
   */
  getOfflineQueueStatus() {
    return offlineQueue.getStatus();
  }
}

export const graphClient = new GraphClient();
