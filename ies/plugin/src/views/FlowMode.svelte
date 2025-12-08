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
    import { getBlockKramdown, exportMdContent } from '../api';

    export let backendUrl: string;
    export let journeyId: string | null = null;
    export let initialConcept: string | null = null;
    export let userId: string | null = null;
    export let contextBlockId: string | null = null; // Optional: SiYuan block ID to check for Context Note

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

    // Context Mode State
    interface ParsedContext {
        context_type: string;
        title: string;
        summary: string | null;
        key_questions: string[];
        areas_of_exploration: string[];
        core_concepts: string[];
    }
    interface ContextSearchResult {
        source_id: string;
        source_title: string;
        snippet: string | null;
        relevance_score: number;
        concepts_found: string[];
    }
    let isContextMode = false;
    let parsedContext: ParsedContext | null = null;
    let savedContextId: string | null = null;
    let activeQuestionIndex: number | null = null;
    let contextSearchResults: ContextSearchResult[] = [];
    let isContextSearching = false;
    let isDetectingContext = false;

    // ========== Navigation State Machine (Phase 1) ==========
    type FocusState = 'idle' | 'question' | 'entity' | 'facet';

    interface TrailItem {
        type: 'context' | 'question' | 'entity' | 'facet';
        label: string;
        data?: any; // Store relevant data for navigation back
    }

    interface EntityDetails {
        name: string;
        type: string;
        description?: string;
        neighbors: Array<{name: string, type: string, relationship: string, direction: 'in' | 'out'}>;
        sourceBooks: string[];
    }

    let focusState: FocusState = 'idle';
    let trailStack: TrailItem[] = [];
    let focusedEntity: EntityDetails | null = null;
    let isLoadingEntity = false;

    // ========== Navigation Functions (Phase 1) ==========
    function pushTrail(item: TrailItem) {
        trailStack = [...trailStack, item];
    }

    function popTrail(): TrailItem | undefined {
        if (trailStack.length === 0) return undefined;
        const item = trailStack[trailStack.length - 1];
        trailStack = trailStack.slice(0, -1);
        return item;
    }

    function navigateToTrailIndex(index: number) {
        if (index < 0 || index >= trailStack.length) return;

        const targetItem = trailStack[index];
        // Truncate trail to this index
        trailStack = trailStack.slice(0, index + 1);

        // Restore state based on item type
        if (targetItem.type === 'context') {
            focusState = 'idle';
            focusedEntity = null;
            activeQuestionIndex = null;
        } else if (targetItem.type === 'question') {
            focusState = 'question';
            focusedEntity = null;
            // Re-select the question if data available
            if (targetItem.data?.questionIndex !== undefined) {
                selectQuestion(targetItem.data.questionIndex);
            }
        } else if (targetItem.type === 'entity') {
            focusState = 'entity';
            if (targetItem.data?.entityName) {
                navigateToEntity(targetItem.data.entityName, false); // Don't push to trail again
            }
        }
    }

    async function navigateToEntity(entityName: string, addToTrail = true) {
        isLoadingEntity = true;
        focusState = 'entity';

        try {
            // Fetch entity details from graph API
            const data = await apiGet(`/graph/explore/${encodeURIComponent(entityName)}?depth=1`);

            // Build EntityDetails from response
            const neighbors: EntityDetails['neighbors'] = [];
            for (const rel of (data.relationships || [])) {
                if (rel.start === entityName) {
                    neighbors.push({
                        name: rel.end,
                        type: data.nodes?.find(n => n.name === rel.end)?.type || 'Unknown',
                        relationship: rel.type,
                        direction: 'out'
                    });
                } else if (rel.end === entityName) {
                    neighbors.push({
                        name: rel.start,
                        type: data.nodes?.find(n => n.name === rel.start)?.type || 'Unknown',
                        relationship: rel.type,
                        direction: 'in'
                    });
                }
            }

            // Extract source books from neighbors or node data
            const sourceBooks: string[] = data.nodes
                ?.filter(n => n.labels?.includes('Book'))
                ?.map(n => n.name) || [];

            focusedEntity = {
                name: entityName,
                type: data.nodes?.find(n => n.name === entityName)?.type || 'Concept',
                description: data.nodes?.find(n => n.name === entityName)?.description,
                neighbors,
                sourceBooks
            };

            // Also update the regular exploration state for compatibility
            currentConcept = entityName;
            nodes = data.nodes || [];
            relationships = data.relationships || [];

            if (addToTrail) {
                pushTrail({
                    type: 'entity',
                    label: entityName,
                    data: { entityName }
                });
            }

            // Track exploration
            const now = new Date().toISOString();
            if (!explorationPath.includes(entityName)) {
                explorationPath = [...explorationPath, entityName];
                explorationTimestamps = [...explorationTimestamps, now];
            }
        } catch (err) {
            showMessage(`Failed to load entity: ${err.message}`, 5000, 'error');
            focusState = trailStack.length > 0 ? 'question' : 'idle';
        } finally {
            isLoadingEntity = false;
        }
    }

    function navigateBack() {
        if (trailStack.length <= 1) {
            // Back to idle state
            focusState = 'idle';
            focusedEntity = null;
            trailStack = [];
            return;
        }

        // Pop current item and go to previous
        popTrail();
        const previousItem = trailStack[trailStack.length - 1];

        if (previousItem.type === 'question') {
            focusState = 'question';
            focusedEntity = null;
        } else if (previousItem.type === 'context') {
            focusState = 'idle';
            focusedEntity = null;
        }
    }

    function initializeContextTrail() {
        if (parsedContext && trailStack.length === 0) {
            pushTrail({
                type: 'context',
                label: parsedContext.title || 'Context',
                data: { contextId: savedContextId }
            });
        }
    }

    onMount(() => {
        mounted = true;
        if (journeyId) {
            loadJourney(journeyId);
        } else if (initialConcept) {
            exploreConcept(initialConcept);
        } else if (contextBlockId) {
            detectContextNote(contextBlockId);
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

    // ========== Context Mode Functions ==========

    /**
     * Detect if a SiYuan document is a Context Note by parsing its markdown
     */
    async function detectContextNote(blockId: string) {
        isDetectingContext = true;
        try {
            // Get the markdown content of the document
            const mdResult = await exportMdContent(blockId);
            if (!mdResult || !mdResult.content) {
                console.log('[IES] No markdown content found for block', blockId);
                return;
            }

            const markdown = mdResult.content;

            // Call our backend parser to detect if this is a Context Note
            const parseResult = await apiPost('/context/parse', {
                siyuan_block_id: blockId,
                markdown: markdown
            });

            if (parseResult.is_context_note) {
                // It's a Context Note!
                isContextMode = true;
                parsedContext = {
                    context_type: parseResult.context_type,
                    title: parseResult.title,
                    summary: parseResult.summary,
                    key_questions: parseResult.key_questions || [],
                    areas_of_exploration: parseResult.areas_of_exploration || [],
                    core_concepts: parseResult.core_concepts || []
                };

                // If there's an existing context_id, use it; otherwise it will be assigned on first save
                savedContextId = parseResult.context_id || null;

                showMessage(`Context Note detected: ${parsedContext.title}`, 3000);
            } else {
                console.log('[IES] Document is not a Context Note');
            }
        } catch (err) {
            console.error('[IES] Error detecting Context Note:', err);
            showMessage(`Failed to detect Context Note: ${err.message}`, 5000, 'error');
        } finally {
            isDetectingContext = false;
        }
    }

    /**
     * Search for entities/snippets related to a Key Question
     */
    async function searchForQuestion(questionIndex: number) {
        if (!parsedContext) return;

        const question = parsedContext.key_questions[questionIndex];
        if (!question) return;

        // Initialize trail with context if first time
        initializeContextTrail();

        // Set navigation state
        focusState = 'question';
        focusedEntity = null;

        // Push question to trail (remove previous question if navigating between questions)
        const lastTrailItem = trailStack[trailStack.length - 1];
        if (lastTrailItem?.type === 'question') {
            // Replace the question in trail
            trailStack = trailStack.slice(0, -1);
        }
        pushTrail({
            type: 'question',
            label: question.length > 40 ? question.substring(0, 40) + '...' : question,
            data: { questionIndex, questionText: question }
        });

        activeQuestionIndex = questionIndex;
        isContextSearching = true;
        contextSearchResults = [];

        try {
            // First, save the parsed context if we don't have an ID yet
            if (!savedContextId) {
                const saveResult = await apiPost('/context/save-parsed', {
                    siyuan_block_id: contextBlockId,
                    context_type: parsedContext.context_type,
                    title: parsedContext.title,
                    summary: parsedContext.summary,
                    key_questions: parsedContext.key_questions,
                    areas_of_exploration: parsedContext.areas_of_exploration,
                    core_concepts: parsedContext.core_concepts
                });
                savedContextId = saveResult.id;
            }

            // Now search using the context
            const searchResult = await apiPost(`/context/${savedContextId}/search`, {
                question_text: question,
                include_areas: false,
                limit: 20
            });

            if (searchResult.results && searchResult.results.length > 0) {
                contextSearchResults = searchResult.results;
            } else {
                showMessage('No relevant entities found for this question', 3000);
            }
        } catch (err) {
            console.error('[IES] Context search error:', err);
            showMessage(`Search failed: ${err.message}`, 5000, 'error');
        } finally {
            isContextSearching = false;
        }
    }

    /**
     * Clear context mode and return to normal Flow
     */
    function clearContextMode() {
        isContextMode = false;
        parsedContext = null;
        savedContextId = null;
        activeQuestionIndex = null;
        contextSearchResults = [];
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
            case 'Theory': return 'var(--entity-theory)';
            case 'Researcher': return 'var(--entity-framework)';
            case 'Concept': return 'var(--entity-concept)';
            default: return 'var(--text-muted)';
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

    <!-- Context Panel (Question-Driven Exploration) -->
    {#if isContextMode && parsedContext}
        <div class="context-panel">
            <div class="context-header">
                <div class="context-info">
                    <span class="context-type-badge">{parsedContext.context_type.replace('_', ' ')}</span>
                    <h2 class="context-title">{parsedContext.title}</h2>
                    {#if parsedContext.summary}
                        <p class="context-summary">{parsedContext.summary}</p>
                    {/if}
                </div>
                <button class="context-close" on:click={clearContextMode} title="Exit Context Mode">
                    <svg viewBox="0 0 24 24" width="16" height="16">
                        <path fill="currentColor" d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/>
                    </svg>
                </button>
            </div>

            <!-- Trail Navigation (Breadcrumbs) -->
            {#if trailStack.length > 0}
                <div class="trail-nav">
                    <div class="trail-breadcrumbs">
                        {#each trailStack as item, i}
                            {#if i > 0}
                                <span class="trail-separator">›</span>
                            {/if}
                            <button
                                class="trail-item"
                                class:active={i === trailStack.length - 1}
                                class:type-context={item.type === 'context'}
                                class:type-question={item.type === 'question'}
                                class:type-entity={item.type === 'entity'}
                                on:click={() => navigateToTrailIndex(i)}
                            >
                                {#if item.type === 'context'}
                                    <span class="trail-icon">📍</span>
                                {:else if item.type === 'question'}
                                    <span class="trail-icon">❓</span>
                                {:else if item.type === 'entity'}
                                    <span class="trail-icon">🔷</span>
                                {/if}
                                <span class="trail-label">{item.label}</span>
                            </button>
                        {/each}
                    </div>
                    {#if trailStack.length > 1}
                        <button class="trail-back" on:click={navigateBack} title="Go Back">
                            <svg viewBox="0 0 24 24" width="16" height="16">
                                <path fill="currentColor" d="M20 11H7.83l5.59-5.59L12 4l-8 8 8 8 1.41-1.41L7.83 13H20v-2z"/>
                            </svg>
                        </button>
                    {/if}
                </div>
            {/if}

            <!-- Entity Focus View -->
            {#if focusState === 'entity' && focusedEntity}
                <div class="entity-focus">
                    <div class="entity-focus-header">
                        <div class="entity-type-badge">{focusedEntity.type}</div>
                        <h3 class="entity-name">{focusedEntity.name}</h3>
                    </div>
                    {#if focusedEntity.description}
                        <p class="entity-description">{focusedEntity.description}</p>
                    {/if}

                    {#if isLoadingEntity}
                        <div class="entity-loading">
                            <span class="spinner"></span>
                            Loading entity details...
                        </div>
                    {:else}
                        <!-- Neighbors Section -->
                        {#if focusedEntity.neighbors.length > 0}
                            <div class="entity-section">
                                <h4 class="entity-section-title">Related Concepts ({focusedEntity.neighbors.length})</h4>
                                <div class="entity-neighbors">
                                    {#each focusedEntity.neighbors as neighbor}
                                        <button
                                            class="neighbor-card"
                                            on:click={() => navigateToEntity(neighbor.name)}
                                        >
                                            <span class="neighbor-relationship" class:incoming={neighbor.direction === 'in'} class:outgoing={neighbor.direction === 'out'}>
                                                {neighbor.direction === 'in' ? '←' : '→'} {neighbor.relationship}
                                            </span>
                                            <span class="neighbor-name">{neighbor.name}</span>
                                            <span class="neighbor-type">{neighbor.type}</span>
                                        </button>
                                    {/each}
                                </div>
                            </div>
                        {/if}

                        <!-- Source Books Section -->
                        {#if focusedEntity.sourceBooks.length > 0}
                            <div class="entity-section">
                                <h4 class="entity-section-title">Source Books</h4>
                                <div class="entity-sources">
                                    {#each focusedEntity.sourceBooks as book}
                                        <span class="source-book">{book}</span>
                                    {/each}
                                </div>
                            </div>
                        {/if}
                    {/if}

                    <!-- Back to Question Button -->
                    <button class="back-to-question" on:click={navigateBack}>
                        <svg viewBox="0 0 24 24" width="14" height="14">
                            <path fill="currentColor" d="M20 11H7.83l5.59-5.59L12 4l-8 8 8 8 1.41-1.41L7.83 13H20v-2z"/>
                        </svg>
                        Back to Question
                    </button>
                </div>
            {/if}

            <!-- Key Questions Section (show when not in entity focus) -->
            {#if focusState !== 'entity' && parsedContext.key_questions.length > 0}
                <div class="context-section">
                    <h3 class="section-title">Key Questions</h3>
                    <div class="question-buttons">
                        {#each parsedContext.key_questions as question, i}
                            <button
                                class="question-btn"
                                class:active={activeQuestionIndex === i}
                                class:searching={activeQuestionIndex === i && isContextSearching}
                                on:click={() => searchForQuestion(i)}
                            >
                                <span class="question-number">Q{i + 1}</span>
                                <span class="question-text">{question}</span>
                                {#if activeQuestionIndex === i && isContextSearching}
                                    <span class="question-spinner"></span>
                                {/if}
                            </button>
                        {/each}
                    </div>
                </div>
            {/if}

            <!-- Areas of Exploration Section (hide when in entity focus) -->
            {#if focusState !== 'entity' && parsedContext.areas_of_exploration.length > 0}
                <div class="context-section">
                    <h3 class="section-title">Areas of Exploration</h3>
                    <div class="area-chips">
                        {#each parsedContext.areas_of_exploration as area}
                            <span class="area-chip">{area}</span>
                        {/each}
                    </div>
                </div>
            {/if}

            <!-- Core Concepts Section (hide when in entity focus) -->
            {#if focusState !== 'entity' && parsedContext.core_concepts.length > 0}
                <div class="context-section">
                    <h3 class="section-title">Core Concepts</h3>
                    <div class="concept-chips">
                        {#each parsedContext.core_concepts as concept}
                            <button class="concept-chip" on:click={() => navigateToEntity(concept)}>
                                {concept}
                            </button>
                        {/each}
                    </div>
                </div>
            {/if}

            <!-- Context Search Results (hide when in entity focus) -->
            {#if focusState !== 'entity' && contextSearchResults.length > 0}
                <div class="context-section context-results">
                    <h3 class="section-title">
                        Related Entities
                        <span class="results-count">{contextSearchResults.length}</span>
                    </h3>
                    <div class="context-results-list">
                        {#each contextSearchResults as result, i}
                            <button
                                class="context-result-card"
                                style="--delay: {i * 30}ms"
                                on:click={() => navigateToEntity(result.entity_name)}
                            >
                                <div class="result-main">
                                    <span class="result-entity">{result.entity_name}</span>
                                    <span class="result-type-badge">{result.entity_type}</span>
                                </div>
                                {#if result.snippet}
                                    <p class="result-snippet">{result.snippet}</p>
                                {/if}
                                {#if result.source_title}
                                    <span class="result-source">{result.source_title}</span>
                                {/if}
                            </button>
                        {/each}
                    </div>
                </div>
            {/if}
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
        padding: var(--space-4);
        gap: var(--space-4);
        background: var(--bg-primary);
        font-family: var(--font-sans);
        color: var(--text-primary);
        opacity: 0;
        transform: translateY(8px);
        transition: opacity var(--duration-base) var(--ease-out),
                    transform var(--duration-base) var(--ease-out);
    }

    .flow-mode.mounted {
        opacity: 1;
        transform: translateY(0);
    }

    /* Header */
    .flow-header {
        display: flex;
        align-items: center;
        gap: var(--space-3);
    }

    .back-btn {
        display: flex;
        align-items: center;
        justify-content: center;
        width: 36px;
        height: 36px;
        background: var(--bg-tertiary);
        border: 1px solid var(--border-default);
        border-radius: var(--radius-sm);
        cursor: pointer;
        color: var(--text-secondary);
        transition: var(--transition-all);
    }

    .back-btn:hover {
        background: var(--bg-secondary);
        border-color: var(--entity-concept);
        color: var(--entity-concept);
    }

    .header-title {
        display: flex;
        align-items: center;
        gap: var(--space-2-5);
        flex: 1;
    }

    .flow-icon {
        color: var(--entity-concept);
    }

    .header-title h1 {
        font-family: var(--font-sans);
        font-size: var(--text-2xl);
        font-weight: var(--font-semibold);
        margin: 0;
        letter-spacing: var(--tracking-tight);
    }

    .clear-btn {
        display: flex;
        align-items: center;
        gap: var(--space-1-5);
        padding: var(--space-2) var(--space-3);
        font-size: var(--text-sm);
        font-weight: var(--font-semibold);
        background: var(--bg-tertiary);
        border: 1px solid var(--border-default);
        border-radius: var(--radius-sm);
        cursor: pointer;
        color: var(--text-muted);
        transition: var(--transition-all);
    }

    .clear-btn:hover {
        background: var(--bg-secondary);
        border-color: var(--border-default);
        color: var(--text-secondary);
    }

    /* Search */
    .search-container {
        display: flex;
        gap: var(--space-2-5);
    }

    .search-wrapper {
        flex: 1;
        position: relative;
        display: flex;
        align-items: center;
    }

    .search-icon {
        position: absolute;
        left: var(--space-3-5);
        color: var(--text-muted);
        pointer-events: none;
    }

    .search-wrapper input {
        width: 100%;
        padding: var(--input-padding-y) var(--space-10) var(--input-padding-y) 44px;
        font-family: var(--font-sans);
        font-size: var(--text-base);
        color: var(--text-primary);
        background: var(--bg-tertiary);
        border: 1px solid var(--border-default);
        border-radius: var(--radius-input);
        outline: none;
        transition: var(--transition-all);
        box-shadow: var(--shadow-input);
    }

    .search-wrapper input::placeholder {
        color: var(--text-muted);
    }

    .search-wrapper input:focus {
        border-color: var(--entity-concept);
        box-shadow: var(--shadow-input-focus);
    }

    .search-clear {
        position: absolute;
        right: var(--space-2-5);
        display: flex;
        align-items: center;
        justify-content: center;
        width: 24px;
        height: 24px;
        background: none;
        border: none;
        cursor: pointer;
        color: var(--text-muted);
        opacity: 0.7;
        transition: opacity var(--duration-fast);
    }

    .search-clear:hover {
        opacity: 1;
    }

    .search-btn {
        padding: var(--button-padding-y) var(--button-padding-x);
        font-family: var(--font-sans);
        font-size: var(--text-sm);
        font-weight: var(--font-semibold);
        color: var(--text-inverse);
        background: var(--entity-concept);
        border: none;
        border-radius: var(--radius-button);
        cursor: pointer;
        transition: var(--transition-all);
        min-width: 90px;
        box-shadow: var(--shadow-button);
    }

    .search-btn:hover:not(:disabled) {
        background: var(--entity-concept-hover);
        box-shadow: var(--shadow-button-hover);
    }

    .search-btn:disabled {
        opacity: 0.5;
        cursor: not-allowed;
    }

    /* Results Panel */
    .results-panel {
        background: var(--bg-tertiary);
        border: 1px solid var(--border-subtle);
        border-radius: var(--radius-card);
        padding: var(--space-3);
        box-shadow: var(--shadow-sm);
    }

    .results-header {
        margin-bottom: var(--space-2-5);
    }

    .results-label {
        font-size: var(--text-xs);
        font-weight: var(--font-bold);
        letter-spacing: var(--tracking-wider);
        text-transform: uppercase;
        color: var(--text-muted);
    }

    .results-list {
        display: flex;
        flex-direction: column;
        gap: var(--space-1-5);
    }

    .result-card {
        display: flex;
        align-items: center;
        gap: var(--space-2-5);
        padding: var(--space-2-5) var(--space-3-5);
        background: var(--bg-secondary);
        border: 1px solid var(--border-subtle);
        border-radius: var(--radius-sm);
        cursor: pointer;
        transition: var(--transition-all);
        animation: ies-slide-up var(--duration-base) var(--ease-out) backwards;
        animation-delay: var(--delay);
    }

    .result-card:hover {
        background: var(--entity-concept-subtle);
        border-color: var(--entity-concept-muted);
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
        font-size: var(--text-base);
        font-weight: var(--font-medium);
        color: var(--text-primary);
    }

    .result-type {
        font-size: var(--text-xs);
        font-weight: var(--font-semibold);
        letter-spacing: var(--tracking-wide);
        text-transform: uppercase;
        color: var(--text-muted);
        padding: var(--space-0-5) var(--space-2);
        background: var(--bg-tertiary);
        border-radius: var(--radius-sm);
    }

    /* Flow Content */
    .flow-content {
        flex: 1;
        display: flex;
        flex-direction: column;
        gap: var(--space-4);
        overflow-y: auto;
        scrollbar-width: thin;
        scrollbar-color: var(--border-default) transparent;
    }

    .flow-content::-webkit-scrollbar {
        width: 6px;
    }

    .flow-content::-webkit-scrollbar-track {
        background: transparent;
    }

    .flow-content::-webkit-scrollbar-thumb {
        background: var(--border-default);
        border-radius: 3px;
    }

    .flow-content::-webkit-scrollbar-thumb:hover {
        background: var(--text-muted);
    }

    /* Flow States */
    .flow-state {
        flex: 1;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        text-align: center;
        padding: var(--space-8);
    }

    .state-icon {
        color: var(--entity-concept);
        margin-bottom: var(--space-4);
        opacity: 0.8;
    }

    .state-icon.loading svg {
        animation: ies-spin 1s linear infinite;
    }

    .state-title {
        font-family: var(--font-sans);
        font-size: var(--text-xl);
        font-weight: var(--font-semibold);
        color: var(--text-primary);
        margin: 0 0 var(--space-2) 0;
    }

    .state-text {
        font-size: var(--text-base);
        color: var(--text-secondary);
        margin: 0 0 var(--space-1) 0;
        max-width: 280px;
        line-height: var(--leading-normal);
    }

    .state-hint {
        font-size: var(--text-sm);
        color: var(--text-muted);
        margin: 0;
        font-style: italic;
    }

    /* Central Concept */
    .concept-center {
        position: relative;
        display: flex;
        justify-content: center;
        padding: var(--space-5);
    }

    .concept-glow {
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        width: 200px;
        height: 200px;
        background: radial-gradient(circle, rgba(var(--entity-concept-rgb), 0.12) 0%, transparent 70%);
        border-radius: 50%;
        pointer-events: none;
        animation: pulse-soft 3s var(--ease-in-out) infinite;
    }

    .concept-core {
        position: relative;
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: var(--space-1);
        padding: var(--space-5) var(--space-8);
        background: var(--bg-tertiary);
        border: 2px solid var(--entity-concept);
        border-radius: var(--radius-card);
        box-shadow: var(--shadow-card), 0 0 20px rgba(var(--entity-concept-rgb), 0.1);
        transition: var(--transition-base);
    }

    .concept-center.exploring .concept-core {
        opacity: 0.7;
    }

    .concept-label {
        font-size: var(--text-xs);
        font-weight: var(--font-bold);
        letter-spacing: var(--tracking-wider);
        text-transform: uppercase;
        color: var(--entity-concept);
    }

    .concept-name {
        font-family: var(--font-sans);
        font-size: var(--text-xl);
        font-weight: var(--font-semibold);
        color: var(--text-primary);
        margin: 0;
        text-align: center;
    }

    .concept-connections {
        font-size: var(--text-sm);
        color: var(--text-muted);
    }

    .concept-tabs {
        display: inline-flex;
        gap: var(--space-2);
        margin: var(--space-4) auto var(--space-2);
        border-radius: var(--radius-button);
        padding: var(--space-1);
        background: var(--bg-tertiary);
        border: 1px solid var(--border-default);
    }

    .tab-btn {
        padding: var(--space-1-5) var(--space-3-5);
        border-radius: var(--radius-button);
        border: none;
        background: transparent;
        font-size: var(--text-sm);
        font-weight: var(--font-semibold);
        color: var(--text-muted);
        cursor: pointer;
        transition: var(--transition-all);
    }

    .tab-btn:hover:not(.active) {
        background: var(--bg-secondary);
        color: var(--text-secondary);
    }

    .tab-btn.active {
        background: var(--entity-concept-subtle);
        color: var(--entity-concept);
    }

    /* Relationships */
    .relationships {
        display: flex;
        flex-direction: column;
        gap: var(--space-3);
    }

    .rel-group {
        background: var(--bg-tertiary);
        border: 1px solid var(--border-subtle);
        border-radius: var(--radius-card);
        padding: var(--space-3);
        animation: ies-slide-up var(--duration-base) var(--ease-out) backwards;
        animation-delay: var(--delay);
    }

    .rel-header {
        display: flex;
        align-items: center;
        gap: var(--space-2);
        padding-bottom: var(--space-2-5);
        margin-bottom: var(--space-2-5);
        border-bottom: 1px solid var(--border-subtle);
    }

    .rel-direction {
        display: flex;
        align-items: center;
        justify-content: center;
        width: 24px;
        height: 24px;
        font-size: var(--text-sm);
        font-weight: var(--font-bold);
        color: var(--entity-theory);
        background: var(--entity-theory-subtle);
        border-radius: 50%;
    }

    .rel-direction.outgoing {
        color: var(--entity-concept);
        background: var(--entity-concept-subtle);
    }

    .rel-type {
        flex: 1;
        font-size: var(--text-sm);
        font-weight: var(--font-semibold);
        color: var(--text-secondary);
        text-transform: capitalize;
    }

    .rel-count {
        font-size: var(--text-xs);
        font-weight: var(--font-semibold);
        color: var(--text-muted);
        padding: var(--space-0-5) var(--space-2);
        background: var(--bg-secondary);
        border-radius: var(--radius-chip);
    }

    .rel-nodes {
        display: flex;
        flex-wrap: wrap;
        gap: var(--space-2);
    }

    .node-chip {
        display: flex;
        align-items: center;
        gap: var(--space-2);
        padding: var(--space-2) var(--space-3);
        background: var(--bg-secondary);
        border: 1px solid var(--border-default);
        border-radius: var(--radius-chip);
        cursor: pointer;
        transition: var(--transition-all);
        animation: ies-fade-in var(--duration-fast) var(--ease-out) backwards;
        animation-delay: var(--delay);
    }

    .node-chip:hover {
        background: var(--entity-concept-subtle);
        border-color: var(--entity-concept-muted);
        transform: translateY(-1px);
        box-shadow: var(--shadow-xs);
    }

    .node-indicator {
        width: 6px;
        height: 6px;
        background: var(--type-color);
        border-radius: 50%;
        flex-shrink: 0;
    }

    .node-name {
        font-size: var(--text-sm);
        font-weight: var(--font-medium);
        color: var(--text-primary);
    }

    .no-connections {
        text-align: center;
        padding: var(--space-6);
        color: var(--text-muted);
    }

    .no-connections p {
        margin: var(--space-1) 0;
    }

    .no-connections .hint {
        font-style: italic;
        font-size: var(--text-sm);
    }

    /* Path Trail */
    .path-trail {
        display: flex;
        align-items: center;
        gap: var(--space-2-5);
        padding: var(--space-2-5) var(--space-3-5);
        background: var(--bg-tertiary);
        border: 1px solid var(--border-subtle);
        border-radius: var(--radius-card);
        overflow-x: auto;
    }

    .path-label {
        font-size: var(--text-xs);
        font-weight: var(--font-bold);
        letter-spacing: var(--tracking-wide);
        text-transform: uppercase;
        color: var(--text-muted);
        flex-shrink: 0;
    }

    .path-steps {
        display: flex;
        align-items: center;
        gap: var(--space-1);
        flex-wrap: wrap;
    }

    .path-step {
        padding: var(--space-1) var(--space-2-5);
        font-family: inherit;
        font-size: var(--text-sm);
        font-weight: var(--font-medium);
        color: var(--text-secondary);
        background: var(--bg-secondary);
        border: 1px solid var(--border-default);
        border-radius: var(--radius-chip);
        cursor: pointer;
        transition: var(--transition-all);
    }

    .path-step:hover:not(:disabled) {
        background: var(--entity-concept-subtle);
        border-color: var(--entity-concept-muted);
    }

    .path-step.current {
        background: var(--entity-concept-subtle);
        border-color: var(--entity-concept);
        color: var(--entity-concept);
        font-weight: var(--font-semibold);
        cursor: default;
    }

    .path-connector {
        color: var(--text-muted);
        display: flex;
        align-items: center;
    }

    /* Thinking Section */
    .thinking-section {
        padding-top: var(--space-3);
        border-top: 1px solid var(--border-subtle);
    }

    .thinking-btn {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: var(--space-2-5);
        width: 100%;
        padding: var(--space-3-5) var(--space-5);
        font-family: inherit;
        font-size: var(--text-base);
        font-weight: var(--font-semibold);
        color: var(--text-primary);
        background: var(--bg-tertiary);
        border: 1px solid var(--border-default);
        border-radius: var(--radius-card);
        cursor: pointer;
        transition: var(--transition-all);
    }

    .thinking-btn:hover:not(:disabled) {
        background: var(--entity-framework-subtle);
        border-color: var(--entity-framework);
        color: var(--entity-framework);
    }

    .thinking-btn:disabled {
        opacity: 0.7;
        cursor: wait;
    }

    .thinking-card {
        padding: var(--space-4);
        background: var(--entity-framework-subtle);
        border: 1px solid var(--entity-framework);
        border-radius: var(--radius-card);
        animation: ies-slide-up var(--duration-base) var(--ease-out);
    }

    .thinking-header {
        display: flex;
        align-items: center;
        gap: var(--space-2);
        color: var(--entity-framework);
        margin-bottom: var(--space-2-5);
    }

    .thinking-header span {
        font-size: var(--text-xs);
        font-weight: var(--font-bold);
        letter-spacing: var(--tracking-wide);
        text-transform: uppercase;
    }

    .thinking-question {
        font-family: var(--font-sans);
        font-size: var(--text-lg);
        font-style: italic;
        line-height: var(--leading-relaxed);
        color: var(--text-primary);
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
        color: var(--badge-color, var(--text-primary));
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
        background: var(--bg-secondary);
        border: 1px solid var(--border-default);
        color: var(--text-secondary);
    }

    .state-chip.subtle {
        background: var(--bg-tertiary);
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
        color: var(--text-secondary);
    }

    .response-box textarea {
        width: 100%;
        padding: 10px 12px;
        font-family: inherit;
        font-size: 0.9375rem;
        color: var(--text-primary);
        background: var(--bg-tertiary);
        border: 1px solid var(--border-default);
        border-radius: var(--radius-sm);
        resize: vertical;
        min-height: 90px;
    }

    .response-box textarea:focus {
        outline: none;
        border-color: var(--entity-framework);
        box-shadow: 0 0 0 3px var(--entity-framework-light);
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
        background: var(--entity-framework);
        border: none;
        border-radius: var(--radius-sm);
        cursor: pointer;
        transition: all 0.15s ease-out;
    }

    .response-submit:disabled {
        opacity: 0.6;
        cursor: not-allowed;
    }

    .response-submit:not(:disabled):hover {
        background: var(--entity-framework-light);
        color: var(--text-primary);
    }

    .question-history {
        margin-top: 12px;
        padding: 12px;
        background: var(--bg-tertiary);
        border: 1px solid var(--border-subtle);
        border-radius: var(--radius-md);
        display: flex;
        flex-direction: column;
        gap: 10px;
        box-shadow: var(--shadow-sm);
    }

    .history-header {
        font-size: 0.85rem;
        font-weight: 700;
        color: var(--text-secondary);
    }

    .history-item {
        padding: 10px;
        border-radius: var(--radius-sm);
        background: var(--bg-secondary);
        border: 1px solid var(--border-subtle);
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
        color: var(--text-primary);
    }

    .history-response {
        margin: 0;
        color: var(--text-secondary);
        line-height: 1.5;
        white-space: pre-wrap;
    }

    /* ========== Context Panel Styles ========== */
    .context-panel {
        background: var(--bg-secondary);
        border: 1px solid var(--border-default);
        border-radius: var(--radius-lg);
        padding: var(--space-4);
        display: flex;
        flex-direction: column;
        gap: var(--space-4);
        animation: ies-slide-up 0.3s ease-out;
    }

    .context-header {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        gap: var(--space-3);
    }

    .context-info {
        flex: 1;
        display: flex;
        flex-direction: column;
        gap: var(--space-2);
    }

    .context-type-badge {
        display: inline-block;
        padding: var(--space-1) var(--space-2);
        font-size: var(--text-xs);
        font-weight: var(--font-semibold);
        text-transform: uppercase;
        letter-spacing: 0.05em;
        background: var(--entity-concept);
        color: white;
        border-radius: var(--radius-sm);
        width: fit-content;
    }

    .context-title {
        margin: 0;
        font-size: var(--text-lg);
        font-weight: var(--font-semibold);
        color: var(--text-primary);
    }

    .context-summary {
        margin: 0;
        font-size: var(--text-sm);
        color: var(--text-secondary);
        line-height: 1.5;
    }

    .context-close {
        display: flex;
        align-items: center;
        justify-content: center;
        width: 28px;
        height: 28px;
        background: var(--bg-tertiary);
        border: 1px solid var(--border-default);
        border-radius: var(--radius-sm);
        cursor: pointer;
        color: var(--text-muted);
        transition: var(--transition-all);
    }

    .context-close:hover {
        background: var(--bg-primary);
        border-color: var(--text-muted);
        color: var(--text-secondary);
    }

    .context-section {
        display: flex;
        flex-direction: column;
        gap: var(--space-2);
    }

    .context-section .section-title {
        margin: 0;
        font-size: var(--text-sm);
        font-weight: var(--font-semibold);
        color: var(--text-secondary);
        display: flex;
        align-items: center;
        gap: var(--space-2);
    }

    .results-count {
        font-size: var(--text-xs);
        padding: 2px 6px;
        background: var(--entity-concept);
        color: white;
        border-radius: var(--radius-full);
    }

    /* Question Buttons */
    .question-buttons {
        display: flex;
        flex-direction: column;
        gap: var(--space-2);
    }

    .question-btn {
        display: flex;
        align-items: flex-start;
        gap: var(--space-2);
        padding: var(--space-3);
        background: var(--bg-tertiary);
        border: 1px solid var(--border-subtle);
        border-radius: var(--radius-md);
        cursor: pointer;
        text-align: left;
        transition: var(--transition-all);
    }

    .question-btn:hover {
        background: var(--bg-primary);
        border-color: var(--entity-concept);
    }

    .question-btn.active {
        background: var(--bg-primary);
        border-color: var(--entity-concept);
        box-shadow: 0 0 0 2px rgba(37, 99, 235, 0.15);
    }

    .question-btn.searching {
        opacity: 0.8;
        pointer-events: none;
    }

    .question-number {
        flex-shrink: 0;
        display: flex;
        align-items: center;
        justify-content: center;
        width: 24px;
        height: 24px;
        font-size: var(--text-xs);
        font-weight: var(--font-bold);
        background: var(--entity-concept);
        color: white;
        border-radius: var(--radius-full);
    }

    .question-text {
        flex: 1;
        font-size: var(--text-sm);
        color: var(--text-primary);
        line-height: 1.5;
    }

    .question-spinner {
        flex-shrink: 0;
        width: 16px;
        height: 16px;
        border: 2px solid var(--border-default);
        border-top-color: var(--entity-concept);
        border-radius: 50%;
        animation: ies-spin 0.8s linear infinite;
    }

    /* Area Chips */
    .area-chips {
        display: flex;
        flex-wrap: wrap;
        gap: var(--space-2);
    }

    .area-chip {
        padding: var(--space-1-5) var(--space-2-5);
        font-size: var(--text-xs);
        background: var(--bg-tertiary);
        border: 1px solid var(--border-subtle);
        border-radius: var(--radius-full);
        color: var(--text-secondary);
    }

    /* Concept Chips (clickable) */
    .concept-chips {
        display: flex;
        flex-wrap: wrap;
        gap: var(--space-2);
    }

    .concept-chip {
        padding: var(--space-1-5) var(--space-2-5);
        font-size: var(--text-xs);
        background: var(--bg-tertiary);
        border: 1px solid var(--border-subtle);
        border-radius: var(--radius-full);
        color: var(--text-secondary);
        cursor: pointer;
        transition: var(--transition-all);
    }

    .concept-chip:hover {
        background: var(--entity-concept);
        border-color: var(--entity-concept);
        color: white;
    }

    /* Context Search Results */
    .context-results {
        border-top: 1px solid var(--border-subtle);
        padding-top: var(--space-4);
    }

    .context-results-list {
        display: flex;
        flex-direction: column;
        gap: var(--space-2);
        max-height: 400px;
        overflow-y: auto;
    }

    .context-result-card {
        display: flex;
        flex-direction: column;
        gap: var(--space-1-5);
        padding: var(--space-3);
        background: var(--bg-tertiary);
        border: 1px solid var(--border-subtle);
        border-radius: var(--radius-md);
        cursor: pointer;
        text-align: left;
        transition: var(--transition-all);
        animation: ies-slide-up 0.2s ease-out backwards;
        animation-delay: var(--delay);
    }

    .context-result-card:hover {
        background: var(--bg-primary);
        border-color: var(--entity-concept);
    }

    .context-result-card .result-main {
        display: flex;
        align-items: center;
        gap: var(--space-2);
    }

    .context-result-card .result-entity {
        font-size: var(--text-sm);
        font-weight: var(--font-semibold);
        color: var(--text-primary);
    }

    .context-result-card .result-type-badge {
        font-size: var(--text-xs);
        padding: 2px 6px;
        background: var(--bg-secondary);
        border: 1px solid var(--border-subtle);
        border-radius: var(--radius-sm);
        color: var(--text-muted);
    }

    .context-result-card .result-snippet {
        margin: 0;
        font-size: var(--text-xs);
        color: var(--text-secondary);
        line-height: 1.5;
        display: -webkit-box;
        -webkit-line-clamp: 2;
        -webkit-box-orient: vertical;
        overflow: hidden;
    }

    .context-result-card .result-source {
        font-size: var(--text-xs);
        color: var(--text-muted);
        font-style: italic;
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
        border-color: var(--text-muted);
        border-top-color: var(--entity-framework);
    }

    /* ========== Trail Navigation Styles ========== */
    .trail-nav {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: var(--space-3);
        padding: var(--space-2) var(--space-3);
        background: var(--bg-tertiary);
        border-radius: var(--radius-md);
        border: 1px solid var(--border-subtle);
    }

    .trail-breadcrumbs {
        display: flex;
        align-items: center;
        gap: var(--space-1);
        flex-wrap: wrap;
        flex: 1;
        min-width: 0;
    }

    .trail-separator {
        color: var(--text-muted);
        font-size: var(--text-sm);
    }

    .trail-item {
        display: flex;
        align-items: center;
        gap: var(--space-1);
        padding: var(--space-1) var(--space-2);
        background: var(--bg-primary);
        border: 1px solid var(--border-subtle);
        border-radius: var(--radius-sm);
        font-size: var(--text-xs);
        color: var(--text-secondary);
        cursor: pointer;
        transition: var(--transition-all);
        max-width: 180px;
    }

    .trail-item:hover {
        border-color: var(--entity-concept);
        color: var(--text-primary);
    }

    .trail-item.active {
        background: var(--entity-concept);
        border-color: var(--entity-concept);
        color: white;
    }

    .trail-item.type-context {
        border-left: 3px solid var(--entity-framework);
    }

    .trail-item.type-question {
        border-left: 3px solid var(--entity-concept);
    }

    .trail-item.type-entity {
        border-left: 3px solid var(--entity-theory);
    }

    .trail-icon {
        font-size: var(--text-xs);
        flex-shrink: 0;
    }

    .trail-label {
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }

    .trail-back {
        display: flex;
        align-items: center;
        justify-content: center;
        width: 28px;
        height: 28px;
        background: var(--bg-primary);
        border: 1px solid var(--border-subtle);
        border-radius: var(--radius-sm);
        color: var(--text-muted);
        cursor: pointer;
        transition: var(--transition-all);
        flex-shrink: 0;
    }

    .trail-back:hover {
        background: var(--bg-secondary);
        border-color: var(--text-muted);
        color: var(--text-primary);
    }

    /* ========== Entity Focus View Styles ========== */
    .entity-focus {
        display: flex;
        flex-direction: column;
        gap: var(--space-4);
        padding: var(--space-4);
        background: var(--bg-primary);
        border: 1px solid var(--border-default);
        border-radius: var(--radius-lg);
        animation: ies-slide-up 0.2s ease-out;
    }

    .entity-focus-header {
        display: flex;
        flex-direction: column;
        gap: var(--space-2);
    }

    .entity-focus .entity-type-badge {
        display: inline-block;
        width: fit-content;
        padding: var(--space-1) var(--space-2);
        font-size: var(--text-xs);
        font-weight: var(--font-semibold);
        text-transform: uppercase;
        letter-spacing: 0.05em;
        background: var(--entity-theory);
        color: white;
        border-radius: var(--radius-sm);
    }

    .entity-focus .entity-name {
        margin: 0;
        font-size: var(--text-xl);
        font-weight: var(--font-bold);
        color: var(--text-primary);
    }

    .entity-focus .entity-description {
        margin: 0;
        font-size: var(--text-sm);
        color: var(--text-secondary);
        line-height: 1.6;
    }

    .entity-loading {
        display: flex;
        align-items: center;
        gap: var(--space-2);
        padding: var(--space-4);
        color: var(--text-muted);
        font-size: var(--text-sm);
    }

    .entity-section {
        display: flex;
        flex-direction: column;
        gap: var(--space-2);
    }

    .entity-section-title {
        margin: 0;
        font-size: var(--text-sm);
        font-weight: var(--font-semibold);
        color: var(--text-secondary);
    }

    .entity-neighbors {
        display: flex;
        flex-direction: column;
        gap: var(--space-2);
        max-height: 300px;
        overflow-y: auto;
    }

    .neighbor-card {
        display: flex;
        flex-direction: column;
        gap: var(--space-1);
        padding: var(--space-2-5) var(--space-3);
        background: var(--bg-tertiary);
        border: 1px solid var(--border-subtle);
        border-radius: var(--radius-md);
        cursor: pointer;
        text-align: left;
        transition: var(--transition-all);
    }

    .neighbor-card:hover {
        background: var(--bg-secondary);
        border-color: var(--entity-concept);
    }

    .neighbor-relationship {
        font-size: var(--text-xs);
        color: var(--text-muted);
        font-family: monospace;
    }

    .neighbor-relationship.incoming {
        color: var(--entity-framework);
    }

    .neighbor-relationship.outgoing {
        color: var(--entity-concept);
    }

    .neighbor-name {
        font-size: var(--text-sm);
        font-weight: var(--font-semibold);
        color: var(--text-primary);
    }

    .neighbor-type {
        font-size: var(--text-xs);
        color: var(--text-muted);
    }

    .entity-sources {
        display: flex;
        flex-wrap: wrap;
        gap: var(--space-2);
    }

    .source-book {
        padding: var(--space-1) var(--space-2);
        font-size: var(--text-xs);
        background: var(--bg-secondary);
        border: 1px solid var(--border-subtle);
        border-radius: var(--radius-sm);
        color: var(--text-secondary);
    }

    .back-to-question {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: var(--space-2);
        padding: var(--space-2) var(--space-4);
        background: var(--bg-tertiary);
        border: 1px solid var(--border-default);
        border-radius: var(--radius-md);
        font-size: var(--text-sm);
        color: var(--text-secondary);
        cursor: pointer;
        transition: var(--transition-all);
        align-self: flex-start;
    }

    .back-to-question:hover {
        background: var(--bg-secondary);
        border-color: var(--entity-concept);
        color: var(--text-primary);
    }

    /* Note: Animations (ies-spin, ies-slide-up, ies-fade-in, pulse-soft)
       are provided by the unified design system in design-system/tokens/animations.css */
</style>
