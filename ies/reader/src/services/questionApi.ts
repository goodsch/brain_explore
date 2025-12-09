/**
 * Question API client for IES Reader.
 *
 * Connects to the IES backend to sync questions with the Context + Question layer.
 */

import type { PassageRankingRequest, PassageRankingResponse } from '../types/api';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8081';

export interface Question {
  id: string;
  context_id: string;
  text: string;
  status: 'open' | 'partial' | 'answered' | 'modeled';
  source: 'siyuan' | 'reader' | 'ai-suggested' | 'dialogue';
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
  source?: 'reader' | 'siyuan' | 'ai-suggested' | 'dialogue';
  parent_question_id?: string;
  siyuan_block_id?: string;
}

export interface QuestionUpdate {
  text?: string;
  status?: 'open' | 'partial' | 'answered' | 'modeled';
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

class QuestionApiClient {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE) {
    this.baseUrl = baseUrl;
  }

  /**
   * List questions with optional filters.
   */
  async list(params?: {
    context_id?: string;
    source?: Question['source'];
    status?: Question['status'];
    limit?: number;
  }): Promise<Question[]> {
    const searchParams = new URLSearchParams();
    if (params?.context_id) searchParams.set('context_id', params.context_id);
    if (params?.source) searchParams.set('source', params.source);
    if (params?.status) searchParams.set('status', params.status);
    if (params?.limit) searchParams.set('limit', String(params.limit));

    const url = `${this.baseUrl}/questions/?${searchParams.toString()}`;
    const res = await fetch(url);

    if (!res.ok) {
      throw new Error(`Failed to fetch questions: ${res.statusText}`);
    }

    return res.json();
  }

  /**
   * Get a single question by ID.
   */
  async get(id: string): Promise<Question | null> {
    const res = await fetch(`${this.baseUrl}/questions/${id}`);

    if (res.status === 404) {
      return null;
    }

    if (!res.ok) {
      throw new Error(`Failed to fetch question: ${res.statusText}`);
    }

    return res.json();
  }

  /**
   * Create a new question.
   */
  async create(data: QuestionCreate): Promise<Question> {
    const res = await fetch(`${this.baseUrl}/questions/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        ...data,
        source: data.source || 'reader',
      }),
    });

    if (!res.ok) {
      throw new Error(`Failed to create question: ${res.statusText}`);
    }

    return res.json();
  }

  /**
   * Update an existing question.
   */
  async update(id: string, data: QuestionUpdate): Promise<Question> {
    const res = await fetch(`${this.baseUrl}/questions/${id}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });

    if (!res.ok) {
      throw new Error(`Failed to update question: ${res.statusText}`);
    }

    return res.json();
  }

  /**
   * Delete a question.
   */
  async delete(id: string): Promise<boolean> {
    const res = await fetch(`${this.baseUrl}/questions/${id}`, {
      method: 'DELETE',
    });

    if (res.status === 404) {
      return false;
    }

    if (!res.ok) {
      throw new Error(`Failed to delete question: ${res.statusText}`);
    }

    return true;
  }

  /**
   * List answers for a question.
   */
  async listAnswers(questionId: string): Promise<AnswerBlock[]> {
    const res = await fetch(`${this.baseUrl}/questions/${questionId}/answers`);

    if (!res.ok) {
      throw new Error(`Failed to fetch answers: ${res.statusText}`);
    }

    return res.json();
  }

  /**
   * Create an answer block for a question.
   */
  async createAnswer(data: AnswerBlockCreate): Promise<AnswerBlock> {
    const res = await fetch(`${this.baseUrl}/questions/${data.question_id}/answers`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });

    if (!res.ok) {
      throw new Error(`Failed to create answer: ${res.statusText}`);
    }

    return res.json();
  }

  /**
   * Get relevant passages for a question (P1 feature).
   *
   * Returns ranked passages from books based on question content.
   */
  async getRelevantPassages(
    questionId: string,
    params?: PassageRankingRequest
  ): Promise<PassageRankingResponse> {
    const searchParams = new URLSearchParams();
    if (params?.max_passages) searchParams.set('max_passages', String(params.max_passages));
    if (params?.min_score) searchParams.set('min_score', String(params.min_score));
    if (params?.source_ids) {
      params.source_ids.forEach((id) => searchParams.append('source_ids', id));
    }

    const url = `${this.baseUrl}/questions/${questionId}/rank-passages?${searchParams.toString()}`;
    const res = await fetch(url);

    if (!res.ok) {
      throw new Error(`Failed to fetch relevant passages: ${res.statusText}`);
    }

    return res.json();
  }
}

// Singleton instance
export const questionApi = new QuestionApiClient();

// Export class for testing/custom instances
export { QuestionApiClient };
