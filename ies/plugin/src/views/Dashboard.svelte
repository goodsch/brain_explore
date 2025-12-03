<script lang="ts">
    /**
     * Dashboard - IES Main View (Layer 3 Processing Hub)
     *
     * Central hub for knowledge exploration with:
     * - Recent explorations (journeys)
     * - Quick Capture queue status
     * - Entry points: Explore Concept, Structured Thinking, Read
     */
    import { onMount } from 'svelte';
    import { showMessage, fetchSyncPost } from 'siyuan';

    import ForgeMode from './ForgeMode.svelte';
    import FlowMode from './FlowMode.svelte';
    import QuickCapture from './QuickCapture.svelte';

    // Backend configuration
    const BACKEND_HOST = '192.168.86.60';
    const BACKEND_URL = `http://${BACKEND_HOST}:8081`;
    const VERSION = '0.3.0';
    const USER_ID = 'chris';

    // View state
    type ViewMode = 'dashboard' | 'structured-thinking' | 'flow' | 'capture';
    let currentView: ViewMode = 'dashboard';

    // Dashboard data
    let stats: {
        entities: number;
        relationships: number;
        books: number;
    } | null = null;

    let suggestions: {
        recent: Array<{name: string, type: string, score: number | null}>;
        connected: Array<{name: string, type: string, score: number | null}>;
        new: Array<{name: string, type: string, score: number | null}>;
    } | null = null;

    // Journey/exploration data
    let recentJourneys: Array<{
        id: string;
        title: string;
        started_at: string;
        status: string;
        breadcrumb_count: number;
    }> = [];

    // Quick Capture queue
    let captureQueue: Array<{
        id: string;
        content_preview: string;
        captured_at: string;
        status: string;
    }> = [];

    let isLoading = true;
    let error: string | null = null;

    // API helper
    async function apiGet(endpoint: string): Promise<any> {
        const url = `${BACKEND_URL}${endpoint}`;

        const response = await fetchSyncPost('/api/network/forwardProxy', {
            url: url,
            method: 'GET',
            timeout: 30000,
            contentType: 'application/json',
            headers: []
        });

        if (response.code !== 0) {
            throw new Error(`Proxy error: ${response.msg}`);
        }

        const proxyData = response.data;
        if (!proxyData || proxyData.status !== 200) {
            throw new Error(`Backend error: ${proxyData?.status || 'unknown'}`);
        }

        return typeof proxyData.body === 'string' ? JSON.parse(proxyData.body) : proxyData.body;
    }

    async function loadDashboardData() {
        isLoading = true;
        error = null;

        try {
            // Load all data in parallel
            const [statsData, suggestionsData, journeysData] = await Promise.all([
                apiGet('/graph/stats'),
                apiGet('/graph/suggestions'),
                apiGet(`/journeys/user/${USER_ID}`).catch(() => ({ journeys: [] }))
            ]);

            stats = statsData;
            suggestions = suggestionsData;
            recentJourneys = journeysData.journeys || [];

            // Quick Capture queue would come from a future endpoint
            // For now, show empty queue
            captureQueue = [];
        } catch (err) {
            error = err.message;
            console.error('[IES] Dashboard load error:', err);
        } finally {
            isLoading = false;
        }
    }

    function formatRelativeTime(isoDate: string): string {
        const date = new Date(isoDate);
        const now = new Date();
        const diffMs = now.getTime() - date.getTime();
        const diffMins = Math.floor(diffMs / 60000);
        const diffHours = Math.floor(diffMins / 60);
        const diffDays = Math.floor(diffHours / 24);

        if (diffMins < 1) return 'just now';
        if (diffMins < 60) return `${diffMins}m ago`;
        if (diffHours < 24) return `${diffHours}h ago`;
        if (diffDays < 7) return `${diffDays}d ago`;
        return date.toLocaleDateString();
    }

    onMount(() => {
        loadDashboardData();
    });

    function navigateTo(view: ViewMode) {
        currentView = view;
    }

    function handleBack() {
        currentView = 'dashboard';
        // Refresh stats when returning to dashboard
        loadDashboardData();
    }

    function resumeJourney(journeyId: string) {
        // Navigate to Flow mode with the journey context
        // TODO: Pass journey ID to FlowMode for resumption
        navigateTo('flow');
    }

    function formatNumber(n: number): string {
        if (n >= 1000) {
            return (n / 1000).toFixed(1) + 'k';
        }
        return n.toString();
    }
</script>

