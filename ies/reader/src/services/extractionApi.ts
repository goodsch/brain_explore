/**
 * Extraction API client for IES Reader.
 *
 * Enables context-aware entity extraction from the Flow panel.
 * Calls backend POST /extraction/run to trigger extraction pipeline.
 */

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8081';

// Request/Response types matching backend schemas

export interface ExtractionRunRequest {
  context_id: string;
  question_id?: string;
  source_ids?: string[];
  max_segments?: number;
}

export interface ExtractionResult {
  context_id: string;
  concepts_found: string[];
  relations_found: Array<{
    source: string;
    target: string;
    type: string;
  }>;
  subquestions_generated: string[];
  sources_processed: number;
  segments_analyzed: number;
}

export interface ExtractionRunResponse {
  result: ExtractionResult;
  journey_entry_id?: string;
}

export interface ExtractionProfile {
  context_id: string;
  core_concepts: string[];
  synonyms: Record<string, string[]>;
  relation_types: string[];
  domain_filters: string[];
}

export interface ExtractionProfileCreate {
  context_id: string;
  core_concepts?: string[];
  synonyms?: Record<string, string[]>;
  relation_types?: string[];
  domain_filters?: string[];
}

class ExtractionApiClient {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE) {
    this.baseUrl = baseUrl;
  }

  /**
   * Run context-aware extraction.
   *
   * Triggers the extraction pipeline which:
   * 1. Loads context and extraction profile
   * 2. Searches for relevant segments in sources
   * 3. Extracts entities/relationships via LLM
   * 4. Logs journey entry
   */
  async runExtraction(request: ExtractionRunRequest): Promise<ExtractionRunResponse> {
    const res = await fetch(`${this.baseUrl}/extraction/run`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(request),
    });

    if (!res.ok) {
      const error = await res.text();
      throw new Error(`Extraction failed: ${error}`);
    }

    return res.json();
  }

  /**
   * Get extraction profile for a context.
   */
  async getProfile(contextId: string): Promise<ExtractionProfile | null> {
    const res = await fetch(`${this.baseUrl}/extraction/profiles/${contextId}`);

    if (res.status === 404) {
      return null;
    }

    if (!res.ok) {
      const error = await res.text();
      throw new Error(`Failed to get profile: ${error}`);
    }

    return res.json();
  }

  /**
   * Create or update an extraction profile for a context.
   */
  async createProfile(profile: ExtractionProfileCreate): Promise<ExtractionProfile> {
    const res = await fetch(`${this.baseUrl}/extraction/profiles`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(profile),
    });

    if (!res.ok) {
      const error = await res.text();
      throw new Error(`Failed to create profile: ${error}`);
    }

    return res.json();
  }
}

// Singleton instance
export const extractionApi = new ExtractionApiClient();

// Export class for testing
export { ExtractionApiClient };
