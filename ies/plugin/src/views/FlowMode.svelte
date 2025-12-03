<script lang="ts">
    /**
     * FlowMode - Layer 3 Visual Graph Exploration
     *
     * Navigate the knowledge graph visually with grouped concept display.
     * "Flow" = navigate freely through the concept space.
     */
    import { onMount, createEventDispatcher } from 'svelte';
    import { showMessage, fetchSyncPost } from 'siyuan';

    export let plugin: any;
    export let backendUrl: string;

    const dispatch = createEventDispatcher();

    // State
    let searchQuery = '';
    let isSearching = false;
    let searchResults: Array<{name: string, type: string}> = [];
    let currentConcept: string | null = null;
    let nodes: Array<{name: string, type: string, labels: string[]}> = [];
    let relationships: Array<{start: string, type: string, end: string}> = [];
    let explorationPath: string[] = [];
    let thinkingQuestion: string | null = null;
    let isLoadingQuestion = false;
    let isExploring = false;

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

            // Add to path (avoid duplicates if navigating back)
            const existingIndex = explorationPath.indexOf(concept);
            if (existingIndex >= 0) {
                // Navigating back - truncate path
                explorationPath = explorationPath.slice(0, existingIndex + 1);
            } else {
                explorationPath = [...explorationPath, concept];
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
        } catch (err) {
            showMessage(`Question failed: ${err.message}`, 5000, 'error');
        } finally {
            isLoadingQuestion = false;
        }
    }

    function handleBack() {
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
        thinkingQuestion = null;
        searchQuery = '';
        searchResults = [];
    }

    function navigateToPathStep(index: number) {
        const concept = explorationPath[index];
        if (concept && concept !== currentConcept) {
            exploreConcept(concept);
        }
    }
</script>

