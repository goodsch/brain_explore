<script lang="ts">
    /**
     * FlowMode - Layer 3 Visual Graph Exploration
     *
     * Navigate the knowledge graph visually with radial concept display.
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
    let currentConcept: string | null = null;
    let nodes: Array<{name: string, type: string, labels: string[]}> = [];
    let relationships: Array<{start: string, type: string, end: string}> = [];
    let explorationPath: string[] = [];
    let thinkingQuestion: string | null = null;
    let isLoadingQuestion = false;

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
        try {
            const data = await apiGet(`/graph/search?q=${encodeURIComponent(searchQuery)}&limit=10`);
            if (data.results && data.results.length > 0) {
                // Navigate to first result
                await exploreConcept(data.results[0].name);
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
        try {
            const data = await apiGet(`/graph/explore/${encodeURIComponent(concept)}?depth=1`);
            currentConcept = concept;
            nodes = data.nodes || [];
            relationships = data.relationships || [];

            // Add to path
            explorationPath = [...explorationPath, concept];

            // Clear thinking question when navigating
            thinkingQuestion = null;
        } catch (err) {
            showMessage(`Explore failed: ${err.message}`, 5000, 'error');
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

    {#if !currentConcept}
        <div class="flow-welcome">
            <p><strong>Flow</strong> is where you explore freely.</p>
            <p>Search for a concept to navigate the knowledge graph.</p>
        </div>
    {:else}
        <div class="flow-graph">
            <div class="flow-center">
                <span class="center-concept">{currentConcept}</span>
            </div>

            <div class="flow-nodes">
                {#each nodes as node}
                    <button
                        class="flow-node"
                        class:flow-node--theory={node.type === 'Theory'}
                        class:flow-node--researcher={node.type === 'Researcher'}
                        on:click={() => exploreConcept(node.name)}
                        title={node.type}
                    >
                        {node.name}
                    </button>
                {/each}
            </div>

            {#if relationships.length > 0}
                <div class="flow-rels">
                    {#each relationships.slice(0, 5) as rel}
                        <span class="flow-rel">{rel.start} → {rel.type} → {rel.end}</span>
                    {/each}
                </div>
            {/if}
        </div>

        {#if explorationPath.length > 1}
            <div class="flow-path">
                <span class="path-label">Path:</span>
                {#each explorationPath as step, i}
                    <span class="path-step">{step}</span>
                    {#if i < explorationPath.length - 1}
                        <span class="path-arrow">→</span>
                    {/if}
                {/each}
            </div>
        {/if}

        <div class="flow-actions">
            <button
                class="b3-button"
                on:click={requestThinkingPartner}
                disabled={isLoadingQuestion}
            >
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
        padding: 16px;
    }
    .center-concept {
        font-size: 18px;
        font-weight: 600;
        padding: 8px 16px;
        background: var(--b3-theme-primary);
        color: var(--b3-theme-on-primary);
        border-radius: 8px;
    }
    .flow-nodes {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        justify-content: center;
    }
    .flow-node {
        padding: 6px 12px;
        background: var(--b3-theme-surface);
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
        border-color: var(--b3-theme-success);
    }
    .flow-node--researcher {
        border-color: var(--b3-theme-secondary);
    }
    .flow-rels {
        display: flex;
        flex-direction: column;
        gap: 4px;
        font-size: 12px;
        color: var(--b3-theme-on-surface-light);
        padding: 8px;
        background: var(--b3-theme-surface);
        border-radius: 6px;
    }
    .flow-rel {
        font-family: monospace;
    }
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
        padding: 2px 6px;
        background: var(--b3-theme-background);
        border-radius: 3px;
    }
    .path-arrow {
        color: var(--b3-theme-on-surface-light);
    }
    .flow-actions {
        padding-top: 8px;
        border-top: 1px solid var(--b3-border-color);
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
