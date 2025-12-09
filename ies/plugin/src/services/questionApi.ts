/**
 * Question API client for SiYuan Plugin.
 *
 * Syncs questions with the IES backend Context + Question layer.
 * Uses SiYuan's forwardProxy to bypass CORS restrictions.
 */

import { fetchSyncPost } from 'siyuan';

// Types matching backend schemas
export type QuestionStatus = 'open' | 'partial' | 'answered' | 'modeled';
export type QuestionSource = 'siyuan' | 'reader' | 'ai-suggested' | 'dialogue';

export interface Question {
    id: string;
    context_id: string;
    text: string;
    status: QuestionStatus;
    source: QuestionSource;
    parent_question_id?: string;
    prerequisite_questions: string[];
    related_concepts: string[];
    linked_sources: string[];
    siyuan_block_id?: string;
    created_at: string;
    updated_at: string;
}

export interface QuestionCreate {
    context_id: string;
    text: string;
    source?: QuestionSource;
    parent_question_id?: string;
    siyuan_block_id?: string;
}

export interface QuestionUpdate {
    text?: string;
    status?: QuestionStatus;
    parent_question_id?: string;
    prerequisite_questions?: string[];
    related_concepts?: string[];
    linked_sources?: string[];
    siyuan_block_id?: string;
}

export interface AnswerBlock {
    id: string;
    question_id: string;
    content: string;
    quality: 'draft' | 'good_enough' | 'polished';
    created_at: string;
    updated_at: string;
}

export interface AnswerBlockCreate {
    question_id: string;
    content: string;
    quality?: 'draft' | 'good_enough' | 'polished';
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
 * Question API client for SiYuan plugin.
 */
export class QuestionApiClient {
    private backendUrl: string;

    constructor(backendUrl: string = 'http://192.168.86.60:8081') {
        this.backendUrl = backendUrl;
    }

    /**
     * List questions with optional filters.
     */
    async list(params?: {
        context_id?: string;
        source?: QuestionSource;
        status?: QuestionStatus;
        limit?: number;
    }): Promise<Question[]> {
        const searchParams = new URLSearchParams();
        if (params?.context_id) searchParams.set('context_id', params.context_id);
        if (params?.source) searchParams.set('source', params.source);
        if (params?.status) searchParams.set('status', params.status);
        if (params?.limit) searchParams.set('limit', String(params.limit));

        const endpoint = `/questions/?${searchParams.toString()}`;
        return forwardProxy<Question[]>('GET', endpoint, this.backendUrl);
    }

    /**
     * Get a single question by ID.
     */
    async get(id: string): Promise<Question | null> {
        try {
            return await forwardProxy<Question>('GET', `/questions/${id}`, this.backendUrl);
        } catch (err) {
            if (err instanceof Error && err.message.includes('404')) {
                return null;
            }
            throw err;
        }
    }

    /**
     * Create a new question.
     */
    async create(data: QuestionCreate): Promise<Question> {
        return forwardProxy<Question>('POST', '/questions/', this.backendUrl, {
            ...data,
            source: data.source || 'siyuan',
        });
    }

    /**
     * Update an existing question.
     */
    async update(id: string, data: QuestionUpdate): Promise<Question> {
        return forwardProxy<Question>('PATCH', `/questions/${id}`, this.backendUrl, data);
    }

    /**
     * Delete a question.
     */
    async delete(id: string): Promise<boolean> {
        try {
            await forwardProxy<unknown>('DELETE', `/questions/${id}`, this.backendUrl);
            return true;
        } catch (err) {
            if (err instanceof Error && err.message.includes('404')) {
                return false;
            }
            throw err;
        }
    }

    /**
     * List answers for a question.
     */
    async listAnswers(questionId: string): Promise<AnswerBlock[]> {
        return forwardProxy<AnswerBlock[]>('GET', `/questions/${questionId}/answers`, this.backendUrl);
    }

    /**
     * Create an answer block for a question.
     */
    async createAnswer(data: AnswerBlockCreate): Promise<AnswerBlock> {
        return forwardProxy<AnswerBlock>(
            'POST',
            `/questions/${data.question_id}/answers`,
            this.backendUrl,
            data
        );
    }
}

// Default singleton instance
let _questionApi: QuestionApiClient | null = null;

/**
 * Get or create the singleton QuestionApiClient.
 */
export function getQuestionApi(backendUrl?: string): QuestionApiClient {
    if (!_questionApi || backendUrl) {
        _questionApi = new QuestionApiClient(backendUrl);
    }
    return _questionApi;
}
