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
        padding: var(--ies-space-3);
        gap: var(--ies-space-3);
        font-family: var(--ies-font-body);
        color: var(--ies-text-primary);
        background: var(--ies-bg-base);
    }
    .forge-header {
        display: flex;
        align-items: center;
        gap: var(--ies-space-2);
    }
    .back-btn {
        background: none;
        border: none;
        cursor: pointer;
        padding: var(--ies-space-1);
        border-radius: var(--ies-radius-sm);
        color: var(--ies-text-secondary);
        display: flex;
        align-items: center;
        transition: var(--ies-transition-all);
    }
    .back-btn:hover {
        background: var(--ies-bg-elevated);
        color: var(--ies-text-primary);
    }
    .forge-title {
        font-weight: var(--ies-font-semibold);
        font-family: var(--ies-font-display);
        font-size: var(--ies-text-lg);
        flex: 1;
    }
    .forge-badge {
        font-size: var(--ies-text-xs);
        padding: var(--ies-space-0-5) var(--ies-space-2);
        background: var(--ies-accent-subtle);
        color: var(--ies-accent);
        border-radius: var(--ies-radius-sm);
        font-weight: var(--ies-font-medium);
    }
    .note-toggle {
        background: none;
        border: none;
        cursor: pointer;
        padding: var(--ies-space-1);
        border-radius: var(--ies-radius-sm);
        color: var(--ies-text-muted);
        display: flex;
        align-items: center;
        transition: var(--ies-transition-all);
    }
    .note-toggle:hover {
        background: var(--ies-bg-elevated);
        color: var(--ies-text-primary);
    }

    /* Main layout - conversation and preview side by side */
    .forge-main {
        flex: 1;
        display: flex;
        gap: var(--ies-space-3);
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
        border: 1px solid var(--ies-border-light);
        border-radius: var(--ies-radius-card);
        overflow: hidden;
        background: var(--ies-bg-elevated);
    }
    .preview-header {
        padding: var(--ies-space-2) var(--ies-space-3);
        background: var(--ies-bg-deep);
        border-bottom: 1px solid var(--ies-border-subtle);
    }
    .preview-title {
        font-size: var(--ies-text-xs);
        font-weight: var(--ies-font-semibold);
        color: var(--ies-text-muted);
        text-transform: uppercase;
        letter-spacing: var(--ies-tracking-wide);
    }
    .preview-content {
        flex: 1;
        overflow-y: auto;
        padding: var(--ies-space-3);
        font-size: var(--ies-text-xs);
        background: var(--ies-bg-base);
    }
    .preview-content pre {
        margin: 0;
        white-space: pre-wrap;
        font-family: var(--ies-font-mono);
        color: var(--ies-text-primary);
        line-height: var(--ies-leading-code);
    }

    /* Setup section (mode selection + topic) */
    .forge-setup {
        display: flex;
        flex-direction: column;
        gap: var(--ies-space-4);
        padding: var(--ies-space-3) 0;
    }
    .setup-section {
        display: flex;
        flex-direction: column;
        gap: var(--ies-space-2);
    }
    .setup-label {
        font-size: var(--ies-text-xs);
        font-weight: var(--ies-font-semibold);
        color: var(--ies-text-muted);
        text-transform: uppercase;
        letter-spacing: var(--ies-tracking-wide);
    }

    /* Mode selector */
    .mode-selector {
        display: flex;
        flex-direction: column;
        gap: var(--ies-space-1-5);
    }
    .mode-option {
        display: flex;
        align-items: center;
        gap: var(--ies-space-2-5);
        padding: var(--ies-space-2-5) var(--ies-space-3);
        background: var(--ies-bg-elevated);
        border: 2px solid var(--ies-border-light);
        border-radius: var(--ies-radius-card);
        cursor: pointer;
        transition: var(--ies-transition-all);
        text-align: left;
    }
    .mode-option:hover {
        border-color: var(--ies-accent-muted);
        background: var(--ies-accent-subtle);
    }
    .mode-option--selected {
        border-color: var(--ies-accent);
        background: var(--ies-accent-subtle);
    }
    .mode-option-icon {
        font-size: var(--ies-text-lg);
    }
    .mode-option-name {
        font-weight: var(--ies-font-semibold);
        font-size: var(--ies-text-sm);
        min-width: 80px;
        color: var(--ies-text-primary);
    }
    .mode-option-desc {
        font-size: var(--ies-text-xs);
        color: var(--ies-text-muted);
    }

    /* Topic input */
    .topic-input {
        width: 100%;
        resize: none;
        border: 1px solid var(--ies-border-light);
        border-radius: var(--ies-radius-input);
        padding: var(--ies-input-padding-y) var(--ies-input-padding-x);
        font-size: var(--ies-text-base);
        background: var(--ies-bg-base);
        color: var(--ies-text-primary);
        font-family: var(--ies-font-body);
        box-shadow: var(--ies-shadow-input);
        transition: var(--ies-transition-all);
    }
    .topic-input::placeholder {
        color: var(--ies-text-subtle);
    }
    .topic-input:focus {
        outline: none;
        border-color: var(--ies-accent);
        box-shadow: var(--ies-shadow-input-focus);
    }
    .start-btn {
        align-self: flex-start;
        padding: var(--ies-space-2-5) var(--ies-space-5);
        background: var(--ies-accent);
        color: var(--ies-text-inverse);
        border: none;
        border-radius: var(--ies-radius-button);
        font-weight: var(--ies-font-medium);
        font-size: var(--ies-text-sm);
        cursor: pointer;
        transition: var(--ies-transition-all);
        box-shadow: var(--ies-shadow-button);
    }
    .start-btn:hover {
        background: var(--ies-accent-hover);
        box-shadow: var(--ies-shadow-button-hover);
    }
    .start-btn:disabled {
        opacity: 0.5;
        cursor: not-allowed;
    }

    /* Loading and error states */
    .forge-loading {
        text-align: center;
        color: var(--ies-text-muted);
        padding: var(--ies-space-6);
        font-size: var(--ies-text-sm);
    }
    .forge-error {
        color: var(--ies-error);
        font-size: var(--ies-text-sm);
        padding: var(--ies-space-3);
        text-align: center;
        background: var(--ies-error-subtle);
        border-radius: var(--ies-radius-sm);
    }

    /* Messages */
    .forge-messages {
        flex: 1;
        overflow-y: auto;
        padding-bottom: var(--ies-space-3);
        scrollbar-width: thin;
        scrollbar-color: var(--ies-border-medium) transparent;
    }
    .forge-messages::-webkit-scrollbar {
        width: 6px;
    }
    .forge-messages::-webkit-scrollbar-track {
        background: transparent;
    }
    .forge-messages::-webkit-scrollbar-thumb {
        background: var(--ies-border-medium);
        border-radius: 3px;
    }
    .forge-msg {
        padding: var(--ies-space-2-5) var(--ies-space-3);
        margin-bottom: var(--ies-space-2);
        border-radius: var(--ies-radius-card);
        background: var(--ies-bg-elevated);
        font-size: var(--ies-text-base);
        line-height: var(--ies-leading-body);
        white-space: pre-wrap;
        animation: ies-slide-up var(--ies-duration-fast) var(--ies-ease-cupertino) forwards;
    }
    .forge-msg--user {
        background: var(--ies-accent-subtle);
        margin-left: var(--ies-space-5);
        border-left: 3px solid var(--ies-accent);
    }
    .forge-msg--ai {
        border-left: 3px solid var(--ies-secondary);
    }

    /* Input area */
    .forge-input {
        display: flex;
        flex-direction: column;
        gap: var(--ies-space-2);
        padding-top: var(--ies-space-3);
        border-top: 1px solid var(--ies-border-subtle);
    }
    .forge-input textarea {
        width: 100%;
        resize: none;
        border: 1px solid var(--ies-border-light);
        border-radius: var(--ies-radius-input);
        padding: var(--ies-space-2);
        font-size: var(--ies-text-base);
        background: var(--ies-bg-base);
        color: var(--ies-text-primary);
        font-family: var(--ies-font-body);
        box-shadow: var(--ies-shadow-input);
        transition: var(--ies-transition-all);
    }
    .forge-input textarea::placeholder {
        color: var(--ies-text-subtle);
    }
    .forge-input textarea:focus {
        outline: none;
        border-color: var(--ies-accent);
        box-shadow: var(--ies-shadow-input-focus);
    }
    .forge-actions {
        display: flex;
        gap: var(--ies-space-2);
        justify-content: flex-end;
    }
    .forge-actions button {
        padding: var(--ies-space-2) var(--ies-space-4);
        border-radius: var(--ies-radius-button);
        font-size: var(--ies-text-sm);
        font-weight: var(--ies-font-medium);
        cursor: pointer;
        transition: var(--ies-transition-all);
        border: none;
    }
    .forge-actions button:disabled {
        opacity: 0.5;
        cursor: not-allowed;
    }
</style>
