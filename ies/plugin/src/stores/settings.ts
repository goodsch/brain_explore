import { writable, get } from 'svelte/store';
import type { Writable } from 'svelte/store';

// ============================================================================
// Settings Schema
// ============================================================================

export type ChatProvider = 'ollama' | 'openai' | 'anthropic';
export type EmbeddingProvider = 'ollama' | 'openai';

export interface IESSettings {
    // Connections
    backendUrl: string;
    ollamaUrl: string;

    // AI Provider Selection
    chatProvider: ChatProvider;
    chatModel: string;

    embeddingProvider: EmbeddingProvider;
    embeddingModel: string;

    // Cloud API Keys (stored locally, never sent to backend)
    openaiApiKey: string;
    anthropicApiKey: string;

    // Notebook Preferences
    preferredNotebooks: string[];

    // User & Display
    userId: string;
    showQuestionBadges: boolean;
    autoSaveSessions: boolean;
}

// ============================================================================
// Default Values
// ============================================================================

export const DEFAULT_SETTINGS: IESSettings = {
    // Connections
    backendUrl: 'http://192.168.86.60:8081',
    ollamaUrl: 'http://localhost:11434',

    // AI Provider Selection - default to cloud for better quality
    chatProvider: 'openai',
    chatModel: 'gpt-4o',

    embeddingProvider: 'openai',
    embeddingModel: 'text-embedding-3-small',

    // Cloud API Keys
    openaiApiKey: '',
    anthropicApiKey: '',

    // Notebook Preferences
    preferredNotebooks: ['Personal', 'Knowledge', 'Notes', 'Intelligent Exploration System'],

    // User & Display
    userId: 'chris',
    showQuestionBadges: true,
    autoSaveSessions: true,
};

// ============================================================================
// Model Lists
// ============================================================================

export const OPENAI_CHAT_MODELS = [
    { id: 'gpt-4o', name: 'GPT-4o' },
    { id: 'gpt-4o-mini', name: 'GPT-4o Mini' },
    { id: 'gpt-4-turbo', name: 'GPT-4 Turbo' },
    { id: 'o1', name: 'o1' },
    { id: 'o1-mini', name: 'o1 Mini' },
];

export const ANTHROPIC_CHAT_MODELS = [
    { id: 'claude-sonnet-4-20250514', name: 'Claude Sonnet 4' },
    { id: 'claude-opus-4-0-20250514', name: 'Claude Opus 4' },
    { id: 'claude-3-5-haiku-20241022', name: 'Claude 3.5 Haiku' },
];

export const OPENAI_EMBEDDING_MODELS = [
    { id: 'text-embedding-3-small', name: 'text-embedding-3-small' },
    { id: 'text-embedding-3-large', name: 'text-embedding-3-large' },
    { id: 'text-embedding-ada-002', name: 'text-embedding-ada-002' },
];

// ============================================================================
// Store
// ============================================================================

export const settingsStore: Writable<IESSettings> = writable({ ...DEFAULT_SETTINGS });

// ============================================================================
// Helper Functions
// ============================================================================

/**
 * Update settings (partial update supported)
 */
export function updateSettings(newSettings: Partial<IESSettings>): void {
    settingsStore.update(current => ({
        ...current,
        ...newSettings,
    }));
}

/**
 * Get current settings synchronously
 */
export function getSettingsSync(): IESSettings {
    return get(settingsStore);
}

/**
 * Get current settings (async for compatibility)
 */
export function getSettings(): Promise<IESSettings> {
    return Promise.resolve(get(settingsStore));
}

/**
 * Reset settings to defaults
 */
export function resetSettings(): void {
    settingsStore.set({ ...DEFAULT_SETTINGS });
}

/**
 * Initialize settings from loaded data (merges with defaults)
 */
export function initializeSettings(loadedSettings: Partial<IESSettings> | null): void {
    if (loadedSettings) {
        settingsStore.set({
            ...DEFAULT_SETTINGS,
            ...loadedSettings,
        });
    } else {
        settingsStore.set({ ...DEFAULT_SETTINGS });
    }
}

/**
 * Get settings as plain object for saving
 */
export function getSettingsForSave(): IESSettings {
    return get(settingsStore);
}
