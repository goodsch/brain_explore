/**
 * IES Backend Client
 * Handles communication with the IES FastAPI backend
 */

export interface Message {
    role: 'user' | 'assistant' | 'system';
    content: string;
    timestamp?: number;
}

export interface SessionStartResponse {
    session_id: string;
    profile_summary: string;
    recent_context: string | null;
    greeting: string;
}

export interface SessionEndResponse {
    doc_id: string;
    entities_extracted: number;
    summary: string;
}

export interface ChatOptions {
    sessionId: string;
    message: string;
    messages?: Message[];
    onChunk?: (chunk: string) => void;
    onComplete?: (fullText: string) => void;
    onError?: (error: Error) => void;
    signal?: AbortSignal;
}

// Backend URL - computed dynamically based on where SiYuan is accessed from
let _backendUrl: string | null = null;

function getComputedBackendUrl(): string {
    if (_backendUrl) return _backendUrl;

    // Compute based on current hostname
    if (typeof window !== 'undefined' && window.location.hostname !== 'localhost') {
        _backendUrl = `http://${window.location.hostname}:8081`;
    } else {
        _backendUrl = 'http://192.168.86.60:8081';
    }
    console.log('[IES-chat] Computed backend URL:', _backendUrl);
    return _backendUrl;
}


/**
 * Set the IES backend URL (override auto-detection)
 */
export function setBackendUrl(url: string) {
    _backendUrl = url.replace(/\/$/, ''); // Remove trailing slash
    console.log('[IES-chat] Backend URL set to:', _backendUrl);
}

/**
 * Get the current backend URL
 */
export function getBackendUrl(): string {
    return getComputedBackendUrl();
}

/**
 * Check if the backend is reachable
 */
export async function checkBackendHealth(): Promise<boolean> {
    const url = `${getComputedBackendUrl()}/health`;
    console.log('[IES-chat] Health check URL:', url);
    try {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 5000);

        const response = await fetch(url, {
            method: 'GET',
            headers: { 'Content-Type': 'application/json' },
            signal: controller.signal
        });
        clearTimeout(timeoutId);
        console.log('[IES-chat] Health check response:', response.ok);
        return response.ok;
    } catch (error) {
        console.error('[IES-chat] Backend health check failed:', error);
        return false;
    }
}

/**
 * Start a new exploration session
 */
export async function startSession(userId: string): Promise<SessionStartResponse> {
    const url = `${getComputedBackendUrl()}/session/start`;
    console.log('[IES-chat] Starting session at:', url);

    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 10000);

    try {
        const response = await fetch(url, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ user_id: userId }),
            signal: controller.signal
        });
        clearTimeout(timeoutId);

        console.log('[IES-chat] Session response status:', response.status);

        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(`Failed to start session: ${response.status} ${errorText}`);
        }

        const data = await response.json();
        console.log('[IES-chat] Session data:', data);
        return data;
    } catch (error) {
        clearTimeout(timeoutId);
        throw error;
    }
}

/**
 * Send a chat message and receive streaming response
 */
export async function chat(options: ChatOptions): Promise<void> {
    const { sessionId, message, messages = [], onChunk, onComplete, onError, signal } = options;

    try {
        const response = await fetch(`${getComputedBackendUrl()}/session/chat`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                session_id: sessionId,
                message: message,
                messages: messages.map(m => ({ role: m.role, content: m.content }))
            }),
            signal
        });

        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(`Chat request failed: ${response.status} ${errorText}`);
        }

        // Handle streaming response (SSE)
        if (response.body) {
            await handleStreamResponse(response.body, { onChunk, onComplete, onError });
        } else {
            // Fallback for non-streaming response
            const data = await response.json();
            const content = data.response || data.content || '';
            onChunk?.(content);
            onComplete?.(content);
        }
    } catch (error) {
        if ((error as Error).name === 'AbortError') {
            console.log('Chat request was aborted');
            onError?.(new Error('Request aborted'));
        } else {
            console.error('Chat error:', error);
            onError?.(error as Error);
        }
        throw error;
    }
}

/**
 * End the current session and trigger entity extraction
 */
export async function endSession(
    sessionId: string,
    userId: string,
    transcript: Message[],
    sessionTitle?: string
): Promise<SessionEndResponse> {
    const response = await fetch(`${getComputedBackendUrl()}/session/end`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            session_id: sessionId,
            user_id: userId,
            transcript: transcript,
            session_title: sessionTitle
        })
    });

    if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`Failed to end session: ${response.status} ${errorText}`);
    }

    return response.json();
}

/**
 * Handle Server-Sent Events (SSE) streaming response
 */
async function handleStreamResponse(
    body: ReadableStream<Uint8Array>,
    callbacks: {
        onChunk?: (chunk: string) => void;
        onComplete?: (fullText: string) => void;
        onError?: (error: Error) => void;
    }
): Promise<void> {
    const { onChunk, onComplete, onError } = callbacks;
    const reader = body.getReader();
    const decoder = new TextDecoder();
    let fullText = '';
    let buffer = '';

    try {
        while (true) {
            const { done, value } = await reader.read();

            if (done) break;

            buffer += decoder.decode(value, { stream: true });
            const lines = buffer.split('\n');
            buffer = lines.pop() || '';

            for (const line of lines) {
                const trimmed = line.trim();
                if (!trimmed || trimmed === 'data: [DONE]') continue;

                if (trimmed.startsWith('data: ')) {
                    try {
                        const json = JSON.parse(trimmed.slice(6));
                        // Handle different response formats
                        const content = json.content || json.delta?.content || json.choices?.[0]?.delta?.content || '';
                        if (content) {
                            fullText += content;
                            onChunk?.(content);
                        }
                    } catch (e) {
                        // If not JSON, treat as plain text chunk
                        const content = trimmed.slice(6);
                        if (content && content !== '[DONE]') {
                            fullText += content;
                            onChunk?.(content);
                        }
                    }
                }
            }
        }

        onComplete?.(fullText);
    } catch (error) {
        if ((error as Error).name === 'AbortError') {
            console.log('Stream reading was aborted');
            if (fullText) {
                onComplete?.(fullText);
            }
        } else {
            console.error('Stream reading error:', error);
            onError?.(error as Error);
        }
        throw error;
    } finally {
        reader.releaseLock();
    }
}

/**
 * Estimate token count for a message (rough approximation)
 */
export function estimateTokens(text: string): number {
    // Rough estimate: ~4 characters per token for English
    // Chinese characters are roughly 1.5 tokens each
    const chineseChars = (text.match(/[\u4e00-\u9fa5]/g) || []).length;
    const otherChars = text.length - chineseChars;
    return Math.ceil(chineseChars * 1.5 + otherChars / 4);
}

/**
 * Calculate total tokens for a conversation
 */
export function calculateTotalTokens(messages: Message[]): number {
    return messages.reduce((total, msg) => total + estimateTokens(msg.content), 0);
}
