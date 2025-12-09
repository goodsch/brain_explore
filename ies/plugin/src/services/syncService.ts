/**
 * SyncService - Cross-app session synchronization for SiYuan Plugin
 *
 * Syncs exploration sessions between SiYuan plugin and ies-reader (Readest)
 * via backend /sync API endpoints.
 */

import { fetchSyncPost } from 'siyuan';

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
    app_source: 'reader' | 'siyuan';
    created_at: string;
    updated_at: string;
    status: 'active' | 'paused' | 'completed';

    // Current state
    current_entity_id?: string;
    current_entity_name?: string;
    reading_position?: ReadingPosition;

    // Journey
    journey_path: JourneyStep[];
    trail_stack: any[];

    // Resume
    resume_hint?: string;
}

export interface CreateSessionRequest {
    user_id: string;
    app_source: 'reader' | 'siyuan';
    current_entity_id?: string;
    current_entity_name?: string;
    reading_position?: ReadingPosition;
    journey_path?: JourneyStep[];
    trail_stack?: any[];
    resume_hint?: string;
}

export interface ResumeData {
    session: ExplorationSession;
    deep_link: string;
    instructions: string;
}

/**
 * Forward proxy helper for API calls via SiYuan's network API
 */
async function forwardProxy<T>(
    method: 'GET' | 'POST' | 'PUT',
    endpoint: string,
    backendUrl: string,
    body?: any
): Promise<T> {
    const url = `${backendUrl}${endpoint}`;

    const payload: any = {
        url,
        method,
        timeout: 60000,
        contentType: 'application/json',
        headers: [],
    };

    if (body) {
        payload.payload = JSON.stringify(body);
    }

    const response = await fetchSyncPost('/api/network/forwardProxy', payload);

    if (response.code !== 0) {
        throw new Error(`Proxy error: ${response.msg}`);
    }

    const proxyData = response.data;
    if (!proxyData || (proxyData.status !== 200 && proxyData.status !== 201)) {
        throw new Error(`Backend error: ${proxyData?.status || 'unknown'}`);
    }

    return typeof proxyData.body === 'string' ? JSON.parse(proxyData.body) : proxyData.body;
}

/**
 * Create or update an exploration session
 */
export async function createOrUpdateSession(
    session: CreateSessionRequest,
    backendUrl: string
): Promise<ExplorationSession> {
    return forwardProxy<ExplorationSession>(
        'POST',
        '/sync/sessions',
        backendUrl,
        session
    );
}

/**
 * Get active and paused sessions for a user
 */
export async function getActiveSessions(
    userId: string,
    backendUrl: string
): Promise<ExplorationSession[]> {
    const response = await forwardProxy<{ sessions: ExplorationSession[] }>(
        'GET',
        `/sync/sessions/active?user_id=${userId}`,
        backendUrl
    );
    return response.sessions || [];
}

/**
 * Get a specific session by ID
 */
export async function getSession(
    sessionId: string,
    backendUrl: string
): Promise<ExplorationSession> {
    return forwardProxy<ExplorationSession>(
        'GET',
        `/sync/sessions/${sessionId}`,
        backendUrl
    );
}

/**
 * Get resume data for a session with deep link for target app
 */
export async function getResumeData(
    sessionId: string,
    targetApp: 'reader' | 'siyuan',
    backendUrl: string
): Promise<ResumeData> {
    return forwardProxy<ResumeData>(
        'GET',
        `/sync/sessions/${sessionId}/resume?target_app=${targetApp}`,
        backendUrl
    );
}

/**
 * Update session status
 */
export async function updateSessionStatus(
    sessionId: string,
    status: 'active' | 'paused' | 'completed',
    backendUrl: string
): Promise<ExplorationSession> {
    return forwardProxy<ExplorationSession>(
        'PUT',
        `/sync/sessions/${sessionId}/status`,
        backendUrl,
        { status }
    );
}
