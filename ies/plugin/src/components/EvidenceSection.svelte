<script lang="ts">
    import { onMount } from 'svelte';
    import { fetchSyncPost } from 'siyuan';

    export let entityName: string;
    export let backendUrl: string;

    type EvidencePassage = {
        id: string;
        text: string;
        source_title: string;
        source_author: string | null;
        location: {
            chapter?: string;
            page?: number;
            cfi?: string;
        } | null;
        confidence: number;
        source_type: 'chunk' | 'book';
    };

    type EvidenceResponse = {
        entity_name: string;
        evidence: EvidencePassage[];
        total_count: number;
        sources_searched: number;
    };

    let evidence: EvidencePassage[] = [];
    let isLoading = false;
    let error: string | null = null;
    let mounted = false;
    let lastEntityName: string | null = null;

    onMount(() => {
        mounted = true;
        if (entityName) {
            loadEvidence();
        }
    });

    $: if (mounted && entityName !== lastEntityName) {
        lastEntityName = entityName;
        if (entityName) {
            loadEvidence();
        } else {
            evidence = [];
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

    async function loadEvidence() {
        if (!entityName) {
            return;
        }
        isLoading = true;
        error = null;
        try {
            const data = await forwardProxy<EvidenceResponse>(
                'GET',
                `/graph/entity/${encodeURIComponent(entityName)}/evidence?limit=10&include_book_mentions=true`
            );
            evidence = data?.evidence || [];
        } catch (err: any) {
            error = err?.message || String(err);
            evidence = [];
        } finally {
            isLoading = false;
        }
    }

    function getConfidenceClass(confidence: number): string {
        if (confidence >= 0.9) return 'confidence-high';
        if (confidence >= 0.7) return 'confidence-medium';
        return 'confidence-low';
    }

    function getConfidenceLabel(confidence: number, sourceType: string): string {
        if (sourceType === 'chunk') return 'Direct';
        return 'Book';
    }

    function truncateText(text: string, maxLength: number = 200): string {
        if (text.length <= maxLength) return text;
        return text.slice(0, maxLength) + '...';
    }

    // Separate direct evidence from book mentions
    $: directEvidence = evidence.filter(e => e.source_type === 'chunk');
    $: bookMentions = evidence.filter(e => e.source_type === 'book');
</script>

<div class="evidence-section">
    <div class="evidence-header">
        <span class="evidence-icon">📖</span>
        <span class="evidence-title">Evidence</span>
        {#if evidence.length > 0}
            <span class="evidence-count">({evidence.length})</span>
        {/if}
    </div>

    {#if isLoading}
        <div class="evidence-loading">
            <div class="spinner"></div>
        </div>
    {:else if error}
        <div class="evidence-error">{error}</div>
    {:else if evidence.length === 0}
        <div class="evidence-empty">No evidence found</div>
    {:else}
        <div class="evidence-list">
            <!-- Direct evidence (high confidence chunks) -->
            {#each directEvidence as passage (passage.id)}
                <div class="evidence-card">
                    <div class="evidence-card-header">
                        <span class="evidence-source">{passage.source_title}</span>
                        <span class="confidence-badge {getConfidenceClass(passage.confidence)}">
                            {getConfidenceLabel(passage.confidence, passage.source_type)}
                        </span>
                    </div>
                    <blockquote class="evidence-quote">
                        "{truncateText(passage.text)}"
                    </blockquote>
                    {#if passage.location?.chapter || passage.source_author}
                        <div class="evidence-meta">
                            {#if passage.source_author}
                                <span>{passage.source_author}</span>
                            {/if}
                            {#if passage.source_author && passage.location?.chapter}
                                <span class="meta-separator">·</span>
                            {/if}
                            {#if passage.location?.chapter}
                                <span>{passage.location.chapter}</span>
                            {/if}
                        </div>
                    {/if}
                </div>
            {/each}

            <!-- Book mentions (lower confidence) -->
            {#if bookMentions.length > 0}
                <div class="book-mentions">
                    <div class="book-mentions-header">Also mentioned in:</div>
                    <ul class="book-mentions-list">
                        {#each bookMentions as passage (passage.id)}
                            <li class="book-mention-item">
                                <span class="book-icon">📚</span>
                                <span class="book-title">{passage.source_title}</span>
                                {#if passage.source_author}
                                    <span class="book-author">by {passage.source_author}</span>
                                {/if}
                            </li>
                        {/each}
                    </ul>
                </div>
            {/if}
        </div>
    {/if}
</div>

<style>
    .evidence-section {
        margin-top: 16px;
        padding: 12px;
        background: var(--b3-theme-surface);
        border-radius: 8px;
        border: 1px solid var(--b3-border-color);
    }

    .evidence-header {
        display: flex;
        align-items: center;
        gap: 8px;
        margin-bottom: 12px;
        font-weight: 600;
        color: var(--b3-theme-on-surface);
    }

    .evidence-icon {
        font-size: 14px;
    }

    .evidence-title {
        font-size: 14px;
    }

    .evidence-count {
        font-size: 12px;
        color: var(--b3-theme-on-surface-light);
        font-weight: normal;
    }

    .evidence-loading {
        display: flex;
        justify-content: center;
        padding: 24px;
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

    .evidence-error {
        color: var(--b3-theme-error);
        font-size: 12px;
        padding: 8px;
    }

    .evidence-empty {
        color: var(--b3-theme-on-surface-light);
        font-size: 12px;
        text-align: center;
        padding: 16px;
    }

    .evidence-list {
        display: flex;
        flex-direction: column;
        gap: 12px;
    }

    .evidence-card {
        background: var(--b3-theme-background);
        border-radius: 6px;
        padding: 12px;
        border: 1px solid var(--b3-border-color);
    }

    .evidence-card-header {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        gap: 8px;
        margin-bottom: 8px;
    }

    .evidence-source {
        font-size: 12px;
        font-weight: 500;
        color: var(--b3-theme-on-surface-light);
        flex: 1;
    }

    .confidence-badge {
        font-size: 10px;
        padding: 2px 8px;
        border-radius: 10px;
        font-weight: 500;
        white-space: nowrap;
    }

    .confidence-high {
        background: rgba(34, 197, 94, 0.15);
        color: #22c55e;
    }

    .confidence-medium {
        background: rgba(234, 179, 8, 0.15);
        color: #eab308;
    }

    .confidence-low {
        background: var(--b3-theme-surface-lighter);
        color: var(--b3-theme-on-surface-light);
    }

    .evidence-quote {
        margin: 0;
        padding-left: 12px;
        border-left: 2px solid var(--b3-theme-primary-lighter);
        font-style: italic;
        font-size: 13px;
        line-height: 1.5;
        color: var(--b3-theme-on-surface);
    }

    .evidence-meta {
        margin-top: 8px;
        font-size: 11px;
        color: var(--b3-theme-on-surface-light);
        display: flex;
        gap: 4px;
    }

    .meta-separator {
        color: var(--b3-theme-on-surface-light);
    }

    .book-mentions {
        background: var(--b3-theme-background);
        border-radius: 6px;
        padding: 12px;
        border: 1px solid var(--b3-border-color);
    }

    .book-mentions-header {
        font-size: 12px;
        font-weight: 500;
        color: var(--b3-theme-on-surface-light);
        margin-bottom: 8px;
    }

    .book-mentions-list {
        list-style: none;
        margin: 0;
        padding: 0;
        display: flex;
        flex-direction: column;
        gap: 6px;
    }

    .book-mention-item {
        display: flex;
        align-items: center;
        gap: 6px;
        font-size: 12px;
        color: var(--b3-theme-on-surface);
    }

    .book-icon {
        font-size: 12px;
        flex-shrink: 0;
    }

    .book-title {
        flex: 1;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
    }

    .book-author {
        font-size: 11px;
        color: var(--b3-theme-on-surface-light);
        flex-shrink: 0;
    }
</style>
