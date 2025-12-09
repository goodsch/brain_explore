<script lang="ts">
    import { onMount } from 'svelte';
    import { fetchSyncPost, showMessage } from 'siyuan';

    export let conceptId: string;
    export let backendUrl: string;

    type Reframe = {
        id: string;
        text: string;
        type: string;
        created_at?: string;
        author?: string;
        feedback?: 'up' | 'down' | null;
    };

    let reframes: Reframe[] = [];
    let isLoading = false;
    let isGenerating = false;
    let error: string | null = null;
    let mounted = false;
    let lastConceptId: string | null = null;
    let feedbackPending: Record<string, boolean> = {};

    onMount(() => {
        mounted = true;
        if (conceptId) {
            loadReframes();
        }
    });

    $: if (mounted && conceptId !== lastConceptId) {
        lastConceptId = conceptId;
        if (conceptId) {
            loadReframes();
        } else {
            reframes = [];
            error = null;
        }
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

    async function loadReframes() {
        if (!conceptId) {
            return;
        }
        isLoading = true;
        error = null;
        try {
            const data = await forwardProxy<{ reframes: Reframe[] }>('GET', `/reframes/concepts/${encodeURIComponent(conceptId)}/reframes`);
            reframes = data?.reframes || [];
        } catch (err: any) {
            error = err?.message || String(err);
            reframes = [];
        } finally {
            isLoading = false;
        }
    }

    async function handleGenerate() {
        if (!conceptId || isGenerating) {
            return;
        }
        isGenerating = true;
        try {
            const data = await forwardProxy<{ reframe?: Reframe; reframes?: Reframe[] }>(
                'POST',
                `/reframes/concepts/${encodeURIComponent(conceptId)}/reframes/generate`,
                {}
            );
            const generated = data?.reframe
                ? [data.reframe]
                : data?.reframes && data.reframes.length
                    ? data.reframes
                    : [];
            if (generated.length) {
                reframes = [...generated, ...reframes];
            } else {
                showMessage('No reframes returned by backend', 4000, 'warning');
            }
        } catch (err: any) {
            showMessage(`Generate failed: ${err?.message || err}`, 5000, 'error');
        } finally {
            isGenerating = false;
        }
    }

    async function sendFeedback(reframeId: string, direction: 'up' | 'down') {
        if (!conceptId || feedbackPending[reframeId]) {
            return;
        }
        feedbackPending = { ...feedbackPending, [reframeId]: true };
        try {
            await forwardProxy(
                'POST',
                `/reframes/reframes/${encodeURIComponent(reframeId)}/feedback`,
                { vote: direction === 'up' ? 'helpful' : 'confusing' }
            );
            reframes = reframes.map(reframe =>
                reframe.id === reframeId ? { ...reframe, feedback: direction } : reframe
            );
        } catch (err: any) {
            showMessage(`Feedback failed: ${err?.message || err}`, 4000, 'error');
        } finally {
            const { [reframeId]: _ignored, ...rest } = feedbackPending;
            feedbackPending = rest;
        }
    }

    function getTypeLabel(type: string): string {
        if (!type) return 'reframe';
        return type.replace(/_/g, ' ').replace(/(^|\s)\w/g, letter => letter.toUpperCase());
    }

    function formatRelativeTime(isoDate?: string): string {
        if (!isoDate) return '';
        const date = new Date(isoDate);
        if (Number.isNaN(date.getTime())) return '';
        const diffMs = Date.now() - date.getTime();
        const diffMinutes = Math.floor(diffMs / 60000);
        if (diffMinutes < 1) return 'just now';
        if (diffMinutes < 60) return `${diffMinutes}m ago`;
        const diffHours = Math.floor(diffMinutes / 60);
        if (diffHours < 24) return `${diffHours}h ago`;
        const diffDays = Math.floor(diffHours / 24);
        if (diffDays < 7) return `${diffDays}d ago`;
        return date.toLocaleDateString();
    }
</script>

<div class="reframes-tab">
    {#if !conceptId}
        <div class="tab-placeholder">
            <p>Select a concept to view reframes.</p>
        </div>
    {:else}
        <div class="tab-header">
            <div>
                <div class="tab-title">Reframes</div>
                <div class="tab-subtitle">Metaphors, analogies, and shifts to re-approach this idea.</div>
            </div>
            <button class="generate-btn" on:click={handleGenerate} disabled={isGenerating}>
                {#if isGenerating}
                    <span class="spinner"></span>
                    Generating...
                {:else}
                    Generate Reframe
                {/if}
            </button>
        </div>

        {#if error}
            <div class="tab-error">{error}</div>
        {:else if isLoading}
            <div class="tab-placeholder loading">
                <span class="spinner"></span>
                <p>Loading reframes...</p>
            </div>
        {:else if reframes.length === 0}
            <div class="tab-placeholder">
                <p>No reframes captured yet.</p>
                <p class="hint">Generate one to capture the current spark.</p>
            </div>
        {:else}
            <div class="reframes-list">
                {#each reframes as reframe}
                    <article class="reframe-card">
                        <header class="card-header">
                            <span class="type-badge">{getTypeLabel(reframe.type)}</span>
                            {#if reframe.created_at}
                                <span class="timestamp">{formatRelativeTime(reframe.created_at)}</span>
                            {/if}
                        </header>
                        <p class="reframe-text">{reframe.text}</p>
                        <footer class="card-actions">
                            <button
                                class="feedback-btn up"
                                class:active={reframe.feedback === 'up'}
                                disabled={!!feedbackPending[reframe.id]}
                                on:click={() => sendFeedback(reframe.id, 'up')}
                                title="Helpful reframe"
                            >
                                👍
                            </button>
                            <button
                                class="feedback-btn down"
                                class:active={reframe.feedback === 'down'}
                                disabled={!!feedbackPending[reframe.id]}
                                on:click={() => sendFeedback(reframe.id, 'down')}
                                title="Off-track reframe"
                            >
                                👎
                            </button>
                        </footer>
                    </article>
                {/each}
            </div>
        {/if}
    {/if}
</div>

<style>
    .reframes-tab {
        background: var(--bg-tertiary, rgba(255, 255, 255, 0.9));
        border: 1px solid var(--border-subtle, rgba(26, 24, 22, 0.06));
        border-radius: var(--radius-md, 10px);
        padding: 16px;
        box-shadow: var(--shadow-sm, 0 2px 4px rgba(0, 0, 0, 0.06));
    }

    .tab-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 12px;
        margin-bottom: 12px;
    }

    .tab-title {
        font-weight: 600;
        font-size: 1rem;
    }

    .tab-subtitle {
        font-size: 0.85rem;
        color: var(--text-muted, #777);
    }

    .generate-btn {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 10px 16px;
        background: var(--entity-concept, #c9872e);
        color: #fff;
        border: none;
        border-radius: var(--radius-sm, 6px);
        font-weight: 600;
        cursor: pointer;
        transition: opacity 0.2s ease;
    }

    .generate-btn:disabled {
        opacity: 0.6;
        cursor: not-allowed;
    }

    .tab-placeholder {
        text-align: center;
        padding: 24px 12px;
        color: var(--text-muted, #777);
    }

    .tab-placeholder.loading {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 8px;
    }

    .tab-placeholder .hint {
        margin-top: 4px;
        font-size: 0.85rem;
    }

    .tab-error {
        padding: 12px;
        border-radius: var(--radius-sm, 6px);
        background: rgba(212, 78, 66, 0.12);
        color: #a32921;
        font-size: 0.9rem;
    }

    .reframes-list {
        display: flex;
        flex-direction: column;
        gap: 12px;
        margin-top: 8px;
    }

    .reframe-card {
        border: 1px solid var(--border-subtle, rgba(26, 24, 22, 0.08));
        border-radius: var(--radius-md, 10px);
        padding: 12px;
        background: var(--bg-secondary, #fff);
        display: flex;
        flex-direction: column;
        gap: 10px;
    }

    .card-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-size: 0.8rem;
    }

    .type-badge {
        text-transform: uppercase;
        letter-spacing: 0.04em;
        font-weight: 600;
        color: var(--entity-concept, #c9872e);
    }

    .timestamp {
        color: var(--text-muted, #999);
    }

    .reframe-text {
        margin: 0;
        font-size: 0.95rem;
        line-height: 1.4;
    }

    .card-actions {
        display: flex;
        gap: 8px;
    }

    .feedback-btn {
        width: 36px;
        height: 32px;
        border-radius: 6px;
        border: 1px solid var(--border-default, rgba(26, 24, 22, 0.1));
        background: transparent;
        cursor: pointer;
        font-size: 1rem;
        transition: all 0.15s ease;
    }

    .feedback-btn.active {
        background: rgba(201, 135, 46, 0.12);
        border-color: var(--entity-concept, #c9872e);
    }

    .feedback-btn:disabled {
        opacity: 0.5;
        cursor: not-allowed;
    }

    .spinner {
        width: 16px;
        height: 16px;
        border-radius: 50%;
        border: 2px solid rgba(255, 255, 255, 0.4);
        border-top-color: rgba(255, 255, 255, 0.9);
        animation: spin 0.8s linear infinite;
    }

    .tab-placeholder.loading .spinner {
        border-color: rgba(0, 0, 0, 0.1);
        border-top-color: rgba(0, 0, 0, 0.4);
    }

    @keyframes spin {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
    }
</style>
