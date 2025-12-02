<script lang="ts">
    import { onMount } from 'svelte';
    import { showMessage, getFrontend, fetchSyncPost } from 'siyuan';

    export let plugin: any;

    // State
    let sessionId: string | null = null;
    let status: 'idle' | 'starting' | 'active' | 'error' = 'idle';
    let messages: Array<{role: string, content: string}> = [];
    let errorMsg = '';
    let inputText = '';
    let isLoading = false;
    let isMobile = false;

    const USER_ID = 'chris';
    const VERSION = '0.1.4';

    // Backend URL - hardcoded because:
    // 1. SiYuan runs in Docker (can't use localhost)
    // 2. iOS app uses local proxy (window.location.hostname = 127.0.0.1)
    const BACKEND_HOST = '192.168.86.60';

    function getBackendUrl(): string {
        return `http://${BACKEND_HOST}:8081`;
    }

    // Use SiYuan's forwardProxy to reach backend
    async function apiPost(endpoint: string, body: any): Promise<any> {
        const url = `${getBackendUrl()}${endpoint}`;

        const response = await fetchSyncPost('/api/network/forwardProxy', {
            url: url,
            method: 'POST',
            timeout: 30000,
            contentType: 'application/json',
            headers: [],
            payload: body  // Don't stringify - pass object directly
        });

        // Check proxy succeeded
        if (response.code !== 0) {
            throw new Error(`Proxy error: ${response.msg}`);
        }

        // Check if data is null
        const proxyData = response.data;
        if (!proxyData) {
            throw new Error(`Proxy returned empty data`);
        }

        // Check backend HTTP status
        if (proxyData.status !== 200) {
            const errorBody = typeof proxyData.body === 'string' ? JSON.parse(proxyData.body) : proxyData.body;
            throw new Error(`Backend error ${proxyData.status}: ${JSON.stringify(errorBody)}`);
        }

        // Parse body if it's a string, otherwise use directly
        return typeof proxyData.body === 'string' ? JSON.parse(proxyData.body) : proxyData.body;
    }

    onMount(() => {
        const frontend = getFrontend();
        isMobile = frontend === 'mobile' || frontend === 'browser-mobile';
    });

    async function handleStart() {
        status = 'starting';
        errorMsg = '';

        apiPost('/session/start', { user_id: USER_ID })
            .then(data => {
                sessionId = data.session_id;
                status = 'active';
                messages = [{
                    role: 'assistant',
                    content: data.greeting
                }];
            })
            .catch(err => {
                console.error('[IES] Start error:', err);
                status = 'error';
                errorMsg = err.message || String(err);
                showMessage(`Error: ${errorMsg}`, 5000, 'error');
            });
    }

    function handleSend() {
        if (!inputText.trim() || isLoading || !sessionId) return;

        const userMsg = inputText.trim();
        inputText = '';
        messages = [...messages, { role: 'user', content: userMsg }];
        messages = [...messages, { role: 'assistant', content: '...' }];
        isLoading = true;

        apiPost('/session/chat-sync', {
            session_id: sessionId,
            message: userMsg,
            messages: messages.slice(0, -1)
        })
            .then(data => {
                messages[messages.length - 1].content = data.response || '';
                messages = messages;
                isLoading = false;
            })
            .catch(err => {
                console.error('[IES] Chat error:', err);
                messages = messages.slice(0, -1);
                showMessage(`Chat error: ${err.message}`, 5000, 'error');
                isLoading = false;
            });
    }

    function handleEnd() {
        if (!sessionId) return;
        status = 'starting'; // reuse for "ending" state

        apiPost('/session/end', {
            session_id: sessionId,
            user_id: USER_ID,
            transcript: messages
        })
            .then(data => {
                showMessage(`Session saved. ${data.entities_extracted} entities extracted.`, 3000);
                sessionId = null;
                status = 'idle';
                messages = [];
            })
            .catch(err => {
                console.error('[IES] End error:', err);
                status = 'error';
                errorMsg = err.message;
                showMessage(`Error: ${err.message}`, 5000, 'error');
            });
    }

    function handleKeydown(e: KeyboardEvent) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSend();
        }
    }