<div class="flow-mode">
    <div class="flow-header">
        <button class="back-btn" on:click={handleBack} title="Back to Dashboard">
            <svg viewBox="0 0 24 24" width="16" height="16">
                <path fill="currentColor" d="M20 11H7.83l5.59-5.59L12 4l-8 8 8 8 1.41-1.41L7.83 13H20v-2z"/>
            </svg>
        </button>
        <span class="flow-title">Flow</span>
        {#if explorationPath.length > 0}
            <button class="clear-btn" on:click={clearExploration} title="Clear exploration">
                Clear
            </button>
        {/if}
    </div>

    <div class="flow-search">
        <input
            type="text"
            bind:value={searchQuery}
            on:keydown={handleKeydown}
            placeholder="Search concepts..."
            disabled={isSearching}
        />
        <button
            class="b3-button b3-button--primary"
            on:click={handleSearch}
            disabled={isSearching || !searchQuery.trim()}
        >
            {isSearching ? '...' : 'Go'}
        </button>
    </div>

    <!-- Search Results -->
    {#if searchResults.length > 0}
        <div class="search-results">
            <div class="search-results-label">Results ({searchResults.length})</div>
            <div class="search-results-list">
                {#each searchResults as result}
                    <button
                        class="search-result"
                        class:search-result--theory={result.type === 'Theory'}
                        class:search-result--researcher={result.type === 'Researcher'}
                        on:click={() => exploreConcept(result.name)}
                    >
                        <span class="result-name">{result.name}</span>
                        <span class="result-type">{result.type}</span>
                    </button>
                {/each}
            </div>
        </div>
    {/if}

    {#if !currentConcept && searchResults.length === 0}
        <div class="flow-welcome">
            <p><strong>Flow</strong> is where you explore freely.</p>
            <p>Search for a concept to navigate the knowledge graph.</p>
        </div>
    {:else if currentConcept}
        <div class="flow-graph">
            <!-- Current concept -->
            <div class="flow-center">
                <span class="center-concept" class:loading={isExploring}>
                    {isExploring ? '...' : currentConcept}
                </span>
            </div>

            <!-- Grouped relationships -->
            {#if groupedNodes.size > 0}
                <div class="flow-groups">
                    {#each [...groupedNodes.entries()] as [relType, relNodes]}
                        <div class="flow-group">
                            <div class="group-header">
                                <span class="group-arrow">{relNodes[0]?.direction === 'outgoing' ? '→' : '←'}</span>
                                <span class="group-label">{formatRelType(relType)}</span>
                                <span class="group-count">({relNodes.length})</span>
                            </div>
                            <div class="group-nodes">
                                {#each relNodes as node}
                                    <button
                                        class="flow-node"
                                        class:flow-node--theory={node.type === 'Theory'}
                                        class:flow-node--researcher={node.type === 'Researcher'}
                                        class:flow-node--concept={node.type === 'Concept'}
                                        on:click={() => exploreConcept(node.name)}
                                        title={node.type}
                                    >
                                        {node.name}
                                    </button>
                                {/each}
                            </div>
                        </div>
                    {/each}
                </div>
            {:else if !isExploring}
                <div class="flow-empty">
                    <p>No connections found for this concept.</p>
                    <p>Try the Thinking Partner for guidance.</p>
                </div>
            {/if}
        </div>

        <!-- Exploration path -->
        {#if explorationPath.length > 1}
            <div class="flow-path">
                <span class="path-label">Path:</span>
                {#each explorationPath as step, i}
                    <button
                        class="path-step"
                        class:path-step--current={i === explorationPath.length - 1}
                        on:click={() => navigateToPathStep(i)}
                        disabled={i === explorationPath.length - 1}
                    >
                        {step}
                    </button>
                    {#if i < explorationPath.length - 1}
                        <span class="path-arrow">→</span>
                    {/if}
                {/each}
            </div>
        {/if}

        <!-- Thinking Partner -->
        <div class="flow-actions">
            <button
                class="thinking-btn"
                on:click={requestThinkingPartner}
                disabled={isLoadingQuestion}
            >
                <svg viewBox="0 0 24 24" width="16" height="16">
                    <path fill="currentColor" d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 17h-2v-2h2v2zm2.07-7.75l-.9.92C13.45 12.9 13 13.5 13 15h-2v-.5c0-1.1.45-2.1 1.17-2.83l1.24-1.26c.37-.36.59-.86.59-1.41 0-1.1-.9-2-2-2s-2 .9-2 2H8c0-2.21 1.79-4 4-4s4 1.79 4 4c0 .88-.36 1.68-.93 2.25z"/>
                </svg>
                {isLoadingQuestion ? 'Thinking...' : 'Ask Thinking Partner'}
            </button>
        </div>

        {#if thinkingQuestion}
            <div class="flow-question">
                <div class="question-label">Thinking Partner</div>
                <div class="question-text">{thinkingQuestion}</div>
            </div>
        {/if}
    {/if}
</div>

<style>
    .flow-mode {
        display: flex;
        flex-direction: column;
        height: 100%;
        padding: 12px;
        gap: 12px;
    }

    .flow-header {
        display: flex;
        align-items: center;
        gap: 8px;
    }

    .back-btn {
        background: none;
        border: none;
        cursor: pointer;
        padding: 4px;
        border-radius: 4px;
        color: var(--b3-theme-on-surface);
        display: flex;
        align-items: center;
    }

    .back-btn:hover {
        background: var(--b3-theme-surface);
    }

    .flow-title {
        font-weight: 600;
        flex: 1;
    }

    .clear-btn {
        font-size: 12px;
        padding: 4px 8px;
        background: var(--b3-theme-surface);
        border: 1px solid var(--b3-border-color);
        border-radius: 4px;
        cursor: pointer;
        color: var(--b3-theme-on-surface);
    }

    .flow-search {
        display: flex;
        gap: 8px;
    }

    .flow-search input {
        flex: 1;
        padding: 8px 12px;
        border: 1px solid var(--b3-border-color);
        border-radius: 6px;
        font-size: 14px;
        background: var(--b3-theme-background);
        color: var(--b3-theme-on-background);
    }

    /* Search Results */
    .search-results {
        background: var(--b3-theme-surface);
        border-radius: 8px;
        padding: 8px;
    }

    .search-results-label {
        font-size: 11px;
        font-weight: 600;
        color: var(--b3-theme-on-surface-light);
        margin-bottom: 8px;
        text-transform: uppercase;
    }

    .search-results-list {
        display: flex;
        flex-direction: column;
        gap: 4px;
    }

    .search-result {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 8px 12px;
        background: var(--b3-theme-background);
        border: 1px solid var(--b3-border-color);
        border-radius: 6px;
        cursor: pointer;
        transition: all 0.15s;
    }

    .search-result:hover {
        border-color: var(--b3-theme-primary);
        background: var(--b3-theme-primary-lightest);
    }

    .search-result--theory {
        border-left: 3px solid var(--b3-theme-success);
    }

    .search-result--researcher {
        border-left: 3px solid var(--b3-theme-secondary);
    }

    .result-name {
        font-size: 14px;
        font-weight: 500;
    }

    .result-type {
        font-size: 11px;
        color: var(--b3-theme-on-surface-light);
        padding: 2px 6px;
        background: var(--b3-theme-surface);
        border-radius: 4px;
    }

    .flow-welcome {
        flex: 1;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        text-align: center;
        color: var(--b3-theme-on-surface-light);
        padding: 24px;
    }

    .flow-welcome p {
        margin: 8px 0;
    }

    .flow-graph {
        flex: 1;
        display: flex;
        flex-direction: column;
        gap: 16px;
        overflow-y: auto;
    }

    .flow-center {
        text-align: center;
        padding: 12px;
    }

    .center-concept {
        display: inline-block;
        font-size: 18px;
        font-weight: 600;
        padding: 10px 20px;
        background: var(--b3-theme-primary);
        color: var(--b3-theme-on-primary);
        border-radius: 24px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
    }

    .center-concept.loading {
        opacity: 0.6;
    }

    /* Grouped relationships */
    .flow-groups {
        display: flex;
        flex-direction: column;
        gap: 12px;
    }

    .flow-group {
        background: var(--b3-theme-surface);
        border-radius: 8px;
        padding: 10px;
    }

    .group-header {
        display: flex;
        align-items: center;
        gap: 6px;
        margin-bottom: 8px;
        padding-bottom: 6px;
        border-bottom: 1px solid var(--b3-border-color);
    }

    .group-arrow {
        font-size: 14px;
        color: var(--b3-theme-primary);
        font-weight: bold;
    }

    .group-label {
        font-size: 12px;
        font-weight: 600;
        color: var(--b3-theme-on-surface);
        text-transform: capitalize;
    }

    .group-count {
        font-size: 11px;
        color: var(--b3-theme-on-surface-light);
    }

    .group-nodes {
        display: flex;
        flex-wrap: wrap;
        gap: 6px;
    }

    .flow-node {
        padding: 5px 10px;
        background: var(--b3-theme-background);
        border: 1px solid var(--b3-border-color);
        border-radius: 6px;
        cursor: pointer;
        font-size: 13px;
        color: var(--b3-theme-on-surface);
        transition: all 0.15s;
    }

    .flow-node:hover {
        background: var(--b3-theme-primary-lightest);
        border-color: var(--b3-theme-primary);
    }

    .flow-node--theory {
        border-left: 3px solid var(--b3-theme-success);
    }

    .flow-node--researcher {
        border-left: 3px solid var(--b3-theme-secondary);
    }

    .flow-node--concept {
        border-left: 3px solid var(--b3-theme-primary-light);
    }

    .flow-empty {
        text-align: center;
        padding: 24px;
        color: var(--b3-theme-on-surface-light);
    }

    .flow-empty p {
        margin: 4px 0;
    }

    /* Path */
    .flow-path {
        display: flex;
        flex-wrap: wrap;
        align-items: center;
        gap: 4px;
        font-size: 12px;
        padding: 8px;
        background: var(--b3-theme-surface);
        border-radius: 6px;
    }

    .path-label {
        font-weight: 600;
        color: var(--b3-theme-on-surface-light);
    }

    .path-step {
        padding: 3px 8px;
        background: var(--b3-theme-background);
        border: 1px solid var(--b3-border-color);
        border-radius: 4px;
        cursor: pointer;
        font-size: 12px;
        color: var(--b3-theme-on-surface);
        transition: all 0.15s;
    }

    .path-step:hover:not(:disabled) {
        background: var(--b3-theme-primary-lightest);
        border-color: var(--b3-theme-primary);
    }

    .path-step--current {
        background: var(--b3-theme-primary-lightest);
        border-color: var(--b3-theme-primary);
        font-weight: 600;
        cursor: default;
    }

    .path-step:disabled {
        cursor: default;
    }

    .path-arrow {
        color: var(--b3-theme-on-surface-light);
    }

    /* Actions */
    .flow-actions {
        padding-top: 8px;
        border-top: 1px solid var(--b3-border-color);
    }

    .thinking-btn {
        display: flex;
        align-items: center;
        gap: 6px;
        padding: 8px 16px;
        background: var(--b3-theme-surface);
        border: 1px solid var(--b3-border-color);
        border-radius: 6px;
        cursor: pointer;
        font-size: 13px;
        color: var(--b3-theme-on-surface);
        transition: all 0.15s;
    }

    .thinking-btn:hover:not(:disabled) {
        background: var(--b3-theme-primary-lightest);
        border-color: var(--b3-theme-primary);
    }

    .thinking-btn:disabled {
        opacity: 0.6;
        cursor: not-allowed;
    }

    .flow-question {
        padding: 12px;
        background: var(--b3-theme-primary-lightest);
        border-radius: 8px;
        border-left: 3px solid var(--b3-theme-primary);
    }

    .question-label {
        font-size: 11px;
        font-weight: 600;
        text-transform: uppercase;
        color: var(--b3-theme-primary);
        margin-bottom: 6px;
    }

    .question-text {
        font-size: 14px;
        line-height: 1.5;
        font-style: italic;
    }
</style>
