/**
 * IES Session Store
 * Manages session state for the IES Explorer plugin
 */

import { writable, derived, get } from 'svelte/store';
import type { Message } from '../ies-chat';

export type SessionStatus = 'idle' | 'starting' | 'active' | 'ending' | 'ended' | 'error';

export interface IESProfile {
    summary: string;
    capacity: number;
    recentContext: string | null;
}

export interface IESSessionState {
    id: string | null;
    status: SessionStatus;
    messages: Message[];
    profile: IESProfile | null;
    startedAt: number | null;
    endedAt: number | null;
    error: string | null;
    // Extraction results (after session ends)
    extractionResult: {
        docId: string;
        entitiesExtracted: number;
        summary: string;
    } | null;
}

// Initial state
const initialState: IESSessionState = {
    id: null,
    status: 'idle',
    messages: [],
    profile: null,
    startedAt: null,
    endedAt: null,
    error: null,
    extractionResult: null
};

// Create the store
function createSessionStore() {
    const { subscribe, set, update } = writable<IESSessionState>(initialState);

    return {
        subscribe,

        /**
         * Start a new session
         */
        startSession: (sessionId: string, profile: IESProfile, greeting: string) => {
            update(state => ({
                ...state,
                id: sessionId,
                status: 'active',
                messages: [{
                    role: 'assistant',
                    content: greeting,
                    timestamp: Date.now()
                }],
                profile,
                startedAt: Date.now(),
                endedAt: null,
                error: null,
                extractionResult: null
            }));
        },

        /**
         * Set session to starting state
         */
        setStarting: () => {
            update(state => ({
                ...state,
                status: 'starting',
                error: null
            }));
        },

        /**
         * Add a user message
         */
        addUserMessage: (content: string) => {
            update(state => ({
                ...state,
                messages: [...state.messages, {
                    role: 'user',
                    content,
                    timestamp: Date.now()
                }]
            }));
        },

        /**
         * Add an assistant message (for streaming, start empty)
         */
        addAssistantMessage: (content: string = '') => {
            update(state => ({
                ...state,
                messages: [...state.messages, {
                    role: 'assistant',
                    content,
                    timestamp: Date.now()
                }]
            }));
        },

        /**
         * Append to the last assistant message (for streaming)
         */
        appendToLastMessage: (chunk: string) => {
            update(state => {
                const messages = [...state.messages];
                const lastIndex = messages.length - 1;
                if (lastIndex >= 0 && messages[lastIndex].role === 'assistant') {
                    messages[lastIndex] = {
                        ...messages[lastIndex],
                        content: messages[lastIndex].content + chunk
                    };
                }
                return { ...state, messages };
            });
        },

        /**
         * Set session to ending state
         */
        setEnding: () => {
            update(state => ({
                ...state,
                status: 'ending'
            }));
        },

        /**
         * End the session with extraction results
         */
        endSession: (result: { docId: string; entitiesExtracted: number; summary: string }) => {
            update(state => ({
                ...state,
                status: 'ended',
                endedAt: Date.now(),
                extractionResult: result
            }));
        },

        /**
         * Set error state
         */
        setError: (error: string) => {
            update(state => ({
                ...state,
                status: 'error',
                error
            }));
        },

        /**
         * Reset to initial state
         */
        reset: () => {
            set(initialState);
        },

        /**
         * Get current state (snapshot)
         */
        getState: () => get({ subscribe })
    };
}

// Export the singleton store
export const iesSession = createSessionStore();

// Derived stores for convenience
export const isSessionActive = derived(iesSession, $session => $session.status === 'active');
export const isSessionStarting = derived(iesSession, $session => $session.status === 'starting');
export const isSessionEnding = derived(iesSession, $session => $session.status === 'ending');
export const canSendMessage = derived(iesSession, $session => $session.status === 'active');
export const sessionDuration = derived(iesSession, $session => {
    if (!$session.startedAt) return 0;
    const endTime = $session.endedAt || Date.now();
    return Math.floor((endTime - $session.startedAt) / 1000);
});
