import type {
  GraphEntity,
  EntityRelationship,
  BookSource,
  ThinkingPartnerQuestion,
  BreadcrumbJourney,
} from '../store/flowStore';
import { offlineQueue } from './offlineQueue';

const API_BASE = '';  // Use Vite proxy - relative URLs

// Book from Calibre library
export interface CalibreBook {
  calibre_id: number;
  title: string;
  author: string;
  path: string;
  format: string;
  cover_url: string;
  file_url: string;
  entity_count?: number;
  indexed?: boolean;
}

interface BooksResponse {
  books: CalibreBook[];
  total: number;
}

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

// Backend response from /graph/explore/{concept}
interface BackendExploreResponse {
  concept: string;
  nodes: Array<{ name: string; type: string; labels: string[] }>;
  relationships: Array<{ start: string; type: string; end: string }>;
}

// Backend response from /graph/sources/{concept}
interface BackendSourcesResponse {
  concept: string;
  sources: Array<{ text: string; book: string; author?: string; chapter?: string }>;
}

class GraphClient {
  private async fetch<T>(path: string, options?: RequestInit): Promise<T> {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 10000); // 10s timeout

    try {
      const response = await fetch(`${API_BASE}${path}`, {
        ...options,
        headers: {
          'Content-Type': 'application/json',
          ...options?.headers,
        },
        signal: options?.signal || controller.signal,
      });

      if (!response.ok) {
        throw new Error(`API error: ${response.status} ${response.statusText}`);
      }

      return response.json();
    } finally {
      clearTimeout(timeoutId);
    }
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
      console.error('Backend availability check failed:', error);
      return false;
    }
    // Redundant return to ensure all code paths return a boolean.
    return false;
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
   * Transforms backend search response to frontend format
   */
  async searchEntities(query: string): Promise<EntitySearchResult> {
    // Backend returns: { query, results: [{ name, type, score }] }
    const backendResponse = await this.fetch<{
      query: string;
      results: Array<{ name: string; type: string; score: number }>;
    }>(`/graph/search?q=${encodeURIComponent(query)}&limit=10`);

    // Transform to frontend format: { entities: GraphEntity[], total }
    const entities: GraphEntity[] = backendResponse.results.map((r) => ({
      id: r.name, // Use name as ID since Neo4j uses name as identifier
      name: r.name,
      type: r.type,
      summary: '', // Search doesn't return summaries
    }));

    return {
      entities,
      total: entities.length,
    };
  }

  /**
   * Get entity details by name (entities use name as identifier in Neo4j)
   * Note: In this system, entityId IS the entity name since Neo4j uses names as identifiers
   */
  async getEntity(entityNameOrId: string): Promise<GraphEntity> {
    // Search for the entity by name
    const searchResult = await this.searchEntities(entityNameOrId);

    if (searchResult.entities.length === 0) {
      throw new Error(`Entity not found: ${entityNameOrId}`);
    }

    // Return the first match
    return searchResult.entities[0];
  }

  /**
   * Get entity with relationships and sources
   * Transforms backend's name-based response to frontend's expected format
   */
  async exploreEntity(entityNameOrId: string): Promise<EntityDetailsResult> {
    // URL-encode the entity name for the path parameter
    const encodedName = encodeURIComponent(entityNameOrId);

    // Fetch relationships from backend (uses concept NAME as path param)
    const exploreResponse = await this.fetch<BackendExploreResponse>(
      `/graph/explore/${encodedName}`
    );

    // Fetch sources from backend
    let sourcesResponse: BackendSourcesResponse = { concept: entityNameOrId, sources: [] };
    try {
      sourcesResponse = await this.fetch<BackendSourcesResponse>(
        `/graph/sources/${encodedName}`
      );
    } catch {
      // Sources endpoint might fail if no chunks exist - that's OK
    }

    // Build the entity object (using name as ID since that's our identifier)
    const entity: GraphEntity = {
      id: entityNameOrId,
      name: entityNameOrId,
      type: 'Concept', // Default type - could be enriched from search
      summary: '', // Backend explore endpoint doesn't return summaries
    };

    // Transform backend relationships to frontend format
    // Backend returns: { start, type, end } - we want: { type, target: GraphEntity }
    const relationships: EntityRelationship[] = exploreResponse.nodes.map((node) => {
      // Find the relationship for this node
      const rel = exploreResponse.relationships.find(
        (r) => r.end === node.name || r.start === node.name
      );

      return {
        type: rel?.type || 'RELATED_TO',
        target: {
          id: node.name,
          name: node.name,
          type: node.type || 'Concept',
          summary: '',
        },
      };
    });

    // Transform backend sources to frontend format
    const sources: BookSource[] = sourcesResponse.sources.map((s) => ({
      bookId: s.book,
      bookTitle: s.book,
      chapter: s.chapter,
    }));

    return { entity, relationships, sources };
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
  ): Promise<{ journeys: BreadcrumbJourney[]; total: number }> {
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

  // ========================================
  // Calibre Library Methods
  // ========================================

  /**
   * Get all books from Calibre library
   */
  async getBooks(search?: string): Promise<BooksResponse> {
    const params = search ? `?search=${encodeURIComponent(search)}` : '';
    return this.fetch<BooksResponse>(`/books${params}`);
  }

  /**
   * Get a single book by Calibre ID
   */
  async getBook(calibreId: number): Promise<CalibreBook> {
    return this.fetch<CalibreBook>(`/books/${calibreId}`);
  }

  /**
   * Get the cover image URL for a book
   */
  getBookCoverUrl(calibreId: number): string {
    return `${API_BASE}/books/${calibreId}/cover`;
  }

  /**
   * Get the EPUB file URL for a book
   */
  getBookFileUrl(calibreId: number): string {
    return `${API_BASE}/books/${calibreId}/file`;
  }

  /**
   * Get entity count for a book (to show indexed badge)
   */
  async getBookEntityCount(calibreId: number): Promise<number> {
    try {
      const result = await this.getEntitiesByBook(calibreId);
      return result.total || result.entities.length;
    } catch {
      return 0;
    }
  }

  // ========================================
  // Ingestion Queue Methods
  // ========================================

  /**
   * Queue a book for entity extraction
   */
  async queueBookForIngestion(calibreId: number): Promise<{ calibre_id: number; message: string; queued_at: string }> {
    return this.fetch(`/books/${calibreId}/queue-ingest`, {
      method: 'POST',
    });
  }

  /**
   * Get the current ingestion queue
   */
  async getIngestionQueue(): Promise<{ items: IngestionQueueItem[]; total: number }> {
    return this.fetch('/books/ingestion-queue');
  }

  /**
   * Remove a book from the ingestion queue
   */
  async removeFromIngestionQueue(calibreId: number): Promise<void> {
    await this.fetch(`/books/${calibreId}/queue-ingest`, {
      method: 'DELETE',
    });
  }
}

// Ingestion queue item type
export interface IngestionQueueItem {
  calibre_id: number;
  title: string;
  author: string;
  queued_at: string;
  status: 'queued' | 'processing' | 'completed' | 'failed';
  error_message?: string;
}

export const graphClient = new GraphClient();
