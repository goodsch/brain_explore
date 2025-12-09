<script lang="ts">
    /**
     * QuestionsSection - Display questions for entity exploration (Sprint 4)
     *
     * Fetches and displays AI-generated questions for an entity.
     * Questions are organized by type (why, how, what, etc.) with
     * interactive state for marking as answered.
     */
    import { onMount, createEventDispatcher } from 'svelte';
    import { fetchSyncPost, showMessage } from 'siyuan';

    export let entityName: string;
    export let backendUrl: string;

    const dispatch = createEventDispatcher();

    type ExtractedQuestion = {
        text: string;
        question_type: string;
        related_concepts: string[];
    };

    type QuestionsResponse = {
        entity_name: string;
        entity_type: string;
        questions: ExtractedQuestion[];
        generated: boolean;
    };

    // Status for local tracking
    type QuestionState = 'open' | 'partial' | 'answered';

    let questions: ExtractedQuestion[] = [];
    let questionStates: Map<number, QuestionState> = new Map();
    let isLoading = false;
    let error: string | null = null;
    let mounted = false;
    let lastEntityName: string | null = null;
    let expandedIndex: number | null = null;
    let showAnswered = false;

    // Question type styling
    const QUESTION_TYPE_STYLES: Record<string, { icon: string; color: string }> = {
        why: { icon: '🤔', color: '#8b5cf6' },
        how: { icon: '🔧', color: '#06b6d4' },
        what: { icon: '📋', color: '#3b82f6' },
        when: { icon: '📅', color: '#f59e0b' },
        who: { icon: '👤', color: '#10b981' },
        where: { icon: '📍', color: '#ef4444' },
        which: { icon: '🎯', color: '#ec4899' },
        general: { icon: '❓', color: '#6b7280' }
    };

    const STATUS_ICONS = {
        open: '○',
        partial: '◐',
        answered: '●'
    };

    onMount(() => {
        mounted = true;
        if (entityName) {
            loadQuestions();
        }
    });

    $: if (mounted && entityName !== lastEntityName) {
        lastEntityName = entityName;
        if (entityName) {
            loadQuestions();
        } else {
            questions = [];
            questionStates = new Map();
            error = null;
        }
    }

    // Filter questions based on showAnswered toggle
    $: visibleQuestions = showAnswered
        ? questions
        : questions.filter((_, i) => questionStates.get(i) !== 'answered');

    $: answeredCount = Array.from(questionStates.values()).filter(s => s === 'answered').length;

    async function forwardProxy<T>(method: 'GET' | 'POST', endpoint: string, body?: any): Promise<T> {
        if (!backendUrl) {
            throw new Error('Backend URL is not configured');
        }
        const url = `${backendUrl}${endpoint}`;
        const payload: any = {
            url,
            method,
            timeout: 60000,
            contentType: 'application/json',
            headers: [],
        };
        if (method === 'POST') {
            payload.payload = body ?? {};
        }
        const response = await fetchSyncPost('/api/network/forwardProxy', payload);
        if (response.code !== 0) {
            throw new Error(`Proxy error: ${response.msg}`);
        }
        const proxyData = response.data;
        if (!proxyData || proxyData.status < 200 || proxyData.status >= 300) {
            throw new Error(`Backend error: ${proxyData?.status || 'unknown'}`);
        }
        return typeof proxyData.body === 'string' ? JSON.parse(proxyData.body) : proxyData.body;
    }

    async function loadQuestions() {
        if (!entityName) {
            return;
        }
        isLoading = true;
        error = null;
        questionStates = new Map();
        try {
            const data = await forwardProxy<QuestionsResponse>(
                'GET',
                `/graph/entity/${encodeURIComponent(entityName)}/questions?generate=true`
            );
            questions = data?.questions || [];
            // Initialize all questions as open
            questions.forEach((_, i) => questionStates.set(i, 'open'));
        } catch (err: any) {
            error = err?.message || String(err);
            questions = [];
        } finally {
            isLoading = false;
        }
    }

    function getTypeStyle(type: string) {
        return QUESTION_TYPE_STYLES[type.toLowerCase()] || QUESTION_TYPE_STYLES.general;
    }

    function toggleExpand(index: number) {
        expandedIndex = expandedIndex === index ? null : index;
    }

    function cycleQuestionState(index: number, event: MouseEvent) {
        event.stopPropagation();
        const current = questionStates.get(index) || 'open';
        let next: QuestionState;

        // Cycle through states: open -> partial -> answered -> open
        if (current === 'open') next = 'partial';
        else if (current === 'partial') next = 'answered';
        else next = 'open';

        questionStates.set(index, next);
        questionStates = new Map(questionStates); // trigger reactivity

        // Show feedback
        const labels = { open: 'Open', partial: 'Partially answered', answered: 'Answered' };
        showMessage(`Question marked as: ${labels[next]}`, 2000);

        // Dispatch event for parent components
        dispatch('statusChange', {
            questionIndex: index,
            questionText: questions[index].text,
            status: next
        });
    }

    function markAsAnswered(index: number, event: MouseEvent) {
        event.stopPropagation();
        questionStates.set(index, 'answered');
        questionStates = new Map(questionStates);
        showMessage('Question marked as answered', 2000);
        dispatch('statusChange', {
            questionIndex: index,
            questionText: questions[index].text,
            status: 'answered'
        });
    }

    // Get actual index in original array for state tracking
    function getOriginalIndex(visibleIndex: number): number {
        if (showAnswered) return visibleIndex;

        let count = 0;
        for (let i = 0; i < questions.length; i++) {
            if (questionStates.get(i) !== 'answered') {
                if (count === visibleIndex) return i;
                count++;
            }
        }
        return visibleIndex;
    }