<div class="ies-container">
    {#if currentView === 'dashboard'}
        <div class="dashboard">
            <div class="dashboard-header">
                <span class="dashboard-title">IES Explorer</span>
                <span class="dashboard-version">v{VERSION}</span>
            </div>

            {#if isLoading}
                <div class="dashboard-loading">Loading...</div>
            {:else if error}
                <div class="dashboard-error">
                    <p>{error}</p>
                    <button class="b3-button" on:click={loadDashboardData}>Retry</button>
                </div>
            {:else}
                <!-- Stats -->
                {#if stats}
                    <div class="dashboard-stats">
                        <div class="stat">
                            <span class="stat-value">{formatNumber(stats.entities)}</span>
                            <span class="stat-label">Entities</span>
                        </div>
                        <div class="stat">
                            <span class="stat-value">{formatNumber(stats.relationships)}</span>
                            <span class="stat-label">Relationships</span>
                        </div>
                        <div class="stat">
                            <span class="stat-value">{stats.books}</span>
                            <span class="stat-label">Books</span>
                        </div>
                    </div>
                {/if}

                <!-- Mode Buttons -->
                <div class="dashboard-modes">
                    <button class="mode-btn mode-btn--thinking" on:click={() => navigateTo('structured-thinking')}>
                        <span class="mode-icon">
                            <svg viewBox="0 0 24 24" width="24" height="24">
                                <path fill="currentColor" d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-5 14H7v-2h7v2zm3-4H7v-2h10v2zm0-4H7V7h10v2z"/>
                            </svg>
                        </span>
                        <span class="mode-name">Think</span>
                        <span class="mode-desc">Structured thinking modes</span>
                    </button>
                    <button class="mode-btn mode-btn--flow" on:click={() => navigateTo('flow')}>
                        <span class="mode-icon">
                            <svg viewBox="0 0 24 24" width="24" height="24">
                                <path fill="currentColor" d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8z"/>
                            </svg>
                        </span>
                        <span class="mode-name">Explore</span>
                        <span class="mode-desc">Navigate the knowledge graph</span>
                    </button>
                    <button class="mode-btn mode-btn--capture" on:click={() => navigateTo('capture')}>
                        <span class="mode-icon">
                            <svg viewBox="0 0 24 24" width="24" height="24">
                                <path fill="currentColor" d="M19 13h-6v6h-2v-6H5v-2h6V5h2v6h6v2z"/>
                            </svg>
                        </span>
                        <span class="mode-name">Capture</span>
                        <span class="mode-desc">Quick thought capture</span>
                    </button>
                </div>

                <!-- Recent Journeys -->
                {#if recentJourneys.length > 0}
                    <div class="dashboard-section">
                        <span class="section-label">Recent Explorations</span>
                        <div class="journey-list">
                            {#each recentJourneys.slice(0, 3) as journey}
                                <button class="journey-item" on:click={() => resumeJourney(journey.id)}>
                                    <span class="journey-title">{journey.title}</span>
                                    <span class="journey-meta">
                                        <span class="journey-crumbs">{journey.breadcrumb_count} steps</span>
                                        <span class="journey-time">{formatRelativeTime(journey.started_at)}</span>
                                    </span>
                                </button>
                            {/each}
                        </div>
                    </div>
                {/if}

                <!-- Quick Capture Queue -->
                {#if captureQueue.length > 0}
                    <div class="dashboard-section">
                        <span class="section-label">
                            Capture Queue
                            <span class="queue-badge">{captureQueue.length}</span>
                        </span>
                        <div class="capture-queue">
                            {#each captureQueue.slice(0, 3) as item}
                                <div class="capture-item">
                                    <span class="capture-preview">{item.content_preview}</span>
                                    <span class="capture-time">{formatRelativeTime(item.captured_at)}</span>
                                </div>
                            {/each}
                        </div>
                    </div>
                {/if}

                <!-- Suggestions -->
                {#if suggestions}
                    <div class="dashboard-suggestions">
                        {#if suggestions.connected.length > 0}
                            <div class="suggestion-group">
                                <span class="suggestion-label">Most Connected</span>
                                <div class="suggestion-items">
                                    {#each suggestions.connected.slice(0, 4) as topic}
                                        <button
                                            class="suggestion-chip"
                                            on:click={() => { navigateTo('flow'); }}
                                            title="Explore in Flow"
                                        >
                                            {topic.name}
                                        </button>
                                    {/each}
                                </div>
                            </div>
                        {/if}

                        {#if suggestions.new.length > 0}
                            <div class="suggestion-group">
                                <span class="suggestion-label">Novel Concepts</span>
                                <div class="suggestion-items">
                                    {#each suggestions.new as topic}
                                        <button
                                            class="suggestion-chip suggestion-chip--new"
                                            on:click={() => { navigateTo('flow'); }}
                                            title="Phase 1 concept - explore in Flow"
                                        >
                                            {topic.name}
                                        </button>
                                    {/each}
                                </div>
                            </div>
                        {/if}
                    </div>
                {/if}
            {/if}
        </div>
    {:else if currentView === 'structured-thinking'}
        <ForgeMode backendUrl={BACKEND_URL} on:back={handleBack} />
    {:else if currentView === 'flow'}
        <FlowMode backendUrl={BACKEND_URL} on:back={handleBack} />
    {:else if currentView === 'capture'}
        <QuickCapture backendUrl={BACKEND_URL} on:back={handleBack} />
    {/if}
</div>

<style>
    .ies-container {
        height: 100%;
        display: flex;
        flex-direction: column;
    }
    .dashboard {
        display: flex;
        flex-direction: column;
        height: 100%;
        padding: 12px;
        gap: 16px;
    }
    .dashboard-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .dashboard-title {
        font-weight: 600;
        font-size: 16px;
    }
    .dashboard-version {
        font-size: 10px;
        padding: 2px 6px;
        background: var(--b3-theme-surface);
        color: var(--b3-theme-on-surface-light);
        border-radius: 3px;
        border: 1px solid var(--b3-border-color);
        font-family: monospace;
    }
    .dashboard-loading {
        flex: 1;
        display: flex;
        align-items: center;
        justify-content: center;
        color: var(--b3-theme-on-surface-light);
    }
    .dashboard-error {
        flex: 1;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        gap: 12px;
        color: var(--b3-theme-error);
    }
    .dashboard-stats {
        display: flex;
        justify-content: space-around;
        padding: 12px;
        background: var(--b3-theme-surface);
        border-radius: 8px;
    }
    .stat {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 4px;
    }
    .stat-value {
        font-size: 20px;
        font-weight: 600;
        color: var(--b3-theme-primary);
    }
    .stat-label {
        font-size: 11px;
        color: var(--b3-theme-on-surface-light);
        text-transform: uppercase;
    }
    .dashboard-modes {
        display: flex;
        gap: 12px;
    }
    .mode-btn {
        flex: 1;
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 8px;
        padding: 16px 12px;
        background: var(--b3-theme-surface);
        border: 2px solid var(--b3-border-color);
        border-radius: 12px;
        cursor: pointer;
        transition: all 0.15s;
    }
    .mode-btn:hover {
        border-color: var(--b3-theme-primary);
        background: var(--b3-theme-primary-lightest);
    }
    .mode-btn--thinking:hover {
        border-color: var(--b3-theme-secondary);
    }
    .mode-btn--flow:hover {
        border-color: var(--b3-theme-primary);
    }
    .mode-btn--capture:hover {
        border-color: #10b981;
    }
    .mode-icon {
        color: var(--b3-theme-on-surface);
    }
    .mode-name {
        font-weight: 600;
        font-size: 14px;
    }
    .mode-desc {
        font-size: 11px;
        color: var(--b3-theme-on-surface-light);
        text-align: center;
    }
    .dashboard-suggestions {
        display: flex;
        flex-direction: column;
        gap: 12px;
    }
    .suggestion-group {
        display: flex;
        flex-direction: column;
        gap: 8px;
    }
    .suggestion-label {
        font-size: 11px;
        font-weight: 600;
        text-transform: uppercase;
        color: var(--b3-theme-on-surface-light);
    }
    .suggestion-items {
        display: flex;
        flex-wrap: wrap;
        gap: 6px;
    }
    .suggestion-chip {
        padding: 4px 10px;
        font-size: 12px;
        background: var(--b3-theme-surface);
        border: 1px solid var(--b3-border-color);
        border-radius: 12px;
        cursor: pointer;
        transition: all 0.15s;
        color: var(--b3-theme-on-surface);
    }
    .suggestion-chip:hover {
        background: var(--b3-theme-primary-lightest);
        border-color: var(--b3-theme-primary);
    }
    .suggestion-chip--new {
        background: var(--b3-theme-primary-lightest);
        border-color: var(--b3-theme-primary-light);
    }

    /* Dashboard sections */
    .dashboard-section {
        display: flex;
        flex-direction: column;
        gap: 8px;
    }
    .section-label {
        font-size: 11px;
        font-weight: 600;
        text-transform: uppercase;
        color: var(--b3-theme-on-surface-light);
        display: flex;
        align-items: center;
        gap: 6px;
    }

    /* Journey list */
    .journey-list {
        display: flex;
        flex-direction: column;
        gap: 4px;
    }
    .journey-item {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 8px 12px;
        background: var(--b3-theme-surface);
        border: 1px solid var(--b3-border-color);
        border-radius: 6px;
        cursor: pointer;
        transition: all 0.15s;
        text-align: left;
    }
    .journey-item:hover {
        border-color: var(--b3-theme-primary);
        background: var(--b3-theme-primary-lightest);
    }
    .journey-title {
        font-size: 13px;
        font-weight: 500;
        color: var(--b3-theme-on-surface);
    }
    .journey-meta {
        display: flex;
        gap: 8px;
        font-size: 11px;
        color: var(--b3-theme-on-surface-light);
    }
    .journey-crumbs {
        opacity: 0.7;
    }
    .journey-time {
        opacity: 0.7;
    }

    /* Capture queue */
    .queue-badge {
        background: #10b981;
        color: white;
        font-size: 10px;
        padding: 1px 6px;
        border-radius: 10px;
        font-weight: 600;
    }
    .capture-queue {
        display: flex;
        flex-direction: column;
        gap: 4px;
    }
    .capture-item {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 8px 12px;
        background: var(--b3-theme-surface);
        border: 1px solid var(--b3-border-color);
        border-radius: 6px;
    }
    .capture-preview {
        font-size: 12px;
        color: var(--b3-theme-on-surface);
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
        max-width: 200px;
    }
    .capture-time {
        font-size: 11px;
        color: var(--b3-theme-on-surface-light);
    }

</style>
