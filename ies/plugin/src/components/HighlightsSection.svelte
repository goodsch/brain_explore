<script lang="ts">
    import { onMount } from 'svelte';
    import { getHighlightApi, type Highlight } from '../services/highlightApi';

    export let bookId: string;
    export let backendUrl: string = 'http://192.168.86.60:8081';

    let highlights: Highlight[] = [];
    let isLoading = false;
    let error: string | null = null;
    let mounted = false;
    let lastBookId: string | null = null;
    let syncingAll = false;
    let syncResult: { synced: number; errors: string[] } | null = null;

    const highlightApi = getHighlightApi(backendUrl);

    onMount(() => {
        mounted = true;
        if (bookId) {
            loadHighlights();
        }
    });

    $: if (mounted && bookId !== lastBookId) {
        lastBookId = bookId;
        if (bookId) {
            loadHighlights();
        } else {
            highlights = [];
            error = null;
        }
    }

    async function loadHighlights() {
        if (!bookId) {
            return;
        }
        isLoading = true;
        error = null;
        try {
            highlights = await highlightApi.listByBook(bookId, 100);
        } catch (err: any) {
            error = err?.message || String(err);
            highlights = [];
        } finally {
            isLoading = false;
        }
    }

    async function syncAllToSiyuan() {
        if (!bookId) return;
        syncingAll = true;
        syncResult = null;
        try {
            const result = await highlightApi.syncBookToSiyuan(bookId);
            syncResult = {
                synced: result.synced,
                errors: result.errors
            };
            // Reload highlights to update siyuan_block_id status
            await loadHighlights();
        } catch (err: any) {
            error = err?.message || String(err);
        } finally {
            syncingAll = false;
        }
    }

    function getColorClass(color: string): string {
        const colorMap: Record<string, string> = {
            yellow: 'hl-yellow',
            green: 'hl-green',
            blue: 'hl-blue',
            pink: 'hl-pink',
            purple: 'hl-purple',
        };
        return colorMap[color] || 'hl-yellow';
    }

    function formatDate(dateStr: string): string {
        const date = new Date(dateStr);
        return date.toLocaleDateString(undefined, {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
        });
    }

    function getUnsyncedCount(): number {
        return highlights.filter(h => !h.siyuan_block_id).length;
    }
</script>

