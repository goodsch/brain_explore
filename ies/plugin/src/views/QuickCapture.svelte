<script lang="ts">
    /**
     * QuickCapture - Fast Thought Capture with AI Routing
     *
     * Captures unstructured text and processes via /capture/process API
     * to extract entities and suggest placements.
     */
    import { createEventDispatcher } from 'svelte';
    import { showMessage, fetchSyncPost } from 'siyuan';

    export let backendUrl: string;

    const dispatch = createEventDispatcher();

    // State
    let inputText = '';
    let captureType: 'text' | 'voice' | 'image' | 'link' = 'text';
    let isProcessing = false;
    let processingResult: {
        summary: string;
        entities: Array<{
            name: string;
            type: string;
            confidence: number;
            graph_match: boolean;
        }>;
        suggested_tags: string[];
        placements: Array<{
            target_type: string;
            target_id: string | null;
            target_name: string;
            confidence: number;
            preview: string;
            action: string;
        }>;
    } | null = null;
    let error: string | null = null;

    // API helper
    async function apiPost(endpoint: string, body: any): Promise<any> {
        const url = `${backendUrl}${endpoint}`;

        const response = await fetchSyncPost('/api/network/forwardProxy', {
            url: url,
            method: 'POST',
            timeout: 60000, // Longer timeout for AI processing
            contentType: 'application/json',
            headers: [],
            payload: body
        });

        if (response.code !== 0) {
            throw new Error(`Proxy error: ${response.msg}`);
        }

        const proxyData = response.data;
        if (!proxyData || proxyData.status !== 200) {
            const errorBody = typeof proxyData?.body === 'string'
                ? JSON.parse(proxyData.body)
                : proxyData?.body;
            throw new Error(errorBody?.detail || `Backend error: ${proxyData?.status || 'unknown'}`);
        }

        return typeof proxyData.body === 'string' ? JSON.parse(proxyData.body) : proxyData.body;
    }

    async function handleProcess() {
        if (!inputText.trim() || isProcessing) return;

        isProcessing = true;
        error = null;
        processingResult = null;

        try {
            const result = await apiPost('/capture/process', {
                content: inputText.trim(),
                capture_type: captureType,
                context: {}
            });

            processingResult = result;
        } catch (err) {
            error = err.message || String(err);
            console.error('[QuickCapture] Process error:', err);
        } finally {
            isProcessing = false;
        }
    }

    function handlePlacementSelect(placement: typeof processingResult.placements[0]) {
        // For now, show message about what would happen
        // Future: Actually route to the target
        showMessage(`Would route to: ${placement.target_name} (${placement.action})`, 3000);

        // Reset for next capture
        inputText = '';
        processingResult = null;
    }

    function handleBack() {
        dispatch('back');
    }

    function handleClear() {
        inputText = '';
        processingResult = null;
        error = null;
    }

    function getConfidenceColor(confidence: number): string {
        if (confidence >= 0.8) return 'var(--b3-theme-success)';
        if (confidence >= 0.5) return 'var(--b3-theme-warning)';
        return 'var(--b3-theme-on-surface-light)';
    }

    function getTypeIcon(type: string): string {
        switch (type) {
            case 'existing_note': return '📄';
            case 'existing_concept': return '🔗';
            case 'active_journey': return '🧭';
            case 'new_note': return '✨';
            default: return '📌';
        }
    }
</script>

