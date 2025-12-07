<script lang="ts">
    /**
     * FlowMode - Layer 3 Visual Graph Exploration
     *
     * "Contemplative Knowledge Space" Design
     * Navigate the knowledge graph visually with grouped concept display.
     * "Flow" = navigate freely through the concept space.
     */
    import { onMount, createEventDispatcher } from 'svelte';
    import { showMessage, fetchSyncPost } from 'siyuan';

    import ReframesTab from '../components/ReframesTab.svelte';
    import { saveJourney, type JourneyData } from '../utils/siyuan-structure';

    export let backendUrl: string;
    export let journeyId: string | null = null;
    export let initialConcept: string | null = null;
    export let userId: string | null = null;

    const dispatch = createEventDispatcher();

    // State
    let searchQuery = '';
    let isSearching = false;
    let isLoadingJourney = false;
    let searchResults: Array<{name: string, type: string}> = [];
    let currentConcept: string | null = null;
    let nodes: Array<{name: string, type: string, labels: string[]}> = [];
    let relationships: Array<{start: string, type: string, end: string}> = [];
    let explorationPath: string[] = [];
    let explorationTimestamps: string[] = []; // Timestamps for each step
    let explorationStartTime: number | null = null; // When exploration began
    let thinkingQuestion: string | null = null;
    let isLoadingQuestion = false;
    let isExploring = false;
    let mounted = false;
    let conceptDetailTab: 'connections' | 'reframes' = 'connections';

    interface QuestionExchange {
        question: string;
        response: string;
        questionClass?: string | null;
        approach?: string | null;
        state?: string | null;
    }

    const QUESTION_CLASS_LABELS: Record<string, { label: string; emoji: string; color: string }> = {
        schema_probe: { label: 'Structure', emoji: '🏗️', color: '#4a90d9' },
        boundary: { label: 'Boundary', emoji: '🔲', color: '#7b68ee' },
        dimensional: { label: 'Dimensional', emoji: '📐', color: '#20b2aa' },
        causal: { label: 'Causal', emoji: '⚡', color: '#f4a460' },
        counterfactual: { label: 'What-If', emoji: '🔮', color: '#da70d6' },
        anchor: { label: 'Anchor', emoji: '⚓', color: '#3cb371' },
        perspective_shift: { label: 'Perspective', emoji: '👁️', color: '#cd853f' },
        meta_cognitive: { label: 'Meta', emoji: '🧠', color: '#778899' },
        reflective_synthesis: { label: 'Synthesis', emoji: '🔗', color: '#6495ed' },
    };

    let questionResponse = '';
    let questionHistory: QuestionExchange[] = [];
    let currentQuestionClass: string | null = null;
    let currentApproach: string | null = null;
    let lastDetectedState: string | null = null;

    onMount(() => {
        mounted = true;
        if (journeyId) {
            loadJourney(journeyId);
        } else if (initialConcept) {
            exploreConcept(initialConcept);
        }
    });

    $: if (!currentConcept) {
        conceptDetailTab = 'connections';
    }

    // Group nodes by relationship type
    $: groupedNodes = groupNodesByRelationship(nodes, relationships, currentConcept);

    function groupNodesByRelationship(
        nodes: Array<{name: string, type: string, labels: string[]}>,
        rels: Array<{start: string, type: string, end: string}>,
        current: string | null
    ): Map<string, Array<{name: string, type: string, direction: 'outgoing' | 'incoming'}>> {
        const groups = new Map<string, Array<{name: string, type: string, direction: 'outgoing' | 'incoming'}>>();

        if (!current) return groups;

        for (const rel of rels) {
            let nodeName: string;
            let direction: 'outgoing' | 'incoming';

            if (rel.start === current) {
                nodeName = rel.end;
                direction = 'outgoing';
            } else if (rel.end === current) {
                nodeName = rel.start;
                direction = 'incoming';
            } else {
                continue;
            }

            const node = nodes.find(n => n.name === nodeName);
            if (!node) continue;

            const key = rel.type;
            if (!groups.has(key)) {
                groups.set(key, []);
            }
            groups.get(key)!.push({
                name: nodeName,
                type: node.type,
                direction
            });
        }

        return groups;
    }

    // Format relationship type for display
    function formatRelType(relType: string): string {
        return relType.replace(/_/g, ' ').toLowerCase();
    }

    // API helper using SiYuan's forward proxy
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

    async function apiPost(endpoint: string, body: any): Promise<any> {
        const url = `${backendUrl}${endpoint}`;

        const response = await fetchSyncPost('/api/network/forwardProxy', {
            url: url,
            method: 'POST',
            timeout: 30000,
            contentType: 'application/json',
            headers: [],
            payload: body
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

    async function handleSearch() {
        if (!searchQuery.trim()) return;

        isSearching = true;
        searchResults = [];
        try {
            const data = await apiGet(`/graph/search?q=${encodeURIComponent(searchQuery)}&limit=10`);
            if (data.results && data.results.length > 0) {
                searchResults = data.results;
            } else {
                showMessage('No concepts found', 3000);
            }
        } catch (err) {
            showMessage(`Search failed: ${err.message}`, 5000, 'error');
        } finally {
            isSearching = false;
        }
    }

    async function exploreConcept(concept: string) {
        isExploring = true;
        searchResults = []; // Clear search results when exploring

        try {
            const data = await apiGet(`/graph/explore/${encodeURIComponent(concept)}?depth=1`);
            currentConcept = concept;
            nodes = data.nodes || [];
            relationships = data.relationships || [];
            questionHistory = [];
            questionResponse = '';
            currentQuestionClass = null;
            currentApproach = null;
            lastDetectedState = null;

            // Track exploration start time
            if (explorationStartTime === null) {
                explorationStartTime = Date.now();
            }

            // Add to path (avoid duplicates if navigating back)
            const now = new Date().toISOString();
            const existingIndex = explorationPath.indexOf(concept);
            if (existingIndex >= 0) {
                // Navigating back - truncate path and timestamps
                explorationPath = explorationPath.slice(0, existingIndex + 1);
                explorationTimestamps = explorationTimestamps.slice(0, existingIndex + 1);
            } else {
                explorationPath = [...explorationPath, concept];
                explorationTimestamps = [...explorationTimestamps, now];
            }

            // Clear thinking question when navigating
            thinkingQuestion = null;
        } catch (err) {
            showMessage(`Explore failed: ${err.message}`, 5000, 'error');
        } finally {
            isExploring = false;
        }
    }

    async function requestThinkingPartner() {
        if (!currentConcept) return;

        isLoadingQuestion = true;
        try {
            const data = await apiPost('/graph/thinking-partner', {
                concept: currentConcept,
                path: explorationPath.slice(-5),
                related: nodes.slice(0, 5).map(n => n.name)
            });
            thinkingQuestion = data.question;
            currentQuestionClass = data.question_class || null;
            currentApproach = null;
            lastDetectedState = null;
            questionResponse = '';
        } catch (err) {
            showMessage(`Question failed: ${err.message}`, 5000, 'error');
        } finally {
            isLoadingQuestion = false;
        }
    }

    async function submitQuestionResponse() {
        if (!thinkingQuestion) {
            showMessage('No active question to respond to', 3000, 'error');
            return;
        }
        if (!questionResponse.trim()) {
            showMessage('Please enter a response', 3000, 'error');
            return;
        }

        isLoadingQuestion = true;
        const responseText = questionResponse.trim();

        try {
            const detection = await apiPost('/question-engine/detect-state', {
                recent_messages: [thinkingQuestion, responseText],
                user_id: 'chris'
            });
            lastDetectedState = detection?.primary_state || null;

            const generated = await apiPost('/question-engine/generate-questions', {
                user_id: 'chris',
                recent_messages: [thinkingQuestion, responseText],
                context: currentConcept || 'exploration',
                num_questions: 1
            });

            const classified = generated?.classified_questions?.[0];
            const followUp = classified?.question || generated?.questions?.[0] || null;

            questionHistory = [
                ...questionHistory,
                {
                    question: thinkingQuestion,
                    response: responseText,
                    questionClass: currentQuestionClass,
                    approach: currentApproach || generated?.approach || null,
                    state: lastDetectedState
                }
            ];

            if (!followUp) {
                thinkingQuestion = null;
                currentQuestionClass = null;
                currentApproach = null;
                questionResponse = '';
                showMessage('No follow-up question returned', 4000, 'error');
                return;
            }

            thinkingQuestion = followUp;
            currentQuestionClass = classified?.question_class || null;
            currentApproach = classified?.approach || generated?.approach || null;
            questionResponse = '';
        } catch (err) {
            console.error('[IES] Question response handling failed:', err);
            const message = err?.message || String(err);
            showMessage(`Could not process response: ${message}`, 5000, 'error');
        } finally {
            isLoadingQuestion = false;
        }
    }

    async function handleBack() {
        // Save journey if we have exploration data
        if (explorationPath.length > 0 && userId) {
            try {
                const now = Date.now();
                const journey: JourneyData = {
                    entryPoint: {
                        type: 'siyuan-flow',
                        reference: initialConcept || explorationPath[0] || 'unknown'
                    },
                    path: explorationPath.map((conceptName, index) => {
                        // Calculate dwell time: time until next step, or until now for last step
                        const stepTime = new Date(explorationTimestamps[index]).getTime();
                        const nextStepTime = index < explorationPath.length - 1
                            ? new Date(explorationTimestamps[index + 1]).getTime()
                            : now;
                        const dwellSeconds = Math.round((nextStepTime - stepTime) / 1000);

                        return {
                            entityId: conceptName, // Using name as ID (simplification)
                            entityName: conceptName,
                            timestamp: explorationTimestamps[index],
                            dwellTimeSeconds: dwellSeconds > 0 ? dwellSeconds : 1
                        };
                    })
                };

                await saveJourney(journey, userId);
                console.log('[FlowMode] Journey saved successfully');
            } catch (e) {
                console.error('[FlowMode] Failed to save journey:', e);
                // Don't block exit on save failure
            }
        }
        dispatch('back');
    }

    function handleKeydown(e: KeyboardEvent) {
        if (e.key === 'Enter') {
            e.preventDefault();
            handleSearch();
        }
    }

    function clearExploration() {
        currentConcept = null;
        nodes = [];
        relationships = [];
        explorationPath = [];
        explorationTimestamps = [];
        explorationStartTime = null;
        thinkingQuestion = null;
        questionHistory = [];
        questionResponse = '';
        currentQuestionClass = null;
        currentApproach = null;
        lastDetectedState = null;
        searchQuery = '';
        searchResults = [];
        conceptDetailTab = 'connections';
    }

    function navigateToPathStep(index: number) {
        const concept = explorationPath[index];
        if (concept && concept !== currentConcept) {
            exploreConcept(concept);
        }
    }

    async function loadJourney(id: string) {
        isLoadingJourney = true;
        try {
            const journey = await apiGet(`/journeys/${id}`);

            // Restore exploration path from journey's path
            if (journey.path && journey.path.length > 0) {
                explorationPath = journey.path.map((step: any) => step.entity_name);

                // Navigate to the last concept in the path
                const lastStep = journey.path[journey.path.length - 1];
                if (lastStep && lastStep.entity_name) {
                    await exploreConcept(lastStep.entity_name);
                }

                showMessage(`Resumed journey: ${journey.title || 'Untitled'}`, 3000);
            }
        } catch (err) {
            console.error('[IES] Failed to load journey:', err);
            showMessage(`Failed to resume journey: ${err.message}`, 5000, 'error');
        } finally {
            isLoadingJourney = false;
        }
    }

    // Get entity type color
    function getTypeColor(type: string): string {
        switch (type) {
            case 'Theory': return 'var(--ies-secondary)';
            case 'Researcher': return 'var(--ies-tertiary)';
            case 'Concept': return 'var(--ies-accent)';
            default: return 'var(--ies-text-muted)';
        }
    }
</script>

<div class="flow-mode" class:mounted>
    <!-- Header -->
    <header class="flow-header">
        <button class="back-btn" on:click={handleBack} title="Back to Dashboard">
            <svg viewBox="0 0 24 24" width="18" height="18">
                <path fill="currentColor" d="M20 11H7.83l5.59-5.59L12 4l-8 8 8 8 1.41-1.41L7.83 13H20v-2z"/>
            </svg>
        </button>
        <div class="header-title">
            <svg class="flow-icon" viewBox="0 0 32 32" width="24" height="24">
                <!-- Network/flow icon -->
                <circle cx="16" cy="8" r="3" fill="currentColor" opacity="0.9"/>
                <circle cx="8" cy="20" r="3" fill="currentColor" opacity="0.7"/>
                <circle cx="24" cy="20" r="3" fill="currentColor" opacity="0.7"/>
                <circle cx="16" cy="26" r="2" fill="currentColor" opacity="0.5"/>
                <line x1="16" y1="11" x2="10" y2="18" stroke="currentColor" stroke-width="1.5" opacity="0.4"/>
                <line x1="16" y1="11" x2="22" y2="18" stroke="currentColor" stroke-width="1.5" opacity="0.4"/>
                <line x1="10" y1="22" x2="16" y2="25" stroke="currentColor" stroke-width="1.5" opacity="0.3"/>
                <line x1="22" y1="22" x2="16" y2="25" stroke="currentColor" stroke-width="1.5" opacity="0.3"/>
            </svg>
            <h1>Flow</h1>
        </div>
        {#if explorationPath.length > 0}
            <button class="clear-btn" on:click={clearExploration}>
                <svg viewBox="0 0 24 24" width="14" height="14">
                    <path fill="currentColor" d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/>
                </svg>
                Clear
            </button>
        {/if}
    </header>

    <!-- Search -->
    <div class="search-container">
        <div class="search-wrapper">
            <svg class="search-icon" viewBox="0 0 24 24" width="18" height="18">
                <path fill="currentColor" d="M15.5 14h-.79l-.28-.27C15.41 12.59 16 11.11 16 9.5 16 5.91 13.09 3 9.5 3S3 5.91 3 9.5 5.91 16 9.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99L20.49 19l-4.99-5zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14z"/>
            </svg>
            <input
                type="text"
                bind:value={searchQuery}
                on:keydown={handleKeydown}
                placeholder="Search the knowledge graph..."
                disabled={isSearching}
            />
            {#if searchQuery}
                <button class="search-clear" on:click={() => { searchQuery = ''; searchResults = []; }}>
                    <svg viewBox="0 0 24 24" width="16" height="16">
                        <path fill="currentColor" d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/>
                    </svg>
                </button>
            {/if}
        </div>
        <button
            class="search-btn"
            on:click={handleSearch}
            disabled={isSearching || !searchQuery.trim()}
        >
            {#if isSearching}
                <span class="spinner"></span>
            {:else}
                Explore
            {/if}
        </button>
    </div>

    <!-- Search Results -->
    {#if searchResults.length > 0}
        <div class="results-panel">
            <div class="results-header">
                <span class="results-label">Found {searchResults.length} concept{searchResults.length !== 1 ? 's' : ''}</span>
            </div>
            <div class="results-list">
                {#each searchResults as result, i}
                    <button
                        class="result-card"
                        style="--delay: {i * 40}ms; --type-color: {getTypeColor(result.type)}"
                        on:click={() => exploreConcept(result.name)}
                    >
                        <span class="result-indicator"></span>
                        <span class="result-name">{result.name}</span>
                        <span class="result-type">{result.type}</span>
                    </button>
                {/each}
            </div>
        </div>
    {/if}

    <!-- Main Content Area -->
    <div class="flow-content">
        {#if isLoadingJourney}
            <div class="flow-state">
                <div class="state-icon loading">
                    <svg viewBox="0 0 32 32" width="48" height="48">
                        <circle cx="16" cy="16" r="12" fill="none" stroke="currentColor" stroke-width="2" opacity="0.2"/>
                        <path d="M16 4 A12 12 0 0 1 28 16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                    </svg>
                </div>
                <p class="state-text">Resuming your journey...</p>
            </div>
        {:else if !currentConcept && searchResults.length === 0}
            <div class="flow-state welcome">
                <div class="state-icon">
                    <svg viewBox="0 0 64 64" width="64" height="64">
                        <!-- Constellation/network welcome icon -->
                        <circle cx="32" cy="16" r="4" fill="currentColor" opacity="0.8"/>
                        <circle cx="16" cy="32" r="3" fill="currentColor" opacity="0.6"/>
                        <circle cx="48" cy="32" r="3" fill="currentColor" opacity="0.6"/>
                        <circle cx="24" cy="48" r="3" fill="currentColor" opacity="0.5"/>
                        <circle cx="40" cy="48" r="3" fill="currentColor" opacity="0.5"/>
                        <circle cx="32" cy="36" r="5" fill="currentColor" opacity="0.9"/>
                        <line x1="32" y1="20" x2="32" y2="31" stroke="currentColor" stroke-width="1.5" opacity="0.3"/>
                        <line x1="19" y1="32" x2="27" y2="34" stroke="currentColor" stroke-width="1.5" opacity="0.3"/>
                        <line x1="45" y1="32" x2="37" y2="34" stroke="currentColor" stroke-width="1.5" opacity="0.3"/>
                        <line x1="26" y1="46" x2="29" y2="40" stroke="currentColor" stroke-width="1.5" opacity="0.3"/>
                        <line x1="38" y1="46" x2="35" y2="40" stroke="currentColor" stroke-width="1.5" opacity="0.3"/>
                    </svg>
                </div>
                <h2 class="state-title">Navigate Knowledge</h2>
                <p class="state-text">Search for a concept to begin exploring connections in the knowledge graph.</p>
                <p class="state-hint">Each concept reveals its relationships, creating paths of understanding.</p>
            </div>
        {:else if currentConcept}
            <!-- Central Concept -->
            <div class="concept-center" class:exploring={isExploring}>
                <div class="concept-glow"></div>
                <div class="concept-core">
                    <span class="concept-label">Exploring</span>
                    <h2 class="concept-name">{currentConcept}</h2>
                    <span class="concept-connections">{nodes.length} connection{nodes.length !== 1 ? 's' : ''}</span>
                </div>
            </div>

            <div class="concept-tabs">
                <button
                    class="tab-btn"
                    class:active={conceptDetailTab === 'connections'}
                    on:click={() => conceptDetailTab = 'connections'}
                >
                    Connections
                </button>
                <button
                    class="tab-btn"
                    class:active={conceptDetailTab === 'reframes'}
                    on:click={() => conceptDetailTab = 'reframes'}
                >
                    Reframes
                </button>
            </div>

            {#if conceptDetailTab === 'connections'}
                {#if groupedNodes.size > 0}
                    <div class="relationships">
                        {#each [...groupedNodes.entries()] as [relType, relNodes], groupIndex}
                            <div class="rel-group" style="--delay: {groupIndex * 60}ms">
                                <div class="rel-header">
                                    <span class="rel-direction" class:outgoing={relNodes[0]?.direction === 'outgoing'}>
                                        {relNodes[0]?.direction === 'outgoing' ? '→' : '←'}
                                    </span>
                                    <span class="rel-type">{formatRelType(relType)}</span>
                                    <span class="rel-count">{relNodes.length}</span>
                                </div>
                                <div class="rel-nodes">
                                    {#each relNodes as node, nodeIndex}
                                        <button
                                            class="node-chip"
                                            style="--delay: {(groupIndex * 60) + (nodeIndex * 30)}ms; --type-color: {getTypeColor(node.type)}"
                                            on:click={() => exploreConcept(node.name)}
                                            title="{node.type}: {node.name}"
                                        >
                                            <span class="node-indicator"></span>
                                            <span class="node-name">{node.name}</span>
                                        </button>
                                    {/each}
                                </div>
                            </div>
                        {/each}
                    </div>
                {:else if !isExploring}
                    <div class="no-connections">
                        <p>No connections found for this concept.</p>
                        <p class="hint">Try the Thinking Partner for guidance.</p>
                    </div>
                {/if}
            {:else}
                <ReframesTab conceptId={currentConcept} backendUrl={backendUrl} />
            {/if}
        {/if}
    </div>

    <!-- Exploration Path -->
    {#if explorationPath.length > 1}
        <div class="path-trail">
            <span class="path-label">Journey</span>
            <div class="path-steps">
                {#each explorationPath as step, i}
                    <button
                        class="path-step"
                        class:current={i === explorationPath.length - 1}
                        on:click={() => navigateToPathStep(i)}
                        disabled={i === explorationPath.length - 1}
                    >
                        {step}
                    </button>
                    {#if i < explorationPath.length - 1}
                        <span class="path-connector">
                            <svg viewBox="0 0 16 16" width="12" height="12">
                                <path fill="currentColor" d="M8 4l4 4-4 4V4z"/>
                            </svg>
                        </span>
                    {/if}
                {/each}
            </div>
        </div>
    {/if}

    <!-- Thinking Partner Section -->
    {#if currentConcept}
        <div class="thinking-section">
            {#if thinkingQuestion}
                <div class="thinking-card">
                    <div class="thinking-header">
                        <svg viewBox="0 0 24 24" width="18" height="18">
                            <path fill="currentColor" d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8zm-1-4h2v2h-2zm1.61-9.96c-2.06-.3-3.88.97-4.43 2.79-.18.58.26 1.17.87 1.17h.2c.41 0 .74-.29.88-.67.32-.89 1.27-1.5 2.3-1.28.95.2 1.65 1.13 1.57 2.1-.1 1.34-1.62 1.63-2.45 2.88 0 .01-.01.01-.01.02-.01.02-.02.03-.03.05-.09.15-.18.32-.25.5-.01.03-.03.05-.04.08-.01.02-.01.04-.02.07-.12.34-.2.75-.2 1.25h2c0-.42.11-.77.28-1.07.02-.03.03-.06.05-.09.08-.14.18-.27.28-.39.01-.01.02-.03.03-.04.1-.12.21-.23.33-.34.96-.91 2.26-1.65 1.99-3.56-.24-1.74-1.61-3.21-3.35-3.47z"/>
                        </svg>
                        <span>Thinking Partner</span>
                    </div>
                    <div class="question-meta">
                        {#if currentQuestionClass}
                            <span class="question-badge" style={`--badge-color: ${QUESTION_CLASS_LABELS[currentQuestionClass]?.color || '#7a756e'}`}>
                                <span class="badge-emoji">{QUESTION_CLASS_LABELS[currentQuestionClass]?.emoji || '💭'}</span>
                                <span>{QUESTION_CLASS_LABELS[currentQuestionClass]?.label || currentQuestionClass}</span>
                            </span>
                        {/if}
                        {#if lastDetectedState}
                            <span class="state-chip">{lastDetectedState}</span>
                        {/if}
                    </div>
                    <p class="thinking-question">{thinkingQuestion}</p>
                    <div class="response-box">
                        <label for="question-response">Your response</label>
                        <textarea
                            id="question-response"
                            rows="4"
                            bind:value={questionResponse}
                            placeholder="Capture your take or next step..."
                            disabled={isLoadingQuestion}
                        ></textarea>
                        <button
                            class="response-submit"
                            on:click={submitQuestionResponse}
                            disabled={isLoadingQuestion || !questionResponse.trim()}
                        >
                            {#if isLoadingQuestion}
                                <span class="spinner small"></span>
                                <span>Sending...</span>
                            {:else}
                                Submit response
                            {/if}
                        </button>
                    </div>
                </div>
                {#if questionHistory.length > 0}
                    <div class="question-history">
                        <div class="history-header">Recent reflections</div>
                        {#each questionHistory as entry, idx}
                            <div class="history-item" style={`--delay: ${idx * 40}ms`}>
                                <div class="history-question">
                                    {#if entry.questionClass}
                                        <span class="question-badge" style={`--badge-color: ${QUESTION_CLASS_LABELS[entry.questionClass]?.color || '#7a756e'}`}>
                                            <span class="badge-emoji">{QUESTION_CLASS_LABELS[entry.questionClass]?.emoji || '💭'}</span>
                                            <span>{QUESTION_CLASS_LABELS[entry.questionClass]?.label || entry.questionClass}</span>
                                        </span>
                                    {/if}
                                    <p>{entry.question}</p>
                                    {#if entry.state}
                                        <span class="state-chip subtle">{entry.state}</span>
                                    {/if}
                                </div>
                                <p class="history-response">{entry.response}</p>
                            </div>
                        {/each}
                    </div>
                {/if}
            {:else}
                <button
                    class="thinking-btn"
                    on:click={requestThinkingPartner}
                    disabled={isLoadingQuestion}
                >
                    {#if isLoadingQuestion}
                        <span class="spinner small"></span>
                        <span>Contemplating...</span>
                    {:else}
                        <svg viewBox="0 0 24 24" width="18" height="18">
                            <path fill="currentColor" d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 17h-2v-2h2v2zm2.07-7.75l-.9.92C13.45 12.9 13 13.5 13 15h-2v-.5c0-1.1.45-2.1 1.17-2.83l1.24-1.26c.37-.36.59-.86.59-1.41 0-1.1-.9-2-2-2s-2 .9-2 2H8c0-2.21 1.79-4 4-4s4 1.79 4 4c0 .88-.36 1.68-.93 2.25z"/>
                        </svg>
                        <span>Ask Thinking Partner</span>
                    {/if}
                </button>
            {/if}
        </div>
    {/if}
</div>

<style>
    /**
     * FlowMode Styles
     * Uses unified IES Design System tokens from design-system/tokens/
     *
     * Note: Colors, typography, spacing, shadows, and animations are inherited
     * from the design system. Dark theme is handled automatically.
     */

    .flow-mode {
        display: flex;
        flex-direction: column;
        height: 100%;
        padding: var(--ies-space-4);
        gap: var(--ies-space-4);
        background: var(--ies-bg-deep);
        font-family: var(--ies-font-body);
        color: var(--ies-text-primary);
        opacity: 0;
        transform: translateY(8px);
        transition: opacity var(--ies-duration-base) var(--ies-ease-cupertino),
                    transform var(--ies-duration-base) var(--ies-ease-cupertino);
    }

    .flow-mode.mounted {
        opacity: 1;
        transform: translateY(0);
    }

    /* Header */
    .flow-header {
        display: flex;
        align-items: center;
        gap: var(--ies-space-3);
    }

    .back-btn {
        display: flex;
        align-items: center;
        justify-content: center;
        width: 36px;
        height: 36px;
        background: var(--ies-bg-elevated);
        border: 1px solid var(--ies-border-light);
        border-radius: var(--ies-radius-sm);
        cursor: pointer;
        color: var(--ies-text-secondary);
        transition: var(--ies-transition-all);
    }

    .back-btn:hover {
        background: var(--ies-bg-base);
        border-color: var(--ies-accent);
        color: var(--ies-accent);
    }

    .header-title {
        display: flex;
        align-items: center;
        gap: var(--ies-space-2-5);
        flex: 1;
    }

    .flow-icon {
        color: var(--ies-accent);
    }

    .header-title h1 {
        font-family: var(--ies-font-display);
        font-size: var(--ies-text-2xl);
        font-weight: var(--ies-font-semibold);
        margin: 0;
        letter-spacing: var(--ies-tracking-tight);
    }

    .clear-btn {
        display: flex;
        align-items: center;
        gap: var(--ies-space-1-5);
        padding: var(--ies-space-2) var(--ies-space-3);
        font-size: var(--ies-text-sm);
        font-weight: var(--ies-font-semibold);
        background: var(--ies-bg-elevated);
        border: 1px solid var(--ies-border-light);
        border-radius: var(--ies-radius-sm);
        cursor: pointer;
        color: var(--ies-text-muted);
        transition: var(--ies-transition-all);
    }

    .clear-btn:hover {
        background: var(--ies-bg-base);
        border-color: var(--ies-border-medium);
        color: var(--ies-text-secondary);
    }

    /* Search */
    .search-container {
        display: flex;
        gap: var(--ies-space-2-5);
    }

    .search-wrapper {
        flex: 1;
        position: relative;
        display: flex;
        align-items: center;
    }

    .search-icon {
        position: absolute;
        left: var(--ies-space-3-5);
        color: var(--ies-text-subtle);
        pointer-events: none;
    }

    .search-wrapper input {
        width: 100%;
        padding: var(--ies-input-padding-y) var(--ies-space-10) var(--ies-input-padding-y) 44px;
        font-family: var(--ies-font-body);
        font-size: var(--ies-text-base);
        color: var(--ies-text-primary);
        background: var(--ies-bg-elevated);
        border: 1px solid var(--ies-border-light);
        border-radius: var(--ies-radius-input);
        outline: none;
        transition: var(--ies-transition-all);
        box-shadow: var(--ies-shadow-input);
    }

    .search-wrapper input::placeholder {
        color: var(--ies-text-subtle);
    }

    .search-wrapper input:focus {
        border-color: var(--ies-accent);
        box-shadow: var(--ies-shadow-input-focus);
    }

    .search-clear {
        position: absolute;
        right: var(--ies-space-2-5);
        display: flex;
        align-items: center;
        justify-content: center;
        width: 24px;
        height: 24px;
        background: none;
        border: none;
        cursor: pointer;
        color: var(--ies-text-subtle);
        opacity: 0.7;
        transition: opacity var(--ies-duration-fast);
    }

    .search-clear:hover {
        opacity: 1;
    }

    .search-btn {
        padding: var(--ies-button-padding-y) var(--ies-button-padding-x);
        font-family: var(--ies-font-body);
        font-size: var(--ies-text-sm);
        font-weight: var(--ies-font-semibold);
        color: var(--ies-text-inverse);
        background: var(--ies-accent);
        border: none;
        border-radius: var(--ies-radius-button);
        cursor: pointer;
        transition: var(--ies-transition-all);
        min-width: 90px;
        box-shadow: var(--ies-shadow-button);
    }

    .search-btn:hover:not(:disabled) {
        background: var(--ies-accent-hover);
        box-shadow: var(--ies-shadow-button-hover);
    }

    .search-btn:disabled {
        opacity: 0.5;
        cursor: not-allowed;
    }

    /* Results Panel */
    .results-panel {
        background: var(--ies-bg-elevated);
        border: 1px solid var(--ies-border-subtle);
        border-radius: var(--ies-radius-card);
        padding: var(--ies-space-3);
        box-shadow: var(--ies-shadow-sm);
    }

    .results-header {
        margin-bottom: var(--ies-space-2-5);
    }

    .results-label {
        font-size: var(--ies-text-xs);
        font-weight: var(--ies-font-bold);
        letter-spacing: var(--ies-tracking-wider);
        text-transform: uppercase;
        color: var(--ies-text-muted);
    }

    .results-list {
        display: flex;
        flex-direction: column;
        gap: var(--ies-space-1-5);
    }

    .result-card {
        display: flex;
        align-items: center;
        gap: var(--ies-space-2-5);
        padding: var(--ies-space-2-5) var(--ies-space-3-5);
        background: var(--ies-bg-base);
        border: 1px solid var(--ies-border-subtle);
        border-radius: var(--ies-radius-sm);
        cursor: pointer;
        transition: var(--ies-transition-all);
        animation: ies-slide-up var(--ies-duration-base) var(--ies-ease-cupertino) backwards;
        animation-delay: var(--delay);
    }

    .result-card:hover {
        background: var(--ies-accent-subtle);
        border-color: var(--ies-accent-muted);
        transform: translateX(4px);
    }

    .result-indicator {
        width: 4px;
        height: 20px;
        background: var(--type-color);
        border-radius: 2px;
        flex-shrink: 0;
    }

    .result-name {
        flex: 1;
        font-size: var(--ies-text-base);
        font-weight: var(--ies-font-medium);
        color: var(--ies-text-primary);
    }

    .result-type {
        font-size: var(--ies-text-xs);
        font-weight: var(--ies-font-semibold);
        letter-spacing: var(--ies-tracking-wide);
        text-transform: uppercase;
        color: var(--ies-text-muted);
        padding: var(--ies-space-0-5) var(--ies-space-2);
        background: var(--ies-bg-elevated);
        border-radius: var(--ies-radius-sm);
    }

    /* Flow Content */
    .flow-content {
        flex: 1;
        display: flex;
        flex-direction: column;
        gap: var(--ies-space-4);
        overflow-y: auto;
        scrollbar-width: thin;
        scrollbar-color: var(--ies-border-medium) transparent;
    }

    .flow-content::-webkit-scrollbar {
        width: 6px;
    }

    .flow-content::-webkit-scrollbar-track {
        background: transparent;
    }

    .flow-content::-webkit-scrollbar-thumb {
        background: var(--ies-border-medium);
        border-radius: 3px;
    }

    .flow-content::-webkit-scrollbar-thumb:hover {
        background: var(--ies-text-subtle);
    }

    /* Flow States */
    .flow-state {
        flex: 1;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        text-align: center;
        padding: var(--ies-space-8);
    }

    .state-icon {
        color: var(--ies-accent);
        margin-bottom: var(--ies-space-4);
        opacity: 0.8;
    }

    .state-icon.loading svg {
        animation: ies-spin 1s linear infinite;
    }

    .state-title {
        font-family: var(--ies-font-display);
        font-size: var(--ies-text-xl);
        font-weight: var(--ies-font-semibold);
        color: var(--ies-text-primary);
        margin: 0 0 var(--ies-space-2) 0;
    }

    .state-text {
        font-size: var(--ies-text-base);
        color: var(--ies-text-secondary);
        margin: 0 0 var(--ies-space-1) 0;
        max-width: 280px;
        line-height: var(--ies-leading-normal);
    }

    .state-hint {
        font-size: var(--ies-text-sm);
        color: var(--ies-text-muted);
        margin: 0;
        font-style: italic;
    }

    /* Central Concept */
    .concept-center {
        position: relative;
        display: flex;
        justify-content: center;
        padding: var(--ies-space-5);
    }

    .concept-glow {
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        width: 200px;
        height: 200px;
        background: radial-gradient(circle, rgba(var(--ies-accent-rgb), 0.12) 0%, transparent 70%);
        border-radius: 50%;
        pointer-events: none;
        animation: ies-pulse-soft 3s var(--ies-ease-in-out) infinite;
    }

    .concept-core {
        position: relative;
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: var(--ies-space-1);
        padding: var(--ies-space-5) var(--ies-space-8);
        background: var(--ies-bg-elevated);
        border: 2px solid var(--ies-accent);
        border-radius: var(--ies-radius-card);
        box-shadow: var(--ies-shadow-card), 0 0 20px rgba(var(--ies-accent-rgb), 0.1);
        transition: var(--ies-transition-base);
    }

    .concept-center.exploring .concept-core {
        opacity: 0.7;
    }

    .concept-label {
        font-size: var(--ies-text-xs);
        font-weight: var(--ies-font-bold);
        letter-spacing: var(--ies-tracking-wider);
        text-transform: uppercase;
        color: var(--ies-accent);
    }

    .concept-name {
        font-family: var(--ies-font-display);
        font-size: var(--ies-text-xl);
        font-weight: var(--ies-font-semibold);
        color: var(--ies-text-primary);
        margin: 0;
        text-align: center;
    }

    .concept-connections {
        font-size: var(--ies-text-sm);
        color: var(--ies-text-muted);
    }

    .concept-tabs {
        display: inline-flex;
        gap: var(--ies-space-2);
        margin: var(--ies-space-4) auto var(--ies-space-2);
        border-radius: var(--ies-radius-button);
        padding: var(--ies-space-1);
        background: var(--ies-bg-elevated);
        border: 1px solid var(--ies-border-light);
    }

    .tab-btn {
        padding: var(--ies-space-1-5) var(--ies-space-3-5);
        border-radius: var(--ies-radius-button);
        border: none;
        background: transparent;
        font-size: var(--ies-text-sm);
        font-weight: var(--ies-font-semibold);
        color: var(--ies-text-muted);
        cursor: pointer;
        transition: var(--ies-transition-all);
    }

    .tab-btn:hover:not(.active) {
        background: var(--ies-bg-base);
        color: var(--ies-text-secondary);
    }

    .tab-btn.active {
        background: var(--ies-accent-subtle);
        color: var(--ies-accent);
    }

    /* Relationships */
    .relationships {
        display: flex;
        flex-direction: column;
        gap: var(--ies-space-3);
    }

    .rel-group {
        background: var(--ies-bg-elevated);
        border: 1px solid var(--ies-border-subtle);
        border-radius: var(--ies-radius-card);
        padding: var(--ies-space-3);
        animation: ies-slide-up var(--ies-duration-base) var(--ies-ease-cupertino) backwards;
        animation-delay: var(--delay);
    }

    .rel-header {
        display: flex;
        align-items: center;
        gap: var(--ies-space-2);
        padding-bottom: var(--ies-space-2-5);
        margin-bottom: var(--ies-space-2-5);
        border-bottom: 1px solid var(--ies-border-subtle);
    }

    .rel-direction {
        display: flex;
        align-items: center;
        justify-content: center;
        width: 24px;
        height: 24px;
        font-size: var(--ies-text-sm);
        font-weight: var(--ies-font-bold);
        color: var(--ies-secondary);
        background: var(--ies-secondary-subtle);
        border-radius: 50%;
    }

    .rel-direction.outgoing {
        color: var(--ies-accent);
        background: var(--ies-accent-subtle);
    }

    .rel-type {
        flex: 1;
        font-size: var(--ies-text-sm);
        font-weight: var(--ies-font-semibold);
        color: var(--ies-text-secondary);
        text-transform: capitalize;
    }

    .rel-count {
        font-size: var(--ies-text-xs);
        font-weight: var(--ies-font-semibold);
        color: var(--ies-text-muted);
        padding: var(--ies-space-0-5) var(--ies-space-2);
        background: var(--ies-bg-base);
        border-radius: var(--ies-radius-chip);
    }

    .rel-nodes {
        display: flex;
        flex-wrap: wrap;
        gap: var(--ies-space-2);
    }

    .node-chip {
        display: flex;
        align-items: center;
        gap: var(--ies-space-2);
        padding: var(--ies-space-2) var(--ies-space-3);
        background: var(--ies-bg-base);
        border: 1px solid var(--ies-border-light);
        border-radius: var(--ies-radius-chip);
        cursor: pointer;
        transition: var(--ies-transition-all);
        animation: ies-fade-in var(--ies-duration-fast) var(--ies-ease-cupertino) backwards;
        animation-delay: var(--delay);
    }

    .node-chip:hover {
        background: var(--ies-accent-subtle);
        border-color: var(--ies-accent-muted);
        transform: translateY(-1px);
        box-shadow: var(--ies-shadow-xs);
    }

    .node-indicator {
        width: 6px;
        height: 6px;
        background: var(--type-color);
        border-radius: 50%;
        flex-shrink: 0;
    }

    .node-name {
        font-size: var(--ies-text-sm);
        font-weight: var(--ies-font-medium);
        color: var(--ies-text-primary);
    }

    .no-connections {
        text-align: center;
        padding: var(--ies-space-6);
        color: var(--ies-text-muted);
    }

    .no-connections p {
        margin: var(--ies-space-1) 0;
    }

    .no-connections .hint {
        font-style: italic;
        font-size: var(--ies-text-sm);
    }

    /* Path Trail */
    .path-trail {
        display: flex;
        align-items: center;
        gap: var(--ies-space-2-5);
        padding: var(--ies-space-2-5) var(--ies-space-3-5);
        background: var(--ies-bg-elevated);
        border: 1px solid var(--ies-border-subtle);
        border-radius: var(--ies-radius-card);
        overflow-x: auto;
    }

    .path-label {
        font-size: var(--ies-text-xs);
        font-weight: var(--ies-font-bold);
        letter-spacing: var(--ies-tracking-wide);
        text-transform: uppercase;
        color: var(--ies-text-muted);
        flex-shrink: 0;
    }

    .path-steps {
        display: flex;
        align-items: center;
        gap: var(--ies-space-1);
        flex-wrap: wrap;
    }

    .path-step {
        padding: var(--ies-space-1) var(--ies-space-2-5);
        font-family: inherit;
        font-size: var(--ies-text-sm);
        font-weight: var(--ies-font-medium);
        color: var(--ies-text-secondary);
        background: var(--ies-bg-base);
        border: 1px solid var(--ies-border-light);
        border-radius: var(--ies-radius-chip);
        cursor: pointer;
        transition: var(--ies-transition-all);
    }

    .path-step:hover:not(:disabled) {
        background: var(--ies-accent-subtle);
        border-color: var(--ies-accent-muted);
    }

    .path-step.current {
        background: var(--ies-accent-subtle);
        border-color: var(--ies-accent);
        color: var(--ies-accent);
        font-weight: var(--ies-font-semibold);
        cursor: default;
    }

    .path-connector {
        color: var(--ies-text-subtle);
        display: flex;
        align-items: center;
    }

    /* Thinking Section */
    .thinking-section {
        padding-top: var(--ies-space-3);
        border-top: 1px solid var(--ies-border-subtle);
    }

    .thinking-btn {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: var(--ies-space-2-5);
        width: 100%;
        padding: var(--ies-space-3-5) var(--ies-space-5);
        font-family: inherit;
        font-size: var(--ies-text-base);
        font-weight: var(--ies-font-semibold);
        color: var(--ies-text-primary);
        background: var(--ies-bg-elevated);
        border: 1px solid var(--ies-border-light);
        border-radius: var(--ies-radius-card);
        cursor: pointer;
        transition: var(--ies-transition-all);
    }

    .thinking-btn:hover:not(:disabled) {
        background: var(--ies-tertiary-subtle);
        border-color: var(--ies-tertiary);
        color: var(--ies-tertiary);
    }

    .thinking-btn:disabled {
        opacity: 0.7;
        cursor: wait;
    }

    .thinking-card {
        padding: var(--ies-space-4);
        background: var(--ies-tertiary-subtle);
        border: 1px solid var(--ies-tertiary);
        border-radius: var(--ies-radius-card);
        animation: ies-slide-up var(--ies-duration-base) var(--ies-ease-cupertino);
    }

    .thinking-header {
        display: flex;
        align-items: center;
        gap: var(--ies-space-2);
        color: var(--ies-tertiary);
        margin-bottom: var(--ies-space-2-5);
    }

    .thinking-header span {
        font-size: var(--ies-text-xs);
        font-weight: var(--ies-font-bold);
        letter-spacing: var(--ies-tracking-wide);
        text-transform: uppercase;
    }

    .thinking-question {
        font-family: var(--ies-font-display);
        font-size: var(--ies-text-lg);
        font-style: italic;
        line-height: var(--ies-leading-relaxed);
        color: var(--ies-text-primary);
        margin: 0;
    }

    .question-meta {
        display: flex;
        align-items: center;
        gap: 8px;
        margin-bottom: 6px;
        flex-wrap: wrap;
    }

    .question-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 6px 10px;
        background: rgba(0, 0, 0, 0.02);
        border: 1px solid var(--badge-color, #7a756e);
        border-radius: 999px;
        font-size: 0.8125rem;
        font-weight: 700;
        color: var(--badge-color, var(--ies-text-primary));
    }

    .badge-emoji {
        font-size: 1rem;
    }

    .state-chip {
        display: inline-flex;
        align-items: center;
        padding: 4px 8px;
        border-radius: 10px;
        font-size: 0.75rem;
        text-transform: capitalize;
        background: var(--ies-bg-base);
        border: 1px solid var(--ies-border-light);
        color: var(--ies-text-secondary);
    }

    .state-chip.subtle {
        background: var(--ies-bg-elevated);
    }

    .response-box {
        display: flex;
        flex-direction: column;
        gap: 8px;
        margin-top: 12px;
    }

    .response-box label {
        font-size: 0.85rem;
        font-weight: 700;
        color: var(--ies-text-secondary);
    }

    .response-box textarea {
        width: 100%;
        padding: 10px 12px;
        font-family: inherit;
        font-size: 0.9375rem;
        color: var(--ies-text-primary);
        background: var(--ies-bg-elevated);
        border: 1px solid var(--ies-border-light);
        border-radius: var(--ies-radius-sm);
        resize: vertical;
        min-height: 90px;
    }

    .response-box textarea:focus {
        outline: none;
        border-color: var(--ies-tertiary);
        box-shadow: 0 0 0 3px var(--ies-tertiary-light);
    }

    .response-submit {
        align-self: flex-end;
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 10px 14px;
        font-size: 0.9rem;
        font-weight: 700;
        color: white;
        background: var(--ies-tertiary);
        border: none;
        border-radius: var(--ies-radius-sm);
        cursor: pointer;
        transition: all 0.15s ease-out;
    }

    .response-submit:disabled {
        opacity: 0.6;
        cursor: not-allowed;
    }

    .response-submit:not(:disabled):hover {
        background: var(--ies-tertiary-light);
        color: var(--ies-text-primary);
    }

    .question-history {
        margin-top: 12px;
        padding: 12px;
        background: var(--ies-bg-elevated);
        border: 1px solid var(--ies-border-subtle);
        border-radius: var(--ies-radius-md);
        display: flex;
        flex-direction: column;
        gap: 10px;
        box-shadow: var(--ies-shadow-sm);
    }

    .history-header {
        font-size: 0.85rem;
        font-weight: 700;
        color: var(--ies-text-secondary);
    }

    .history-item {
        padding: 10px;
        border-radius: var(--ies-radius-sm);
        background: var(--ies-bg-base);
        border: 1px solid var(--ies-border-subtle);
        animation: slideIn 0.25s ease-out backwards;
        animation-delay: var(--delay);
    }

    .history-question {
        display: flex;
        align-items: center;
        gap: 8px;
        flex-wrap: wrap;
        margin-bottom: 6px;
    }

    .history-question p {
        margin: 0;
        font-weight: 600;
        color: var(--ies-text-primary);
    }

    .history-response {
        margin: 0;
        color: var(--ies-text-secondary);
        line-height: 1.5;
        white-space: pre-wrap;
    }

    /* Spinner */
    .spinner {
        display: inline-block;
        width: 18px;
        height: 18px;
        border: 2px solid rgba(255, 255, 255, 0.3);
        border-top-color: white;
        border-radius: 50%;
        animation: ies-spin 0.8s linear infinite;
    }

    .spinner.small {
        width: 14px;
        height: 14px;
        border-width: 2px;
        border-color: var(--ies-text-muted);
        border-top-color: var(--ies-tertiary);
    }

    /* Note: Animations (ies-spin, ies-slide-up, ies-fade-in, ies-pulse-soft)
       are provided by the unified design system in design-system/tokens/animations.css */
</style>