<div class="highlights-section">
    <div class="highlights-header">
        <h3>📝 Highlights</h3>
        {#if highlights.length > 0}
            <span class="highlight-count">
                {highlights.length} highlight{highlights.length !== 1 ? 's' : ''}
            </span>
        {/if}
    </div>

    {#if isLoading}
        <div class="highlights-loading">
            <span class="spinner"></span>
            Loading highlights...
        </div>
    {:else if error}
        <div class="highlights-error">
            <span class="error-icon">⚠️</span>
            <span>{error}</span>
            <button class="retry-btn" on:click={loadHighlights}>Retry</button>
        </div>
    {:else if highlights.length === 0}
        <div class="highlights-empty">
            <span class="empty-icon">📖</span>
            <span>No highlights yet. Start reading in IES Reader to add highlights!</span>
        </div>
    {:else}
        <!-- Sync button if there are unsynced highlights -->
        {#if getUnsyncedCount() > 0}
            <div class="sync-bar">
                <span class="sync-info">
                    {getUnsyncedCount()} highlight{getUnsyncedCount() !== 1 ? 's' : ''} not synced to SiYuan
                </span>
                <button
                    class="sync-btn"
                    on:click={syncAllToSiyuan}
                    disabled={syncingAll}
                >
                    {#if syncingAll}
                        <span class="spinner small"></span>
                        Syncing...
                    {:else}
                        Sync to SiYuan
                    {/if}
                </button>
            </div>
        {/if}

        {#if syncResult}
            <div class="sync-result" class:has-errors={syncResult.errors.length > 0}>
                {#if syncResult.synced > 0}
                    <span class="success">✓ Synced {syncResult.synced} highlight{syncResult.synced !== 1 ? 's' : ''}</span>
                {/if}
                {#if syncResult.errors.length > 0}
                    <span class="error">{syncResult.errors.length} error{syncResult.errors.length !== 1 ? 's' : ''}</span>
                {/if}
            </div>
        {/if}

        <div class="highlights-list">
            {#each highlights as highlight (highlight.id)}
                <div class="highlight-card {getColorClass(highlight.color)}">
                    <div class="highlight-text">
                        "{highlight.text}"
                    </div>
                    {#if highlight.note}
                        <div class="highlight-note">
                            <span class="note-label">Note:</span>
                            {highlight.note}
                        </div>
                    {/if}
                    <div class="highlight-meta">
                        {#if highlight.chapter}
                            <span class="meta-chapter">{highlight.chapter}</span>
                        {/if}
                        <span class="meta-date">{formatDate(highlight.created_at)}</span>
                        {#if highlight.siyuan_block_id}
                            <span class="meta-synced" title="Synced to SiYuan">✓</span>
                        {/if}
                    </div>
                    {#if highlight.entity_refs && highlight.entity_refs.length > 0}
                        <div class="highlight-entities">
                            {#each highlight.entity_refs as entity}
                                <span class="entity-tag">{entity}</span>
                            {/each}
                        </div>
                    {/if}
                </div>
            {/each}
        </div>
    {/if}
</div>

<style>
    .highlights-section {
        padding: 12px;
    }

    .highlights-header {
        display: flex;
        align-items: center;
        gap: 8px;
        margin-bottom: 12px;
    }

    .highlights-header h3 {
        margin: 0;
        font-size: 14px;
        font-weight: 600;
        color: var(--b3-theme-on-background);
    }

    .highlight-count {
        font-size: 12px;
        color: var(--b3-theme-on-surface-light);
        background: var(--b3-theme-surface);
        padding: 2px 8px;
        border-radius: 10px;
    }

    .highlights-loading,
    .highlights-empty,
    .highlights-error {
        display: flex;
        align-items: center;
        gap: 8px;
        padding: 16px;
        color: var(--b3-theme-on-surface-light);
        font-size: 13px;
    }

    .highlights-error {
        color: var(--b3-theme-error);
        background: rgba(var(--b3-theme-error-rgb), 0.1);
        border-radius: 8px;
    }

    .retry-btn {
        margin-left: auto;
        padding: 4px 12px;
        font-size: 12px;
        background: var(--b3-theme-primary);
        color: var(--b3-theme-on-primary);
        border: none;
        border-radius: 4px;
        cursor: pointer;
    }

    .sync-bar {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 8px 12px;
        background: var(--b3-theme-surface);
        border-radius: 6px;
        margin-bottom: 12px;
    }

    .sync-info {
        font-size: 12px;
        color: var(--b3-theme-on-surface-light);
    }

    .sync-btn {
        display: flex;
        align-items: center;
        gap: 6px;
        padding: 6px 12px;
        font-size: 12px;
        background: var(--b3-theme-primary);
        color: var(--b3-theme-on-primary);
        border: none;
        border-radius: 4px;
        cursor: pointer;
    }

    .sync-btn:disabled {
        opacity: 0.7;
        cursor: not-allowed;
    }

    .sync-result {
        padding: 8px 12px;
        font-size: 12px;
        background: rgba(var(--b3-theme-success-rgb), 0.1);
        border-radius: 6px;
        margin-bottom: 12px;
    }

    .sync-result.has-errors {
        background: rgba(var(--b3-theme-warning-rgb), 0.1);
    }

    .sync-result .success {
        color: var(--b3-theme-success);
    }

    .sync-result .error {
        color: var(--b3-theme-error);
        margin-left: 8px;
    }

    .highlights-list {
        display: flex;
        flex-direction: column;
        gap: 8px;
    }

    .highlight-card {
        padding: 12px;
        border-radius: 8px;
        background: var(--b3-theme-surface);
        border-left: 4px solid;
    }

    .highlight-card.hl-yellow {
        border-left-color: #ffd93d;
        background: rgba(255, 217, 61, 0.08);
    }

    .highlight-card.hl-green {
        border-left-color: #6bcb77;
        background: rgba(107, 203, 119, 0.08);
    }

    .highlight-card.hl-blue {
        border-left-color: #4d96ff;
        background: rgba(77, 150, 255, 0.08);
    }

    .highlight-card.hl-pink {
        border-left-color: #ff6b9d;
        background: rgba(255, 107, 157, 0.08);
    }

    .highlight-card.hl-purple {
        border-left-color: #9d4edd;
        background: rgba(157, 78, 221, 0.08);
    }

    .highlight-text {
        font-size: 13px;
        line-height: 1.5;
        color: var(--b3-theme-on-background);
        font-style: italic;
    }

    .highlight-note {
        margin-top: 8px;
        padding-top: 8px;
        border-top: 1px solid var(--b3-theme-surface-lighter);
        font-size: 12px;
        color: var(--b3-theme-on-surface);
    }

    .note-label {
        font-weight: 600;
        margin-right: 4px;
        color: var(--b3-theme-on-surface-light);
    }

    .highlight-meta {
        display: flex;
        align-items: center;
        gap: 8px;
        margin-top: 8px;
        font-size: 11px;
        color: var(--b3-theme-on-surface-light);
    }

    .meta-chapter {
        background: var(--b3-theme-surface-lighter);
        padding: 2px 6px;
        border-radius: 4px;
    }

    .meta-synced {
        color: var(--b3-theme-success);
    }

    .highlight-entities {
        display: flex;
        flex-wrap: wrap;
        gap: 4px;
        margin-top: 8px;
    }

    .entity-tag {
        font-size: 10px;
        padding: 2px 6px;
        background: var(--b3-theme-primary-lighter);
        color: var(--b3-theme-primary);
        border-radius: 4px;
    }

    .spinner {
        display: inline-block;
        width: 16px;
        height: 16px;
        border: 2px solid var(--b3-theme-surface-lighter);
        border-top-color: var(--b3-theme-primary);
        border-radius: 50%;
        animation: spin 1s linear infinite;
    }

    .spinner.small {
        width: 12px;
        height: 12px;
        border-width: 1.5px;
    }

    @keyframes spin {
        to {
            transform: rotate(360deg);
        }
    }

    .empty-icon,
    .error-icon {
        font-size: 20px;
    }
</style>