</script>

<div class="questions-section">
    <div class="questions-header">
        <div class="header-left">
            <span class="questions-icon">💡</span>
            <span class="questions-title">Exploration Questions</span>
            {#if questions.length > 0}
                <span class="questions-count">
                    ({visibleQuestions.length}{answeredCount > 0 ? ` / ${questions.length}` : ''})
                </span>
            {/if}
        </div>
        {#if answeredCount > 0}
            <button
                class="toggle-answered"
                class:active={showAnswered}
                on:click={() => showAnswered = !showAnswered}
            >
                {showAnswered ? 'Hide answered' : `Show ${answeredCount} answered`}
            </button>
        {/if}
    </div>

    {#if isLoading}
        <div class="questions-loading">
            <div class="spinner"></div>
            <span class="loading-text">Generating questions...</span>
        </div>
    {:else if error}
        <div class="questions-error">{error}</div>
    {:else if questions.length === 0}
        <div class="questions-empty">No questions generated yet</div>
    {:else if visibleQuestions.length === 0}
        <div class="questions-empty">
            All questions answered!
            <button class="show-all-btn" on:click={() => showAnswered = true}>
                Show answered questions
            </button>
        </div>
    {:else}
        <div class="questions-list">
            {#each visibleQuestions as question, visibleIndex (getOriginalIndex(visibleIndex))}
                {@const originalIndex = getOriginalIndex(visibleIndex)}
                {@const style = getTypeStyle(question.question_type)}
                {@const state = questionStates.get(originalIndex) || 'open'}
                <div class="question-card" class:expanded={expandedIndex === originalIndex} class:answered={state === 'answered'}>
                    <button class="question-header" on:click={() => toggleExpand(originalIndex)}>
                        <button
                            class="status-indicator"
                            class:open={state === 'open'}
                            class:partial={state === 'partial'}
                            class:answered={state === 'answered'}
                            on:click={(e) => cycleQuestionState(originalIndex, e)}
                            title="Click to cycle: Open → Partial → Answered"
                        >
                            {STATUS_ICONS[state]}
                        </button>
                        <span class="question-type-badge" style="background-color: {style.color}20; color: {style.color}">
                            <span class="type-icon">{style.icon}</span>
                            <span class="type-label">{question.question_type}</span>
                        </span>
                        <span class="question-text">{question.text}</span>
                        <span class="expand-icon">{expandedIndex === originalIndex ? '−' : '+'}</span>
                    </button>

                    {#if expandedIndex === originalIndex}
                        <div class="question-details">
                            {#if question.related_concepts.length > 0}
                                <div class="related-concepts">
                                    <span class="related-label">Related concepts:</span>
                                    <div class="concept-tags">
                                        {#each question.related_concepts as concept}
                                            <span class="concept-tag">{concept}</span>
                                        {/each}
                                    </div>
                                </div>
                            {/if}

                            <div class="question-actions">
                                {#if state !== 'answered'}
                                    <button class="action-btn mark-answered" on:click={(e) => markAsAnswered(originalIndex, e)}>
                                        <span class="action-icon">✓</span>
                                        Mark as Answered
                                    </button>
                                {:else}
                                    <button class="action-btn mark-open" on:click={(e) => { questionStates.set(originalIndex, 'open'); questionStates = new Map(questionStates); e.stopPropagation(); }}>
                                        <span class="action-icon">↺</span>
                                        Reopen Question
                                    </button>
                                {/if}
                            </div>
                        </div>
                    {/if}
                </div>
            {/each}
        </div>
    {/if}
</div>

<style>
    .questions-section {
        margin-top: 16px;
        padding: 12px;
        background: var(--b3-theme-surface);
        border-radius: 8px;
        border: 1px solid var(--b3-border-color);
    }

    .questions-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 12px;
    }

    .header-left {
        display: flex;
        align-items: center;
        gap: 8px;
        font-weight: 600;
        color: var(--b3-theme-on-surface);
    }

    .questions-icon {
        font-size: 14px;
    }

    .questions-title {
        font-size: 14px;
    }

    .questions-count {
        font-size: 12px;
        color: var(--b3-theme-on-surface-light);
        font-weight: normal;
    }

    .toggle-answered {
        font-size: 11px;
        padding: 4px 10px;
        background: transparent;
        border: 1px solid var(--b3-border-color);
        border-radius: 12px;
        color: var(--b3-theme-on-surface-light);
        cursor: pointer;
        transition: all 0.2s;
    }

    .toggle-answered:hover {
        background: var(--b3-theme-surface-lighter);
        border-color: var(--b3-theme-primary-lighter);
    }

    .toggle-answered.active {
        background: var(--b3-theme-primary-lightest);
        border-color: var(--b3-theme-primary-lighter);
        color: var(--b3-theme-primary);
    }

    .questions-loading {
        display: flex;
        flex-direction: column;
        align-items: center;
        padding: 24px;
        gap: 8px;
    }

    .loading-text {
        font-size: 12px;
        color: var(--b3-theme-on-surface-light);
    }

    .spinner {
        width: 24px;
        height: 24px;
        border: 2px solid var(--b3-theme-primary-lighter);
        border-top-color: var(--b3-theme-primary);
        border-radius: 50%;
        animation: spin 0.8s linear infinite;
    }

    @keyframes spin {
        to { transform: rotate(360deg); }
    }

    .questions-error {
        color: var(--b3-theme-error);
        font-size: 12px;
        padding: 8px;
    }

    .questions-empty {
        color: var(--b3-theme-on-surface-light);
        font-size: 12px;
        text-align: center;
        padding: 16px;
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 8px;
    }

    .show-all-btn {
        font-size: 11px;
        padding: 4px 12px;
        background: var(--b3-theme-primary-lightest);
        border: 1px solid var(--b3-theme-primary-lighter);
        border-radius: 12px;
        color: var(--b3-theme-primary);
        cursor: pointer;
    }

    .questions-list {
        display: flex;
        flex-direction: column;
        gap: 8px;
    }

    .question-card {
        background: var(--b3-theme-background);
        border-radius: 6px;
        border: 1px solid var(--b3-border-color);
        overflow: hidden;
        transition: border-color 0.2s, opacity 0.2s;
    }

    .question-card:hover {
        border-color: var(--b3-theme-primary-lighter);
    }

    .question-card.expanded {
        border-color: var(--b3-theme-primary);
    }

    .question-card.answered {
        opacity: 0.7;
        background: var(--b3-theme-surface);
    }

    .question-card.answered .question-text {
        text-decoration: line-through;
        color: var(--b3-theme-on-surface-light);
    }

    .question-header {
        display: flex;
        align-items: flex-start;
        gap: 10px;
        padding: 12px;
        width: 100%;
        text-align: left;
        background: transparent;
        border: none;
        cursor: pointer;
        color: inherit;
        font-family: inherit;
    }

    .question-header:hover {
        background: var(--b3-theme-surface);
    }

    .status-indicator {
        width: 20px;
        height: 20px;
        display: flex;
        align-items: center;
        justify-content: center;
        border: none;
        background: transparent;
        cursor: pointer;
        font-size: 14px;
        padding: 0;
        flex-shrink: 0;
        border-radius: 50%;
        transition: all 0.2s;
    }

    .status-indicator:hover {
        background: var(--b3-theme-surface-lighter);
        transform: scale(1.1);
    }

    .status-indicator.open {
        color: var(--b3-theme-on-surface-light);
    }

    .status-indicator.partial {
        color: #f59e0b;
    }

    .status-indicator.answered {
        color: #22c55e;
    }

    .question-type-badge {
        display: flex;
        align-items: center;
        gap: 4px;
        padding: 2px 8px;
        border-radius: 10px;
        font-size: 11px;
        font-weight: 500;
        white-space: nowrap;
        flex-shrink: 0;
    }

    .type-icon {
        font-size: 11px;
    }

    .type-label {
        text-transform: capitalize;
    }

    .question-text {
        flex: 1;
        font-size: 13px;
        line-height: 1.4;
        color: var(--b3-theme-on-surface);
        transition: color 0.2s;
    }

    .expand-icon {
        font-size: 14px;
        color: var(--b3-theme-on-surface-light);
        flex-shrink: 0;
        width: 18px;
        text-align: center;
    }

    .question-details {
        padding: 0 12px 12px;
        border-top: 1px solid var(--b3-border-color);
        margin-top: -4px;
        padding-top: 12px;
    }

    .related-concepts {
        display: flex;
        flex-direction: column;
        gap: 6px;
        margin-bottom: 12px;
    }

    .related-label {
        font-size: 11px;
        color: var(--b3-theme-on-surface-light);
    }

    .concept-tags {
        display: flex;
        flex-wrap: wrap;
        gap: 6px;
    }

    .concept-tag {
        font-size: 11px;
        padding: 3px 10px;
        background: var(--b3-theme-surface);
        color: var(--b3-theme-primary);
        border-radius: 12px;
        border: 1px solid var(--b3-theme-primary-lighter);
    }

    .question-actions {
        display: flex;
        gap: 8px;
        padding-top: 8px;
        border-top: 1px dashed var(--b3-border-color);
    }

    .action-btn {
        display: flex;
        align-items: center;
        gap: 6px;
        padding: 6px 14px;
        font-size: 12px;
        border-radius: 6px;
        border: none;
        cursor: pointer;
        transition: all 0.2s;
    }

    .action-icon {
        font-size: 12px;
    }

    .mark-answered {
        background: rgba(34, 197, 94, 0.15);
        color: #22c55e;
    }

    .mark-answered:hover {
        background: rgba(34, 197, 94, 0.25);
    }

    .mark-open {
        background: var(--b3-theme-surface-lighter);
        color: var(--b3-theme-on-surface-light);
    }

    .mark-open:hover {
        background: var(--b3-theme-surface);
        color: var(--b3-theme-on-surface);
    }
</style>
