<script lang="ts">
    /**
     * ForgeMode - Structured Thinking Interface (Layer 2)
     *
     * Template-driven AI-guided questioning with 5 specialized thinking modes:
     * - Learning: Understand new concepts (Mechanism Map)
     * - Articulating: Clarify vague intuitions (Clarify Intuition)
     * - Planning: Develop action strategies
     * - Ideating: Generate creative options
     * - Reflecting: Personal insight
     *
     * Features split view: conversation (left) + template progress (right)
     */
    import { onMount, createEventDispatcher } from 'svelte';
    import { showMessage, getFrontend, fetchSyncPost } from 'siyuan';
    import { createSessionDocument } from '../utils/siyuan-structure';

    export let backendUrl: string;

    const dispatch = createEventDispatcher();

    // Thinking modes with template mappings
    type ThinkingMode = 'learning' | 'articulating' | 'planning' | 'ideating' | 'reflecting';

    const THINKING_MODES: Record<ThinkingMode, {
        name: string;
        description: string;
        aiPrompt: string;
        icon: string;
        templateId?: string;
    }> = {
        learning: {
            name: 'Learning',
            description: 'Understand a new concept',
            aiPrompt: 'Use Socratic questioning to help explore and understand this concept deeply. Ask probing questions that reveal assumptions and connections.',
            icon: '📚',
            templateId: 'learning-mechanism-map'
        },
        articulating: {
            name: 'Articulating',
            description: 'Clarify a vague intuition',
            aiPrompt: 'Help articulate vague thoughts precisely. Mirror back what you hear, use precise language, and help crystallize unclear ideas.',
            icon: '💭',
            templateId: 'articulating-clarify-intuition'
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

    // Template structure (fetched from backend)
    interface TemplateSection {
        id: string;
        prompt: string;
        input_type: string | null;
        ai_behavior: string | null;
        required: boolean;
    }

    interface Template {
        id: string;
        mode: string;
        name: string;
        description: string;
        sections: TemplateSection[];
        graph_mapping: any;
    }

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

    // Template-driven session state
    let template: Template | null = null;
    let currentSectionIndex = 0;
    let sectionResponses: Record<string, string> = {};
    let showProgress = false;

    // Question engine state
    let detectedState: string = 'exploring';
    let currentApproach: string = 'socratic';

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

    async function apiGet(endpoint: string): Promise<any> {
        const url = `${backendUrl}${endpoint}`;

        const response = await fetchSyncPost('/api/network/forwardProxy', {
            url: url,
            method: 'GET',
            timeout: 30000,
            contentType: 'application/json',
            headers: [],
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

    // Question Engine integration
    async function detectUserState(messages: Array<{role: string, content: string}>): Promise<string> {
        try {
            // Get last few user messages for state detection
            const recentUserMessages = messages
                .filter(m => m.role === 'user')
                .slice(-3)
                .map(m => m.content);

            if (recentUserMessages.length === 0) return 'exploring';

            const data = await apiPost('/question-engine/detect-state', {
                messages: recentUserMessages,
                context: {
                    mode: selectedMode,
                    topic: sessionTopic,
                    section: template?.sections[currentSectionIndex]?.id || null
                }
            });

            return data.detected_state || 'exploring';
        } catch (err) {
            console.warn('[IES] State detection failed, using default:', err);
            return 'exploring';
        }
    }

    async function selectApproach(state: string): Promise<string> {
        try {
            // Map thinking modes to preferred approaches
            const modeApproachHints: Record<ThinkingMode, string> = {
                learning: 'socratic',
                articulating: 'phenomenological',
                planning: 'solution_focused',
                ideating: 'systems',
                reflecting: 'phenomenological'
            };

            const data = await apiPost('/question-engine/select-approach', {
                user_state: state,
                context: {
                    mode: selectedMode,
                    preferred_approach: modeApproachHints[selectedMode]
                }
            });

            return data.selected_approach || modeApproachHints[selectedMode];
        } catch (err) {
            console.warn('[IES] Approach selection failed:', err);
            return 'socratic';
        }
    }

    async function generateThinkingQuestion(
        userMessage: string,
        aiResponse: string,
        state: string,
        approach: string
    ): Promise<string | null> {
        try {
            const data = await apiPost('/question-engine/generate-questions', {
                approach,
                user_state: state,
                context: {
                    mode: selectedMode,
                    topic: sessionTopic,
                    user_message: userMessage,
                    ai_response: aiResponse,
                    section: template?.sections[currentSectionIndex]?.id || null,
                    section_prompt: template?.sections[currentSectionIndex]?.prompt || null
                },
                count: 1
            });

            if (data.questions && data.questions.length > 0) {
                return data.questions[0];
            }
            return null;
        } catch (err) {
            console.warn('[IES] Question generation failed:', err);
            return null;
        }
    }

    onMount(() => {
        const frontend = getFrontend();
        isMobile = frontend === 'mobile' || frontend === 'browser-mobile';
    });

    async function loadTemplate(templateId: string) {
        try {
            template = await apiGet(`/templates/${templateId}`);
            currentSectionIndex = 0;
            sectionResponses = {};
            showProgress = true;
        } catch (err) {
            console.warn('[IES] Template load failed, using default mode:', err);
            template = null;
            showProgress = false;
        }
    }

    async function handleStart() {
        if (!sessionTopic.trim()) {
            showMessage('Please enter a topic or question to explore', 3000, 'error');
            return;
        }

        status = 'starting';
        errorMsg = '';

        const modeConfig = THINKING_MODES[selectedMode];

        // Load template if available
        if (modeConfig.templateId) {
            await loadTemplate(modeConfig.templateId);
        }

        apiPost('/session/start', {
            user_id: USER_ID,
            mode: selectedMode,
            topic: sessionTopic,
            system_prompt: modeConfig.aiPrompt
        })
            .then(data => {
                sessionId = data.session_id;
                status = 'active';

                // Start with first section prompt if template-driven
                let greeting = data.greeting || 'What would you like to explore?';
                if (template && template.sections.length > 0) {
                    const firstSection = template.sections[0];
                    greeting = `Let's ${modeConfig.description.toLowerCase()} using the ${template.name} approach.\n\n${firstSection.prompt}`;
                } else {
                    greeting = `Let's ${modeConfig.description.toLowerCase()}. ${greeting}`;
                }

                messages = [{
                    role: 'assistant',
                    content: greeting
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

        // Store section response if template-driven
        if (template && currentSectionIndex < template.sections.length) {
            const section = template.sections[currentSectionIndex];
            sectionResponses[section.id] = userMsg;
        }

        const modeConfig = THINKING_MODES[selectedMode];

        // Build enhanced prompt with section context
        let enhancedPrompt = userMsg;
        if (template && currentSectionIndex < template.sections.length) {
            const section = template.sections[currentSectionIndex];
            if (section.ai_behavior) {
                enhancedPrompt = `${section.ai_behavior}\n\nUser response: ${userMsg}`;
            }
        }

        apiPost('/session/chat-sync', {
            session_id: sessionId,
            message: enhancedPrompt,
            messages: messages.slice(0, -1),
            mode: selectedMode,
            mode_prompt: modeConfig.aiPrompt
        })
            .then(async data => {
                let response = data.response || '';

                // Advance to next section if template-driven
                if (template && currentSectionIndex < template.sections.length - 1) {
                    currentSectionIndex++;
                    const nextSection = template.sections[currentSectionIndex];

                    // Detect state and potentially add a thinking question before next section
                    detectedState = await detectUserState(messages);
                    currentApproach = await selectApproach(detectedState);

                    // Only add thinking question if user seems stuck or overwhelmed
                    if (detectedState === 'stuck' || detectedState === 'overwhelmed' || detectedState === 'uncertain') {
                        const thinkingQuestion = await generateThinkingQuestion(
                            userMsg,
                            response,
                            detectedState,
                            currentApproach
                        );
                        if (thinkingQuestion) {
                            response += `\n\n💭 *${thinkingQuestion}*`;
                        }
                    }

                    response += `\n\n${nextSection.prompt}`;
                } else if (!template) {
                    // Use question engine for non-template sessions
                    // Detect user state from conversation
                    detectedState = await detectUserState(messages);

                    // Select appropriate questioning approach
                    currentApproach = await selectApproach(detectedState);

                    // Generate a thinking partner question
                    const thinkingQuestion = await generateThinkingQuestion(
                        userMsg,
                        response,
                        detectedState,
                        currentApproach
                    );

                    if (thinkingQuestion) {
                        response += `\n\n💭 *${thinkingQuestion}*`;
                    }
                }

                messages[messages.length - 1].content = response;
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

    async function handleEnd() {
        if (!sessionId) return;
        status = 'starting';

        const endPayload: any = {
            session_id: sessionId,
            user_id: USER_ID,
            transcript: messages
        };

        // Add template data if available
        if (template) {
            endPayload.template_id = template.id;
            endPayload.section_responses = sectionResponses;
        }

        try {
            const data = await apiPost('/session/end', endPayload);

            // Create session document in SiYuan
            const docId = await createSessionDocument({
                sessionId: sessionId,
                mode: selectedMode,
                topic: sessionTopic,
                templateId: template?.id,
                templateName: template?.name,
                sectionResponses: template ? sectionResponses : undefined,
                transcript: messages,
                entitiesExtracted: data.entities_extracted,
                graphMappingExecuted: !!template,
            });

            const docMsg = docId ? ' Session document saved to SiYuan.' : '';
            const msg = template
                ? `Session saved. Template mapping executed. ${data.entities_extracted} entities extracted.${docMsg}`
                : `Session saved. ${data.entities_extracted} entities extracted.${docMsg}`;
            showMessage(msg, 4000);

            // Reset state
            sessionId = null;
            status = 'idle';
            messages = [];
            template = null;
            sectionResponses = {};
            currentSectionIndex = 0;
            showProgress = false;
        } catch (err) {
            console.error('[IES] End error:', err);
            status = 'error';
            errorMsg = err.message;
            showMessage(`Error: ${err.message}`, 5000, 'error');
        }
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

    // Helper to get section completion status
    function getSectionStatus(sectionId: string, index: number): 'complete' | 'current' | 'pending' {
        if (sectionId in sectionResponses) return 'complete';
        if (index === currentSectionIndex) return 'current';
        return 'pending';
    }
</script>

<div class="forge-mode" class:forge-mode--split={showProgress && status === 'active'}>
    <div class="forge-header">
        <button class="back-btn" on:click={handleBack} title="Back to Dashboard">
            <svg viewBox="0 0 24 24" width="16" height="16">
                <path fill="currentColor" d="M20 11H7.83l5.59-5.59L12 4l-8 8 8 8 1.41-1.41L7.83 13H20v-2z"/>
            </svg>
        </button>
        <span class="forge-title">Structured Thinking</span>
        {#if status === 'active'}
            <span class="forge-badge">{THINKING_MODES[selectedMode].icon} {THINKING_MODES[selectedMode].name}</span>
            {#if template}
                <span class="template-badge">{template.name}</span>
            {/if}
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
                                    {#if mode.templateId}
                                        <span class="template-indicator" title="Template-driven session">⚙️</span>
                                    {/if}
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

        {#if showProgress && template && status === 'active'}
            <div class="forge-progress">
                <div class="progress-header">
                    <span class="progress-title">{template.name}</span>
                    <span class="progress-count">{Object.keys(sectionResponses).length}/{template.sections.length}</span>
                </div>
                <div class="progress-sections">
                    {#each template.sections as section, index}
                        {@const sectionStatus = getSectionStatus(section.id, index)}
                        <div class="progress-section" class:progress-section--complete={sectionStatus === 'complete'} class:progress-section--current={sectionStatus === 'current'}>
                            <div class="progress-section-header">
                                <span class="progress-section-icon">
                                    {#if sectionStatus === 'complete'}✓
                                    {:else if sectionStatus === 'current'}▶
                                    {:else}○
                                    {/if}
                                </span>
                                <span class="progress-section-label">{section.prompt}</span>
                            </div>
                            {#if section.id in sectionResponses}
                                <div class="progress-section-response">
                                    {sectionResponses[section.id]}
                                </div>
                            {/if}
                        </div>
                    {/each}
                </div>
                {#if template.graph_mapping && template.graph_mapping.on_complete}
                    <div class="progress-footer">
                        <span class="progress-footer-label">On completion:</span>
                        <ul class="progress-actions">
                            {#each template.graph_mapping.on_complete as action}
                                <li class="progress-action">
                                    {#if action.action === 'create_or_link'}
                                        Create {action.entity_type || 'spark'} entity
                                    {:else if action.action === 'update_journey'}
                                        Update journey
                                    {:else}
                                        {action.action}
                                    {/if}
                                </li>
                            {/each}
                        </ul>
                    </div>
                {/if}
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
    .template-badge {
        font-size: 11px;
        padding: 2px 6px;
        background: var(--b3-theme-secondary-lightest, #e8f5e9);
        color: var(--b3-theme-secondary, #4caf50);
        border-radius: 4px;
    }

    /* Main layout - conversation and progress side by side */
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

    /* Progress panel */
    .forge-progress {
        width: 300px;
        display: flex;
        flex-direction: column;
        border: 1px solid var(--b3-border-color);
        border-radius: 8px;
        overflow: hidden;
        background: var(--b3-theme-background);
    }
    .progress-header {
        padding: 10px 12px;
        background: var(--b3-theme-surface);
        border-bottom: 1px solid var(--b3-border-color);
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .progress-title {
        font-size: 12px;
        font-weight: 600;
        color: var(--b3-theme-on-surface);
    }
    .progress-count {
        font-size: 11px;
        padding: 2px 6px;
        background: var(--b3-theme-primary-lightest);
        color: var(--b3-theme-primary);
        border-radius: 3px;
    }
    .progress-sections {
        flex: 1;
        overflow-y: auto;
        padding: 8px;
    }
    .progress-section {
        margin-bottom: 10px;
        padding: 8px;
        border-radius: 6px;
        background: var(--b3-theme-surface);
        border: 1px solid var(--b3-border-color);
    }
    .progress-section--current {
        border-color: var(--b3-theme-primary);
        background: var(--b3-theme-primary-lightest);
    }
    .progress-section--complete {
        opacity: 0.7;
    }
    .progress-section-header {
        display: flex;
        gap: 6px;
        align-items: flex-start;
    }
    .progress-section-icon {
        font-size: 12px;
        margin-top: 1px;
    }
    .progress-section-label {
        flex: 1;
        font-size: 12px;
        line-height: 1.4;
        color: var(--b3-theme-on-surface);
    }
    .progress-section-response {
        margin-top: 6px;
        padding-top: 6px;
        border-top: 1px solid var(--b3-border-color);
        font-size: 11px;
        color: var(--b3-theme-on-surface-light);
        white-space: pre-wrap;
        max-height: 60px;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    .progress-footer {
        padding: 8px 12px;
        border-top: 1px solid var(--b3-border-color);
        background: var(--b3-theme-surface-light, #fafafa);
    }
    .progress-footer-label {
        font-size: 10px;
        font-weight: 600;
        text-transform: uppercase;
        color: var(--b3-theme-on-surface-light);
    }
    .progress-actions {
        margin: 4px 0 0 0;
        padding: 0 0 0 16px;
        list-style: disc;
    }
    .progress-action {
        font-size: 11px;
        color: var(--b3-theme-on-surface);
        margin: 2px 0;
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
        flex: 1;
        font-size: 12px;
        color: var(--b3-theme-on-surface-light);
    }
    .template-indicator {
        font-size: 12px;
        opacity: 0.6;
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
