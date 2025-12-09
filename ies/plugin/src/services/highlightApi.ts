/**
 * Highlight API client for SiYuan Plugin.
 *
 * Fetches highlights from IES backend for display in Book Notes.
 * Uses SiYuan's forwardProxy to bypass CORS restrictions.
 */

import { fetchSyncPost } from 'siyuan';

// Types matching backend schemas
export type HighlightColor = 'yellow' | 'green' | 'blue' | 'pink' | 'purple';

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

export interface HighlightListResponse {
    highlights: Highlight[];
    total: number;
    book_id?: string;
}

export interface SyncToSiyuanResponse {
    message: string;
    book_id: string;
    synced: number;
    already_synced: number;
    errors: string[];
}

/**
 * Forward proxy helper for API calls via SiYuan's network API.
 * Bypasses CORS restrictions when calling backend from plugin.
 */
async function forwardProxy<T>(
    method: 'GET' | 'POST' | 'PATCH' | 'DELETE',
    endpoint: string,
    backendUrl: string,
    body?: unknown
): Promise<T> {
    const url = `${backendUrl}${endpoint}`;

    const payload: Record<string, unknown> = {
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
    if (!proxyData || (proxyData.status !== 200 && proxyData.status !== 201 && proxyData.status !== 204)) {
        throw new Error(`Backend error: ${proxyData?.status || 'unknown'}`);
    }

    // Handle empty responses (DELETE returns 204)
    if (proxyData.status === 204 || !proxyData.body) {
        return {} as T;
    }

    return typeof proxyData.body === 'string' ? JSON.parse(proxyData.body) : proxyData.body;
}

/**
 * Highlight API client for SiYuan plugin.
 */
export class HighlightApiClient {
    private backendUrl: string;

    constructor(backendUrl: string = 'http://192.168.86.60:8081') {
        this.backendUrl = backendUrl;
    }

    /**
     * List highlights for a specific book.
     */
    async listByBook(bookId: string, limit: number = 100): Promise<Highlight[]> {
        const response = await forwardProxy<HighlightListResponse>(
            'GET',
            `/highlights/book/${bookId}?limit=${limit}`,
            this.backendUrl
        );
        return response.highlights;
    }

    /**
     * List all highlights with optional filtering.
     */
    async list(params?: {
        book_id?: string;
        context_id?: string;
        limit?: number;
    }): Promise<Highlight[]> {
        const searchParams = new URLSearchParams();
        if (params?.book_id) searchParams.set('book_id', params.book_id);
        if (params?.context_id) searchParams.set('context_id', params.context_id);
        if (params?.limit) searchParams.set('limit', String(params.limit));

        const endpoint = `/highlights?${searchParams.toString()}`;
        const response = await forwardProxy<HighlightListResponse>('GET', endpoint, this.backendUrl);
        return response.highlights;
    }

    /**
     * Get a single highlight by ID.
     */
    async get(id: string): Promise<Highlight | null> {
        try {
            return await forwardProxy<Highlight>('GET', `/highlights/${id}`, this.backendUrl);
        } catch (err) {
            if (err instanceof Error && err.message.includes('404')) {
                return null;
            }
            throw err;
        }
    }

    /**
     * Sync a highlight to SiYuan Book Note.
     */
    async syncToSiyuan(highlightId: string): Promise<{ siyuan_block_id: string }> {
        return forwardProxy<{ siyuan_block_id: string }>(
            'POST',
            `/highlights/${highlightId}/sync-siyuan`,
            this.backendUrl
        );
    }

    /**
     * Sync all highlights for a book to SiYuan.
     */
    async syncBookToSiyuan(bookId: string): Promise<SyncToSiyuanResponse> {
        return forwardProxy<SyncToSiyuanResponse>(
            'POST',
            `/highlights/book/${bookId}/sync-siyuan`,
            this.backendUrl
        );
    }

    /**
     * Get unsynced highlights (highlights without siyuan_block_id).
     */
    async getUnsyncedHighlights(bookId: string): Promise<Highlight[]> {
        const highlights = await this.listByBook(bookId);
        return highlights.filter(h => !h.siyuan_block_id);
    }
}

// Default singleton instance
let _highlightApi: HighlightApiClient | null = null;

/**
 * Get or create the singleton HighlightApiClient.
 */
export function getHighlightApi(backendUrl?: string): HighlightApiClient {
    if (!_highlightApi || backendUrl) {
        _highlightApi = new HighlightApiClient(backendUrl);
    }
    return _highlightApi;
}
