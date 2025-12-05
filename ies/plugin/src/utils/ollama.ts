/**
 * Ollama API Client
 *
 * Handles communication with local Ollama server for model discovery and health checks.
 */

export interface OllamaModel {
    name: string;
    size: number;
    digest: string;
    modified_at: string;
}

export interface OllamaHealthStatus {
    ok: boolean;
    modelCount: number;
    error?: string;
}

export interface OllamaModelsResponse {
    models: OllamaModel[];
}

// Patterns to identify embedding models
const EMBEDDING_PATTERNS = [
    'embed',
    'nomic',
    'bge',
    'e5',
    'gte',
    'instructor',
];

/**
 * Check if Ollama server is healthy and return model count
 */
export async function checkOllamaHealth(ollamaUrl: string): Promise<OllamaHealthStatus> {
    try {
        const response = await fetch(`${ollamaUrl}/api/tags`, {
            method: 'GET',
            headers: { 'Content-Type': 'application/json' },
        });

        if (!response.ok) {
            return {
                ok: false,
                modelCount: 0,
                error: `HTTP ${response.status}: ${response.statusText}`,
            };
        }

        const data: OllamaModelsResponse = await response.json();
        return {
            ok: true,
            modelCount: data.models?.length ?? 0,
        };
    } catch (error) {
        return {
            ok: false,
            modelCount: 0,
            error: error instanceof Error ? error.message : 'Connection failed',
        };
    }
}

/**
 * Fetch all available models from Ollama
 */
export async function fetchOllamaModels(ollamaUrl: string): Promise<OllamaModel[]> {
    try {
        const response = await fetch(`${ollamaUrl}/api/tags`, {
            method: 'GET',
            headers: { 'Content-Type': 'application/json' },
        });

        if (!response.ok) {
            console.error(`Ollama API error: ${response.status}`);
            return [];
        }

        const data: OllamaModelsResponse = await response.json();
        return data.models ?? [];
    } catch (error) {
        console.error('Failed to fetch Ollama models:', error);
        return [];
    }
}

/**
 * Check if a model name looks like an embedding model
 */
export function isEmbeddingModel(modelName: string): boolean {
    const lowerName = modelName.toLowerCase();
    return EMBEDDING_PATTERNS.some(pattern => lowerName.includes(pattern));
}

/**
 * Get chat models (non-embedding models)
 */
export function filterChatModels(models: OllamaModel[]): OllamaModel[] {
    return models.filter(m => !isEmbeddingModel(m.name));
}

/**
 * Get embedding models
 */
export function filterEmbeddingModels(models: OllamaModel[]): OllamaModel[] {
    return models.filter(m => isEmbeddingModel(m.name));
}

/**
 * Format model name for display (remove tag if :latest)
 */
export function formatModelName(name: string): string {
    return name.replace(/:latest$/, '');
}

/**
 * Format file size for display
 */
export function formatModelSize(bytes: number): string {
    const gb = bytes / (1024 * 1024 * 1024);
    if (gb >= 1) {
        return `${gb.toFixed(1)} GB`;
    }
    const mb = bytes / (1024 * 1024);
    return `${mb.toFixed(0)} MB`;
}