<div class="capture-mode">
    <div class="capture-header">
        <button class="back-btn" on:click={handleBack} title="Back to Dashboard">
            <svg viewBox="0 0 24 24" width="16" height="16">
                <path fill="currentColor" d="M20 11H7.83l5.59-5.59L12 4l-8 8 8 8 1.41-1.41L7.83 13H20v-2z"/>
            </svg>
        </button>
        <span class="capture-title">Quick Capture</span>
    </div>

    {#if !processingResult}
        <!-- Input Phase -->
        <div class="capture-input-section">
            <div class="capture-type-selector">
                <button
                    class="type-btn"
                    class:type-btn--active={captureType === 'text'}
                    on:click={() => captureType = 'text'}
                >
                    Text
                </button>
                <button
                    class="type-btn"
                    class:type-btn--active={captureType === 'link'}
                    on:click={() => captureType = 'link'}
                >
                    Link
                </button>
            </div>

            <textarea
                class="capture-textarea"
                bind:value={inputText}
                placeholder={captureType === 'link'
                    ? "Paste a URL to analyze..."
                    : "Capture a thought, idea, or insight..."}
                rows="6"
                disabled={isProcessing}
            ></textarea>

            {#if error}
                <div class="capture-error">
                    {error}
                </div>
            {/if}

            <div class="capture-actions">
                <button
                    class="b3-button b3-button--primary"
                    on:click={handleProcess}
                    disabled={isProcessing || !inputText.trim()}
                >
                    {isProcessing ? 'Processing...' : 'Process'}
                </button>
            </div>

            <div class="capture-help">
                <p>AI will extract entities and suggest where to route your capture.</p>
            </div>
        </div>
    {:else}
        <!-- Results Phase -->
        <div class="capture-results">
            <!-- Summary -->
            <div class="result-section">
                <span class="result-label">Summary</span>
                <p class="result-summary">{processingResult.summary}</p>
            </div>

            <!-- Extracted Entities -->
            {#if processingResult.entities.length > 0}
                <div class="result-section">
                    <span class="result-label">Extracted Entities</span>
                    <div class="entity-list">
                        {#each processingResult.entities as entity}
                            <span
                                class="entity-chip"
                                class:entity-chip--matched={entity.graph_match}
                                title="{entity.type} - {Math.round(entity.confidence * 100)}% confidence{entity.graph_match ? ' (in graph)' : ''}"
                            >
                                {entity.name}
                                {#if entity.graph_match}
                                    <span class="entity-match-indicator">✓</span>
                                {/if}
                            </span>
                        {/each}
                    </div>
                </div>
            {/if}

            <!-- Suggested Tags -->
            {#if processingResult.suggested_tags.length > 0}
                <div class="result-section">
                    <span class="result-label">Suggested Tags</span>
                    <div class="tag-list">
                        {#each processingResult.suggested_tags as tag}
                            <span class="tag-chip">#{tag}</span>
                        {/each}
                    </div>
                </div>
            {/if}

            <!-- Placement Suggestions -->
            <div class="result-section">
                <span class="result-label">Route To</span>
                <div class="placement-list">
                    {#each processingResult.placements as placement, index}
                        <button
                            class="placement-item"
                            class:placement-item--recommended={index === 0}
                            on:click={() => handlePlacementSelect(placement)}
                        >
                            <span class="placement-icon">{getTypeIcon(placement.target_type)}</span>
                            <div class="placement-info">
                                <span class="placement-name">{placement.target_name}</span>
                                <span class="placement-action">{placement.action}</span>
                            </div>
                            <span
                                class="placement-confidence"
                                style="color: {getConfidenceColor(placement.confidence)}"
                            >
                                {Math.round(placement.confidence * 100)}%
                            </span>
                        </button>
                    {/each}
                </div>
            </div>

            <!-- Actions -->
            <div class="result-actions">
                <button class="b3-button" on:click={handleClear}>
                    New Capture
                </button>
            </div>
        </div>
    {/if}
</div>

<style>
    .capture-mode {
        display: flex;
        flex-direction: column;
        height: 100%;
        padding: 12px;
        gap: 16px;
    }

    .capture-header {
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

    .capture-title {
        font-weight: 600;
        flex: 1;
    }

    .capture-input-section {
        display: flex;
        flex-direction: column;
        gap: 12px;
    }

    .capture-type-selector {
        display: flex;
        gap: 8px;
    }

    .type-btn {
        padding: 6px 16px;
        border: 1px solid var(--b3-border-color);
        background: var(--b3-theme-surface);
        border-radius: 6px;
        cursor: pointer;
        font-size: 13px;
        color: var(--b3-theme-on-surface);
        transition: all 0.15s;
    }

    .type-btn:hover {
        border-color: var(--b3-theme-primary);
    }

    .type-btn--active {
        background: var(--b3-theme-primary);
        color: var(--b3-theme-on-primary);
        border-color: var(--b3-theme-primary);
    }

    .capture-textarea {
        width: 100%;
        resize: none;
        border: 1px solid var(--b3-border-color);
        border-radius: 8px;
        padding: 12px;
        font-size: 14px;
        line-height: 1.5;
        background: var(--b3-theme-background);
        color: var(--b3-theme-on-background);
    }

    .capture-textarea:focus {
        outline: none;
        border-color: var(--b3-theme-primary);
    }

    .capture-error {
        padding: 8px 12px;
        background: var(--b3-theme-error-lighter);
        color: var(--b3-theme-error);
        border-radius: 6px;
        font-size: 13px;
    }

    .capture-actions {
        display: flex;
        justify-content: flex-end;
    }

    .capture-help {
        color: var(--b3-theme-on-surface-light);
        font-size: 12px;
        text-align: center;
    }

    .capture-results {
        display: flex;
        flex-direction: column;
        gap: 16px;
        overflow-y: auto;
        flex: 1;
    }

    .result-section {
        display: flex;
        flex-direction: column;
        gap: 8px;
    }

    .result-label {
        font-size: 11px;
        font-weight: 600;
        text-transform: uppercase;
        color: var(--b3-theme-on-surface-light);
    }

    .result-summary {
        margin: 0;
        font-size: 14px;
        line-height: 1.5;
        padding: 12px;
        background: var(--b3-theme-surface);
        border-radius: 8px;
    }

    .entity-list, .tag-list {
        display: flex;
        flex-wrap: wrap;
        gap: 6px;
    }

    .entity-chip {
        padding: 4px 10px;
        font-size: 12px;
        background: var(--b3-theme-surface);
        border: 1px solid var(--b3-border-color);
        border-radius: 12px;
        display: flex;
        align-items: center;
        gap: 4px;
    }

    .entity-chip--matched {
        background: var(--b3-theme-primary-lightest);
        border-color: var(--b3-theme-primary-light);
    }

    .entity-match-indicator {
        font-size: 10px;
        color: var(--b3-theme-success);
    }

    .tag-chip {
        padding: 4px 10px;
        font-size: 12px;
        background: var(--b3-theme-secondary-lighter);
        border-radius: 12px;
        color: var(--b3-theme-secondary);
    }

    .placement-list {
        display: flex;
        flex-direction: column;
        gap: 8px;
    }

    .placement-item {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 12px;
        background: var(--b3-theme-surface);
        border: 2px solid var(--b3-border-color);
        border-radius: 10px;
        cursor: pointer;
        text-align: left;
        transition: all 0.15s;
    }

    .placement-item:hover {
        border-color: var(--b3-theme-primary);
        background: var(--b3-theme-primary-lightest);
    }

    .placement-item--recommended {
        border-color: var(--b3-theme-primary);
        background: var(--b3-theme-primary-lightest);
    }

    .placement-icon {
        font-size: 20px;
    }

    .placement-info {
        flex: 1;
        display: flex;
        flex-direction: column;
        gap: 2px;
    }

    .placement-name {
        font-weight: 500;
        font-size: 14px;
    }

    .placement-action {
        font-size: 12px;
        color: var(--b3-theme-on-surface-light);
    }

    .placement-confidence {
        font-size: 13px;
        font-weight: 600;
    }

    .result-actions {
        padding-top: 8px;
        border-top: 1px solid var(--b3-border-color);
        display: flex;
        justify-content: center;
    }
</style>
