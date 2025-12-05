<script lang="ts">
    /**
     * Dashboard - IES Main View (Layer 3 Processing Hub)
     *
     * Central hub for knowledge exploration with:
     * - Recent explorations (journeys)
     * - Quick Capture queue status
     * - Entry points: Explore Concept, Structured Thinking, Capture
     */
    import { onMount } from 'svelte';
    import { showMessage, fetchSyncPost } from 'siyuan';

    import ForgeMode from './ForgeMode.svelte';
    import FlowMode from './FlowMode.svelte';
    import QuickCapture from './QuickCapture.svelte';

    // Backend configuration
    const BACKEND_HOST = '192.168.86.60';
    const BACKEND_URL = `http://${BACKEND_HOST}:8081`;
    const VERSION = '0.3.1';
    const USER_ID = 'chris';

    // View state
    type ViewMode = 'dashboard' | 'structured-thinking' | 'flow' | 'capture';
    let currentView: ViewMode = 'dashboard';
    let selectedJourneyId: string | null = null;

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
        title: string | null;
        started_at: string;
        ended_at: string | null;
        path: Array<{entity_name: string}>;
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
    let mounted = false;

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
            const [statsData, suggestionsData, journeysData] = await Promise.all([
                apiGet('/graph/stats'),
                apiGet('/graph/suggestions'),
                apiGet(`/journeys/user/${USER_ID}`).catch(() => ({ journeys: [] }))
            ]);

            stats = statsData;
            suggestions = suggestionsData;
            recentJourneys = journeysData.journeys || [];
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
        mounted = true;
        loadDashboardData();
    });

    function navigateTo(view: ViewMode) {
        if (view === 'flow') {
            selectedJourneyId = null;
        }
        currentView = view;
    }

    function handleBack() {
        currentView = 'dashboard';
        selectedJourneyId = null;
        loadDashboardData();
    }

    function resumeJourney(journeyId: string) {
        selectedJourneyId = journeyId;
        currentView = 'flow';
    }

    function formatNumber(n: number): string {
        if (n >= 1000) {
            return (n / 1000).toFixed(1) + 'k';
        }
        return n.toString();
    }
</script>

