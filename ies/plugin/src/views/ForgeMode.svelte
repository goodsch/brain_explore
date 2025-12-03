<script lang="ts">
    /**
     * ForgeMode - Structured Thinking Interface (Layer 2)
     *
     * AI-guided questioning with 5 specialized thinking modes:
     * - Learning: Understand new concepts (Socratic questioning)
     * - Articulating: Clarify vague intuitions (Mirroring, precise language)
     * - Planning: Develop action strategies (Goal clarification)
     * - Ideating: Generate creative options (Divergent prompts)
     * - Reflecting: Personal insight (Phenomenological questions)
     *
     * Features split view: conversation (left) + live note preview (right)
     */
    import { onMount, createEventDispatcher } from 'svelte';
    import { showMessage, getFrontend, fetchSyncPost } from 'siyuan';

    export let backendUrl: string;

    const dispatch = createEventDispatcher();

    // Thinking modes with descriptions and AI behavior hints
    type ThinkingMode = 'learning' | 'articulating' | 'planning' | 'ideating' | 'reflecting';

    const THINKING_MODES: Record<ThinkingMode, {
        name: string;
        description: string;
        aiPrompt: string;
        icon: string;
    }> = {
        learning: {
            name: 'Learning',
            description: 'Understand a new concept',
            aiPrompt: 'Use Socratic questioning to help explore and understand this concept deeply. Ask probing questions that reveal assumptions and connections.',
            icon: '📚'
        },
        articulating: {
            name: 'Articulating',
            description: 'Clarify a vague intuition',
            aiPrompt: 'Help articulate vague thoughts precisely. Mirror back what you hear, use precise language, and help crystallize unclear ideas.',
            icon: '💭'
        },
        planning: {
            name: 'Planning',
            description: 'Develop an action strategy',
            aiPrompt: 'Help develop a clear action plan. Clarify goals, identify obstacles, break down steps, and ensure the plan is actionable.',
            icon: '🎯'
        },
        ideating: {
            name: 'Ideating',
            description: 'Generate creative options',
            aiPrompt: 'Encourage divergent thinking. Generate many possibilities, explore unconventional options, and help expand the solution space.',
            icon: '💡'
        },
        reflecting: {
            name: 'Reflecting',
            description: 'Gain personal insight',
            aiPrompt: 'Use phenomenological questioning to explore personal experience. Focus on feelings, meanings, and self-understanding.',
            icon: '🪞'
        }
    };

    // State
    let sessionId: string | null = null;
    let status: 'idle' | 'starting' | 'active' | 'error' = 'idle';
    let messages: Array<{role: string, content: string}> = [];
    let errorMsg = '';
    let inputText = '';
    let isLoading = false;
    let isMobile = false;

    // Thinking mode state
    let selectedMode: ThinkingMode = 'learning';
    let sessionTopic = '';

    // Note preview state (for split view)
    let notePreview = '';
    let showNotePreview = false;

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
        if (!sessionTopic.trim()) {
            showMessage('Please enter a topic or question to explore', 3000, 'error');
            return;
        }

        status = 'starting';
        errorMsg = '';

        const modeConfig = THINKING_MODES[selectedMode];

        apiPost('/session/start', {
            user_id: USER_ID,
            mode: selectedMode,
            topic: sessionTopic,
            system_prompt: modeConfig.aiPrompt
        })
            .then(data => {
                sessionId = data.session_id;
                status = 'active';

                // Customize greeting based on mode
                const modeGreeting = `Let's ${modeConfig.description.toLowerCase()}. ${data.greeting || 'What would you like to explore?'}`;

                messages = [{
                    role: 'assistant',
                    content: modeGreeting
                }];

                // Initialize note preview
                updateNotePreview();
            })
            .catch(err => {
                console.error('[IES] Start error:', err);
                status = 'error';
                errorMsg = err.message || String(err);
                showMessage(`Error: ${errorMsg}`, 5000, 'error');
            });
    }

    function updateNotePreview() {
        // Generate a markdown note from the conversation
        if (messages.length === 0) {
            notePreview = '';
            return;
        }

        const modeConfig = THINKING_MODES[selectedMode];
        let note = `# ${sessionTopic}\n\n`;
        note += `*Mode: ${modeConfig.name} ${modeConfig.icon}*\n\n`;

        // Extract key insights from assistant messages
        const insights = messages
            .filter(m => m.role === 'assistant' && m.content !== '...')
            .map((m, i) => {
                // Truncate long messages for preview
                const content = m.content.length > 200
                    ? m.content.substring(0, 200) + '...'
                    : m.content;
                return `**Insight ${i + 1}:** ${content}`;
            });

        if (insights.length > 0) {
            note += '## Key Points\n\n';
            note += insights.join('\n\n');
        }

        notePreview = note;
    }

    function handleSend() {
        if (!inputText.trim() || isLoading || !sessionId) return;

        const userMsg = inputText.trim();
        inputText = '';
        messages = [...messages, { role: 'user', content: userMsg }];
        messages = [...messages, { role: 'assistant', content: '...' }];
        isLoading = true;

        const modeConfig = THINKING_MODES[selectedMode];

        apiPost('/session/chat-sync', {
            session_id: sessionId,
            message: userMsg,
            messages: messages.slice(0, -1),
            mode: selectedMode,
            mode_prompt: modeConfig.aiPrompt
        })
            .then(data => {
                messages[messages.length - 1].content = data.response || '';
                messages = messages;
                isLoading = false;
                updateNotePreview();
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

<div class="forge-mode" class:forge-mode--split={showNotePreview && status === 'active'}>
    <div class="forge-header">
        <button class="back-btn" on:click={handleBack} title="Back to Dashboard">
            <svg viewBox="0 0 24 24" width="16" height="16">
                <path fill="currentColor" d="M20 11H7.83l5.59-5.59L12 4l-8 8 8 8 1.41-1.41L7.83 13H20v-2z"/>
            </svg>
        </button>
        <span class="forge-title">Structured Thinking</span>
        {#if status === 'active'}
            <span class="forge-badge">{THINKING_MODES[selectedMode].icon} {THINKING_MODES[selectedMode].name}</span>
            <button
                class="note-toggle"
                on:click={() => showNotePreview = !showNotePreview}
                title={showNotePreview ? 'Hide note preview' : 'Show note preview'}
            >
                <svg viewBox="0 0 24 24" width="16" height="16">
                    <path fill="currentColor" d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-5 14H7v-2h7v2zm3-4H7v-2h10v2zm0-4H7V7h10v2z"/>
                </svg>
            </button>
        {/if}
    </div>

    <div class="forge-main">
        <div class="forge-conversation">
            {#if status === 'idle'}
                <!-- Mode Selection -->
                <div class="forge-setup">
                    <div class="setup-section">
                        <label class="setup-label">Thinking Mode</label>
                        <div class="mode-selector">
                            {#each Object.entries(THINKING_MODES) as [key, mode]}
                                <button
                                    class="mode-option"
                                    class:mode-option--selected={selectedMode === key}
                                    on:click={() => selectedMode = key}
                                >
                                    <span class="mode-option-icon">{mode.icon}</span>
                                    <span class="mode-option-name">{mode.name}</span>
                                    <span class="mode-option-desc">{mode.description}</span>
                                </button>
                            {/each}
                        </div>
                    </div>

                    <div class="setup-section">
                        <label class="setup-label">What do you want to explore?</label>
                        <textarea
                            class="topic-input"
                            bind:value={sessionTopic}
                            placeholder="Enter your topic, question, or idea..."
                            rows="2"
                        ></textarea>
                    </div>

                    <button
                        class="b3-button b3-button--primary start-btn"
                        on:click={handleStart}
                        disabled={!sessionTopic.trim()}
                    >
                        Start {THINKING_MODES[selectedMode].name} Session
                    </button>
                </div>

            {:else if status === 'starting'}
                <div class="forge-loading">Starting {THINKING_MODES[selectedMode].name} session...</div>

            {:else if status === 'error'}
                <div class="forge-error">{errorMsg}</div>
                <button class="b3-button" on:click={() => status = 'idle'}>Try Again</button>

            {:else}
                <!-- Active Session -->
                <div class="forge-messages">
                    {#each messages as msg}
                        <div class="forge-msg" class:forge-msg--user={msg.role === 'user'}>
                            {msg.content}
                        </div>
                    {/each}
                </div>

                <div class="forge-input">
                    <textarea
                        bind:value={inputText}
                        on:keydown={handleKeydown}
                        placeholder="Type your response..."
                        rows="2"
                        disabled={isLoading}
                    ></textarea>
                    <div class="forge-actions">
                        <button
                            class="b3-button b3-button--primary"
                            on:click={handleSend}
                            disabled={isLoading || !inputText.trim()}
                        >
                            {isLoading ? '...' : 'Send'}
                        </button>
                        <button class="b3-button" on:click={handleEnd}>
                            End
                        </button>
                    </div>
                </div>
            {/if}
        </div>

        {#if showNotePreview && status === 'active'}
            <div class="forge-preview">
                <div class="preview-header">
                    <span class="preview-title">Note Preview</span>
                </div>
                <div class="preview-content">
                    <pre>{notePreview}</pre>
                </div>
            </div>
        {/if}
    </div>
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
    .note-toggle {
        background: none;
        border: none;
        cursor: pointer;
        padding: 4px;
        border-radius: 4px;
        color: var(--b3-theme-on-surface-light);
        display: flex;
        align-items: center;
    }
    .note-toggle:hover {
        background: var(--b3-theme-surface);
        color: var(--b3-theme-on-surface);
    }

    /* Main layout - conversation and preview side by side */
    .forge-main {
        flex: 1;
        display: flex;
        gap: 12px;
        overflow: hidden;
    }
    .forge-conversation {
        flex: 1;
        display: flex;
        flex-direction: column;
        overflow: hidden;
    }
    .forge-mode--split .forge-conversation {
        flex: 1;
    }
    .forge-preview {
        width: 280px;
        display: flex;
        flex-direction: column;
        border: 1px solid var(--b3-border-color);
        border-radius: 8px;
        overflow: hidden;
    }
    .preview-header {
        padding: 8px 12px;
        background: var(--b3-theme-surface);
        border-bottom: 1px solid var(--b3-border-color);
    }
    .preview-title {
        font-size: 12px;
        font-weight: 600;
        color: var(--b3-theme-on-surface-light);
        text-transform: uppercase;
    }
    .preview-content {
        flex: 1;
        overflow-y: auto;
        padding: 12px;
        font-size: 12px;
        background: var(--b3-theme-background);
    }
    .preview-content pre {
        margin: 0;
        white-space: pre-wrap;
        font-family: inherit;
        color: var(--b3-theme-on-surface);
    }

    /* Setup section (mode selection + topic) */
    .forge-setup {
        display: flex;
        flex-direction: column;
        gap: 16px;
        padding: 12px 0;
    }
    .setup-section {
        display: flex;
        flex-direction: column;
        gap: 8px;
    }
    .setup-label {
        font-size: 12px;
        font-weight: 600;
        color: var(--b3-theme-on-surface-light);
        text-transform: uppercase;
    }

    /* Mode selector */
    .mode-selector {
        display: flex;
        flex-direction: column;
        gap: 6px;
    }
    .mode-option {
        display: flex;
        align-items: center;
        gap: 10px;
        padding: 10px 12px;
        background: var(--b3-theme-surface);
        border: 2px solid var(--b3-border-color);
        border-radius: 8px;
        cursor: pointer;
        transition: all 0.15s;
        text-align: left;
    }
    .mode-option:hover {
        border-color: var(--b3-theme-primary-light);
        background: var(--b3-theme-primary-lightest);
    }
    .mode-option--selected {
        border-color: var(--b3-theme-primary);
        background: var(--b3-theme-primary-lightest);
    }
    .mode-option-icon {
        font-size: 18px;
    }
    .mode-option-name {
        font-weight: 600;
        font-size: 13px;
        min-width: 80px;
    }
    .mode-option-desc {
        font-size: 12px;
        color: var(--b3-theme-on-surface-light);
    }

    /* Topic input */
    .topic-input {
        width: 100%;
        resize: none;
        border: 1px solid var(--b3-border-color);
        border-radius: 8px;
        padding: 10px 12px;
        font-size: 14px;
        background: var(--b3-theme-background);
        color: var(--b3-theme-on-background);
        font-family: inherit;
    }
    .topic-input:focus {
        outline: none;
        border-color: var(--b3-theme-primary);
    }
    .start-btn {
        align-self: flex-start;
        padding: 10px 20px;
    }

    /* Loading and error states */
    .forge-loading {
        text-align: center;
        color: var(--b3-theme-on-surface-light);
        padding: 24px;
    }
    .forge-error {
        color: var(--b3-theme-error);
        font-size: 13px;
        padding: 12px;
        text-align: center;
    }

    /* Messages */
    .forge-messages {
        flex: 1;
        overflow-y: auto;
        padding-bottom: 12px;
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

    /* Input area */
    .forge-input {
        display: flex;
        flex-direction: column;
        gap: 8px;
        padding-top: 12px;
        border-top: 1px solid var(--b3-border-color);
    }
    .forge-input textarea {
        width: 100%;
        resize: none;
        border: 1px solid var(--b3-border-color);
        border-radius: 6px;
        padding: 8px;
        font-size: 14px;
        background: var(--b3-theme-background);
        color: var(--b3-theme-on-background);
        font-family: inherit;
    }
    .forge-input textarea:focus {
        outline: none;
        border-color: var(--b3-theme-primary);
    }
    .forge-actions {
        display: flex;
        gap: 8px;
        justify-content: flex-end;
    }
</style>