</script>

<div class="ies-sidebar">
    <div class="ies-header">
        <span class="ies-title">IES Develop</span>
        <span class="ies-version">v{VERSION}</span>
        {#if status === 'active'}
            <span class="ies-badge">Active</span>
        {/if}
    </div>

    <div class="ies-controls">
        {#if status === 'idle'}
            <button class="b3-button b3-button--primary" on:click={handleStart}>
                Start Session
            </button>
        {:else if status === 'starting'}
            <div class="ies-loading">Starting...</div>
        {:else if status === 'active'}
            <button class="b3-button" on:click={handleEnd}>
                End Session
            </button>
        {:else if status === 'error'}
            <div class="ies-error">{errorMsg}</div>
            <button class="b3-button" on:click={handleStart}>Retry</button>
        {/if}
    </div>

    <div class="ies-messages">
        {#if messages.length === 0 && status === 'idle'}
            <div class="ies-welcome">
                <p>Start a session to begin.</p>
            </div>
        {:else}
            {#each messages as msg}
                <div class="ies-msg" class:ies-msg--user={msg.role === 'user'}>
                    {msg.content}
                </div>
            {/each}
        {/if}
    </div>

    {#if status === 'active'}
        <div class="ies-input">
            <textarea
                bind:value={inputText}
                on:keydown={handleKeydown}
                placeholder="Type your message..."
                rows="2"
                disabled={isLoading}
            ></textarea>
            <button
                class="b3-button b3-button--primary"
                on:click={handleSend}
                disabled={isLoading || !inputText.trim()}
            >
                {isLoading ? '...' : 'Send'}
            </button>
        </div>
    {/if}
</div>

<style>
    .ies-sidebar {
        display: flex;
        flex-direction: column;
        height: 100%;
        padding: 12px;
        gap: 12px;
    }
    .ies-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .ies-title {
        font-weight: 600;
    }
    .ies-version {
        font-size: 10px;
        padding: 2px 6px;
        background: var(--b3-theme-surface);
        color: var(--b3-theme-on-surface-light);
        border-radius: 3px;
        border: 1px solid var(--b3-border-color);
        font-family: monospace;
    }
    .ies-badge {
        font-size: 12px;
        padding: 2px 8px;
        background: var(--b3-theme-primary-lightest);
        color: var(--b3-theme-primary);
        border-radius: 4px;
    }
    .ies-controls {
        padding-bottom: 12px;
        border-bottom: 1px solid var(--b3-border-color);
    }
    .ies-loading {
        text-align: center;
        color: var(--b3-theme-on-surface-light);
    }
    .ies-error {
        color: var(--b3-theme-error);
        font-size: 13px;
        margin-bottom: 8px;
    }
    .ies-messages {
        flex: 1;
        overflow-y: auto;
    }
    .ies-welcome {
        text-align: center;
        color: var(--b3-theme-on-surface-light);
        padding: 24px;
    }
    .ies-msg {
        padding: 10px 12px;
        margin-bottom: 8px;
        border-radius: 8px;
        background: var(--b3-theme-surface);
        font-size: 14px;
        line-height: 1.5;
    }
    .ies-msg--user {
        background: var(--b3-theme-primary-lightest);
        margin-left: 20px;
    }
    .ies-input {
        display: flex;
        gap: 8px;
        padding-top: 12px;
        border-top: 1px solid var(--b3-border-color);
    }
    .ies-input textarea {
        flex: 1;
        resize: none;
        border: 1px solid var(--b3-border-color);
        border-radius: 6px;
        padding: 8px;
        font-size: 14px;
    }
    .ies-input button {
        align-self: flex-end;
    }
</style>
