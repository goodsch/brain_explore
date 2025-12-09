<script lang="ts">
    /**
     * ClarificationDialog - Guided clarification before facet decomposition (Sprint 4)
     *
     * Shows a clarifying question to understand user's exploration intent before
     * generating facets for an entity. Helps guide the exploration in a direction
     * that matches the user's goals.
     */
    import { createEventDispatcher, onMount } from 'svelte';
    import { fetchSyncPost, showMessage } from 'siyuan';

    export let entityName: string;
    export let backendUrl: string;
    export let userGoal: string = '';
    export let isOpen: boolean = false;

    const dispatch = createEventDispatcher();

    type ClarificationResponse = {
        entity_name: string;
        clarifying_question: string;
        suggested_facets: string[];
        prerequisites: string[];
        why_it_matters: string | null;
    };

    let clarification: ClarificationResponse | null = null;
    let isLoading = false;
    let error: string | null = null;
    let userResponse = '';
    let selectedFacets: Set<string> = new Set();

    onMount(() => {
        if (isOpen && entityName) {
            loadClarification();
        }
    });

    $: if (isOpen && entityName && !clarification && !isLoading) {
        loadClarification();
    }

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
            payload.payload = JSON.stringify(body) ?? {};
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

    async function loadClarification() {
        isLoading = true;
        error = null;
        try {
            clarification = await forwardProxy<ClarificationResponse>(
                'POST',
                '/graph/clarify',
                {
                    entity_name: entityName,
                    user_goal: userGoal || null
                }
            );
        } catch (err: any) {
            error = err?.message || String(err);
            clarification = null;
        } finally {
            isLoading = false;
        }
    }

    function toggleFacet(facet: string) {
        if (selectedFacets.has(facet)) {
            selectedFacets.delete(facet);
        } else {
            selectedFacets.add(facet);
        }
        selectedFacets = new Set(selectedFacets);
    }

    function handleProceed() {
        dispatch('proceed', {
            entityName,
            userResponse,
            selectedFacets: Array.from(selectedFacets),
            clarification
        });
        close();
    }

    function handleSkip() {
        dispatch('skip', { entityName });
        close();
    }

    function close() {
        isOpen = false;
        clarification = null;
        userResponse = '';
        selectedFacets = new Set();
        dispatch('close');
    }

    function navigateToPrerequisite(concept: string) {
        dispatch('navigateToEntity', { entityName: concept });
    }
</script>

