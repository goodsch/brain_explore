<script lang="ts">
    /**
     * ForgeMode - Layer 2 Dialogue Interface
     *
     * AI-guided questioning for thinking pattern revelation.
     * Renamed from "Dialogue" to "Forge" (shaping ideas through dialogue).
     */
    import { onMount, createEventDispatcher } from 'svelte';
    import { showMessage, getFrontend, fetchSyncPost } from 'siyuan';

    export let backendUrl: string;

    const dispatch = createEventDispatcher();

    // State
    let sessionId: string | null = null;
    let status: 'idle' | 'starting' | 'active' | 'error' = 'idle';
    let messages: Array<{role: string, content: string}> = [];
    let errorMsg = '';
    let inputText = '';
    let isLoading = false;
    let isMobile = false;

    const USER_ID = 'chris';

    // Use SiYuan's forwardProxy to reach backend
    async function apiPost(endpoint: string, body: any): Promise<any> {
        const url = `${backendUrl}${endpoint}`;

        const response = await fetchSyncPost('/api/network/forwardProxy', {
            url: url,
            method: 'POST',
            timeout: 30000,
            contentType: 'application/json',
            headers: [],
            payload: body
        });

        if (response.code !== 0) {
            throw new Error(`Proxy error: ${response.msg}`);
        }

        const proxyData = response.data;
        if (!proxyData) {
            throw new Error(`Proxy returned empty data`);
        }

        if (proxyData.status !== 200) {
            const errorBody = typeof proxyData.body === 'string' ? JSON.parse(proxyData.body) : proxyData.body;
            throw new Error(`Backend error ${proxyData.status}: ${JSON.stringify(errorBody)}`);
        }

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
        status = 'starting';

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

    function handleBack() {
        dispatch('back');
    }
</script>

<div class="forge-mode">
    <div class="forge-header">
        <button class="back-btn" on:click={handleBack} title="Back to Dashboard">
            <svg viewBox="0 0 24 24" width="16" height="16">
                <path fill="currentColor" d="M20 11H7.83l5.59-5.59L12 4l-8 8 8 8 1.41-1.41L7.83 13H20v-2z"/>
            </svg>
        </button>
        <span class="forge-title">Forge</span>
        {#if status === 'active'}
            <span class="forge-badge">Active</span>
        {/if}
    </div>

    <div class="forge-controls">
        {#if status === 'idle'}
            <button class="b3-button b3-button--primary" on:click={handleStart}>
                Start Session
            </button>
        {:else if status === 'starting'}
            <div class="forge-loading">Starting...</div>
        {:else if status === 'active'}
            <button class="b3-button" on:click={handleEnd}>
                End Session
            </button>
        {:else if status === 'error'}
            <div class="forge-error">{errorMsg}</div>
            <button class="b3-button" on:click={handleStart}>Retry</button>
        {/if}
    </div>

    <div class="forge-messages">
        {#if messages.length === 0 && status === 'idle'}
            <div class="forge-welcome">
                <p><strong>Forge</strong> is where ideas take shape.</p>
                <p>Start a session to explore your thinking with AI-guided questions.</p>
            </div>
        {:else}
            {#each messages as msg}
                <div class="forge-msg" class:forge-msg--user={msg.role === 'user'}>
                    {msg.content}
                </div>
            {/each}
        {/if}
    </div>

    {#if status === 'active'}
        <div class="forge-input">
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
    .forge-mode {
        display: flex;
        flex-direction: column;
        height: 100%;
        padding: 12px;
        gap: 12px;
    }
    .forge-header {
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .back-btn {
        background: none;
        border: none;
        cursor: pointer;
        padding: 4px;
        border-radius: 4px;
        color: var(--b3-theme-on-surface);
        display: flex;
        align-items: center;
    }
    .back-btn:hover {
        background: var(--b3-theme-surface);
    }
    .forge-title {
        font-weight: 600;
        flex: 1;
    }
    .forge-badge {
        font-size: 12px;
        padding: 2px 8px;
        background: var(--b3-theme-primary-lightest);
        color: var(--b3-theme-primary);
        border-radius: 4px;
    }
    .forge-controls {
        padding-bottom: 12px;
        border-bottom: 1px solid var(--b3-border-color);
    }
    .forge-loading {
        text-align: center;
        color: var(--b3-theme-on-surface-light);
    }
    .forge-error {
        color: var(--b3-theme-error);
        font-size: 13px;
        margin-bottom: 8px;
    }
    .forge-messages {
        flex: 1;
        overflow-y: auto;
    }
    .forge-welcome {
        text-align: center;
        color: var(--b3-theme-on-surface-light);
        padding: 24px;
    }
    .forge-welcome p {
        margin: 8px 0;
    }
    .forge-msg {
        padding: 10px 12px;
        margin-bottom: 8px;
        border-radius: 8px;
        background: var(--b3-theme-surface);
        font-size: 14px;
        line-height: 1.5;
        white-space: pre-wrap;
    }
    .forge-msg--user {
        background: var(--b3-theme-primary-lightest);
        margin-left: 20px;
    }
    .forge-input {
        display: flex;
        gap: 8px;
        padding-top: 12px;
        border-top: 1px solid var(--b3-border-color);
    }
    .forge-input textarea {
        flex: 1;
        resize: none;
        border: 1px solid var(--b3-border-color);
        border-radius: 6px;
        padding: 8px;
        font-size: 14px;
        background: var(--b3-theme-background);
        color: var(--b3-theme-on-background);
    }
    .forge-input button {
        align-self: flex-end;
    }
</style>
