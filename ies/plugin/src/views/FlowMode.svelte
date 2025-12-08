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
    import EvidenceSection from '../components/EvidenceSection.svelte';
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
    let entityDescription: string | null = null;
    let entitySourceBooks: Array<{title: string, author?: string, snippet?: string}> = [];

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
        type: 'context' | 'question' | 'entity' | 'facet' | 'search';
        label: string;
        data?: any; // Store relevant data for navigation back
    }

    interface EntityDetails {
        name: string;
        type: string;
        description?: string;
        neighbors: Array<{name: string, type: string, relationship: string, direction: 'in' | 'out'}>;
        sourceBooks: string[];
        facets?: Array<{name: string, description?: string, entity_count: number}>;
    }

    interface FacetDetails {
        parentEntityName: string;
        parentEntityType: string;
        facetName: string;
        description?: string;
        entities: Array<{name: string, type: string, relationship: string}>;
    }

    let focusState: FocusState = 'idle';
    let trailStack: TrailItem[] = [];
    let standaloneTrailStack: TrailItem[] = []; // Standalone mode trail
    let focusedEntity: EntityDetails | null = null;
    let focusedFacet: FacetDetails | null = null;
    let isLoadingEntity = false;
    let isLoadingFacet = false;

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
            focusedFacet = null;
            activeQuestionIndex = null;
        } else if (targetItem.type === 'question') {
            focusState = 'question';
            focusedEntity = null;
            focusedFacet = null;
            // Re-select the question if data available
            if (targetItem.data?.questionIndex !== undefined) {
                selectQuestion(targetItem.data.questionIndex);
            }
        } else if (targetItem.type === 'entity') {
            focusState = 'entity';
            focusedFacet = null;
            if (targetItem.data?.entityName) {
                navigateToEntity(targetItem.data.entityName, false); // Don't push to trail again
            }
        } else if (targetItem.type === 'facet') {
            focusState = 'facet';
            if (targetItem.data?.entityName && targetItem.data?.facetName) {
                navigateToFacet(targetItem.data.entityName, targetItem.data.facetName, false);
            }
        }
    }

    async function navigateToEntity(entityName: string, addToTrail = true) {
        isLoadingEntity = true;
        focusState = 'entity';
        focusedFacet = null;

        try {
            // Fetch entity details from backend
            const data = await apiGet(`/graph/entity/${encodeURIComponent(entityName)}`);

            // Simplified transformation using pre-computed data
            const neighbors: EntityDetails['neighbors'] = data.related?.map(rel => ({
                name: rel.name,
                type: rel.type,
                relationship: rel.relationship,
                direction: 'out'
            })) || [];

            const sourceBooks: string[] = data.source_books?.map(book =>
                book.author ? `${book.title} - ${book.author}` : book.title
            ) || [];

            // Fetch facets for this entity
            let facets = [];
            try {
                const facetsData = await apiGet(`/graph/entity/${encodeURIComponent(entityName)}/facets`);
                facets = facetsData.facets || [];
            } catch (facetErr) {
                // Facets are optional, don't fail if endpoint returns 404
                console.log('[FlowMode] No facets found for entity:', entityName);
            }

            focusedEntity = {
                name: data.name,
                type: data.type,
                description: data.description || null,
                neighbors,
                sourceBooks,
                facets
            };

            if (addToTrail) {
                // Add to context trail if in context mode
                if (isContextMode) {
                    pushTrail({
                        type: 'entity',
                        label: entityName,
                        data: { entityName }
                    });
                } else {
                    // Add to standalone trail
                    standaloneTrailStack = [...standaloneTrailStack, {
                        type: 'entity',
                        label: entityName,
                        data: { entityName }
                    }];
                }
            }

            // Track exploration
            const now = new Date().toISOString();
            if (!explorationPath.includes(entityName)) {
                explorationPath = [...explorationPath, entityName];
                explorationTimestamps = [...explorationTimestamps, now];
            }
        } catch (err) {
            console.error('[FlowMode] Error loading entity:', err);
            showMessage(`Failed to load entity: ${err.message}`, 5000, 'error');
            focusState = trailStack.length > 0 ? 'question' : 'idle';
        } finally {
            isLoadingEntity = false;
        }
    }

    async function navigateToFacet(entityName: string, facetName: string, addToTrail = true) {
        isLoadingFacet = true;
        focusState = 'facet';

        try {
            // Fetch facets for entity
            const data = await apiGet(`/graph/entity/${encodeURIComponent(entityName)}/facets`);

            // Find the selected facet
            const facet = data.facets.find(f => f.name === facetName);
            if (!facet) {
                throw new Error(`Facet '${facetName}' not found for entity '${entityName}'`);
            }

            focusedFacet = {
                parentEntityName: data.entity_name,
                parentEntityType: data.entity_type,
                facetName: facet.name,
                description: facet.description,
                entities: facet.entities || []
            };

            if (addToTrail) {
                // Add to context trail if in context mode
                if (isContextMode) {
                    pushTrail({
                        type: 'facet',
                        label: facetName,
                        data: { entityName, facetName }
                    });
                } else {
                    // Add to standalone trail
                    standaloneTrailStack = [...standaloneTrailStack, {
                        type: 'facet',
                        label: facetName,
                        data: { entityName, facetName }
                    }];
                }
            }
        } catch (err) {
            showMessage(`Failed to load facet: ${err.message}`, 5000, 'error');
            focusState = 'entity';
        } finally {
            isLoadingFacet = false;
        }
    }

    /**
     * Check if a facet exists as an entity in the knowledge graph.
     * A facet "exists in graph" if its name matches any entity in the overall graph.
     * We determine this by checking if the facet name appears in the facet's own entities list.
     */
    function facetExistsInGraph(facet: any): boolean {
        if (!facet || !facet.name || !facet.entities) {
            return false;
        }

        const facetName = facet.name.toLowerCase().trim();

        // Check if facet name matches any entity in the entities array
        // If the facet itself exists as an entity in the graph, it should appear here
        return facet.entities.some((entity: any) =>
            entity.name && entity.name.toLowerCase().trim() === facetName
        );
    }

    function navigateBack() {
        // Handle standalone mode
        if (!isContextMode) {
            navigateStandaloneBack();
            return;
        }

        // Context mode navigation
        if (trailStack.length <= 1) {
            // Back to idle state
            focusState = 'idle';
            focusedEntity = null;
            focusedFacet = null;
            trailStack = [];
            return;
        }

        // Pop current item and go to previous
        popTrail();
        const previousItem = trailStack[trailStack.length - 1];

        if (previousItem.type === 'question') {
            focusState = 'question';
            focusedEntity = null;
            focusedFacet = null;
        } else if (previousItem.type === 'context') {
            focusState = 'idle';
            focusedEntity = null;
            focusedFacet = null;
        } else if (previousItem.type === 'entity') {
            focusState = 'entity';
            focusedFacet = null;
            if (previousItem.data?.entityName) {
                navigateToEntity(previousItem.data.entityName, false);
            }
        }
    }

    function navigateStandaloneBack() {
        if (standaloneTrailStack.length === 0) {
            // No trail, just return to idle
            focusState = 'idle';
            focusedEntity = null;
            focusedFacet = null;
            return;
        }

        // Remove current item
        standaloneTrailStack = standaloneTrailStack.slice(0, -1);

        if (standaloneTrailStack.length === 0) {
            // Back to search results
            focusState = 'idle';
            focusedEntity = null;
            focusedFacet = null;
        } else {
            // Go to previous item
            const previousItem = standaloneTrailStack[standaloneTrailStack.length - 1];

            if (previousItem.type === 'entity') {
                focusState = 'entity';
                focusedFacet = null;
                if (previousItem.data?.entityName) {
                    navigateToEntity(previousItem.data.entityName, false);
                }
            } else if (previousItem.type === 'facet') {
                focusState = 'facet';
                if (previousItem.data?.entityName && previousItem.data?.facetName) {
                    navigateToFacet(previousItem.data.entityName, previousItem.data.facetName, false);
                }
            }
        }
    }

    function navigateStandaloneToIndex(index: number) {
        if (index < 0 || index >= standaloneTrailStack.length) return;

        // Truncate trail to this index
        standaloneTrailStack = standaloneTrailStack.slice(0, index + 1);
        const targetItem = standaloneTrailStack[index];

        // Navigate to the selected item
        if (targetItem.type === 'entity') {
            focusState = 'entity';
            focusedFacet = null;
            if (targetItem.data?.entityName) {
                navigateToEntity(targetItem.data.entityName, false);
            }
        } else if (targetItem.type === 'facet') {
            focusState = 'facet';
            if (targetItem.data?.entityName && targetItem.data?.facetName) {
                navigateToFacet(targetItem.data.entityName, targetItem.data.facetName, false);
            }
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
                name: node.name,
                type: node.type,
                direction
            });
        }

        return groups;
    }

    async function apiGet(path: string): Promise<any> {
        const url = `${backendUrl}${path}`;

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

    async function apiPost(path: string, body: any): Promise<any> {
        const url = `${backendUrl}${path}`;

        const response = await fetchSyncPost('/api/network/forwardProxy', {
            url: url,
            method: 'POST',
            timeout: 30000,
            contentType: 'application/json',
            headers: [],
            payload: JSON.stringify(body)
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
        const query = searchQuery.trim();
        if (!query) return;

        isSearching = true;
        searchResults = [];

        try {
            const data = await apiGet(`/graph/search?q=${encodeURIComponent(query)}`);
            searchResults = data.results || [];
            if (searchResults.length === 0) {
                showMessage('No concepts found', 3000);
            }
        } catch (err) {
            console.error('[IES] Search failed:', err);
            const message = err?.message || String(err);
            showMessage(`Search failed: ${message}`, 5000, 'error');
        } finally {
            isSearching = false;
        }
    }

    async function exploreConcept(concept: string) {
        if (!concept) return;

        currentConcept = concept;
        isExploring = true;
        searchResults = [];

        try {
            const data = await apiGet(`/graph/explore/${encodeURIComponent(concept)}`);
            nodes = data.nodes || [];
            relationships = data.relationships || [];

            // Track in path if new
            const now = new Date().toISOString();
            if (!explorationPath.includes(concept)) {
                explorationPath = [...explorationPath, concept];
                explorationTimestamps = [...explorationTimestamps, now];
            }

            if (!explorationStartTime) {
                explorationStartTime = Date.now();
            }

            // Generate thinking question
            if (userId) {
                await generateThinkingQuestion();
            }
        } catch (err) {
            console.error('[IES] Explore failed:', err);
            const message = err?.message || String(err);
            showMessage(`Failed to explore ${concept}: ${message}`, 5000, 'error');
        } finally {
            isExploring = false;
        }
    }

    async function generateThinkingQuestion() {
        isLoadingQuestion = true;
        try {
            const recentPath = explorationPath.slice(-5);
            const data = await apiPost('/graph/thinking-partner', {
                concept: currentConcept,
                path: recentPath,
                related: Array.from(groupedNodes.keys())
            });
            thinkingQuestion = data.question || null;
        } catch (err) {
            console.log('[IES] Could not generate thinking question:', err);
        } finally {
            isLoadingQuestion = false;
        }
    }

    async function detectContextNote(blockId: string) {
        isDetectingContext = true;
        try {
            // Get block content
            const kramdown = await getBlockKramdown(blockId);
            if (!kramdown) {
                console.log('[IES] No block content found for context detection');
                return;
            }

            // Convert to markdown
            const markdown = await exportMdContent(blockId);
            if (!markdown) {
                console.log('[IES] Failed to export markdown for context detection');
                return;
            }

            // Call backend to parse context
            const parsed = await apiPost('/context/parse', { text: markdown });
            if (!parsed || !parsed.is_context) {
                console.log('[IES] Block is not a Context Note');
                return;
            }

            // Save context
            const saved = await apiPost('/context/save', parsed);
            parsedContext = parsed;
            savedContextId = saved.context_id;
            isContextMode = true;

            // Initialize trail with context
            initializeContextTrail();

            showMessage(`Context loaded: ${parsed.title}`, 3000);
        } catch (err) {
            console.error('[IES] Context detection failed:', err);
        } finally {
            isDetectingContext = false;
        }
    }

    function clearContextMode() {
        isContextMode = false;
        parsedContext = null;
        savedContextId = null;
        activeQuestionIndex = null;
        contextSearchResults = [];
        trailStack = [];
        focusState = 'idle';
        focusedEntity = null;
        focusedFacet = null;
    }

    async function selectQuestion(index: number) {
        if (!parsedContext || !savedContextId) return;

        activeQuestionIndex = index;
        focusState = 'question';
        focusedEntity = null;
        focusedFacet = null;

        // Add question to trail if not already there
        if (trailStack.length > 0 && trailStack[trailStack.length - 1].type !== 'question') {
            const question = parsedContext.key_questions[index];
            pushTrail({
                type: 'question',
                label: `Q${index + 1}`,
                data: { questionIndex: index, question }
            });
        }
    }

    async function searchForQuestion(index: number) {
        if (!parsedContext || !savedContextId) return;

        selectQuestion(index);
        isContextSearching = true;

        try {
            const question = parsedContext.key_questions[index];
            const results = await apiPost('/context/search', {
                context_id: savedContextId,
                question
            });

            contextSearchResults = results.results || [];
        } catch (err) {
            console.error('[IES] Context search failed:', err);
            showMessage(`Search failed: ${err.message}`, 5000, 'error');
        } finally {
            isContextSearching = false;
        }
    }

    async function handleQuestionResponse() {
        if (!questionResponse.trim() || !thinkingQuestion) return;

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
        entityDescription = null;
        entitySourceBooks = [];
        standaloneTrailStack = [];
        focusState = 'idle';
        focusedEntity = null;
        focusedFacet = null;
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
            <span class="flow-version">v0.4.0</span>
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

    <!-- Search Results (hide when viewing entity or facet) -->
    {#if searchResults.length > 0 && focusState === 'idle'}
        <div class="results-panel">
            <div class="results-header">
                <span class="results-label">Found {searchResults.length} concept{searchResults.length !== 1 ? 's' : ''}</span>
            </div>
            <div class="results-list">
                {#each searchResults as result, i}
                    <button
                        class="result-card"
                        style="--delay: {i * 40}ms; --type-color: {getTypeColor(result.type)}"
                        on:click={() => navigateToEntity(result.name)}
                    >
                        <span class="result-indicator"></span>
                        <span class="result-name">{result.name}</span>
                        <span class="result-type">{result.type}</span>
                    </button>
                {/each}
            </div>
        </div>
    {/if}

    <!-- Standalone Entity View (for search results outside Context Mode) -->
    {#if !isContextMode && focusState === 'entity' && focusedEntity}
        <div class="entity-panel">
            <div class="entity-header">
                <button class="entity-back" on:click={() => { focusState = 'idle'; focusedEntity = null; standaloneTrailStack = []; }} title="Back to Search">
                    <svg viewBox="0 0 24 24" width="16" height="16">
                        <path fill="currentColor" d="M20 11H7.83l5.59-5.59L12 4l-8 8 8 8 1.41-1.41L7.83 13H20v-2z"/>
                    </svg>
                    Back
                </button>
            </div>

            <!-- Standalone Trail Navigation -->
            {#if standaloneTrailStack.length > 0}
                <div class="trail-nav">
                    <div class="trail-breadcrumbs">
                        {#each standaloneTrailStack as item, i}
                            {#if i > 0}
                                <span class="trail-separator">›</span>
                            {/if}
                            <button
                                class="trail-item"
                                class:active={i === standaloneTrailStack.length - 1}
                                class:type-entity={item.type === 'entity'}
                                class:type-facet={item.type === 'facet'}
                                on:click={() => navigateStandaloneToIndex(i)}
                            >
                                {#if item.type === 'entity'}
                                    <span class="trail-icon">🔷</span>
                                {:else if item.type === 'facet'}
                                    <span class="trail-icon">📂</span>
                                {/if}
                                <span class="trail-label">{item.label}</span>
                            </button>
                        {/each}
                    </div>
                    {#if standaloneTrailStack.length > 1}
                        <button class="trail-back" on:click={navigateStandaloneBack} title="Go Back">
                            <svg viewBox="0 0 24 24" width="16" height="16">
                                <path fill="currentColor" d="M20 11H7.83l5.59-5.59L12 4l-8 8 8 8 1.41-1.41L7.83 13H20v-2z"/>
                            </svg>
                        </button>
                    {/if}
                </div>
            {/if}

            <div class="entity-focus-content">
                <div class="entity-focus-header">
                    <div class="entity-type-badge">{focusedEntity.type}</div>
                    <h3 class="entity-name">{focusedEntity.name}</h3>
                </div>
                {#if focusedEntity.description}
                    <p class="entity-description">{focusedEntity.description}</p>
                {/if}

                <!-- Facets -->
                {#if focusedEntity.facets && focusedEntity.facets.length > 0}
                    <div class="entity-section">
                        <h4 class="entity-section-title">Facets ({focusedEntity.facets.length})</h4>
                        <div class="facet-chips">
                            {#each focusedEntity.facets as facet}
                                <button class="facet-chip" on:click={() => navigateToFacet(focusedEntity.name, facet.name)}>
                                    {facet.name}
                                    {#if facetExistsInGraph(facet)}
                                        <span class="facet-exists-badge" title="This facet exists as an entity in the knowledge graph">●</span>
                                    {/if}
                                    {#if facet.entity_count > 0}
                                        <span class="facet-count">{facet.entity_count}</span>
                                    {/if}
                                </button>
                            {/each}
                        </div>
                    </div>
                {/if}

                <!-- Related Concepts -->
                {#if focusedEntity.neighbors.length > 0}
                    <div class="entity-section">
                        <h4 class="entity-section-title">Related ({focusedEntity.neighbors.length})</h4>
                        <div class="neighbor-list">
                            {#each focusedEntity.neighbors as neighbor}
                                <button class="neighbor-item" on:click={() => navigateToEntity(neighbor.name)}>
                                    <span class="neighbor-name">{neighbor.name}</span>
                                    <span class="neighbor-type">{neighbor.type}</span>
                                    <span class="neighbor-rel">{neighbor.relationship}</span>
                                </button>
                            {/each}
                        </div>
                    </div>
                {/if}

                <!-- Source Books -->
                {#if focusedEntity.sourceBooks.length > 0}
                    <div class="entity-section">
                        <h4 class="entity-section-title">Sources ({focusedEntity.sourceBooks.length})</h4>
                        <ul class="source-list">
                            {#each focusedEntity.sourceBooks as book}
                                <li>{book}</li>
                            {/each}
                        </ul>
                    </div>
                {/if}

                <!-- Evidence Section (Sprint 2) -->
                <EvidenceSection entityName={focusedEntity.name} {backendUrl} />
            </div>
        </div>
    {/if}

    <!-- Standalone Facet View (for facet exploration outside Context Mode) -->
    {#if !isContextMode && focusState === 'facet' && focusedFacet}
        <div class="entity-panel">
            <div class="entity-header">
                <button class="entity-back" on:click={navigateStandaloneBack} title="Back">
                    <svg viewBox="0 0 24 24" width="16" height="16">
                        <path fill="currentColor" d="M20 11H7.83l5.59-5.59L12 4l-8 8 8 8 1.41-1.41L7.83 13H20v-2z"/>
                    </svg>
                    Back to {focusedFacet.parentEntityName}
                </button>
            </div>

            <!-- Standalone Trail Navigation -->
            {#if standaloneTrailStack.length > 0}
                <div class="trail-nav">
                    <div class="trail-breadcrumbs">
                        {#each standaloneTrailStack as item, i}
                            {#if i > 0}
                                <span class="trail-separator">›</span>
                            {/if}
                            <button
                                class="trail-item"
                                class:active={i === standaloneTrailStack.length - 1}
                                class:type-entity={item.type === 'entity'}
                                class:type-facet={item.type === 'facet'}
                                on:click={() => navigateStandaloneToIndex(i)}
                            >
                                {#if item.type === 'entity'}
                                    <span class="trail-icon">🔷</span>
                                {:else if item.type === 'facet'}
                                    <span class="trail-icon">📂</span>
                                {/if}
                                <span class="trail-label">{item.label}</span>
                            </button>
                        {/each}
                    </div>
                    {#if standaloneTrailStack.length > 1}
                        <button class="trail-back" on:click={navigateStandaloneBack} title="Go Back">
                            <svg viewBox="0 0 24 24" width="16" height="16">
                                <path fill="currentColor" d="M20 11H7.83l5.59-5.59L12 4l-8 8 8 8 1.41-1.41L7.83 13H20v-2z"/>
                            </svg>
                        </button>
                    {/if}
                </div>
            {/if}

            <div class="entity-focus-content">
                <div class="facet-focus-header">
                    <div class="facet-parent-info">
                        <span class="entity-type-badge">{focusedFacet.parentEntityType}</span>
                        <span class="facet-parent-name">{focusedFacet.parentEntityName}</span>
                    </div>
                    <h3 class="entity-name">{focusedFacet.facetName}</h3>
                    {#if focusedFacet.description}
                        <p class="entity-description">{focusedFacet.description}</p>
                    {/if}
                </div>

                {#if isLoadingFacet}
                    <div class="entity-section">
                        <span class="spinner"></span>
                        Loading facet entities...
                    </div>
                {:else if focusedFacet.entities.length > 0}
                    <div class="entity-section">
                        <h4 class="entity-section-title">Entities ({focusedFacet.entities.length})</h4>
                        <div class="neighbor-list">
                            {#each focusedFacet.entities as entity}
                                <button class="neighbor-item" on:click={() => navigateToEntity(entity.name)}>
                                    <span class="neighbor-name">{entity.name}</span>
                                    <span class="neighbor-type">{entity.type}</span>
                                    <span class="neighbor-rel">{entity.relationship}</span>
                                </button>
                            {/each}
                        </div>
                    </div>
                {:else}
                    <div class="entity-section">
                        <p class="entity-description">No entities in this facet yet</p>
                    </div>
                {/if}
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
                                class:type-facet={item.type === 'facet'}
                                on:click={() => navigateToTrailIndex(i)}
                            >
                                {#if item.type === 'context'}
                                    <span class="trail-icon">📍</span>
                                {:else if item.type === 'question'}
                                    <span class="trail-icon">❓</span>
                                {:else if item.type === 'entity'}
                                    <span class="trail-icon">🔷</span>
                                {:else if item.type === 'facet'}
                                    <span class="trail-icon">📂</span>
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

            <!-- Facet Focus View -->
            {#if focusState === 'facet' && focusedFacet}
                <div class="facet-focus">
                    <div class="facet-focus-header">
                        <div class="facet-parent-info">
                            <span class="facet-parent-badge">{focusedFacet.parentEntityType}</span>
                            <span class="facet-parent-name">{focusedFacet.parentEntityName}</span>
                        </div>
                        <h3 class="facet-name">{focusedFacet.facetName}</h3>
                        {#if focusedFacet.description}
                            <p class="facet-description">{focusedFacet.description}</p>
                        {/if}
                    </div>

                    {#if isLoadingFacet}
                        <div class="facet-loading">
                            <span class="spinner"></span>
                            Loading facet entities...
                        </div>
                    {:else if focusedFacet.entities.length > 0}
                        <div class="facet-section">
                            <h4 class="facet-section-title">Entities in this Facet ({focusedFacet.entities.length})</h4>
                            <div class="facet-entities">
                                {#each focusedFacet.entities as entity}
                                    <button
                                        class="facet-entity-card"
                                        on:click={() => navigateToEntity(entity.name)}
                                    >
                                        <div class="facet-entity-main">
                                            <span class="facet-entity-name">{entity.name}</span>
                                            <span class="facet-entity-type">{entity.type}</span>
                                        </div>
                                        <span class="facet-entity-relationship">{entity.relationship}</span>
                                    </button>
                                {/each}
                            </div>
                        </div>
                    {:else}
                        <div class="facet-empty">
                            <p>No entities in this facet yet</p>
                        </div>
                    {/if}

                    <!-- Back to Entity Button -->
                    <button class="back-to-entity" on:click={navigateBack}>
                        <svg viewBox="0 0 24 24" width="14" height="14">
                            <path fill="currentColor" d="M20 11H7.83l5.59-5.59L12 4l-8 8 8 8 1.41-1.41L7.83 13H20v-2z"/>
                        </svg>
                        Back to {focusedFacet.parentEntityName}
                    </button>
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
                        <!-- Facets Section -->
                        {#if focusedEntity.facets && focusedEntity.facets.length > 0}
                            <div class="entity-section">
                                <h4 class="entity-section-title">Facets ({focusedEntity.facets.length})</h4>
                                <div class="entity-facets">
                                    {#each focusedEntity.facets as facet}
                                        <button
                                            class="facet-chip"
                                            on:click={() => navigateToFacet(focusedEntity.name, facet.name)}
                                        >
                                            <span class="facet-chip-icon">📂</span>
                                            <div class="facet-chip-content">
                                                <span class="facet-chip-name">
                                                    {facet.name}
                                                    {#if facetExistsInGraph(facet)}
                                                        <span class="facet-exists-badge" title="This facet exists as an entity in the knowledge graph">●</span>
                                                    {/if}
                                                </span>
                                                <span class="facet-chip-count">{facet.entity_count} {facet.entity_count === 1 ? 'entity' : 'entities'}</span>
                                            </div>
                                        </button>
                                    {/each}
                                </div>
                            </div>
                        {/if}

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

                        <!-- Evidence Section (Sprint 2) -->
                        <EvidenceSection entityName={focusedEntity.name} {backendUrl} />
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

            <!-- Key Questions Section (show when not in entity or facet focus) -->
            {#if focusState !== 'entity' && focusState !== 'facet' && parsedContext.key_questions.length > 0}
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

            <!-- Areas of Exploration Section (hide when in entity or facet focus) -->
            {#if focusState !== 'entity' && focusState !== 'facet' && parsedContext.areas_of_exploration.length > 0}
                <div class="context-section">
                    <h3 class="section-title">Areas of Exploration</h3>
                    <div class="area-chips">
                        {#each parsedContext.areas_of_exploration as area}
                            <span class="area-chip">{area}</span>
                        {/each}
                    </div>
                </div>
            {/if}

            <!-- Context Search Results (hide when in entity or facet focus) -->
            {#if focusState !== 'entity' && focusState !== 'facet' && contextSearchResults.length > 0}
                <div class="context-section">
                    <h3 class="section-title">
                        Related Entities
                        <span class="results-count">{contextSearchResults.length}</span>
                    </h3>
                    <div class="context-results-list">
                        {#each contextSearchResults as result, i}
                            <button
                                class="context-result-card"
                                style="--delay: {i * 50}ms"
                                on:click={() => navigateToEntity(result.source_id)}
                            >
                                <div class="result-main">
                                    <span class="result-entity">{result.source_title}</span>
                                    {#if result.concepts_found.length > 0}
                                        <span class="result-type-badge">{result.concepts_found.length} concepts</span>
                                    {/if}
                                </div>
                                {#if result.snippet}
                                    <p class="result-snippet">{result.snippet}</p>
                                {/if}
                                <span class="result-source">Relevance: {(result.relevance_score * 100).toFixed(0)}%</span>
                            </button>
                        {/each}
                    </div>
                </div>
            {/if}
        </div>
    {/if}

    <!-- Loading Journey State -->
    {#if isLoadingJourney}
        <div class="flow-state">
            <div class="state-icon loading">
                <svg viewBox="0 0 24 24" width="48" height="48">
                    <path fill="currentColor" d="M12,4V2A10,10 0 0,0 2,12H4A8,8 0 0,1 12,4Z" />
                </svg>
            </div>
            <h2 class="state-title">Loading Journey...</h2>
            <p class="state-text">Restoring your exploration path</p>
        </div>
    {/if}
</div>

<style>
    /* Base */
    .flow-mode {
        display: flex;
        flex-direction: column;
        gap: var(--space-3);
        height: 100%;
        padding: var(--space-3);
        opacity: 0;
        transition: opacity var(--duration-base);
    }

    .flow-mode.mounted {
        opacity: 1;
    }

    /* Header */
    .flow-header {
        display: flex;
        align-items: center;
        gap: var(--space-3);
        padding-bottom: var(--space-2);
        border-bottom: 1px solid var(--border-subtle);
    }

    .back-btn {
        display: flex;
        align-items: center;
        justify-content: center;
        width: 32px;
        height: 32px;
        background: var(--bg-tertiary);
        border: 1px solid var(--border-default);
        border-radius: var(--radius-button);
        color: var(--text-muted);
        cursor: pointer;
        transition: var(--transition-all);
    }

    .back-btn:hover {
        background: var(--bg-secondary);
        border-color: var(--text-muted);
        color: var(--text-primary);
    }

    .header-title {
        display: flex;
        align-items: center;
        gap: var(--space-2);
        flex: 1;
    }

    .flow-version {
        font-size: 0.7rem;
        color: var(--text-muted);
        background: var(--bg-secondary);
        padding: 2px 6px;
        border-radius: var(--radius-sm);
        margin-left: var(--space-1);
    }

    .flow-icon {
        color: var(--entity-concept);
    }

    .header-title h1 {
        font-family: var(--font-sans);
        font-size: var(--text-xl);
        font-weight: var(--font-bold);
        color: var(--text-primary);
        margin: 0;
    }

    .clear-btn {
        display: flex;
        align-items: center;
        gap: var(--space-1-5);
        padding: var(--space-1-5) var(--space-3);
        font-family: var(--font-sans);
        font-size: var(--text-sm);
        font-weight: var(--font-semibold);
        color: var(--text-muted);
        background: var(--bg-tertiary);
        border: 1px solid var(--border-default);
        border-radius: var(--radius-button);
        cursor: pointer;
        transition: var(--transition-all);
    }

    .clear-btn:hover {
        background: var(--bg-secondary);
        border-color: var(--text-muted);
        color: var(--text-secondary);
    }

    /* Search */
    .search-container {
        display: flex;
        gap: var(--space-2);
    }

    .search-wrapper {
        position: relative;
        flex: 1;
        display: flex;
        align-items: center;
    }

    .search-icon {
        position: absolute;
        left: var(--space-3);
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

    /* Context Panel */
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
        border-color: var(--entity-concept);
        background: var(--entity-concept-subtle);
    }

    .question-number {
        display: flex;
        align-items: center;
        justify-content: center;
        width: 24px;
        height: 24px;
        flex-shrink: 0;
        background: var(--entity-concept);
        color: white;
        border-radius: 50%;
        font-size: var(--text-xs);
        font-weight: var(--font-bold);
    }

    .question-text {
        flex: 1;
        font-size: var(--text-sm);
        color: var(--text-primary);
        line-height: 1.5;
    }

    .area-chips {
        display: flex;
        flex-wrap: wrap;
        gap: var(--space-2);
    }

    .area-chip {
        padding: var(--space-1) var(--space-2);
        font-size: var(--text-xs);
        background: var(--bg-tertiary);
        border: 1px solid var(--border-subtle);
        border-radius: var(--radius-sm);
        color: var(--text-secondary);
    }

    .context-results-list {
        display: flex;
        flex-direction: column;
        gap: var(--space-2);
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

    /* Trail Navigation Styles */
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

    .trail-item.type-facet {
        border-left: 3px solid var(--entity-person);
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

    /* Facet Focus View Styles */
    .facet-focus {
        display: flex;
        flex-direction: column;
        gap: var(--space-4);
        padding: var(--space-4);
        background: var(--bg-primary);
        border: 1px solid var(--border-default);
        border-radius: var(--radius-lg);
        animation: ies-slide-up 0.2s ease-out;
    }

    .facet-focus-header {
        display: flex;
        flex-direction: column;
        gap: var(--space-2);
    }

    .facet-parent-info {
        display: flex;
        align-items: center;
        gap: var(--space-2);
        font-size: var(--text-xs);
        color: var(--text-muted);
    }

    .facet-parent-badge {
        display: inline-block;
        padding: var(--space-0-5) var(--space-1-5);
        font-weight: var(--font-semibold);
        text-transform: uppercase;
        letter-spacing: 0.05em;
        background: var(--entity-theory);
        color: white;
        border-radius: var(--radius-sm);
    }

    .facet-parent-name {
        font-weight: var(--font-medium);
        color: var(--text-secondary);
    }

    .facet-name {
        margin: 0;
        font-size: var(--text-xl);
        font-weight: var(--font-bold);
        color: var(--text-primary);
    }

    .facet-description {
        margin: 0;
        font-size: var(--text-sm);
        color: var(--text-secondary);
        line-height: 1.6;
    }

    .facet-loading {
        display: flex;
        align-items: center;
        gap: var(--space-2);
        padding: var(--space-4);
        color: var(--text-muted);
        font-size: var(--text-sm);
    }

    .facet-section {
        display: flex;
        flex-direction: column;
        gap: var(--space-2);
    }

    .facet-section-title {
        margin: 0;
        font-size: var(--text-sm);
        font-weight: var(--font-semibold);
        color: var(--text-secondary);
    }

    .facet-entities {
        display: flex;
        flex-direction: column;
        gap: var(--space-2);
        max-height: 400px;
        overflow-y: auto;
    }

    .facet-entity-card {
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

    .facet-entity-card:hover {
        background: var(--bg-secondary);
        border-color: var(--entity-concept);
    }

    .facet-entity-main {
        display: flex;
        align-items: center;
        gap: var(--space-2);
    }

    .facet-entity-name {
        flex: 1;
        font-size: var(--text-sm);
        font-weight: var(--font-semibold);
        color: var(--text-primary);
    }

    .facet-entity-type {
        font-size: var(--text-xs);
        padding: var(--space-0-5) var(--space-1-5);
        background: var(--bg-secondary);
        border: 1px solid var(--border-subtle);
        border-radius: var(--radius-sm);
        color: var(--text-muted);
    }

    .facet-entity-relationship {
        font-size: var(--text-xs);
        color: var(--text-muted);
        font-family: monospace;
    }

    .facet-empty {
        padding: var(--space-4);
        text-align: center;
        color: var(--text-muted);
        font-size: var(--text-sm);
    }

    .back-to-entity {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: var(--space-2);
        padding: var(--space-2) var(--space-3);
        background: var(--bg-tertiary);
        border: 1px solid var(--border-default);
        border-radius: var(--radius-button);
        font-size: var(--text-sm);
        font-weight: var(--font-semibold);
        color: var(--text-secondary);
        cursor: pointer;
        transition: var(--transition-all);
    }

    .back-to-entity:hover {
        background: var(--bg-secondary);
        border-color: var(--text-muted);
        color: var(--text-primary);
    }

    /* Entity Focus View Styles */
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

    /* Facet Chips in Entity View */
    .entity-facets {
        display: flex;
        flex-wrap: wrap;
        gap: var(--space-2);
    }

    .facet-chip {
        display: flex;
        align-items: center;
        gap: var(--space-2);
        padding: var(--space-2-5) var(--space-3);
        background: var(--bg-tertiary);
        border: 1px solid var(--border-subtle);
        border-radius: var(--radius-md);
        cursor: pointer;
        transition: var(--transition-all);
    }

    .facet-chip:hover {
        background: var(--entity-person-subtle);
        border-color: var(--entity-person);
        transform: translateY(-1px);
        box-shadow: var(--shadow-xs);
    }

    .facet-chip-icon {
        font-size: var(--text-base);
        flex-shrink: 0;
    }

    .facet-chip-content {
        display: flex;
        flex-direction: column;
        gap: var(--space-0-5);
    }

    .facet-chip-name {
        font-size: var(--text-sm);
        font-weight: var(--font-semibold);
        color: var(--text-primary);
    }

    .facet-chip-count {
        font-size: var(--text-xs);
        color: var(--text-muted);
    }

    .facet-exists-badge {
        display: inline-block;
        margin-left: var(--space-1);
        color: var(--entity-concept);
        font-size: var(--text-xs);
        opacity: 0.7;
        transition: opacity var(--transition-all);
    }

    .facet-chip:hover .facet-exists-badge {
        opacity: 1;
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
        padding: var(--space-2) var(--space-3);
        background: var(--bg-tertiary);
        border: 1px solid var(--border-default);
        border-radius: var(--radius-button);
        font-size: var(--text-sm);
        font-weight: var(--font-semibold);
        color: var(--text-secondary);
        cursor: pointer;
        transition: var(--transition-all);
    }

    .back-to-question:hover {
        background: var(--bg-secondary);
        border-color: var(--text-muted);
        color: var(--text-primary);
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

    /* Animations */
    @keyframes ies-slide-up {
        from {
            opacity: 0;
            transform: translateY(10px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    @keyframes ies-fade-in {
        from {
            opacity: 0;
        }
        to {
            opacity: 1;
        }
    }

    @keyframes ies-spin {
        to {
            transform: rotate(360deg);
        }
    }

    /* Standalone Entity Panel */
    .entity-panel {
        background: var(--bg-primary);
        border-radius: var(--radius-lg);
        border: 1px solid var(--border-light);
        margin-top: var(--space-3);
        max-height: 70vh;
        display: flex;
        flex-direction: column;
    }

    .entity-header {
        padding: var(--space-2) var(--space-3);
        border-bottom: 1px solid var(--border-light);
        background: var(--bg-secondary);
    }

    .entity-back {
        display: flex;
        align-items: center;
        gap: var(--space-1);
        background: none;
        border: none;
        color: var(--text-muted);
        cursor: pointer;
        font-size: 0.85rem;
        padding: var(--space-1) var(--space-2);
        border-radius: var(--radius-sm);
        transition: var(--transition-all);
    }

    .entity-back:hover {
        background: var(--bg-elevated);
        color: var(--text-primary);
    }

    .entity-focus-content {
        padding: var(--space-3);
        overflow-y: auto;
        flex: 1;
    }

    .entity-focus-header {
        margin-bottom: var(--space-2);
    }

    .entity-type-badge {
        display: inline-block;
        font-size: 0.7rem;
        text-transform: uppercase;
        color: var(--text-muted);
        background: var(--bg-secondary);
        padding: 2px 8px;
        border-radius: var(--radius-sm);
        margin-bottom: var(--space-1);
    }

    .entity-name {
        font-size: 1.2rem;
        font-weight: 600;
        margin: 0;
        color: var(--text-primary);
    }

    .entity-description {
        font-size: 0.9rem;
        color: var(--text-secondary);
        margin: var(--space-2) 0;
        line-height: 1.5;
    }

    .entity-section {
        margin-top: var(--space-3);
        padding-top: var(--space-3);
        border-top: 1px solid var(--border-light);
    }

    .entity-section-title {
        font-size: 0.85rem;
        font-weight: 600;
        color: var(--text-muted);
        margin: 0 0 var(--space-2) 0;
    }

    .facet-chips {
        display: flex;
        flex-wrap: wrap;
        gap: var(--space-1);
    }

    .facet-chip {
        background: var(--bg-secondary);
        border: 1px solid var(--border-light);
        border-radius: var(--radius-md);
        padding: var(--space-1) var(--space-2);
        font-size: 0.85rem;
        cursor: pointer;
        transition: var(--transition-all);
        display: flex;
        align-items: center;
        gap: var(--space-1);
    }

    .facet-chip:hover {
        background: var(--bg-elevated);
        border-color: var(--accent);
    }

    .facet-count {
        font-size: 0.75rem;
        background: var(--accent);
        color: white;
        padding: 0 6px;
        border-radius: 10px;
    }

    .neighbor-list {
        display: flex;
        flex-direction: column;
        gap: var(--space-1);
    }

    .neighbor-item {
        display: flex;
        align-items: center;
        gap: var(--space-2);
        background: var(--bg-secondary);
        border: 1px solid var(--border-light);
        border-radius: var(--radius-md);
        padding: var(--space-2);
        cursor: pointer;
        transition: var(--transition-all);
        text-align: left;
    }

    .neighbor-item:hover {
        background: var(--bg-elevated);
        border-color: var(--accent);
    }

    .neighbor-name {
        flex: 1;
        font-weight: 500;
    }

    .neighbor-type {
        font-size: 0.75rem;
        color: var(--text-muted);
        background: var(--bg-primary);
        padding: 2px 6px;
        border-radius: var(--radius-sm);
    }

    .neighbor-rel {
        font-size: 0.7rem;
        color: var(--text-subtle);
    }

    .source-list {
        margin: 0;
        padding-left: var(--space-4);
        font-size: 0.85rem;
        color: var(--text-secondary);
    }

    .source-list li {
        margin-bottom: var(--space-1);
    }
</style>
