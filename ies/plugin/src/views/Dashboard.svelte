<script lang="ts">
    /**
     * Dashboard - IES Main View
     *
     * Landing page with graph stats, suggested topics, and mode selection.
     * Routes to Forge (dialogue) or Flow (exploration) modes.
     */
    import { onMount } from 'svelte';
    import { showMessage, fetchSyncPost } from 'siyuan';

    import ForgeMode from './ForgeMode.svelte';
    import FlowMode from './FlowMode.svelte';

    export let plugin: any;

    // Backend configuration
    const BACKEND_HOST = '192.168.86.60';
    const BACKEND_URL = `http://${BACKEND_HOST}:8081`;
    const VERSION = '0.2.0';

    // View state
    type ViewMode = 'dashboard' | 'forge' | 'flow';
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
            const [statsData, suggestionsData] = await Promise.all([
                apiGet('/graph/stats'),
                apiGet('/graph/suggestions')
            ]);

            stats = statsData;
            suggestions = suggestionsData;
        } catch (err) {
            error = err.message;
            console.error('[IES] Dashboard load error:', err);
        } finally {
            isLoading = false;
        }
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
                    <button class="mode-btn mode-btn--forge" on:click={() => navigateTo('forge')}>
                        <span class="mode-icon">
                            <svg viewBox="0 0 24 24" width="24" height="24">
                                <path fill="currentColor" d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-5 14H7v-2h7v2zm3-4H7v-2h10v2zm0-4H7V7h10v2z"/>
                            </svg>
                        </span>
                        <span class="mode-name">Forge</span>
                        <span class="mode-desc">Shape ideas through dialogue</span>
                    </button>
                    <button class="mode-btn mode-btn--flow" on:click={() => navigateTo('flow')}>
                        <span class="mode-icon">
                            <svg viewBox="0 0 24 24" width="24" height="24">
                                <path fill="currentColor" d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8zm-1-13h2v6h-2zm0 8h2v2h-2z"/>
                            </svg>
                        </span>
                        <span class="mode-name">Flow</span>
                        <span class="mode-desc">Explore the knowledge graph</span>
                    </button>
                </div>

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
    {:else if currentView === 'forge'}
        <ForgeMode {plugin} backendUrl={BACKEND_URL} on:back={handleBack} />
    {:else if currentView === 'flow'}
        <FlowMode {plugin} backendUrl={BACKEND_URL} on:back={handleBack} />
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
    .mode-btn--forge:hover {
        border-color: var(--b3-theme-secondary);
    }
    .mode-btn--flow:hover {
        border-color: var(--b3-theme-primary);
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
</style>
