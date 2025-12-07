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
    import Inbox from './Inbox.svelte';

    // Backend configuration
    const BACKEND_HOST = '192.168.86.60';
    const BACKEND_URL = `http://${BACKEND_HOST}:8081`;
    const VERSION = '0.3.1';
    const USER_ID = 'chris';

    // View state
    type ViewMode = 'dashboard' | 'structured-thinking' | 'flow' | 'inbox';
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

    // Inbox queue
    let inboxQueue: Array<{
        id: string;
        text: string;
        source: string;
        captured_at: string;
        status: string;
    }> = [];

    // Source icon mapping
    function getSourceIcon(source: string): string {
        switch (source) {
            case 'ios_shortcut': return '📱';
            case 'browser': return '🌐';
            case 'voice': return '🎤';
            case 'siyuan': return '📝';
            case 'ies_reader': return '📖';
            case 'email': return '✉️';
            case 'phone': return '📱';  // Legacy
            default: return '📥';
        }
    }

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
            const [statsData, suggestionsData, journeysData, inboxData] = await Promise.all([
                apiGet('/graph/stats'),
                apiGet('/graph/suggestions'),
                apiGet(`/journeys/user/${USER_ID}`).catch(() => ({ journeys: [] })),
                apiGet('/inbox?status=queued').catch(() => ({ items: [] }))
            ]);

            stats = statsData;
            suggestions = suggestionsData;
            recentJourneys = journeysData.journeys || [];
            inboxQueue = inboxData.items || [];
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

                    <button class="mode-card mode-card--inbox" on:click={() => navigateTo('inbox')}>
                        <div class="mode-glow"></div>
                        <div class="mode-icon">
                            <svg viewBox="0 0 24 24" width="28" height="28">
                                <path fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"
                                    d="M12 5v14M5 12h14"/>
                                <circle cx="12" cy="12" r="9" fill="none" stroke="currentColor" stroke-width="1" opacity="0.3"/>
                            </svg>
                        </div>
                        <span class="mode-title">Inbox</span>
                        <span class="mode-subtitle">Process captures</span>
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

                <!-- Inbox Queue -->
                {#if inboxQueue.length > 0}
                    <section class="section">
                        <h3 class="section-title">
                            Inbox
                            <span class="queue-badge">{inboxQueue.length}</span>
                        </h3>
                        <div class="inbox-list">
                            {#each inboxQueue.slice(0, 3) as item}
                                <div class="inbox-card" on:click={() => navigateTo('inbox')}>
                                    <span class="inbox-source" title={item.source}>{getSourceIcon(item.source)}</span>
                                    <span class="inbox-preview">{item.text.slice(0, 80)}{item.text.length > 80 ? '...' : ''}</span>
                                    <span class="inbox-time">{formatRelativeTime(item.captured_at)}</span>
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
    {:else if currentView === 'inbox'}
        <Inbox backendUrl={BACKEND_URL} on:back={handleBack} />
    {/if}
</div>

<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Crimson+Pro:wght@400;500;600;700&family=Nunito:wght@400;500;600;700&display=swap');

    /* Design tokens */
    .ies-root {
        --font-display: 'Crimson Pro', Georgia, serif;
        --font-body: 'Nunito', system-ui, sans-serif;
        --font-mono: 'JetBrains Mono', monospace;

        --space-1: 0.25rem;
        --space-2: 0.5rem;
        --space-3: 0.75rem;
        --space-4: 1rem;
        --space-5: 1.25rem;
        --space-6: 1.5rem;

        --radius-sm: 8px;
        --radius-md: 12px;
        --radius-lg: 16px;
        --radius-full: 9999px;

        /* Light theme (default) */
        --bg-deep: #f7f5f2;
        --bg-base: #fffefa;
        --bg-elevated: #ffffff;
        --bg-overlay: rgba(255, 254, 250, 0.95);

        --text-primary: #1a1816;
        --text-secondary: #4a4641;
        --text-muted: #7a756e;
        --text-subtle: #a9a29a;

        --border-subtle: rgba(26, 24, 22, 0.06);
        --border-light: rgba(26, 24, 22, 0.1);
        --border-medium: rgba(26, 24, 22, 0.15);

        --accent: #c98b2f;
        --accent-light: #f5ddb8;
        --accent-lighter: #fdf4e6;
        --accent-dark: #9a6820;

        --secondary: #5a8a7a;
        --secondary-light: #c4ddd5;
        --secondary-lighter: #eef5f3;

        --tertiary: #8b7aa0;
        --tertiary-light: #ddd6e8;

        --shadow-sm: 0 1px 3px rgba(0,0,0,0.04), 0 1px 2px rgba(0,0,0,0.06);
        --shadow-md: 0 4px 12px rgba(0,0,0,0.06), 0 2px 4px rgba(0,0,0,0.04);
        --shadow-lg: 0 8px 24px rgba(0,0,0,0.08), 0 4px 8px rgba(0,0,0,0.04);
    }

    /* Dark theme detection */
    :global([data-theme-mode="dark"]) .ies-root {
        --bg-deep: #141312;
        --bg-base: #1c1a18;
        --bg-elevated: #242220;
        --bg-overlay: rgba(28, 26, 24, 0.95);

        --text-primary: #f4f2ef;
        --text-secondary: #c9c5bf;
        --text-muted: #8a857e;
        --text-subtle: #5a5650;

        --border-subtle: rgba(244, 242, 239, 0.04);
        --border-light: rgba(244, 242, 239, 0.08);
        --border-medium: rgba(244, 242, 239, 0.12);

        --accent-light: #4a3a20;
        --accent-lighter: #2a2218;

        --secondary-light: #2a3a35;
        --secondary-lighter: #1a2522;

        --shadow-sm: 0 1px 3px rgba(0,0,0,0.2);
        --shadow-md: 0 4px 12px rgba(0,0,0,0.25);
        --shadow-lg: 0 8px 24px rgba(0,0,0,0.3);
    }

    .ies-root {
        height: 100%;
        font-family: var(--font-body);
        font-size: 14px;
        line-height: 1.5;
        color: var(--text-primary);
        background: var(--bg-deep);
        -webkit-font-smoothing: antialiased;
    }

    /* Dashboard Layout */
    .dashboard {
        display: flex;
        flex-direction: column;
        height: 100%;
        padding: var(--space-4);
        gap: var(--space-5);
        overflow-y: auto;
        opacity: 0;
        transform: translateY(4px);
        transition: opacity 0.4s ease, transform 0.4s ease;
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
        gap: var(--space-3);
    }

    .logo {
        width: 36px;
        height: 36px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: var(--accent);
        background: var(--accent-lighter);
        border-radius: var(--radius-md);
    }

    .brand-text {
        display: flex;
        flex-direction: column;
        gap: 1px;
    }

    .brand-name {
        font-family: var(--font-display);
        font-size: 17px;
        font-weight: 600;
        letter-spacing: -0.02em;
        color: var(--text-primary);
    }

    .brand-version {
        font-family: var(--font-mono);
        font-size: 10px;
        color: var(--text-muted);
        letter-spacing: 0.02em;
    }

    /* Loading & Error States */
    .loading-state, .error-state {
        flex: 1;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        gap: var(--space-4);
        color: var(--text-muted);
        text-align: center;
        padding: var(--space-6);
    }

    .loading-spinner {
        width: 32px;
        height: 32px;
        border: 2px solid var(--border-light);
        border-top-color: var(--accent);
        border-radius: 50%;
        animation: spin 0.8s linear infinite;
    }

    @keyframes spin {
        to { transform: rotate(360deg); }
    }

    .error-state svg {
        color: var(--text-muted);
    }

    /* Stats Bar */
    .stats-bar {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: var(--space-4);
        padding: var(--space-4) var(--space-5);
        background: var(--bg-elevated);
        border: 1px solid var(--border-subtle);
        border-radius: var(--radius-md);
        box-shadow: var(--shadow-sm);
    }

    .stat {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 2px;
        padding: 0 var(--space-3);
    }

    .stat-value {
        font-family: var(--font-display);
        font-size: 22px;
        font-weight: 600;
        color: var(--accent);
        letter-spacing: -0.02em;
    }

    .stat-label {
        font-size: 10px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: var(--text-muted);
    }

    .stat-divider {
        width: 1px;
        height: 28px;
        background: var(--border-light);
    }

    /* Mode Cards */
    .mode-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: var(--space-3);
    }

    .mode-card {
        position: relative;
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: var(--space-2);
        padding: var(--space-5) var(--space-3);
        background: var(--bg-elevated);
        border: 1px solid var(--border-subtle);
        border-radius: var(--radius-md);
        cursor: pointer;
        transition: all 0.2s ease;
        overflow: hidden;
    }

    .mode-card:hover {
        transform: translateY(-2px);
        box-shadow: var(--shadow-md);
        border-color: var(--border-light);
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
        background: radial-gradient(circle at center, var(--accent-lighter) 0%, transparent 70%);
        opacity: 0;
        transition: opacity 0.3s ease;
        pointer-events: none;
    }

    .mode-card:hover .mode-glow {
        opacity: 0.5;
    }

    .mode-card--think:hover { border-color: var(--accent); }
    .mode-card--think:hover .mode-glow { background: radial-gradient(circle at center, var(--accent-lighter) 0%, transparent 70%); }

    .mode-card--explore:hover { border-color: var(--secondary); }
    .mode-card--explore:hover .mode-glow { background: radial-gradient(circle at center, var(--secondary-lighter) 0%, transparent 70%); }

    .mode-card--inbox:hover { border-color: var(--tertiary); }
    .mode-card--inbox:hover .mode-glow { background: radial-gradient(circle at center, var(--tertiary-light) 0%, transparent 70%); }

    .mode-icon {
        position: relative;
        z-index: 1;
        color: var(--text-secondary);
        transition: color 0.2s ease;
    }

    .mode-card--think:hover .mode-icon { color: var(--accent); }
    .mode-card--explore:hover .mode-icon { color: var(--secondary); }
    .mode-card--inbox:hover .mode-icon { color: var(--tertiary); }

    .mode-title {
        position: relative;
        z-index: 1;
        font-family: var(--font-display);
        font-size: 15px;
        font-weight: 600;
        color: var(--text-primary);
    }

    .mode-subtitle {
        position: relative;
        z-index: 1;
        font-size: 11px;
        color: var(--text-muted);
    }

    /* Sections */
    .section {
        display: flex;
        flex-direction: column;
        gap: var(--space-3);
    }

    .section-title {
        font-family: var(--font-display);
        font-size: 13px;
        font-weight: 600;
        color: var(--text-muted);
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin: 0;
        display: flex;
        align-items: center;
        gap: var(--space-2);
    }

    .queue-badge {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        min-width: 18px;
        height: 18px;
        padding: 0 6px;
        font-size: 10px;
        font-weight: 700;
        color: white;
        background: var(--secondary);
        border-radius: var(--radius-full);
    }

    /* Journey Cards */
    .journey-list {
        display: flex;
        flex-direction: column;
        gap: var(--space-2);
    }

    .journey-card {
        display: flex;
        align-items: center;
        gap: var(--space-3);
        padding: var(--space-3) var(--space-4);
        background: var(--bg-elevated);
        border: 1px solid var(--border-subtle);
        border-radius: var(--radius-sm);
        cursor: pointer;
        transition: all 0.15s ease;
        text-align: left;
        animation: slideUp 0.3s ease backwards;
    }

    @keyframes slideUp {
        from {
            opacity: 0;
            transform: translateY(8px);
        }
    }

    .journey-card:hover {
        border-color: var(--accent);
        box-shadow: var(--shadow-sm);
    }

    .journey-indicator {
        width: 3px;
        height: 24px;
        background: var(--accent);
        border-radius: 2px;
        opacity: 0.6;
        transition: opacity 0.15s ease;
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
        font-weight: 500;
        color: var(--text-primary);
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }

    .journey-meta {
        font-size: 12px;
        color: var(--text-muted);
    }

    .journey-arrow {
        color: var(--text-subtle);
        opacity: 0;
        transform: translateX(-4px);
        transition: all 0.15s ease;
    }

    .journey-card:hover .journey-arrow {
        opacity: 1;
        transform: translateX(0);
    }

    /* Inbox Cards */
    .inbox-list {
        display: flex;
        flex-direction: column;
        gap: var(--space-2);
    }

    .inbox-card {
        display: flex;
        align-items: center;
        gap: var(--space-3);
        padding: var(--space-3) var(--space-4);
        background: var(--bg-elevated);
        border: 1px solid var(--border-subtle);
        border-radius: var(--radius-sm);
        cursor: pointer;
        transition: all 0.15s ease;
    }

    .inbox-card:hover {
        border-color: var(--tertiary);
        background: var(--bg-surface);
    }

    .inbox-source {
        font-size: 16px;
        flex-shrink: 0;
    }

    .inbox-preview {
        flex: 1;
        font-size: 13px;
        color: var(--text-secondary);
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }

    .inbox-time {
        font-size: 11px;
        color: var(--text-muted);
        flex-shrink: 0;
    }

    /* Suggestions */
    .suggestions-section {
        padding-top: var(--space-2);
        border-top: 1px solid var(--border-subtle);
    }

    .suggestion-group {
        display: flex;
        flex-direction: column;
        gap: var(--space-2);
    }

    .suggestion-label {
        font-size: 11px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: var(--text-muted);
        margin: 0;
    }

    .chip-grid {
        display: flex;
        flex-wrap: wrap;
        gap: var(--space-2);
    }

    .chip {
        display: inline-flex;
        align-items: center;
        gap: var(--space-1);
        padding: 5px 12px;
        font-size: 12px;
        font-weight: 500;
        color: var(--text-secondary);
        background: var(--bg-base);
        border: 1px solid var(--border-light);
        border-radius: var(--radius-full);
        cursor: pointer;
        transition: all 0.15s ease;
    }

    .chip:hover {
        background: var(--accent-lighter);
        border-color: var(--accent-light);
        color: var(--accent-dark);
    }

    .chip--accent {
        background: var(--accent-lighter);
        border-color: var(--accent-light);
        color: var(--accent-dark);
    }

    .chip-dot {
        width: 5px;
        height: 5px;
        background: var(--accent);
        border-radius: 50%;
    }

    /* Button */
    .btn {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        gap: var(--space-2);
        padding: var(--space-2) var(--space-4);
        font-family: var(--font-body);
        font-size: 13px;
        font-weight: 600;
        color: var(--text-primary);
        background: var(--bg-elevated);
        border: 1px solid var(--border-medium);
        border-radius: var(--radius-sm);
        cursor: pointer;
        transition: all 0.15s ease;
    }

    .btn:hover {
        box-shadow: var(--shadow-sm);
    }

    .btn--primary {
        background: var(--accent);
        border-color: var(--accent);
        color: white;
    }

    .btn--primary:hover {
        background: var(--accent-dark);
        border-color: var(--accent-dark);
    }
</style>
