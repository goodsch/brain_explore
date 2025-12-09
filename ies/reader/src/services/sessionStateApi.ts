/**
 * Session State API client for IES Reader.
 *
 * Enables cross-app continuity by syncing active session state
 * (context, question, reading position) with the backend.
 */

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8081';

export type AppSource = 'reader' | 'siyuan';

export interface ReadingPosition {
  calibre_id: number;
  cfi: string;
  chapter_title?: string;
  page_number?: number;
  progress_percent?: number;
  last_read_at: string;
}

export interface JourneyTrailItem {
  entity_id: string;
  entity_name: string;
  entity_type?: string | null;
  source_app: AppSource;
  timestamp: string;
  dwell_seconds?: number | null;
  source_context?: string | null;
}

export interface SessionState {
  user_id: string;
  active_context_id?: string;
  active_question_id?: string;
  current_book?: ReadingPosition;
  // Journey continuity fields
  current_entity_id?: string | null;
  current_entity_name?: string | null;
  journey_trail: JourneyTrailItem[];
  last_app_source?: AppSource | null;
  last_activity_at: string;
  created_at: string;
  updated_at: string;
}

export interface SessionStateUpdate {
  active_context_id?: string | null;
  active_question_id?: string | null;
  current_book?: ReadingPosition | null;
  // Journey continuity fields
  current_entity_id?: string | null;
  current_entity_name?: string | null;
  add_trail_item?: JourneyTrailItem | null;
  app_source?: AppSource | null;
}

export interface ContinueExplorationResponse {
  user_id: string;
  has_active_exploration: boolean;
  current_entity_id?: string | null;
  current_entity_name?: string | null;
  active_context_id?: string | null;
  active_question_id?: string | null;
  journey_trail: JourneyTrailItem[];
  last_app_source?: AppSource | null;
  reader_deep_link?: string | null;
  siyuan_deep_link?: string | null;
  resume_hint?: string | null;
  last_activity_at?: string | null;
}

export interface SessionStateHistory {
  user_id: string;
  context_id?: string;
  question_id?: string;
  book_position?: ReadingPosition;
  timestamp: string;
  change_type: 'context_opened' | 'question_selected' | 'book_opened' | 'reading_progress' | 'session_ended';
}

export interface HeartbeatResponse {
  user_id: string;
  last_activity_at: string;
  session_active: boolean;
}

export interface SessionStateHistoryResponse {
  user_id: string;
  history: SessionStateHistory[];
  total: number;
}

class SessionStateApiClient {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE) {
    this.baseUrl = baseUrl;
  }

  /**
   * Get current session state for a user.
   */
  async getState(userId: string = 'default_user'): Promise<SessionState> {
    const res = await fetch(`${this.baseUrl}/session-state/${userId}`);

    if (!res.ok) {
      throw new Error(`Failed to fetch session state: ${res.statusText}`);
    }

    return res.json();
  }

  /**
   * Update session state with partial data.
   *
   * Only provided fields will be updated. Use null to clear a field.
   */
  async updateState(
    userId: string = 'default_user',
    update: SessionStateUpdate
  ): Promise<SessionState> {
    const res = await fetch(`${this.baseUrl}/session-state/${userId}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(update),
    });

    if (!res.ok) {
      throw new Error(`Failed to update session state: ${res.statusText}`);
    }

    return res.json();
  }

  /**
   * Send heartbeat to update last activity timestamp.
   *
   * Use this to indicate the user is still active without making
   * full state changes.
   */
  async heartbeat(userId: string = 'default_user'): Promise<HeartbeatResponse> {
    const res = await fetch(`${this.baseUrl}/session-state/${userId}/heartbeat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ user_id: userId }),
    });

    if (!res.ok) {
      throw new Error(`Failed to send heartbeat: ${res.statusText}`);
    }

    return res.json();
  }

  /**
   * Get session state history for resume features.
   *
   * Returns historical snapshots of session state changes.
   */
  async getHistory(
    userId: string = 'default_user',
    limit?: number
  ): Promise<SessionStateHistoryResponse> {
    const searchParams = new URLSearchParams();
    if (limit) searchParams.set('limit', String(limit));

    const url = `${this.baseUrl}/session-state/${userId}/history?${searchParams.toString()}`;
    const res = await fetch(url);

    if (!res.ok) {
      throw new Error(`Failed to fetch session history: ${res.statusText}`);
    }

    return res.json();
  }

  /**
   * Add a journey trail item (entity visit).
   *
   * Automatically updates current_entity tracking and last_app_source.
   */
  async addTrailItem(
    userId: string = 'default_user',
    item: JourneyTrailItem
  ): Promise<SessionState> {
    return this.updateState(userId, { add_trail_item: item });
  }

  /**
   * Get data for "Continue Exploration" feature.
   *
   * Returns current state with deep links for Reader and SiYuan.
   */
  async getContinueExploration(
    userId: string = 'default_user',
    trailLimit: number = 10
  ): Promise<ContinueExplorationResponse> {
    const url = `${this.baseUrl}/session-state/${userId}/continue?trail_limit=${trailLimit}`;
    const res = await fetch(url);

    if (!res.ok) {
      throw new Error(`Failed to get continue exploration: ${res.statusText}`);
    }

    return res.json();
  }
}

// Singleton instance
export const sessionStateApi = new SessionStateApiClient();

// Export class for testing/custom instances
export { SessionStateApiClient };
