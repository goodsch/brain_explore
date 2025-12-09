/**
 * Context API client for SiYuan Plugin.
 *
 * Manages Contexts in the IES backend Context + Question layer.
 * Uses SiYuan's forwardProxy to bypass CORS restrictions.
 */

import { fetchSyncPost } from 'siyuan';

// Types matching backend schemas
export type ContextType = 'feynman_problem' | 'project' | 'theory' | 'concept_cluster' | 'life_area';
export type ContextStatus = 'idea' | 'active' | 'paused' | 'archived';

export interface Context {
    id: string;
    type: ContextType;
    title: string;
    summary?: string;
    parent_context_id?: string;
    status: ContextStatus;
    key_questions: string[];
    core_concepts: string[];
    linked_sources: string[];
    areas_of_exploration: string[];
    siyuan_block_id?: string;
    created_at: string;
    updated_at: string;
}

export interface ContextCreate {
    type: ContextType;
    title: string;
    summary?: string;
    parent_context_id?: string;
    status?: ContextStatus;
    siyuan_doc_id?: string;
}

export interface ContextUpdate {
    type?: ContextType;
    title?: string;
    summary?: string;
    status?: ContextStatus;
    key_questions?: string[];
    core_concepts?: string[];
    linked_sources?: string[];
    areas_of_exploration?: string[];
    siyuan_doc_id?: string;
}

/**
 * Forward proxy helper for API calls via SiYuan's network API.
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

    if (proxyData.status === 204 || !proxyData.body) {
        return {} as T;
    }

    return typeof proxyData.body === 'string' ? JSON.parse(proxyData.body) : proxyData.body;
}

/**
 * Context API client for SiYuan plugin.
 */
export class ContextApiClient {
    private backendUrl: string;

    constructor(backendUrl: string = 'http://localhost:8081') {
        this.backendUrl = backendUrl;
    }

    /**
     * List contexts with optional filters.
     */
    async list(params?: {
        type?: ContextType;
        status?: ContextStatus;
        limit?: number;
    }): Promise<Context[]> {
        const searchParams = new URLSearchParams();
        if (params?.type) searchParams.set('type', params.type);
        if (params?.status) searchParams.set('status', params.status);
        if (params?.limit) searchParams.set('limit', String(params.limit));

        const endpoint = `/context?${searchParams.toString()}`;
        const response = await forwardProxy<{ contexts: Context[] }>('GET', endpoint, this.backendUrl);
        return response.contexts || [];
    }

    /**
     * Get a single context by ID.
     */
    async get(id: string): Promise<Context | null> {
        try {
            return await forwardProxy<Context>('GET', `/context/${id}`, this.backendUrl);
        } catch (err) {
            if (err instanceof Error && err.message.includes('404')) {
                return null;
            }
            throw err;
        }
    }

    /**
     * Create a new context.
     */
    async create(data: ContextCreate): Promise<Context> {
        const response = await forwardProxy<{ context: Context }>(
            'POST',
            '/context',
            this.backendUrl,
            data
        );
        return response.context;
    }

    /**
     * Get or create a default context for SiYuan sessions.
     */
    async getOrCreateDefault(title: string = 'SiYuan Session'): Promise<Context> {
        // Try to get active contexts
        const contexts = await this.list({ status: 'active', limit: 1 });

        if (contexts.length > 0) {
            return contexts[0];
        }

        // Create a new context
        return this.create({
            type: 'project',
            title,
            status: 'active',
        });
    }

    /**
     * Link a SiYuan document to a context.
     */
    async linkSiyuanDoc(contextId: string, siyuanDocId: string): Promise<Context> {
        return forwardProxy<Context>(
            'PATCH',
            `/context/${contextId}`,
            this.backendUrl,
            { siyuan_doc_id: siyuanDocId }
        );
    }
}

// Default singleton instance
let _contextApi: ContextApiClient | null = null;

/**
 * Get or create the singleton ContextApiClient.
 */
export function getContextApi(backendUrl?: string): ContextApiClient {
    if (!_contextApi || backendUrl) {
        _contextApi = new ContextApiClient(backendUrl);
    }
    return _contextApi;
}