<div class="ies-root">
    {#if currentView === 'dashboard'}
        <div class="dashboard" class:mounted>
            <!-- Header -->
            <header class="header">
                <div class="header-brand">
                    <div class="logo">
                        <svg viewBox="0 0 24 24" width="20" height="20">
                            <circle cx="12" cy="12" r="3" fill="currentColor" opacity="0.9"/>
                            <circle cx="12" cy="12" r="7" fill="none" stroke="currentColor" stroke-width="1.5" opacity="0.5"/>
                            <circle cx="12" cy="12" r="10.5" fill="none" stroke="currentColor" stroke-width="1" opacity="0.25"/>
                        </svg>
                    </div>
                    <div class="brand-text">
                        <span class="brand-name">IES Explorer</span>
                        <span class="brand-version">v{VERSION}</span>
                    </div>
                </div>
            </header>

            {#if isLoading}
                <div class="loading-state">
                    <div class="loading-spinner"></div>
                    <span>Loading knowledge graph...</span>
                </div>
            {:else if error}
                <div class="error-state">
                    <svg viewBox="0 0 24 24" width="32" height="32">
                        <circle cx="12" cy="12" r="10" fill="none" stroke="currentColor" stroke-width="1.5"/>
                        <path d="M12 8v4M12 16h.01" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                    </svg>
                    <p>{error}</p>
                    <button class="btn btn--primary" on:click={loadDashboardData}>
                        Try Again
                    </button>
                </div>
            {:else}
                <!-- Stats Bar -->
                {#if stats}
                    <div class="stats-bar">
                        <div class="stat">
                            <span class="stat-value">{formatNumber(stats.entities)}</span>
                            <span class="stat-label">Entities</span>
                        </div>
                        <div class="stat-divider"></div>
                        <div class="stat">
                            <span class="stat-value">{formatNumber(stats.relationships)}</span>
                            <span class="stat-label">Relations</span>
                        </div>
                        <div class="stat-divider"></div>
                        <div class="stat">
                            <span class="stat-value">{stats.books}</span>
                            <span class="stat-label">Sources</span>
                        </div>
                    </div>
                {/if}

                <!-- Mode Cards -->
                <div class="mode-grid">
                    <button class="mode-card mode-card--think" on:click={() => navigateTo('structured-thinking')}>
                        <div class="mode-glow"></div>
                        <div class="mode-icon">
                            <svg viewBox="0 0 24 24" width="28" height="28">
                                <path fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"
                                    d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707"/>
                                <circle cx="12" cy="12" r="4" fill="none" stroke="currentColor" stroke-width="1.5"/>
                            </svg>
                        </div>
                        <span class="mode-title">Think</span>
                        <span class="mode-subtitle">Structured dialogue</span>
                    </button>

                    <button class="mode-card mode-card--explore" on:click={() => navigateTo('flow')}>
                        <div class="mode-glow"></div>
                        <div class="mode-icon">
                            <svg viewBox="0 0 24 24" width="28" height="28">
                                <circle cx="12" cy="12" r="2" fill="currentColor"/>
                                <circle cx="6" cy="8" r="1.5" fill="currentColor" opacity="0.6"/>
                                <circle cx="18" cy="8" r="1.5" fill="currentColor" opacity="0.6"/>
                                <circle cx="6" cy="16" r="1.5" fill="currentColor" opacity="0.6"/>
                                <circle cx="18" cy="16" r="1.5" fill="currentColor" opacity="0.6"/>
                                <path fill="none" stroke="currentColor" stroke-width="1" opacity="0.4"
                                    d="M12 12L6 8M12 12L18 8M12 12L6 16M12 12L18 16"/>
                            </svg>
                        </div>
                        <span class="mode-title">Explore</span>
                        <span class="mode-subtitle">Navigate concepts</span>
                    </button>

                    <button class="mode-card mode-card--capture" on:click={() => navigateTo('capture')}>
                        <div class="mode-glow"></div>
                        <div class="mode-icon">
                            <svg viewBox="0 0 24 24" width="28" height="28">
                                <path fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"
                                    d="M12 5v14M5 12h14"/>
                                <circle cx="12" cy="12" r="9" fill="none" stroke="currentColor" stroke-width="1" opacity="0.3"/>
                            </svg>
                        </div>
                        <span class="mode-title">Capture</span>
                        <span class="mode-subtitle">Quick thoughts</span>
                    </button>
                </div>

                <!-- Recent Journeys -->
                {#if recentJourneys.length > 0}
                    <section class="section">
                        <h3 class="section-title">Recent Explorations</h3>
                        <div class="journey-list">
                            {#each recentJourneys.slice(0, 3) as journey, i}
                                <button
                                    class="journey-card"
                                    style="animation-delay: {i * 60}ms"
                                    on:click={() => resumeJourney(journey.id)}
                                >
                                    <div class="journey-indicator"></div>
                                    <div class="journey-content">
                                        <span class="journey-title">
                                            {journey.title || journey.path[0]?.entity_name || 'Untitled'}
                                        </span>
                                        <span class="journey-meta">
                                            {journey.path.length} steps · {formatRelativeTime(journey.started_at)}
                                        </span>
                                    </div>
                                    <svg class="journey-arrow" viewBox="0 0 24 24" width="16" height="16">
                                        <path fill="currentColor" d="M8.59 16.59L13.17 12 8.59 7.41 10 6l6 6-6 6-1.41-1.41z"/>
                                    </svg>
                                </button>
                            {/each}
                        </div>
                    </section>
                {/if}

                <!-- Capture Queue -->
                {#if captureQueue.length > 0}
                    <section class="section">
                        <h3 class="section-title">
                            Capture Queue
                            <span class="queue-badge">{captureQueue.length}</span>
                        </h3>
                        <div class="capture-list">
                            {#each captureQueue.slice(0, 3) as item}
                                <div class="capture-card">
                                    <span class="capture-preview">{item.content_preview}</span>
                                    <span class="capture-time">{formatRelativeTime(item.captured_at)}</span>
                                </div>
                            {/each}
                        </div>
                    </section>
                {/if}

                <!-- Concept Suggestions -->
                {#if suggestions && (suggestions.connected.length > 0 || suggestions.new.length > 0)}
                    <section class="section suggestions-section">
                        {#if suggestions.connected.length > 0}
                            <div class="suggestion-group">
                                <h4 class="suggestion-label">Most Connected</h4>
                                <div class="chip-grid">
                                    {#each suggestions.connected.slice(0, 4) as topic}
                                        <button class="chip" on:click={() => navigateTo('flow')}>
                                            {topic.name}
                                        </button>
                                    {/each}
                                </div>
                            </div>
                        {/if}

                        {#if suggestions.new.length > 0}
                            <div class="suggestion-group">
                                <h4 class="suggestion-label">Novel Concepts</h4>
                                <div class="chip-grid">
                                    {#each suggestions.new as topic}
                                        <button class="chip chip--accent" on:click={() => navigateTo('flow')}>
                                            <span class="chip-dot"></span>
                                            {topic.name}
                                        </button>
                                    {/each}
                                </div>
                            </div>
                        {/if}
                    </section>
                {/if}
            {/if}
        </div>
    {:else if currentView === 'structured-thinking'}
        <ForgeMode backendUrl={BACKEND_URL} on:back={handleBack} />
    {:else if currentView === 'flow'}
        <FlowMode backendUrl={BACKEND_URL} journeyId={selectedJourneyId} on:back={handleBack} />
    {:else if currentView === 'capture'}
        <QuickCapture backendUrl={BACKEND_URL} on:back={handleBack} />
    {/if}
</div>

<style>
    /**
     * Dashboard Styles
     * Uses unified IES Design System tokens from design-system/tokens/
     * All --ies-* variables are defined in the unified design system
     */

    .ies-root {
        height: 100%;
        font-family: var(--ies-font-body);
        font-size: var(--ies-text-base);
        line-height: var(--ies-leading-body);
        color: var(--ies-text-primary);
        background: var(--ies-bg-deep);
        -webkit-font-smoothing: antialiased;
        -moz-osx-font-smoothing: grayscale;
    }

    /* Dashboard Layout */
    .dashboard {
        display: flex;
        flex-direction: column;
        height: 100%;
        padding: var(--ies-space-4);
        gap: var(--ies-space-5);
        overflow-y: auto;
        opacity: 0;
        transform: translateY(4px);
        transition: opacity var(--ies-duration-base) var(--ies-ease-cupertino),
                    transform var(--ies-duration-base) var(--ies-ease-cupertino);
    }

    .dashboard.mounted {
        opacity: 1;
        transform: translateY(0);
    }

    /* Header */
    .header {
        display: flex;
        align-items: center;
        justify-content: space-between;
    }

    .header-brand {
        display: flex;
        align-items: center;
        gap: var(--ies-space-3);
    }

    .logo {
        width: 36px;
        height: 36px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: var(--ies-accent);
        background: var(--ies-accent-subtle);
        border-radius: var(--ies-radius-md);
    }

    .brand-text {
        display: flex;
        flex-direction: column;
        gap: 1px;
    }

    .brand-name {
        font-family: var(--ies-font-display);
        font-size: var(--ies-text-lg);
        font-weight: var(--ies-font-semibold);
        letter-spacing: var(--ies-tracking-tight);
        color: var(--ies-text-primary);
    }

    .brand-version {
        font-family: var(--ies-font-mono);
        font-size: var(--ies-text-xs);
        color: var(--ies-text-muted);
        letter-spacing: var(--ies-tracking-wide);
    }

    /* Loading & Error States */
    .loading-state, .error-state {
        flex: 1;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        gap: var(--ies-space-4);
        color: var(--ies-text-muted);
        text-align: center;
        padding: var(--ies-space-6);
    }

    .loading-spinner {
        width: 32px;
        height: 32px;
        border: 2px solid var(--ies-border-light);
        border-top-color: var(--ies-accent);
        border-radius: 50%;
        animation: ies-spin 0.8s linear infinite;
    }

    .error-state svg {
        color: var(--ies-text-muted);
    }

    /* Stats Bar */
    .stats-bar {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: var(--ies-space-4);
        padding: var(--ies-space-4) var(--ies-space-5);
        background: var(--ies-bg-elevated);
        border: 1px solid var(--ies-border-subtle);
        border-radius: var(--ies-radius-md);
        box-shadow: var(--ies-shadow-sm);
    }

    .stat {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 2px;
        padding: 0 var(--ies-space-3);
    }

    .stat-value {
        font-family: var(--ies-font-display);
        font-size: var(--ies-text-2xl);
        font-weight: var(--ies-font-semibold);
        color: var(--ies-accent);
        letter-spacing: var(--ies-tracking-tight);
    }

    .stat-label {
        font-size: var(--ies-text-xs);
        font-weight: var(--ies-font-semibold);
        text-transform: uppercase;
        letter-spacing: var(--ies-tracking-wider);
        color: var(--ies-text-muted);
    }

    .stat-divider {
        width: 1px;
        height: 28px;
        background: var(--ies-border-light);
    }

    /* Mode Cards */
    .mode-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: var(--ies-space-3);
    }

    .mode-card {
        position: relative;
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: var(--ies-space-2);
        padding: var(--ies-space-5) var(--ies-space-3);
        background: var(--ies-bg-elevated);
        border: 1px solid var(--ies-border-subtle);
        border-radius: var(--ies-radius-md);
        cursor: pointer;
        transition: var(--ies-transition-all);
        overflow: hidden;
    }

    .mode-card:hover {
        transform: translateY(-2px);
        box-shadow: var(--ies-shadow-md);
        border-color: var(--ies-border-light);
    }

    .mode-card:active {
        transform: translateY(0);
    }

    .mode-glow {
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle at center, var(--ies-accent-subtle) 0%, transparent 70%);
        opacity: 0;
        transition: opacity var(--ies-duration-base) var(--ies-ease-cupertino);
        pointer-events: none;
    }

    .mode-card:hover .mode-glow {
        opacity: 0.5;
    }

    .mode-card--think:hover { border-color: var(--ies-accent); }
    .mode-card--think:hover .mode-glow { background: radial-gradient(circle at center, var(--ies-accent-subtle) 0%, transparent 70%); }

    .mode-card--explore:hover { border-color: var(--ies-secondary); }
    .mode-card--explore:hover .mode-glow { background: radial-gradient(circle at center, var(--ies-secondary-subtle) 0%, transparent 70%); }

    .mode-card--capture:hover { border-color: var(--ies-tertiary); }
    .mode-card--capture:hover .mode-glow { background: radial-gradient(circle at center, var(--ies-tertiary-subtle) 0%, transparent 70%); }

    .mode-icon {
        position: relative;
        z-index: 1;
        color: var(--ies-text-secondary);
        transition: color var(--ies-duration-fast) var(--ies-ease-cupertino);
    }

    .mode-card--think:hover .mode-icon { color: var(--ies-accent); }
    .mode-card--explore:hover .mode-icon { color: var(--ies-secondary); }
    .mode-card--capture:hover .mode-icon { color: var(--ies-tertiary); }

    .mode-title {
        position: relative;
        z-index: 1;
        font-family: var(--ies-font-display);
        font-size: var(--ies-text-base);
        font-weight: var(--ies-font-semibold);
        color: var(--ies-text-primary);
    }

    .mode-subtitle {
        position: relative;
        z-index: 1;
        font-size: var(--ies-text-xs);
        color: var(--ies-text-muted);
    }

    /* Sections */
    .section {
        display: flex;
        flex-direction: column;
        gap: var(--ies-space-3);
    }

    .section-title {
        font-family: var(--ies-font-display);
        font-size: var(--ies-text-sm);
        font-weight: var(--ies-font-semibold);
        color: var(--ies-text-muted);
        text-transform: uppercase;
        letter-spacing: var(--ies-tracking-wider);
        margin: 0;
        display: flex;
        align-items: center;
        gap: var(--ies-space-2);
    }

    .queue-badge {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        min-width: 18px;
        height: 18px;
        padding: 0 6px;
        font-size: var(--ies-text-xs);
        font-weight: var(--ies-font-bold);
        color: var(--ies-text-inverse);
        background: var(--ies-secondary);
        border-radius: var(--ies-radius-full);
    }

    /* Journey Cards */
    .journey-list {
        display: flex;
        flex-direction: column;
        gap: var(--ies-space-2);
    }

    .journey-card {
        display: flex;
        align-items: center;
        gap: var(--ies-space-3);
        padding: var(--ies-space-3) var(--ies-space-4);
        background: var(--ies-bg-elevated);
        border: 1px solid var(--ies-border-subtle);
        border-radius: var(--ies-radius-sm);
        cursor: pointer;
        transition: var(--ies-transition-fast);
        text-align: left;
        animation: ies-slide-up var(--ies-duration-base) var(--ies-ease-cupertino) backwards;
    }

    .journey-card:hover {
        border-color: var(--ies-accent);
        box-shadow: var(--ies-shadow-sm);
    }

    .journey-indicator {
        width: 3px;
        height: 24px;
        background: var(--ies-accent);
        border-radius: 2px;
        opacity: 0.6;
        transition: opacity var(--ies-duration-fast) var(--ies-ease-cupertino);
    }

    .journey-card:hover .journey-indicator {
        opacity: 1;
    }

    .journey-content {
        flex: 1;
        display: flex;
        flex-direction: column;
        gap: 2px;
        min-width: 0;
    }

    .journey-title {
        font-weight: var(--ies-font-medium);
        color: var(--ies-text-primary);
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }

    .journey-meta {
        font-size: var(--ies-text-sm);
        color: var(--ies-text-muted);
    }

    .journey-arrow {
        color: var(--ies-text-subtle);
        opacity: 0;
        transform: translateX(-4px);
        transition: var(--ies-transition-fast);
    }

    .journey-card:hover .journey-arrow {
        opacity: 1;
        transform: translateX(0);
    }

    /* Capture Cards */
    .capture-list {
        display: flex;
        flex-direction: column;
        gap: var(--ies-space-2);
    }

    .capture-card {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: var(--ies-space-3) var(--ies-space-4);
        background: var(--ies-bg-elevated);
        border: 1px solid var(--ies-border-subtle);
        border-radius: var(--ies-radius-sm);
    }

    .capture-preview {
        font-size: var(--ies-text-sm);
        color: var(--ies-text-secondary);
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        max-width: 180px;
    }

    .capture-time {
        font-size: var(--ies-text-xs);
        color: var(--ies-text-muted);
    }

    /* Suggestions */
    .suggestions-section {
        padding-top: var(--ies-space-2);
        border-top: 1px solid var(--ies-border-subtle);
    }

    .suggestion-group {
        display: flex;
        flex-direction: column;
        gap: var(--ies-space-2);
    }

    .suggestion-label {
        font-size: var(--ies-text-xs);
        font-weight: var(--ies-font-semibold);
        text-transform: uppercase;
        letter-spacing: var(--ies-tracking-wider);
        color: var(--ies-text-muted);
        margin: 0;
    }

    .chip-grid {
        display: flex;
        flex-wrap: wrap;
        gap: var(--ies-space-2);
    }

    .chip {
        display: inline-flex;
        align-items: center;
        gap: var(--ies-space-1);
        padding: var(--ies-chip-padding-y) var(--ies-chip-padding-x);
        font-size: var(--ies-text-sm);
        font-weight: var(--ies-font-medium);
        color: var(--ies-text-secondary);
        background: var(--ies-bg-base);
        border: 1px solid var(--ies-border-light);
        border-radius: var(--ies-radius-chip);
        cursor: pointer;
        transition: var(--ies-transition-fast);
    }

    .chip:hover {
        background: var(--ies-accent-subtle);
        border-color: var(--ies-accent-muted);
        color: var(--ies-accent);
        transform: translateY(-1px);
    }

    .chip--accent {
        background: var(--ies-accent-subtle);
        border-color: var(--ies-accent-muted);
        color: var(--ies-accent);
    }

    .chip-dot {
        width: 5px;
        height: 5px;
        background: var(--ies-accent);
        border-radius: 50%;
    }

    /* Button */
    .btn {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        gap: var(--ies-space-2);
        padding: var(--ies-button-padding-y) var(--ies-button-padding-x);
        font-family: var(--ies-font-body);
        font-size: var(--ies-text-sm);
        font-weight: var(--ies-font-semibold);
        color: var(--ies-text-primary);
        background: var(--ies-bg-elevated);
        border: 1px solid var(--ies-border-medium);
        border-radius: var(--ies-radius-button);
        cursor: pointer;
        transition: var(--ies-transition-fast);
        box-shadow: var(--ies-shadow-button);
    }

    .btn:hover {
        box-shadow: var(--ies-shadow-button-hover);
    }

    .btn:active {
        transform: scale(0.98);
    }

    .btn--primary {
        background: var(--ies-accent);
        border-color: var(--ies-accent);
        color: var(--ies-text-inverse);
    }

    .btn--primary:hover {
        background: var(--ies-accent-hover);
        border-color: var(--ies-accent-hover);
    }
</style>
