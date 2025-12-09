/**
 * API client for highlights sync with IES backend.
 */

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8081';

export type HighlightColor = 'yellow' | 'green' | 'blue' | 'pink' | 'purple';

export interface HighlightCreate {
  book_id: string;
  text: string;
  cfi: string;
  note?: string;
  color?: HighlightColor;
  context_id?: string;
  chapter?: string;
}

export interface Highlight {
  id: string;
  book_id: string;
  book_title?: string;
  book_author?: string;
  text: string;
  cfi: string;
  note?: string;
  color: HighlightColor;
  context_id?: string;
  chapter?: string;
  created_at: string;
  updated_at: string;
  processed: boolean;
  entity_refs: string[];
  siyuan_block_id?: string;
}

export interface HighlightResponse {
  highlight: Highlight;
  message: string;
  siyuan_synced: boolean;
}

export interface HighlightListResponse {
  highlights: Highlight[];
  total: number;
  book_id?: string;
}

export interface HighlightBatchCreate {
  book_id: string;
  highlights: HighlightCreate[];
}

export interface HighlightBatchResponse {
  created: number;
  updated: number;
  errors: string[];
  message: string;
}

class HighlightApiClient {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE) {
    this.baseUrl = baseUrl;
  }

  /**
   * Get the API URL, using current host for network access.
   */
  private getApiUrl(): string {
    // If we're accessing from a different host (e.g., network IP),
    // use the same host for API calls
    if (typeof window !== 'undefined') {
      const hostname = window.location.hostname;
      if (hostname !== 'localhost' && hostname !== '127.0.0.1') {
        return `http://${hostname}:8081`;
      }
    }
    return this.baseUrl;
  }

  /**
   * Create a new highlight.
   */
  async create(data: HighlightCreate): Promise<Highlight> {
    const response = await fetch(`${this.getApiUrl()}/highlights`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    if (!response.ok) {
      throw new Error(`Failed to create highlight: ${response.statusText}`);
    }
    const result: HighlightResponse = await response.json();
    return result.highlight;
  }

  /**
   * Get a highlight by ID.
   */
  async get(highlightId: string): Promise<Highlight> {
    const response = await fetch(`${this.getApiUrl()}/highlights/${highlightId}`);
    if (!response.ok) {
      throw new Error(`Failed to get highlight: ${response.statusText}`);
    }
    return response.json();
  }

  /**
   * List highlights for a book.
   */
  async listByBook(bookId: string, limit: number = 100): Promise<Highlight[]> {
    const response = await fetch(
      `${this.getApiUrl()}/highlights/book/${bookId}?limit=${limit}`
    );
    if (!response.ok) {
      throw new Error(`Failed to list highlights: ${response.statusText}`);
    }
    const result: HighlightListResponse = await response.json();
    return result.highlights;
  }

  /**
   * Batch sync highlights for a book.
   */
  async batchSync(data: HighlightBatchCreate): Promise<HighlightBatchResponse> {
    const response = await fetch(`${this.getApiUrl()}/highlights/sync`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    if (!response.ok) {
      throw new Error(`Failed to sync highlights: ${response.statusText}`);
    }
    return response.json();
  }

  /**
   * Sync a highlight to SiYuan.
   */
  async syncToSiyuan(highlightId: string): Promise<{ siyuan_block_id: string }> {
    const response = await fetch(
      `${this.getApiUrl()}/highlights/${highlightId}/sync-siyuan`,
      { method: 'POST' }
    );
    if (!response.ok) {
      throw new Error(`Failed to sync to SiYuan: ${response.statusText}`);
    }
    return response.json();
  }

  /**
   * Sync all highlights for a book to SiYuan.
   */
  async syncBookToSiyuan(bookId: string): Promise<{
    synced: number;
    already_synced: number;
    errors: string[];
  }> {
    const response = await fetch(
      `${this.getApiUrl()}/highlights/book/${bookId}/sync-siyuan`,
      { method: 'POST' }
    );
    if (!response.ok) {
      throw new Error(`Failed to sync book to SiYuan: ${response.statusText}`);
    }
    return response.json();
  }

  /**
   * Delete a highlight.
   */
  async delete(highlightId: string): Promise<void> {
    const response = await fetch(`${this.getApiUrl()}/highlights/${highlightId}`, {
      method: 'DELETE',
    });
    if (!response.ok) {
      throw new Error(`Failed to delete highlight: ${response.statusText}`);
    }
  }
}

export const highlightApi = new HighlightApiClient();
export { HighlightApiClient };
