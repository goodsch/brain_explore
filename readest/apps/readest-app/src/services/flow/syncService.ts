/**
 * Sync Service for Cross-App Exploration Sessions
 *
 * Manages session synchronization between IES Reader and SiYuan,
 * enabling users to pause exploration in one app and resume in another.
 */

// Shared API base URL configuration (matches graphClient pattern)
const DEFAULT_API_BASE =
  typeof window !== 'undefined' && window.location.hostname !== 'localhost'
    ? `http://${window.location.hostname}:8081`
    : 'http://localhost:8081';

// Type definitions matching backend schemas
export enum AppSource {
  READER = 'reader',
  SIYUAN = 'siyuan',
}

export enum SessionStatus {
  ACTIVE = 'active',
  PAUSED = 'paused',
  COMPLETED = 'completed',
}

export interface ReadingPosition {
  book_hash: string;
  calibre_id?: number;
  cfi?: string;
  chapter?: string;
  progress_percent?: number;
}

export interface JourneyStep {
  entity_id: string;
  entity_name: string;
  timestamp: string;
  source_passage?: string;
  dwell_time: number;
}

export interface TrailItem {
  entity_id: string;
  entity_name: string;
  timestamp: string;
  context?: Record<string, unknown>;
}

export interface ExplorationSession {
  id: string;
  user_id: string;
  app_source: AppSource;
  created_at: string;
  updated_at: string;
  status: SessionStatus;
  current_entity_id?: string;
  current_entity_name?: string;
  reading_position?: ReadingPosition;
  journey_path: JourneyStep[];
  trail_stack: TrailItem[];
  resume_hint?: string;
}

export interface SessionCreateRequest {
  user_id: string;
  app_source: AppSource;
  status?: SessionStatus;
  current_entity_id?: string;
  current_entity_name?: string;
  reading_position?: ReadingPosition;
  journey_path?: JourneyStep[];
  trail_stack?: TrailItem[];
  resume_hint?: string;
}

export interface SessionUpdateRequest {
  status?: SessionStatus;
  current_entity_id?: string;
  current_entity_name?: string;
  reading_position?: ReadingPosition;
  journey_path?: JourneyStep[];
  trail_stack?: TrailItem[];
  resume_hint?: string;
}

export interface ResumeData {
  session: ExplorationSession;
  deep_link?: string;
  instructions?: string;
}

interface SyncServiceConfig {
  baseUrl?: string;
  timeout?: number;
}

/**
 * Sync Service Client
 */
class SyncService {
  private baseUrl: string;
  private timeout: number;

  constructor(config: SyncServiceConfig = {}) {
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
   * Create or update an exploration session
   */
  async createOrUpdateSession(
    session: SessionCreateRequest,
    sessionId?: string,
  ): Promise<ExplorationSession> {
    const params = sessionId ? `?session_id=${encodeURIComponent(sessionId)}` : '';
    const response = await this.fetch<{ session: ExplorationSession }>(
      `/sync/sessions${params}`,
      {
        method: 'POST',
        body: JSON.stringify(session),
      },
    );
    return response.session;
  }

  /**
   * Get active/paused sessions for user
   */
  async getActiveSessions(userId: string, includePaused = true): Promise<ExplorationSession[]> {
    const params = new URLSearchParams({
      user_id: userId,
      include_paused: String(includePaused),
    });
    const response = await this.fetch<{ sessions: ExplorationSession[]; total: number }>(
      `/sync/sessions/active?${params}`,
    );
    return response.sessions;
  }

  /**
   * Get specific session by ID
   */
  async getSession(sessionId: string): Promise<ExplorationSession> {
    const response = await this.fetch<{ session: ExplorationSession }>(
      `/sync/sessions/${encodeURIComponent(sessionId)}`,
    );
    return response.session;
  }

  /**
   * Get resume data for target app
   */
  async getResumeData(sessionId: string, targetApp: AppSource): Promise<ResumeData> {
    const params = new URLSearchParams({ target_app: targetApp });
    return this.fetch<ResumeData>(
      `/sync/sessions/${encodeURIComponent(sessionId)}/resume?${params}`,
    );
  }

  /**
   * Update session status
   */
  async updateSessionStatus(sessionId: string, status: SessionStatus): Promise<ExplorationSession> {
    const response = await this.fetch<{ session: ExplorationSession }>(
      `/sync/sessions/${encodeURIComponent(sessionId)}/status`,
      {
        method: 'PUT',
        body: JSON.stringify({ status }),
      },
    );
    return response.session;
  }

  /**
   * Update session fields
   */
  async updateSession(
    sessionId: string,
    updates: SessionUpdateRequest,
  ): Promise<ExplorationSession> {
    const response = await this.fetch<{ session: ExplorationSession }>(
      `/sync/sessions/${encodeURIComponent(sessionId)}`,
      {
        method: 'PUT',
        body: JSON.stringify(updates),
      },
    );
    return response.session;
  }

  /**
   * Pause session (convenience method)
   */
  async pauseSession(sessionId: string): Promise<ExplorationSession> {
    return this.updateSessionStatus(sessionId, SessionStatus.PAUSED);
  }

  /**
   * Delete session
   */
  async deleteSession(sessionId: string): Promise<void> {
    await this.fetch(`/sync/sessions/${encodeURIComponent(sessionId)}`, {
      method: 'DELETE',
    });
  }
}

// Singleton instance with config tracking
let syncService: SyncService | null = null;
let clientConfigHash: string | null = null;

function hashConfig(config?: SyncServiceConfig): string {
  return JSON.stringify({
    baseUrl: config?.baseUrl || DEFAULT_API_BASE,
    timeout: config?.timeout || 10000,
  });
}

export function getSyncService(config?: SyncServiceConfig): SyncService {
  const newConfigHash = hashConfig(config);

  // Recreate service if config has changed
  if (!syncService || clientConfigHash !== newConfigHash) {
    syncService = new SyncService(config);
    clientConfigHash = newConfigHash;
  }
  return syncService;
}

export function resetSyncService(): void {
  syncService = null;
  clientConfigHash = null;
}

export { SyncService };
export type { SyncServiceConfig };
