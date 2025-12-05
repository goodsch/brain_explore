<script lang="ts">
    /**
     * QuickCapture - Fast Thought Capture with AI Routing
     *
     * Captures unstructured text and processes via /capture/process API
     * to extract entities and suggest placements.
     */
    import { createEventDispatcher } from 'svelte';
    import { showMessage, fetchSyncPost } from 'siyuan';
    import { createSparkWithBackend } from '../utils/siyuan-structure';

    export let backendUrl: string;

    const dispatch = createEventDispatcher();

    // State
    let inputText = '';
    let captureType: 'text' | 'voice' | 'image' | 'link' = 'text';
    let isProcessing = false;
    let isSaving = false;
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

    // Spark metadata selection
    let selectedResonance: string = '';
    let selectedEnergy: 'low' | 'medium' | 'high' = 'medium';

    const resonanceOptions = [
        { value: '', label: 'None' },
        { value: 'curious', label: '🤔 Curious' },
        { value: 'excited', label: '✨ Excited' },
        { value: 'surprised', label: '😮 Surprised' },
        { value: 'moved', label: '💚 Moved' },
        { value: 'disturbed', label: '😟 Disturbed' },
        { value: 'unclear', label: '🤷 Unclear' },
        { value: 'connected', label: '🔗 Connected' },
        { value: 'validated', label: '✓ Validated' },
    ];

    const energyOptions = [
        { value: 'low', label: '🔋 Low Energy' },
        { value: 'medium', label: '⚡ Medium Energy' },
        { value: 'high', label: '🚀 High Energy' },
    ];

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

    async function handlePlacementSelect(placement: typeof processingResult.placements[0]) {
        if (!processingResult) return;

        isSaving = true;
        error = null;

        try {
            // Extract title from the first line of summary or use a default
            const title = processingResult.summary.split('\n')[0].slice(0, 100) || 'Quick Capture';

            // Build content from summary and original input
            const content = `${processingResult.summary}\n\n---\n\n${inputText.trim()}`;

            // Extract concept IDs from matched entities
            const concept_ids = processingResult.entities
                .filter(e => e.graph_match)
                .map(e => e.name);

            // Create spark in backend and SiYuan Daily log
            const result = await createSparkWithBackend(title, content, {
                resonance_signal: selectedResonance || undefined,
                energy_level: selectedEnergy,
                concept_ids,
            });

            if (result) {
                showMessage(`✓ Spark created: ${result.sparkId.slice(0, 8)}... (block: ${result.blockId.slice(0, 8)}...)`, 4000, 'info');

                // Reset form for next capture
                handleClear();
            } else {
                throw new Error('Failed to create spark - no result returned');
            }
        } catch (err) {
            error = err.message || String(err);
            console.error('[QuickCapture] Save error:', err);
            showMessage(`Error saving capture: ${error}`, 5000, 'error');
        } finally {
            isSaving = false;
        }
    }

    function handleBack() {
        dispatch('back');
    }

    function handleClear() {
        inputText = '';
        processingResult = null;
        error = null;
        selectedResonance = '';
        selectedEnergy = 'medium';
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

            <!-- Spark Metadata Selection -->
            <div class="result-section">
                <span class="result-label">Capture Metadata</span>
                <div class="metadata-grid">
                    <div class="metadata-field">
                        <label for="resonance-select">Resonance Signal</label>
                        <select
                            id="resonance-select"
                            class="metadata-select"
                            bind:value={selectedResonance}
                            disabled={isSaving}
                        >
                            {#each resonanceOptions as option}
                                <option value={option.value}>{option.label}</option>
                            {/each}
                        </select>
                    </div>
                    <div class="metadata-field">
                        <label for="energy-select">Energy Level</label>
                        <select
                            id="energy-select"
                            class="metadata-select"
                            bind:value={selectedEnergy}
                            disabled={isSaving}
                        >
                            {#each energyOptions as option}
                                <option value={option.value}>{option.label}</option>
                            {/each}
                        </select>
                    </div>
                </div>
            </div>

            <!-- Placement Suggestions -->
            <div class="result-section">
                <span class="result-label">Route To</span>
                <div class="placement-list">
                    {#each processingResult.placements as placement, index}
                        <button
                            class="placement-item"
                            class:placement-item--recommended={index === 0}
                            on:click={() => handlePlacementSelect(placement)}
                            disabled={isSaving}
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
                <button class="b3-button" on:click={handleClear} disabled={isSaving}>
                    {isSaving ? 'Saving...' : 'New Capture'}
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

    .metadata-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 12px;
    }

    .metadata-field {
        display: flex;
        flex-direction: column;
        gap: 4px;
    }

    .metadata-field label {
        font-size: 12px;
        font-weight: 500;
        color: var(--b3-theme-on-surface);
    }

    .metadata-select {
        padding: 8px 10px;
        border: 1px solid var(--b3-border-color);
        border-radius: 6px;
        background: var(--b3-theme-background);
        color: var(--b3-theme-on-background);
        font-size: 13px;
        cursor: pointer;
    }

    .metadata-select:focus {
        outline: none;
        border-color: var(--b3-theme-primary);
    }

    .metadata-select:disabled {
        opacity: 0.5;
        cursor: not-allowed;
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

    .placement-item:hover:not(:disabled) {
        border-color: var(--b3-theme-primary);
        background: var(--b3-theme-primary-lightest);
    }

    .placement-item:disabled {
        opacity: 0.6;
        cursor: not-allowed;
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
