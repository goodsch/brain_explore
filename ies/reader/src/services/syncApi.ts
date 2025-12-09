/**
 * Sync API client for IES Reader.
 *
 * Enables cross-app session synchronization with SiYuan plugin
 * via backend /sync endpoints.
 */

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8081';

// Types matching backend schemas
export type AppSource = 'reader' | 'siyuan';
export type SessionStatus = 'active' | 'paused' | 'completed';

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
    dwell_time?: number;
}

export interface ExplorationSession {
    id: string;
    user_id: string;
    app_source: AppSource;
    created_at: string;
    updated_at: string;
    status: SessionStatus;

    // Current state
    current_entity_id?: string;
    current_entity_name?: string;
    reading_position?: ReadingPosition;

    // Journey
    journey_path: JourneyStep[];
    trail_stack: unknown[];

    // Resume
    resume_hint?: string;
}

export interface SessionCreateRequest {
    user_id: string;
    app_source: AppSource;
    current_entity_id?: string;
    current_entity_name?: string;
    reading_position?: ReadingPosition;
    journey_path?: JourneyStep[];
    trail_stack?: unknown[];
    resume_hint?: string;
}

export interface SessionUpdateRequest {
    current_entity_id?: string;
    current_entity_name?: string;
    reading_position?: ReadingPosition;
    journey_path?: JourneyStep[];
    trail_stack?: unknown[];
    resume_hint?: string;
    status?: SessionStatus;
}

export interface ResumeData {
    session: ExplorationSession;
    deep_link: string;
    instructions: string;
}

/**
 * Get dynamic API base URL based on current window location.
 * Supports network access (e.g., from iPad on same network).
 */
function getApiBase(): string {
    if (typeof window === 'undefined') return API_BASE;

    const hostname = window.location.hostname;
    if (hostname === 'localhost' || hostname === '127.0.0.1') {
        return API_BASE;
    }
    // Use same hostname for backend when accessed via network IP
    return `http://${hostname}:8081`;
}

/**
 * Sync API client for cross-app session management.
 */
export class SyncApiClient {
    /**
     * Create a new exploration session or update existing one.
     */
    async createOrUpdate(
        data: SessionCreateRequest,
        sessionId?: string
    ): Promise<ExplorationSession> {
        const url = sessionId
            ? `${getApiBase()}/sync/sessions?session_id=${sessionId}`
            : `${getApiBase()}/sync/sessions`;

        const res = await fetch(url, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data),
        });

        if (!res.ok) {
            throw new Error(`Failed to create/update session: ${res.status}`);
        }

        const result = await res.json();
        return result.session;
    }

    /**
     * Get active and paused sessions for a user.
     */
    async getActiveSessions(
        userId: string,
        includePaused = true
    ): Promise<ExplorationSession[]> {
        const url = `${getApiBase()}/sync/sessions/active?user_id=${userId}&include_paused=${includePaused}`;
        const res = await fetch(url);

        if (!res.ok) {
            throw new Error(`Failed to get active sessions: ${res.status}`);
        }

        const result = await res.json();
        return result.sessions || [];
    }

    /**
     * Get a specific session by ID.
     */
    async getSession(sessionId: string): Promise<ExplorationSession | null> {
        const res = await fetch(`${getApiBase()}/sync/sessions/${sessionId}`);

        if (res.status === 404) {
            return null;
        }

        if (!res.ok) {
            throw new Error(`Failed to get session: ${res.status}`);
        }

        const result = await res.json();
        return result.session;
    }

    /**
     * Get resume data for switching to another app.
     */
    async getResumeData(
        sessionId: string,
        targetApp: AppSource
    ): Promise<ResumeData | null> {
        const res = await fetch(
            `${getApiBase()}/sync/sessions/${sessionId}/resume?target_app=${targetApp}`
        );

        if (res.status === 404) {
            return null;
        }

        if (!res.ok) {
            throw new Error(`Failed to get resume data: ${res.status}`);
        }

        return res.json();
    }

    /**
     * Update an existing session.
     */
    async updateSession(
        sessionId: string,
        data: SessionUpdateRequest
    ): Promise<ExplorationSession | null> {
        const res = await fetch(`${getApiBase()}/sync/sessions/${sessionId}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data),
        });

        if (res.status === 404) {
            return null;
        }

        if (!res.ok) {
            throw new Error(`Failed to update session: ${res.status}`);
        }

        const result = await res.json();
        return result.session;
    }

    /**
     * Update session status only.
     */
    async updateStatus(
        sessionId: string,
        status: SessionStatus
    ): Promise<ExplorationSession | null> {
        const res = await fetch(
            `${getApiBase()}/sync/sessions/${sessionId}/status`,
            {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ status }),
            }
        );

        if (res.status === 404) {
            return null;
        }

        if (!res.ok) {
            throw new Error(`Failed to update session status: ${res.status}`);
        }

        const result = await res.json();
        return result.session;
    }

    /**
     * Delete a session.
     */
    async deleteSession(sessionId: string): Promise<boolean> {
        const res = await fetch(`${getApiBase()}/sync/sessions/${sessionId}`, {
            method: 'DELETE',
        });

        if (res.status === 404) {
            return false;
        }

        if (!res.ok) {
            throw new Error(`Failed to delete session: ${res.status}`);
        }

        return true;
    }
}

// Default singleton instance
export const syncApi = new SyncApiClient();
