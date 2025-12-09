/**
 * Context API client for IES Reader.
 *
 * Connects to the IES backend to work with Contexts in the Context + Question layer.
 */

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8081';

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

class ContextApiClient {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE) {
    this.baseUrl = baseUrl;
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

    const url = `${this.baseUrl}/context?${searchParams.toString()}`;
    const res = await fetch(url);

    if (!res.ok) {
      throw new Error(`Failed to fetch contexts: ${res.statusText}`);
    }

    const data = await res.json();
    return data.contexts || [];
  }

  /**
   * Get a single context by ID.
   */
  async get(id: string): Promise<Context | null> {
    const res = await fetch(`${this.baseUrl}/context/${id}`);

    if (res.status === 404) {
      return null;
    }

    if (!res.ok) {
      throw new Error(`Failed to fetch context: ${res.statusText}`);
    }

    return res.json();
  }

  /**
   * Create a new context.
   */
  async create(data: ContextCreate): Promise<Context> {
    const res = await fetch(`${this.baseUrl}/context`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });

    if (!res.ok) {
      throw new Error(`Failed to create context: ${res.statusText}`);
    }

    const response = await res.json();
    return response.context;
  }

  /**
   * Get or create a default context for the reader.
   *
   * If no active context exists, creates a new one with the given title.
   */
  async getOrCreateDefault(title: string = 'Reading Session'): Promise<Context> {
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
}

// Singleton instance
export const contextApi = new ContextApiClient();

// Export class for testing/custom instances
export { ContextApiClient };
