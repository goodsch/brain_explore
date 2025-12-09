<script lang="ts">
    /**
     * Dashboard - IES Main View (Layer 3 Processing Hub)
     *
     * Central hub for knowledge exploration with:
     * - Recent explorations (journeys)
     * - Quick Capture queue status with capture_status filtering
     * - Entry points: Explore Concept, Structured Thinking, Capture
     */
    import { onMount, onDestroy } from 'svelte';
    import { showMessage, fetchSyncPost } from 'siyuan';

    import ForgeMode from './ForgeMode.svelte';
    import FlowMode from './FlowMode.svelte';
    import Inbox from './Inbox.svelte';
    import SettingsPanel from '../components/SettingsPanel.svelte';
    import { promoteToInsight, getBackendUrl, checkBackendHealth, login, processOfflineQueue } from '../utils/siyuan-structure';
    import { offlineQueue } from '../utils/offlineQueue';
    import { settingsStore, initializeSettings, getSettingsForSave, type IESSettings } from '../stores/settings';
    import { noteContext, hasNoteOpen, currentNoteTitle } from '../stores/contextStore';
    import type { CaptureStatus } from '../types/blocks';
    import { CAPTURE_STATUS_LABELS } from '../types/blocks';
    import * as SyncService from '../services/syncService';

    // Plugin instance (optional, for settings persistence)
    export let plugin: any = null;

    // Backend configuration
    let backendUrl = getBackendUrl();
    const VERSION = '0.4.0';

    // User identity (fetched from profile service)
    let userId: string | null = null;

    // Settings state
    let showSettings = false;

    // View state
    type ViewMode = 'dashboard' | 'structured-thinking' | 'flow' | 'inbox';
    let currentView: ViewMode = 'dashboard';
    let selectedJourneyId: string | null = null;
    let selectedConcept: string | null = null;

    // Dashboard data
    let stats: {
        entities: number;
        relationships: number;
        books: number;
    } | null = null;

    let personalStats: {
        total_sparks: number;
        total_insights: number;
        sparks_by_status: Record<string, number>;
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

    // Resume sessions from Reader
    let resumeSessions: SyncService.ExplorationSession[] = [];
    let isLoadingResumeSessions = false;

    // Sparks data
    interface Spark {
        id: string;
        title: string;
        content: string;
        resonance_signal: string | null;
        energy_level: string;
        status: string;
        siyuan_block_id: string | null;
        created_at: string;
    }

    let recentSparks: Spark[] = [];
    let promotingSparkId: string | null = null;

    // Energy-based navigation filters (ADHD-friendly retrieval)
    type EnergyFilter = 'all' | 'low' | 'medium' | 'high';
    type ResonanceFilter = string | null;
    let energyFilter: EnergyFilter = 'all';
    let resonanceFilter: ResonanceFilter = null;
    let isLoadingSparks = false;

    const RESONANCE_OPTIONS = [
        { value: 'curious', emoji: '🤔', label: 'Curious' },
        { value: 'excited', emoji: '✨', label: 'Excited' },
        { value: 'surprised', emoji: '😲', label: 'Surprised' },
        { value: 'moved', emoji: '❤️', label: 'Moved' },
        { value: 'disturbed', emoji: '😟', label: 'Disturbed' },
        { value: 'unclear', emoji: '🤷', label: 'Unclear' },
        { value: 'connected', emoji: '🔗', label: 'Connected' },
        { value: 'validated', emoji: '✅', label: 'Validated' }
    ];

    // Quick Capture queue with capture_status filtering
    let captureQueue: Array<{
        id: string;
        title: string;
        content_preview: string;
        captured_at: string;
        capture_status: CaptureStatus;
        resonance_signal?: string;
        energy_level?: string;
    }> = [];
    let captureStatusFilter: CaptureStatus | 'all' = 'all';

    // Capture status filter options
    const captureStatusOptions: Array<{ value: CaptureStatus | 'all'; label: string; emoji: string }> = [
        { value: 'all', label: 'All', emoji: '📥' },
        { value: 'raw', label: CAPTURE_STATUS_LABELS.raw, emoji: '⬜' },
        { value: 'classified', label: CAPTURE_STATUS_LABELS.classified, emoji: '🔄' },
        { value: 'processed', label: CAPTURE_STATUS_LABELS.processed, emoji: '✅' },
    ];

    // Resonance options for emoji lookup in capture queue
    const resonanceOptions = [
        { value: '', label: 'None', emoji: '' },
        { value: 'curious', label: 'Curious', emoji: '🤔' },
        { value: 'excited', label: 'Excited', emoji: '✨' },
        { value: 'surprised', label: 'Surprised', emoji: '😮' },
        { value: 'moved', label: 'Moved', emoji: '💚' },
        { value: 'disturbed', label: 'Disturbed', emoji: '😟' },
        { value: 'unclear', label: 'Unclear', emoji: '🤷' },
        { value: 'connected', label: 'Connected', emoji: '🔗' },
        { value: 'validated', label: 'Validated', emoji: '✓' },
    ];

    // Computed filtered queue
    $: filteredCaptureQueue = captureStatusFilter === 'all'
        ? captureQueue
        : captureQueue.filter(item => item.capture_status === captureStatusFilter);

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
    let backendStatus: 'connected' | 'disconnected' | 'checking' = 'checking';
    let backendStatusMessage = '';

    // Offline queue status
    let queuedOperationsCount = 0;
    let failedOperationsCount = 0;
    let isProcessingQueue = false;

    function updateQueueStatus() {
        const status = offlineQueue.getQueueStatus();
        queuedOperationsCount = status.pending;
        failedOperationsCount = status.failed;
    }

    async function handleRetryQueue() {
        if (queuedOperationsCount === 0) return;
        isProcessingQueue = true;
        try {
            await processOfflineQueue();
            updateQueueStatus();
            if (queuedOperationsCount === 0) {
                showMessage('All queued operations synced successfully');
            }
        } catch (err) {
            showMessage('Some operations failed to sync');
        } finally {
            isProcessingQueue = false;
        }
    }

    // API helper
    async function apiGet(endpoint: string): Promise<any> {
        const url = `${backendUrl}${endpoint}`;

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
            const journeyEndpoint = userId ? `/journeys/user/${userId}` : null;
            const [statsData, suggestionsData, journeysData, personalStatsData, sparksData] = await Promise.all([
                apiGet('/graph/stats'),
                apiGet('/graph/suggestions'),
                journeyEndpoint ? apiGet(journeyEndpoint).catch(() => ({ journeys: [] })) : Promise.resolve({ journeys: [] }),
                apiGet('/personal/stats').catch(() => null),
                apiGet('/personal/sparks/unvisited?limit=10').catch(() => ({ sparks: [] }))
            ]);

            stats = statsData;
            suggestions = suggestionsData;
            recentJourneys = journeysData.journeys || [];
            personalStats = personalStatsData;
            recentSparks = sparksData.sparks || [];

            // Transform sparks into capture queue format
            // Sparks that are unvisited are effectively in "raw" or "classified" status
            captureQueue = (sparksData.sparks || []).map((spark: any) => ({
                id: spark.id,
                title: spark.title || 'Untitled capture',
                content_preview: spark.content?.slice(0, 100) || '',
                captured_at: spark.created_at || new Date().toISOString(),
                capture_status: spark.capture_status || 'raw' as CaptureStatus,
                resonance_signal: spark.resonance_signal,
                energy_level: spark.energy_level,
            }));
            
            // Load resume sessions from Reader
            loadResumeSessions();
        } catch (err) {
            error = err.message;
            console.error('[IES] Dashboard load error:', err);
        } finally {
            isLoading = false;
        }

    async function loadResumeSessions() {
        if (!userId) return;
        
        isLoadingResumeSessions = true;
        try {
            const sessions = await SyncService.getActiveSessions(userId, backendUrl);
            // Filter for reader sessions that are paused
            resumeSessions = sessions.filter(s => 
                s.app_source === 'reader' && s.status === 'paused'
            ).slice(0, 5); // Show max 5
        } catch (err) {
            console.error('[Dashboard] Failed to load resume sessions:', err);
            // Don't show error - this is optional feature
        } finally {
            isLoadingResumeSessions = false;
        }
    }

    async function openDeepLink(deepLink: string) {
        // Try to open deep link
        try {
            window.open(deepLink, '_blank');
        } catch (err) {
            // Fallback: show instructions
            showMessage(`Deep link: ${deepLink}`, 10000, 'info');
        }
    }

    async function resumeReaderSession(sessionId: string) {
        try {
            const resumeData = await SyncService.getResumeData(sessionId, 'reader', backendUrl);
            openDeepLink(resumeData.deep_link);
        } catch (err) {
            console.error('[Dashboard] Failed to get resume data:', err);
            showMessage(`Failed to resume session: ${err.message}`, 5000, 'error');
        }
    }
    }

    async function refreshBackendStatus(force = false) {
        isLoading = true;
        backendStatus = 'checking';
        backendStatusMessage = '';
        error = null;

        try {
            const health = await checkBackendHealth({ force });
            backendUrl = health.backendUrl || backendUrl;
            backendStatus = health.ok ? 'connected' : 'disconnected';
            backendStatusMessage = health.message || (health.ok ? 'Backend reachable' : 'No response from backend');

            if (health.ok) {
                await loadDashboardData();
            } else {
                isLoading = false;
                error = `Backend unreachable at ${backendUrl}. ${backendStatusMessage}`.trim();
            }
        } catch (err) {
            backendStatus = 'disconnected';
            backendStatusMessage = err.message || 'Unable to reach backend';
            error = `Backend unreachable at ${backendUrl}. ${backendStatusMessage}`.trim();
            isLoading = false;
        }
    }

    async function handlePromoteSpark(spark: Spark) {
        if (!spark.siyuan_block_id) {
            showMessage('This spark is not linked to a SiYuan block and cannot be promoted', 3000, 'error');
            return;
        }

        promotingSparkId = spark.id;

        try {
            await promoteToInsight(spark.siyuan_block_id, {
                backendSparkId: spark.id,
                insightTitle: spark.title
            });

            showMessage(`"${spark.title}" promoted to Insights!`, 3000, 'info');

            // Refresh dashboard data
            await loadDashboardData();
        } catch (err) {
            console.error('[IES] Promotion error:', err);
            showMessage(`Failed to promote: ${err.message}`, 3000, 'error');
        } finally {
            promotingSparkId = null;
        }
    }

    // Energy-based navigation: Load sparks filtered by energy or resonance
    async function loadSparksWithFilters() {
        isLoadingSparks = true;

        try {
            let endpoint = '/personal/sparks/unvisited?limit=10';

            // Energy filter takes precedence (mood-appropriate navigation)
            if (energyFilter !== 'all') {
                endpoint = `/personal/sparks/by-energy/${energyFilter}?limit=10`;
            }
            // Resonance filter for emotional retrieval cues
            else if (resonanceFilter) {
                endpoint = `/personal/sparks/by-resonance/${resonanceFilter}?limit=10`;
            }

            const data = await apiGet(endpoint);
            recentSparks = data.sparks || [];
        } catch (err) {
            console.error('[IES] Error loading filtered sparks:', err);
            // Keep existing sparks on error
        } finally {
            isLoadingSparks = false;
        }
    }

    // Reactive filter handlers
    function handleEnergyFilterChange(newFilter: EnergyFilter) {
        energyFilter = newFilter;
        // Clear resonance when energy is selected (mutually exclusive filters)
        if (newFilter !== 'all') {
            resonanceFilter = null;
        }
        loadSparksWithFilters();
    }

    function handleResonanceFilterChange(newResonance: string | null) {
        resonanceFilter = newResonance;
        // Clear energy when resonance is selected (mutually exclusive filters)
        if (newResonance) {
            energyFilter = 'all';
        }
        loadSparksWithFilters();
    }

    function clearFilters() {
        energyFilter = 'all';
        resonanceFilter = null;
        loadSparksWithFilters();
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

    function getResonanceEmoji(signal: string | null): string {
        if (!signal) return '💭';
        const map: Record<string, string> = {
            curious: '🤔',
            excited: '✨',
            surprised: '😲',
            moved: '❤️',
            disturbed: '😟',
            unclear: '🤷',
            connected: '🔗',
            validated: '✅'
        };
        return map[signal] || '💭';
    }

    function getResonanceColor(signal: string | null): string {
        if (!signal) return 'var(--text-muted)';
        const map: Record<string, string> = {
            curious: '#8b7aa0',
            excited: '#c9872e',
            surprised: '#5a8a7a',
            moved: '#d94f5c',
            disturbed: '#8b4f4f',
            unclear: '#7a756e',
            connected: '#5a8a7a',
            validated: '#5a8a7a'
        };
        return map[signal] || 'var(--text-muted)';
    }

    onMount(async () => {
        mounted = true;
        // Load settings from plugin storage if available
        if (plugin) {
            try {
                const savedSettings = await plugin.loadData('settings.json');
                initializeSettings(savedSettings);
                // Update backendUrl from settings
                backendUrl = $settingsStore.backendUrl;
            } catch (e) {
                console.log('[IES] No saved settings, using defaults');
            }
        }

        // Login to get user ID from profile service
        try {
            const profile = await login();
            userId = profile.user_id;
            console.log('[IES] Logged in as:', userId);
        } catch (e) {
            console.error('[IES] Login failed, journeys will not be saved:', e);
            // Continue without login - userId remains null
        }

        refreshBackendStatus();
        updateQueueStatus();

        // Listen for context menu Flow initiation events
        window.addEventListener('ies-start-flow-from-context', handleStartFlowFromContext);
    });

    onDestroy(() => {
        window.removeEventListener('ies-start-flow-from-context', handleStartFlowFromContext);
    });

    // Handler for context menu Flow initiation
    function handleStartFlowFromContext() {
        console.log('[IES] Received start-flow-from-context event');
        startFlowFromContext();
    }

    async function handleSaveSettings(settings: IESSettings) {
        if (plugin) {
            try {
                await plugin.saveData('settings.json', settings);
                showMessage('Settings saved');
                // Update local backendUrl
                backendUrl = settings.backendUrl;
            } catch (e) {
                console.error('[IES] Failed to save settings:', e);
                showMessage('Failed to save settings');
            }
        }
    }

    function navigateTo(view: ViewMode, concept: string | null = null) {
        if (view === 'flow') {
            selectedJourneyId = null;
            selectedConcept = concept;
        } else {
            selectedConcept = null;
        }
        currentView = view;
    }

    // Start Flow from current note context
    function startFlowFromContext() {
        const sparkSource = noteContext.getSparkSource();
        if (!sparkSource) {
            showMessage('No note is currently open');
            return;
        }

        // For now, we use the note title as the initial concept
        // In Phase 2, this will call the orientation endpoint
        const initialConcept = sparkSource.type === 'selection'
            ? sparkSource.text?.slice(0, 100)
            : sparkSource.noteTitle;

        navigateTo('flow', initialConcept);
    }

    function handleBack() {
        currentView = 'dashboard';
        selectedJourneyId = null;
        selectedConcept = null;
        refreshBackendStatus(true);
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

                <div class="backend-status" data-status={backendStatus}>
                    <span class="status-dot"></span>
                    <div class="status-text">
                        <span class="status-label">
                            {backendStatus === 'connected'
                                ? 'Connected'
                                : backendStatus === 'checking'
                                    ? 'Checking...'
                                    : 'Disconnected'}
                        </span>
                        <span class="status-subtext">
                            {backendStatus === 'disconnected'
                                ? `Backend at ${backendUrl}`
                                : backendStatusMessage || backendUrl}
                        </span>
                    </div>
                    {#if backendStatus === 'disconnected'}
                        <button class="status-retry" on:click={() => refreshBackendStatus(true)} disabled={backendStatus === 'checking'}>
                            Retry
                        </button>
                    {:else if backendStatus === 'checking'}
                        <div class="status-spinner"></div>
                    {/if}
                </div>

                {#if queuedOperationsCount > 0 || failedOperationsCount > 0}
                    <div class="queue-status" class:has-pending={queuedOperationsCount > 0} class:has-failed={failedOperationsCount > 0}>
                        <span class="queue-icon">📴</span>
                        <div class="queue-text">
                            <span class="queue-label">
                                {queuedOperationsCount > 0 ? `${queuedOperationsCount} pending` : ''}
                                {queuedOperationsCount > 0 && failedOperationsCount > 0 ? ', ' : ''}
                                {failedOperationsCount > 0 ? `${failedOperationsCount} failed` : ''}
                            </span>
                        </div>
                        <button
                            class="queue-retry"
                            on:click={handleRetryQueue}
                            disabled={isProcessingQueue || queuedOperationsCount === 0}
                            title="Retry syncing queued operations"
                        >
                            {isProcessingQueue ? '...' : 'Sync'}
                        </button>
                    </div>
                {/if}

                <button class="settings-btn" on:click={() => showSettings = true} title="Settings">
                    <svg viewBox="0 0 24 24" width="18" height="18">
                        <path fill="currentColor" d="M19.14 12.94c.04-.31.06-.63.06-.94 0-.31-.02-.63-.06-.94l2.03-1.58c.18-.14.23-.41.12-.61l-1.92-3.32c-.12-.22-.37-.29-.59-.22l-2.39.96c-.5-.38-1.03-.7-1.62-.94l-.36-2.54c-.04-.24-.24-.41-.48-.41h-3.84c-.24 0-.43.17-.47.41l-.36 2.54c-.59.24-1.13.57-1.62.94l-2.39-.96c-.22-.08-.47 0-.59.22L2.74 8.87c-.12.21-.08.47.12.61l2.03 1.58c-.04.31-.06.63-.06.94s.02.63.06.94l-2.03 1.58c-.18.14-.23.41-.12.61l1.92 3.32c.12.22.37.29.59.22l2.39-.96c.5.38 1.03.7 1.62.94l.36 2.54c.05.24.24.41.48.41h3.84c.24 0 .44-.17.47-.41l.36-2.54c.59-.24 1.13-.56 1.62-.94l2.39.96c.22.08.47 0 .59-.22l1.92-3.32c.12-.22.07-.47-.12-.61l-2.01-1.58zM12 15.6c-1.98 0-3.6-1.62-3.6-3.6s1.62-3.6 3.6-3.6 3.6 1.62 3.6 3.6-1.62 3.6-3.6 3.6z"/>
                    </svg>
                </button>
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
                    <button class="btn btn--primary" on:click={() => refreshBackendStatus(true)}>
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
                        {#if personalStats}
                            <div class="stat-divider"></div>
                            <div class="stat stat--spark">
                                <span class="stat-value">{personalStats.total_sparks}</span>
                                <span class="stat-label">Sparks</span>
                            </div>
                            <div class="stat-divider"></div>
                            <div class="stat stat--insight">
                                <span class="stat-value">{personalStats.total_insights}</span>
                                <span class="stat-label">Insights</span>
                            </div>
                        {/if}
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
                        <span class="mode-subtitle">Quick thoughts</span>
                    </button>
                </div>

                <!-- Context-Aware Flow Entry Point -->
                {#if $hasNoteOpen}
                    <section class="context-section">
                        <h3 class="section-title">Continue Exploring</h3>
                        <button class="context-card" on:click={startFlowFromContext}>
                            <div class="context-icon">
                                <svg viewBox="0 0 24 24" width="24" height="24">
                                    <path fill="currentColor" d="M14 2H6c-1.1 0-2 .9-2 2v16c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V8l-6-6zm-1 7V3.5L18.5 9H13z"/>
                                </svg>
                            </div>
                            <div class="context-info">
                                <span class="context-title">{$currentNoteTitle}</span>
                                <span class="context-hint">Start Flow from this note</span>
                            </div>
                            <div class="context-arrow">
                                <svg viewBox="0 0 24 24" width="20" height="20">
                                    <path fill="currentColor" d="M8.59 16.59L13.17 12 8.59 7.41 10 6l6 6-6 6-1.41-1.41z"/>
                                </svg>
                            </div>
                        </button>
                    </section>
                {/if}

                <!-- Recent Sparks with Energy-Based Navigation -->
                {#if recentSparks.length > 0 || energyFilter !== 'all' || resonanceFilter}
                    <section class="section">
                        <h3 class="section-title">
                            {#if energyFilter !== 'all'}
                                {energyFilter.charAt(0).toUpperCase() + energyFilter.slice(1)} Energy Sparks
                            {:else if resonanceFilter}
                                {RESONANCE_OPTIONS.find(r => r.value === resonanceFilter)?.emoji} {resonanceFilter.charAt(0).toUpperCase() + resonanceFilter.slice(1)} Sparks
                            {:else}
                                Recent Sparks
                            {/if}
                            <span class="spark-badge">{recentSparks.length}</span>
                        </h3>

                        <!-- Energy-Based Navigation Filters -->
                        <div class="spark-filters">
                            <div class="filter-group">
                                <span class="filter-label">Energy:</span>
                                <div class="filter-pills">
                                    <button
                                        class="filter-pill"
                                        class:active={energyFilter === 'all' && !resonanceFilter}
                                        on:click={() => handleEnergyFilterChange('all')}
                                    >
                                        All
                                    </button>
                                    <button
                                        class="filter-pill filter-pill--low"
                                        class:active={energyFilter === 'low'}
                                        on:click={() => handleEnergyFilterChange('low')}
                                    >
                                        🔋 Low
                                    </button>
                                    <button
                                        class="filter-pill filter-pill--medium"
                                        class:active={energyFilter === 'medium'}
                                        on:click={() => handleEnergyFilterChange('medium')}
                                    >
                                        ⚡ Medium
                                    </button>
                                    <button
                                        class="filter-pill filter-pill--high"
                                        class:active={energyFilter === 'high'}
                                        on:click={() => handleEnergyFilterChange('high')}
                                    >
                                        🔥 High
                                    </button>
                                </div>
                            </div>

                            <div class="filter-group">
                                <span class="filter-label">Resonance:</span>
                                <select
                                    class="filter-select"
                                    value={resonanceFilter || ''}
                                    on:change={(e) => handleResonanceFilterChange(e.currentTarget.value || null)}
                                >
                                    <option value="">Any feeling</option>
                                    {#each RESONANCE_OPTIONS as option}
                                        <option value={option.value}>{option.emoji} {option.label}</option>
                                    {/each}
                                </select>
                            </div>

                            {#if energyFilter !== 'all' || resonanceFilter}
                                <button class="filter-clear" on:click={clearFilters}>
                                    <svg viewBox="0 0 24 24" width="14" height="14">
                                        <path fill="currentColor" d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/>
                                    </svg>
                                    Clear
                                </button>
                            {/if}

                            {#if isLoadingSparks}
                                <div class="filter-loading">
                                    <div class="filter-spinner"></div>
                                </div>
                            {/if}
                        </div>

                        {#if recentSparks.length > 0}
                            <div class="spark-list">
                                {#each recentSparks as spark, i}
                                    <div class="spark-card" style="animation-delay: {i * 60}ms">
                                        <div class="spark-indicator" style="background: {getResonanceColor(spark.resonance_signal)}"></div>
                                        <div class="spark-content">
                                            <div class="spark-header">
                                                <span class="spark-emoji" style="color: {getResonanceColor(spark.resonance_signal)}">
                                                    {getResonanceEmoji(spark.resonance_signal)}
                                                </span>
                                                <span class="spark-title">{spark.title}</span>
                                            </div>
                                            <p class="spark-preview">{spark.content.substring(0, 80)}{spark.content.length > 80 ? '...' : ''}</p>
                                            <div class="spark-meta">
                                                <span class="spark-time">{formatRelativeTime(spark.created_at)}</span>
                                                {#if spark.resonance_signal}
                                                    <span class="spark-resonance">{spark.resonance_signal}</span>
                                                {/if}
                                                <span class="spark-energy">{spark.energy_level} energy</span>
                                            </div>
                                        </div>
                                        <button
                                            class="btn-promote"
                                            on:click={() => handlePromoteSpark(spark)}
                                            disabled={promotingSparkId === spark.id || !spark.siyuan_block_id}
                                            title={spark.siyuan_block_id ? 'Promote to Insight' : 'Not linked to SiYuan block'}
                                        >
                                            {#if promotingSparkId === spark.id}
                                                <div class="btn-spinner"></div>
                                            {:else}
                                                <svg viewBox="0 0 24 24" width="16" height="16">
                                                    <path fill="currentColor" d="M7 14l5-5 5 5z"/>
                                                </svg>
                                            {/if}
                                        </button>
                                    </div>
                                {/each}
                            </div>
                        {:else}
                            <!-- Empty state when filter returns no results -->
                            <div class="spark-empty">
                                <svg class="spark-empty-icon" viewBox="0 0 24 24" width="32" height="32">
                                    <circle cx="12" cy="12" r="10" fill="none" stroke="currentColor" stroke-width="1.5"/>
                                    <path d="M8 14s1.5 2 4 2 4-2 4-2" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
                                    <circle cx="9" cy="10" r="1" fill="currentColor"/>
                                    <circle cx="15" cy="10" r="1" fill="currentColor"/>
                                </svg>
                                <p class="spark-empty-text">
                                    {#if energyFilter !== 'all'}
                                        No sparks with {energyFilter} energy right now
                                    {:else if resonanceFilter}
                                        No sparks matching "{resonanceFilter}" feeling
                                    {:else}
                                        No recent sparks yet
                                    {/if}
                                </p>
                                {#if energyFilter !== 'all' || resonanceFilter}
                                    <button class="btn" on:click={clearFilters}>Show all sparks</button>
                                {/if}
                            </div>
                        {/if}
                    </section>
                {/if}

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

                <!-- Capture Queue with Status Filtering -->
                {#if captureQueue.length > 0}
                    <section class="section">
                        <h3 class="section-title">
                            Inbox
                            <span class="queue-badge">{filteredCaptureQueue.length}</span>
                        </h3>

                        <!-- Capture Status Filter -->
                        <div class="capture-status-filters">
                            {#each captureStatusOptions as option}
                                <button
                                    class="status-filter-btn"
                                    class:status-filter-btn--active={captureStatusFilter === option.value}
                                    on:click={() => captureStatusFilter = option.value}
                                    title={option.label}
                                >
                                    <span class="filter-emoji">{option.emoji}</span>
                                    <span class="filter-label">{option.label}</span>
                                    {#if option.value !== 'all'}
                                        <span class="filter-count">
                                            {captureQueue.filter(c => c.capture_status === option.value).length}
                                        </span>
                                    {/if}
                                </button>
                            {/each}

                <!-- Resume Reading Sessions -->
                {#if resumeSessions.length > 0}
                    <section class="section">
                        <h3 class="section-title">Resume Reading Sessions</h3>
                        <div class="journey-list">
                            {#each resumeSessions as session, i}
                                <button
                                    class="journey-card journey-card--reader"
                                    style="animation-delay: {i * 60}ms"
                                    on:click={() => resumeReaderSession(session.id)}
                                >
                                    <div class="journey-indicator journey-indicator--reader"></div>
                                    <div class="journey-content">
                                        <span class="journey-title">
                                            {session.current_entity_name || 'Unnamed entity'}
                                        </span>
                                        <span class="journey-meta">
                                            {#if session.reading_position?.book_hash}
                                                Reading · {formatRelativeTime(session.updated_at)}
                                            {:else}
                                                Exploring · {formatRelativeTime(session.updated_at)}
                                            {/if}
                                        </span>
                                        {#if session.resume_hint}
                                            <span class="journey-hint">{session.resume_hint}</span>
                                        {/if}
                                    </div>
                                    <svg class="journey-arrow" viewBox="0 0 24 24" width="16" height="16">
                                        <path fill="currentColor" d="M8.59 16.59L13.17 12 8.59 7.41 10 6l6 6-6 6-1.41-1.41z"/>
                                    </svg>
                                </button>
                            {/each}
                        </div>
                    </section>
                {/if}
                        </div>

                        <div class="capture-list">
                            {#each filteredCaptureQueue.slice(0, 5) as item}
                                <div class="capture-card" on:click={() => navigateTo('capture')}>
                                    <div class="capture-header-row">
                                        <span class="capture-status-badge capture-status-badge--{item.capture_status}">
                                            {#if item.capture_status === 'raw'}⬜{:else if item.capture_status === 'classified'}🔄{:else}✅{/if}
                                        </span>
                                        <span class="capture-title">{item.title}</span>
                                    </div>
                                    <span class="capture-preview">{item.content_preview}</span>
                                    <div class="capture-meta-row">
                                        <span class="capture-time">{formatRelativeTime(item.captured_at)}</span>
                                        {#if item.resonance_signal}
                                            <span class="capture-resonance" title="Resonance: {item.resonance_signal}">
                                                {resonanceOptions.find(r => r.value === item.resonance_signal)?.emoji || ''}
                                            </span>
                                        {/if}
                                    </div>
                                </div>
                            {/each}
                        </div>

                        {#if filteredCaptureQueue.length === 0}
                            <div class="empty-queue">
                                No captures with status "{captureStatusFilter === 'all' ? 'All' : CAPTURE_STATUS_LABELS[captureStatusFilter]}"
                            </div>
                        {/if}
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
                                        <button class="chip" on:click={() => navigateTo('flow', topic.name)}>
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
                                        <button class="chip chip--accent" on:click={() => navigateTo('flow', topic.name)}>
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
        <ForgeMode backendUrl={backendUrl} on:back={handleBack} />
    {:else if currentView === 'flow'}
        <FlowMode backendUrl={backendUrl} journeyId={selectedJourneyId} initialConcept={selectedConcept} {userId} on:back={handleBack} />
    {:else if currentView === 'capture'}
        <Inbox backendUrl={backendUrl} on:back={handleBack} />
    {/if}

    {#if showSettings}
        <SettingsPanel
            onClose={() => showSettings = false}
            onSave={handleSaveSettings}
        />
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

    /* Settings Button */
    .settings-btn {
        display: flex;
        align-items: center;
        justify-content: center;
        width: 32px;
        height: 32px;
        background: none;
        border: none;
        border-radius: var(--radius-sm);
        color: var(--text-muted);
        cursor: pointer;
        transition: all var(--transition-fast);
        margin-left: var(--space-2);
    }

    .settings-btn:hover {
        background: var(--bg-hover);
        color: var(--text-primary);
    }

    .settings-btn:active {
        transform: scale(0.95);
    }

    /* Offline Queue Status */
    .queue-status {
        display: flex;
        align-items: center;
        gap: var(--space-2);
        padding: var(--space-2) var(--space-3);
        background: var(--bg-elevated);
        border: 1px solid var(--border-light);
        border-radius: var(--radius-sm);
        font-size: 12px;
    }

    .queue-status.has-pending {
        background: #ede7f6;
        border-color: #b39ddb;
    }

    .queue-status.has-failed {
        background: #ffebee;
        border-color: #ef9a9a;
    }

    .queue-icon {
        font-size: 14px;
    }

    .queue-text {
        display: flex;
        flex-direction: column;
    }

    .queue-label {
        color: var(--text-secondary);
        font-weight: 500;
    }

    .queue-retry {
        padding: var(--space-1) var(--space-2);
        background: var(--accent);
        color: white;
        border: none;
        border-radius: var(--radius-sm);
        font-size: 11px;
        font-weight: 500;
        cursor: pointer;
        transition: opacity 0.15s;
    }

    .queue-retry:hover:not(:disabled) {
        opacity: 0.9;
    }

    .queue-retry:disabled {
        opacity: 0.5;
        cursor: not-allowed;
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

    .stat--spark .stat-value {
        color: #c98b2f;
    }

    .stat--insight .stat-value {
        color: var(--secondary);
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

    .queue-badge, .spark-badge {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        min-width: 18px;
        height: 18px;
        padding: 0 6px;
        font-size: 10px;
        font-weight: 700;
        color: white;
        border-radius: var(--radius-full);
    }

    .queue-badge {
        background: var(--secondary);
    }

    .spark-badge {
        background: #c98b2f;
    }

    /* Spark Cards */
    .spark-list {
        display: flex;
        flex-direction: column;
        gap: var(--space-2);
    }

    .spark-card {
        display: flex;
        align-items: stretch;
        gap: var(--space-3);
        padding: var(--space-3) var(--space-4);
        background: var(--bg-elevated);
        border: 1px solid var(--border-subtle);
        border-left: 3px solid #c98b2f;
        border-radius: var(--radius-sm);
        transition: all 0.15s ease;
        animation: slideUp 0.3s ease backwards;
    }

    @keyframes slideUp {
        from {
            opacity: 0;
            transform: translateY(8px);
        }
    }

    .spark-card:hover {
        box-shadow: var(--shadow-sm);
        border-left-color: #f5a623;
    }

    .spark-indicator {
        width: 3px;
        height: auto;
        border-radius: 2px;
        opacity: 0.8;
    }

    .spark-content {
        flex: 1;
        display: flex;
        flex-direction: column;
        gap: var(--space-1);
        min-width: 0;
    }

    .spark-header {
        display: flex;
        align-items: center;
        gap: var(--space-2);
    }

    .spark-emoji {
        font-size: 16px;
        line-height: 1;
    }

    .spark-title {
        font-weight: 600;
        color: var(--text-primary);
        flex: 1;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }

    .spark-preview {
        font-size: 12px;
        color: var(--text-secondary);
        margin: 0;
        line-height: 1.4;
    }

    .spark-meta {
        display: flex;
        align-items: center;
        gap: var(--space-2);
        font-size: 11px;
        color: var(--text-muted);
    }

    .spark-time {
        font-weight: 500;
    }

    .spark-resonance {
        padding: 2px 6px;
        background: var(--accent-lighter);
        border-radius: 4px;
        font-weight: 500;
    }

    .spark-energy {
        opacity: 0.7;
    }

    .btn-promote {
        display: flex;
        align-items: center;
        justify-content: center;
        width: 32px;
        height: 32px;
        padding: 0;
        background: var(--secondary-lighter);
        border: 1px solid var(--secondary-light);
        border-radius: var(--radius-sm);
        cursor: pointer;
        transition: all 0.15s ease;
        color: var(--secondary);
    }

    .btn-promote:hover:not(:disabled) {
        background: var(--secondary);
        color: white;
        transform: translateY(-1px);
        box-shadow: var(--shadow-sm);
    }

    .btn-promote:disabled {
        opacity: 0.5;
        cursor: not-allowed;
    }

    .btn-spinner {
        width: 14px;
        height: 14px;
        border: 2px solid var(--border-light);
        border-top-color: var(--secondary);
        border-radius: 50%;
        animation: spin 0.6s linear infinite;
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

    /* Capture Status Filters */
    .capture-status-filters {
        display: flex;
        gap: var(--space-2);
        flex-wrap: wrap;
        margin-bottom: var(--space-2);
    }

    .status-filter-btn {
        display: inline-flex;
        align-items: center;
        gap: 4px;
        padding: 4px 10px;
        font-size: 11px;
        font-weight: 500;
        color: var(--text-muted);
        background: var(--bg-base);
        border: 1px solid var(--border-light);
        border-radius: var(--radius-full);
        cursor: pointer;
        transition: all 0.15s ease;
    }

    .status-filter-btn:hover {
        background: var(--bg-elevated);
        border-color: var(--accent);
        color: var(--accent);
    }

    .status-filter-btn--active {
        background: var(--accent-lighter);
        border-color: var(--accent);
        color: var(--accent);
    }

    .filter-emoji {
        font-size: 12px;
    }

    .filter-label {
        font-size: 11px;
    }

    .filter-count {
        font-size: 10px;
        padding: 1px 5px;
        background: var(--bg-deep);
        border-radius: 8px;
        margin-left: 2px;
    }

    .status-filter-btn--active .filter-count {
        background: var(--accent);
        color: white;
    }

    /* Capture Cards */
    .capture-list {
        display: flex;
        flex-direction: column;
        gap: var(--space-2);
    }

    .inbox-card {
        display: flex;
        flex-direction: column;
        gap: var(--space-2);
        padding: var(--space-3) var(--space-4);
        background: var(--bg-elevated);
        border: 1px solid var(--border-subtle);
        border-radius: var(--radius-sm);
        cursor: pointer;
        transition: all 0.15s ease;
    }

    .capture-card:hover {
        border-color: var(--accent);
        background: var(--accent-lighter);
    }

    .capture-header-row {
        display: flex;
        align-items: center;
        gap: var(--space-2);
    }

    .capture-status-badge {
        font-size: 12px;
        line-height: 1;
    }

    .capture-status-badge--raw {
        opacity: 0.6;
    }

    .capture-status-badge--classified {
        opacity: 0.9;
    }

    .capture-status-badge--processed {
        opacity: 1;
    }

    .capture-title {
        font-size: 13px;
        font-weight: 500;
        color: var(--text-primary);
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }

    .capture-preview {
        font-size: 12px;
        color: var(--text-muted);
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        max-width: 100%;
    }

    .capture-meta-row {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: var(--space-2);
    }

    .inbox-time {
        font-size: 11px;
        color: var(--text-subtle);
    }

    .capture-resonance {
        font-size: 12px;
    }

    .empty-queue {
        font-size: 12px;
        color: var(--text-muted);
        font-style: italic;
        text-align: center;
        padding: var(--space-4);
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

    /* Energy-Based Navigation Filters */
    .spark-filters {
        display: flex;
        flex-wrap: wrap;
        align-items: center;
        gap: var(--space-3);
        padding: var(--space-3);
        background: var(--bg-base);
        border: 1px solid var(--border-subtle);
        border-radius: var(--radius-sm);
        margin-bottom: var(--space-2);
    }

    .filter-group {
        display: flex;
        align-items: center;
        gap: var(--space-2);
    }

    .filter-label {
        font-size: 11px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: var(--text-muted);
    }

    .filter-pills {
        display: flex;
        gap: var(--space-1);
    }

    .filter-pill {
        display: inline-flex;
        align-items: center;
        gap: 4px;
        padding: 4px 10px;
        font-size: 12px;
        font-weight: 500;
        color: var(--text-secondary);
        background: var(--bg-elevated);
        border: 1px solid var(--border-light);
        border-radius: var(--radius-full);
        cursor: pointer;
        transition: all 0.15s ease;
    }

    .filter-pill:hover {
        background: var(--accent-lighter);
        border-color: var(--accent-light);
        color: var(--accent-dark);
    }

    .filter-pill.active {
        background: var(--accent);
        border-color: var(--accent);
        color: white;
    }

    /* Energy level specific colors */
    .filter-pill--low.active {
        background: #6b8e9f;
        border-color: #6b8e9f;
    }

    .filter-pill--medium.active {
        background: #c98b2f;
        border-color: #c98b2f;
    }

    .filter-pill--high.active {
        background: #d94f5c;
        border-color: #d94f5c;
    }

    .filter-select {
        padding: 4px 8px;
        font-size: 12px;
        font-family: var(--font-body);
        color: var(--text-secondary);
        background: var(--bg-elevated);
        border: 1px solid var(--border-light);
        border-radius: var(--radius-sm);
        cursor: pointer;
        transition: all 0.15s ease;
    }

    .filter-select:hover {
        border-color: var(--accent-light);
    }

    .filter-select:focus {
        outline: none;
        border-color: var(--accent);
        box-shadow: 0 0 0 2px var(--accent-lighter);
    }

    .filter-clear {
        display: inline-flex;
        align-items: center;
        gap: 4px;
        padding: 4px 8px;
        font-size: 11px;
        font-weight: 500;
        color: var(--text-muted);
        background: transparent;
        border: 1px solid var(--border-light);
        border-radius: var(--radius-sm);
        cursor: pointer;
        transition: all 0.15s ease;
    }

    .filter-clear:hover {
        color: var(--text-primary);
        border-color: var(--border-medium);
        background: var(--bg-elevated);
    }

    .filter-loading {
        display: flex;
        align-items: center;
        margin-left: auto;
    }

    .filter-spinner {
        width: 14px;
        height: 14px;
        border: 2px solid var(--border-light);
        border-top-color: var(--accent);
        border-radius: 50%;
        animation: spin 0.6s linear infinite;
    }

    /* Empty state when filters return no results */
    .spark-empty {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: var(--space-2);
        padding: var(--space-5);
        color: var(--text-muted);
        text-align: center;
    }

    .spark-empty-icon {
        opacity: 0.5;
    }

    .spark-empty-text {
        font-size: 13px;
    }

    /* Context-Aware Flow Entry */
    .context-section {
        display: flex;
        flex-direction: column;
        gap: var(--space-3);
        margin-top: var(--space-2);
    }

    .context-card {
        display: flex;
        align-items: center;
        gap: var(--space-4);
        padding: var(--space-4);
        background: linear-gradient(135deg, var(--secondary-lighter) 0%, var(--bg-elevated) 100%);
        border: 1px solid var(--secondary-light);
        border-radius: var(--radius-md);
        cursor: pointer;
        transition: all 0.2s ease;
        text-align: left;
        width: 100%;
    }

    .context-card:hover {
        border-color: var(--secondary);
        box-shadow: var(--shadow-md);
        transform: translateY(-1px);
    }

    .context-icon {
        display: flex;
        align-items: center;
        justify-content: center;
        width: 44px;
        height: 44px;
        background: var(--secondary-lighter);
        border-radius: var(--radius-sm);
        color: var(--secondary);
        flex-shrink: 0;
    }

    .context-info {
        flex: 1;
        display: flex;
        flex-direction: column;
        gap: 2px;
        min-width: 0;
    }

    .context-title {
        font-family: var(--font-display);
        font-size: 15px;
        font-weight: 600;
        color: var(--text-primary);
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }

    .context-hint {
        font-size: 12px;
        color: var(--text-muted);
    }

    .context-arrow {
        display: flex;
        align-items: center;
        justify-content: center;
        color: var(--secondary);
        opacity: 0.6;
        transition: all 0.15s ease;
    }

    .context-card:hover .context-arrow {
        opacity: 1;
        transform: translateX(2px);
    }
    
    /* Reader session cards */
    .journey-card--reader {
        border-left-color: var(--secondary);
    }
    
    .journey-card--reader:hover {
        border-color: var(--secondary);
    }
    
    .journey-indicator--reader {
        background: var(--secondary);
    }
    
    .journey-hint {
        font-size: 11px;
        color: var(--text-muted);
        font-style: italic;
        margin-top: 2px;
    }
</style>
