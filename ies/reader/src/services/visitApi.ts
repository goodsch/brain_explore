/**
 * Visit Tracking API client for IES Reader.
 *
 * Implements "What's New" functionality by tracking when users last visited
 * contexts, books, and entities, then surfacing new content since last session.
 */

import type {
  VisitScope,
  RecordVisitResponse,
  NewItemsSummary,
  NewItemsDetailResponse,
} from '../types/api';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8081';

export interface RecordVisitParams {
  user_id?: string;
  scope: VisitScope;
  scope_id: string;
}

export interface NewItemsDetailParams {
  user_id?: string;
  scope: VisitScope;
  scope_id: string;
  limit?: number;
}

class VisitApiClient {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE) {
    this.baseUrl = baseUrl;
  }

  /**
   * Record a visit to a scope (context, book, entity, or global).
   */
  async recordVisit(params: RecordVisitParams): Promise<RecordVisitResponse> {
    const res = await fetch(`${this.baseUrl}/visits/record`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        user_id: params.user_id || 'default_user',
        scope: params.scope,
        scope_id: params.scope_id,
      }),
    });

    if (!res.ok) {
      throw new Error(`Failed to record visit: ${res.statusText}`);
    }

    return res.json();
  }

  /**
   * Get summary of new items since last visit to a scope.
   */
  async getNewItemsSummary(
    scope: VisitScope,
    scopeId: string,
    userId: string = 'default_user'
  ): Promise<NewItemsSummary> {
    const res = await fetch(
      `${this.baseUrl}/visits/new-items-summary/${scope}/${scopeId}?user_id=${userId}`
    );

    if (!res.ok) {
      throw new Error(`Failed to fetch new items summary: ${res.statusText}`);
    }

    return res.json();
  }

  /**
   * Get detailed list of new items since last visit.
   */
  async getNewItemsDetail(params: NewItemsDetailParams): Promise<NewItemsDetailResponse> {
    const res = await fetch(`${this.baseUrl}/visits/new-items-detail`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        user_id: params.user_id || 'default_user',
        scope: params.scope,
        scope_id: params.scope_id,
        limit: params.limit || 50,
      }),
    });

    if (!res.ok) {
      throw new Error(`Failed to fetch new items detail: ${res.statusText}`);
    }

    return res.json();
  }

  /**
   * Get last visit timestamp for a scope.
   */
  async getLastVisit(
    scope: VisitScope,
    scopeId: string,
    userId: string = 'default_user'
  ): Promise<{ last_visited_at: string | null }> {
    const res = await fetch(
      `${this.baseUrl}/visits/last-visit/${scope}/${scopeId}?user_id=${userId}`
    );

    if (!res.ok) {
      throw new Error(`Failed to fetch last visit: ${res.statusText}`);
    }

    return res.json();
  }

  /**
   * Clear all visit history (for testing/reset).
   */
  async clearVisits(): Promise<{ message: string }> {
    const res = await fetch(`${this.baseUrl}/visits/clear`, {
      method: 'DELETE',
    });

    if (!res.ok) {
      throw new Error(`Failed to clear visits: ${res.statusText}`);
    }

    return res.json();
  }
}

// Singleton instance
export const visitApi = new VisitApiClient();

// Export class for testing/custom instances
export { VisitApiClient };