{#if isOpen}
    <div class="clarification-overlay" on:click|self={close}>
        <div class="clarification-dialog">
            <div class="dialog-header">
                <h3 class="dialog-title">
                    <span class="title-icon">💭</span>
                    Before exploring "{entityName}"
                </h3>
                <button class="close-btn" on:click={close} title="Close">×</button>
            </div>

            {#if isLoading}
                <div class="dialog-loading">
                    <div class="spinner"></div>
                    <span>Preparing clarifying questions...</span>
                </div>
            {:else if error}
                <div class="dialog-error">
                    <span class="error-icon">⚠️</span>
                    <span>{error}</span>
                    <button class="retry-btn" on:click={loadClarification}>Retry</button>
                </div>
            {:else if clarification}
                <div class="dialog-content">
                    <!-- Clarifying Question -->
                    <div class="clarification-section">
                        <div class="section-label">A question to guide your exploration:</div>
                        <div class="clarifying-question">{clarification.clarifying_question}</div>
                        <textarea
                            class="response-input"
                            bind:value={userResponse}
                            placeholder="Your thoughts (optional)..."
                            rows="3"
                        ></textarea>
                    </div>

                    <!-- Why It Matters -->
                    {#if clarification.why_it_matters}
                        <div class="why-matters-section">
                            <div class="section-label">
                                <span class="label-icon">✨</span>
                                Why this matters
                            </div>
                            <p class="why-text">{clarification.why_it_matters}</p>
                        </div>
                    {/if}

                    <!-- Suggested Facets -->
                    {#if clarification.suggested_facets.length > 0}
                        <div class="facets-section">
                            <div class="section-label">
                                <span class="label-icon">📂</span>
                                Suggested areas to explore
                            </div>
                            <div class="facet-chips">
                                {#each clarification.suggested_facets as facet}
                                    <button
                                        class="facet-chip"
                                        class:selected={selectedFacets.has(facet)}
                                        on:click={() => toggleFacet(facet)}
                                    >
                                        <span class="check-icon">{selectedFacets.has(facet) ? '✓' : ''}</span>
                                        {facet}
                                    </button>
                                {/each}
                            </div>
                            {#if selectedFacets.size > 0}
                                <div class="selection-hint">
                                    {selectedFacets.size} facet{selectedFacets.size > 1 ? 's' : ''} selected for focused exploration
                                </div>
                            {/if}
                        </div>
                    {/if}

                    <!-- Prerequisites -->
                    {#if clarification.prerequisites.length > 0}
                        <div class="prereq-section">
                            <div class="section-label">
                                <span class="label-icon">📚</span>
                                You might want to understand first
                            </div>
                            <div class="prereq-list">
                                {#each clarification.prerequisites as prereq}
                                    <button class="prereq-item" on:click={() => navigateToPrerequisite(prereq)}>
                                        <span class="prereq-icon">→</span>
                                        {prereq}
                                    </button>
                                {/each}
                            </div>
                        </div>
                    {/if}
                </div>

                <div class="dialog-footer">
                    <button class="skip-btn" on:click={handleSkip}>
                        Skip & Explore Directly
                    </button>
                    <button class="proceed-btn" on:click={handleProceed}>
                        <span>Continue Exploration</span>
                        <span class="proceed-arrow">→</span>
                    </button>
                </div>
            {/if}
        </div>
    </div>
{/if}

<style>
    .clarification-overlay {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(0, 0, 0, 0.5);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 1000;
        backdrop-filter: blur(2px);
    }

    .clarification-dialog {
        background: var(--b3-theme-background);
        border-radius: 12px;
        width: 90%;
        max-width: 520px;
        max-height: 80vh;
        overflow: hidden;
        display: flex;
        flex-direction: column;
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.2);
    }

    .dialog-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 16px 20px;
        border-bottom: 1px solid var(--b3-border-color);
        background: var(--b3-theme-surface);
    }

    .dialog-title {
        margin: 0;
        font-size: 16px;
        font-weight: 600;
        display: flex;
        align-items: center;
        gap: 8px;
        color: var(--b3-theme-on-surface);
    }

    .title-icon {
        font-size: 18px;
    }

    .close-btn {
        width: 28px;
        height: 28px;
        border: none;
        background: transparent;
        font-size: 20px;
        color: var(--b3-theme-on-surface-light);
        cursor: pointer;
        border-radius: 6px;
        display: flex;
        align-items: center;
        justify-content: center;
        transition: all 0.2s;
    }

    .close-btn:hover {
        background: var(--b3-theme-surface-lighter);
        color: var(--b3-theme-on-surface);
    }

    .dialog-content {
        padding: 20px;
        overflow-y: auto;
        flex: 1;
    }

    .dialog-loading {
        padding: 40px;
        text-align: center;
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 12px;
        color: var(--b3-theme-on-surface-light);
    }

    .spinner {
        width: 28px;
        height: 28px;
        border: 2px solid var(--b3-theme-primary-lighter);
        border-top-color: var(--b3-theme-primary);
        border-radius: 50%;
        animation: spin 0.8s linear infinite;
    }

    @keyframes spin {
        to { transform: rotate(360deg); }
    }

    .dialog-error {
        padding: 20px;
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 12px;
        color: var(--b3-theme-error);
    }

    .error-icon {
        font-size: 24px;
    }

    .retry-btn {
        padding: 6px 16px;
        border: 1px solid var(--b3-border-color);
        background: transparent;
        border-radius: 6px;
        cursor: pointer;
        color: var(--b3-theme-on-surface);
    }

    .clarification-section {
        margin-bottom: 20px;
    }

    .section-label {
        font-size: 12px;
        font-weight: 500;
        color: var(--b3-theme-on-surface-light);
        margin-bottom: 8px;
        display: flex;
        align-items: center;
        gap: 6px;
    }

    .label-icon {
        font-size: 14px;
    }

    .clarifying-question {
        font-size: 15px;
        line-height: 1.5;
        color: var(--b3-theme-on-surface);
        padding: 12px 16px;
        background: var(--b3-theme-surface);
        border-radius: 8px;
        border-left: 3px solid var(--b3-theme-primary);
        margin-bottom: 12px;
    }

    .response-input {
        width: 100%;
        padding: 10px 12px;
        border: 1px solid var(--b3-border-color);
        border-radius: 6px;
        font-size: 13px;
        font-family: inherit;
        resize: vertical;
        background: var(--b3-theme-background);
        color: var(--b3-theme-on-surface);
        transition: border-color 0.2s;
    }

    .response-input:focus {
        outline: none;
        border-color: var(--b3-theme-primary);
    }

    .why-matters-section {
        margin-bottom: 20px;
        padding: 12px 16px;
        background: rgba(139, 92, 246, 0.1);
        border-radius: 8px;
    }

    .why-text {
        margin: 0;
        font-size: 13px;
        line-height: 1.5;
        color: var(--b3-theme-on-surface);
    }

    .facets-section {
        margin-bottom: 20px;
    }

    .facet-chips {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
    }

    .facet-chip {
        display: flex;
        align-items: center;
        gap: 6px;
        padding: 6px 14px;
        border: 1px solid var(--b3-border-color);
        border-radius: 20px;
        background: transparent;
        font-size: 13px;
        cursor: pointer;
        transition: all 0.2s;
        color: var(--b3-theme-on-surface);
    }

    .facet-chip:hover {
        background: var(--b3-theme-surface);
        border-color: var(--b3-theme-primary-lighter);
    }

    .facet-chip.selected {
        background: var(--b3-theme-primary-lightest);
        border-color: var(--b3-theme-primary);
        color: var(--b3-theme-primary);
    }

    .check-icon {
        width: 14px;
        font-size: 12px;
        font-weight: bold;
    }

    .selection-hint {
        margin-top: 8px;
        font-size: 11px;
        color: var(--b3-theme-primary);
    }

    .prereq-section {
        margin-bottom: 8px;
    }

    .prereq-list {
        display: flex;
        flex-direction: column;
        gap: 4px;
    }

    .prereq-item {
        display: flex;
        align-items: center;
        gap: 8px;
        padding: 8px 12px;
        border: none;
        background: var(--b3-theme-surface);
        border-radius: 6px;
        font-size: 13px;
        cursor: pointer;
        transition: all 0.2s;
        color: var(--b3-theme-on-surface);
        text-align: left;
    }

    .prereq-item:hover {
        background: var(--b3-theme-surface-lighter);
        color: var(--b3-theme-primary);
    }

    .prereq-icon {
        font-size: 12px;
        color: var(--b3-theme-primary);
    }

    .dialog-footer {
        display: flex;
        justify-content: space-between;
        padding: 16px 20px;
        border-top: 1px solid var(--b3-border-color);
        background: var(--b3-theme-surface);
    }

    .skip-btn {
        padding: 8px 16px;
        border: 1px solid var(--b3-border-color);
        background: transparent;
        border-radius: 6px;
        font-size: 13px;
        cursor: pointer;
        color: var(--b3-theme-on-surface-light);
        transition: all 0.2s;
    }

    .skip-btn:hover {
        background: var(--b3-theme-surface-lighter);
        color: var(--b3-theme-on-surface);
    }

    .proceed-btn {
        display: flex;
        align-items: center;
        gap: 8px;
        padding: 8px 20px;
        border: none;
        background: var(--b3-theme-primary);
        color: white;
        border-radius: 6px;
        font-size: 13px;
        font-weight: 500;
        cursor: pointer;
        transition: all 0.2s;
    }

    .proceed-btn:hover {
        background: var(--b3-theme-primary-light);
    }

    .proceed-arrow {
        font-size: 14px;
    }
</style>
