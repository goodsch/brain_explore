<script lang="ts">
    import { createEventDispatcher, onMount } from 'svelte';
    import { fetchSyncPost, showMessage } from 'siyuan';
    import { getBackendUrl, createConceptDocument } from '../utils/siyuan-structure';
    import type { ConceptBlockMeta } from '../types/blocks';

    // Types
    interface ExtractedEntity {
        name: string;
        type: string;
        mention_count?: number;
    }

    interface ConceptRelationship {
        target_name: string;
        relationship_type: string;
        evidence?: string;
    }

    interface SessionData {
        sessionId: string;
        topic: string;
        mode: string;
        messages: Array<{ role: string; content: string }>;
        entitiesExtracted: number;
        questionClassesUsed: string[];
    }

    // Props
    export let sessionData: SessionData;
    export let extractedEntities: ExtractedEntity[] = [];
    export let onClose: () => void;
    export let onComplete: (conceptName: string, conceptId: string) => void;

    const dispatch = createEventDispatcher();
    const backendUrl = getBackendUrl();

    // Wizard state
    type WizardStep = 'select' | 'define' | 'relate' | 'review';
    let currentStep: WizardStep = 'select';
    let isSubmitting = false;
    let error: string | null = null;

    // Concept data
    const CONCEPT_TYPES = [
        { value: 'concept', label: 'Concept', icon: '💡', description: 'A general idea or notion' },
        { value: 'theory', label: 'Theory', icon: '🔬', description: 'An explanatory framework' },
        { value: 'framework', label: 'Framework', icon: '🏗️', description: 'A structural approach' },
        { value: 'mechanism', label: 'Mechanism', icon: '⚙️', description: 'How something works' },
        { value: 'pattern', label: 'Pattern', icon: '🔄', description: 'A recurring phenomenon' },
        { value: 'distinction', label: 'Distinction', icon: '⚖️', description: 'A key difference' },
    ];

    const RELATIONSHIP_TYPES = [
        { value: 'supports', label: 'Supports' },
        { value: 'contradicts', label: 'Contradicts' },
        { value: 'component_of', label: 'Component of' },
        { value: 'operationalizes', label: 'Operationalizes' },
        { value: 'develops', label: 'Develops' },
        { value: 'enables', label: 'Enables' },
        { value: 'contrasts_with', label: 'Contrasts with' },
    ];

    // Form data
    let conceptName = '';
    let conceptType = 'concept';
    let description = '';
    let aliases: string[] = [];
    let aliasInput = '';
    let relationships: ConceptRelationship[] = [];
    let selectedQuotes: string[] = [];

    // Related concepts for relationship selection
    let existingConcepts: string[] = [];
    let loadingConcepts = false;
    let newRelTarget = '';
    let newRelType = 'supports';
    let newRelEvidence = '';

    // Pre-fill from entity selection
    let selectedEntity: ExtractedEntity | null = null;

    onMount(async () => {
        await loadExistingConcepts();
        extractQuotesFromSession();
    });

    async function loadExistingConcepts() {
        loadingConcepts = true;
        try {
            const response = await fetchSyncPost('/api/network/forwardProxy', {
                url: `${backendUrl}/concepts?limit=100`,
                method: 'GET',
                timeout: 10000,
                contentType: 'application/json',
                headers: []
            });

            if (response.code === 0 && response.data?.status === 200) {
                const body = JSON.parse(response.data.body);
                existingConcepts = (body.concepts || []).map((c: any) => c.name);
            }
        } catch (err) {
            console.error('[IES] Failed to load concepts:', err);
        } finally {
            loadingConcepts = false;
        }
    }

    function extractQuotesFromSession() {
        // Extract user messages as potential source quotes
        const userMessages = sessionData.messages
            .filter(m => m.role === 'user')
            .map(m => m.content)
            .filter(c => c.length > 20 && c.length < 500);
        selectedQuotes = userMessages.slice(0, 5);
    }

    function selectEntity(entity: ExtractedEntity) {
        selectedEntity = entity;
        conceptName = entity.name;
        // Auto-advance to define step
        currentStep = 'define';
    }

    function startFromScratch() {
        selectedEntity = null;
        conceptName = '';
        currentStep = 'define';
    }

    function addAlias() {
        const alias = aliasInput.trim();
        if (alias && !aliases.includes(alias)) {
            aliases = [...aliases, alias];
            aliasInput = '';
        }
    }

    function removeAlias(alias: string) {
        aliases = aliases.filter(a => a !== alias);
    }

    function addRelationship() {
        if (!newRelTarget.trim()) return;
        const rel: ConceptRelationship = {
            target_name: newRelTarget.trim(),
            relationship_type: newRelType,
            evidence: newRelEvidence.trim() || undefined,
        };
        relationships = [...relationships, rel];
        newRelTarget = '';
        newRelEvidence = '';
    }

    function removeRelationship(index: number) {
        relationships = relationships.filter((_, i) => i !== index);
    }

    function toggleQuote(quote: string) {
        if (selectedQuotes.includes(quote)) {
            selectedQuotes = selectedQuotes.filter(q => q !== quote);
        } else {
            selectedQuotes = [...selectedQuotes, quote];
        }
    }

    function goToStep(step: WizardStep) {
        error = null;
        currentStep = step;
    }

    function validateDefineStep(): boolean {
        if (!conceptName.trim()) {
            error = 'Concept name is required';
            return false;
        }
        if (!description.trim() || description.length < 10) {
            error = 'Description must be at least 10 characters';
            return false;
        }
        return true;
    }

    async function handleSubmit() {
        if (isSubmitting) return;

        error = null;
        isSubmitting = true;

        try {
            // 1. Create concept in backend
            const payload = {
                name: conceptName.trim(),
                concept_type: conceptType,
                description: description.trim(),
                aliases,
                relationships,
                source_session_id: sessionData.sessionId,
                source_quotes: selectedQuotes,
                user_id: 'chris', // TODO: Get from settings
            };

            const response = await fetchSyncPost('/api/network/forwardProxy', {
                url: `${backendUrl}/concepts`,
                method: 'POST',
                timeout: 15000,
                contentType: 'application/json',
                headers: [],
                payload: JSON.stringify(payload),
            });

            if (response.code !== 0 || response.data?.status !== 200) {
                const errorBody = response.data?.body ? JSON.parse(response.data.body) : {};
                throw new Error(errorBody.detail || 'Failed to create concept');
            }

            const result = JSON.parse(response.data.body);

            // 2. Create concept document in SiYuan
            const docId = await createConceptDocument({
                conceptId: result.concept_id,
                name: conceptName.trim(),
                conceptType: conceptType,
                description: description.trim(),
                aliases,
                relationships: relationships.map(r => ({
                    targetName: r.target_name,
                    relationshipType: r.relationship_type,
                    evidence: r.evidence,
                })),
                sourceSessionId: sessionData.sessionId,
                sourceQuotes: selectedQuotes,
                userId: 'chris', // TODO: Get from settings
            });

            showMessage(`Concept "${conceptName}" created successfully!`, 3000);
            onComplete(conceptName, result.concept_id);
        } catch (err: any) {
            console.error('[IES] Concept creation failed:', err);
            error = err.message || 'Failed to create concept';
            showMessage(`Error: ${error}`, 5000, 'error');
        } finally {
            isSubmitting = false;
        }
    }

    // Step navigation helpers
    $: canProceedFromDefine = conceptName.trim().length > 0 && description.trim().length >= 10;
    $: stepNumber = { select: 1, define: 2, relate: 3, review: 4 }[currentStep];
</script>

<div class="concept-extractor">
    <div class="extractor-header">
        <h2>Extract Concept</h2>
        <button class="close-btn" on:click={onClose}>×</button>
    </div>

    <!-- Progress indicator -->
    <div class="progress-steps">
        {#each ['Select', 'Define', 'Relate', 'Review'] as step, i}
            <div
                class="progress-step"
                class:active={stepNumber === i + 1}
                class:completed={stepNumber > i + 1}
            >
                <span class="step-number">{i + 1}</span>
                <span class="step-label">{step}</span>
            </div>
        {/each}
    </div>

    <!-- Error display -->
    {#if error}
        <div class="error-banner">
            <span class="error-icon">⚠️</span>
            <span>{error}</span>
            <button class="dismiss-btn" on:click={() => error = null}>×</button>
        </div>
    {/if}

    <!-- Step 1: Select source -->
    {#if currentStep === 'select'}
        <div class="step-content">
            <h3>Choose a starting point</h3>
            <p class="step-description">
                Select an entity mentioned in your session, or define a new concept from scratch.
            </p>

            {#if extractedEntities.length > 0}
                <div class="entity-list">
                    <h4>Entities from this session</h4>
                    {#each extractedEntities as entity}
                        <button
                            class="entity-card"
                            on:click={() => selectEntity(entity)}
                        >
                            <span class="entity-name">{entity.name}</span>
                            <span class="entity-type">{entity.type}</span>
                            {#if entity.mention_count}
                                <span class="mention-count">{entity.mention_count}×</span>
                            {/if}
                        </button>
                    {/each}
                </div>
            {:else}
                <div class="no-entities">
                    <p>No entities were extracted from this session.</p>
                </div>
            {/if}

            <div class="divider">
                <span>or</span>
            </div>

            <button class="btn btn-secondary" on:click={startFromScratch}>
                Define New Concept
            </button>
        </div>
    {/if}

    <!-- Step 2: Define -->
    {#if currentStep === 'define'}
        <div class="step-content">
            <h3>Define the Concept</h3>

            <div class="form-group">
                <label for="concept-name">Name</label>
                <input
                    id="concept-name"
                    type="text"
                    bind:value={conceptName}
                    placeholder="Enter concept name..."
                    class="input-field"
                />
            </div>

            <div class="form-group">
                <label for="concept-type">Type</label>
                <div class="type-selector">
                    {#each CONCEPT_TYPES as ct}
                        <button
                            class="type-option"
                            class:selected={conceptType === ct.value}
                            on:click={() => conceptType = ct.value}
                            title={ct.description}
                        >
                            <span class="type-icon">{ct.icon}</span>
                            <span class="type-label">{ct.label}</span>
                        </button>
                    {/each}
                </div>
            </div>

            <div class="form-group">
                <label for="description">Definition</label>
                <textarea
                    id="description"
                    bind:value={description}
                    placeholder="What is this concept? How would you explain it?"
                    rows="4"
                    class="textarea-field"
                ></textarea>
                <span class="char-count" class:warning={description.length < 10}>
                    {description.length} characters (min 10)
                </span>
            </div>

            <div class="form-group">
                <label>Aliases (optional)</label>
                <div class="alias-input-row">
                    <input
                        type="text"
                        bind:value={aliasInput}
                        placeholder="Add alternative name..."
                        class="input-field"
                        on:keydown={(e) => e.key === 'Enter' && addAlias()}
                    />
                    <button class="btn btn-small" on:click={addAlias}>Add</button>
                </div>
                {#if aliases.length > 0}
                    <div class="alias-tags">
                        {#each aliases as alias}
                            <span class="alias-tag">
                                {alias}
                                <button class="remove-alias" on:click={() => removeAlias(alias)}>×</button>
                            </span>
                        {/each}
                    </div>
                {/if}
            </div>

            <div class="step-actions">
                <button class="btn btn-secondary" on:click={() => goToStep('select')}>Back</button>
                <button
                    class="btn btn-primary"
                    disabled={!canProceedFromDefine}
                    on:click={() => validateDefineStep() && goToStep('relate')}
                >
                    Next: Relationships
                </button>
            </div>
        </div>
    {/if}

    <!-- Step 3: Relationships -->
    {#if currentStep === 'relate'}
        <div class="step-content">
            <h3>Connect to Other Concepts</h3>
            <p class="step-description">
                How does "{conceptName}" relate to existing concepts? (Optional)
            </p>

            <div class="relationship-form">
                <div class="rel-row">
                    <select bind:value={newRelType} class="select-field">
                        {#each RELATIONSHIP_TYPES as rt}
                            <option value={rt.value}>{rt.label}</option>
                        {/each}
                    </select>

                    <input
                        type="text"
                        list="concept-suggestions"
                        bind:value={newRelTarget}
                        placeholder="Target concept..."
                        class="input-field"
                    />
                    <datalist id="concept-suggestions">
                        {#each existingConcepts as c}
                            <option value={c} />
                        {/each}
                    </datalist>

                    <button
                        class="btn btn-small"
                        on:click={addRelationship}
                        disabled={!newRelTarget.trim()}
                    >
                        Add
                    </button>
                </div>

                <input
                    type="text"
                    bind:value={newRelEvidence}
                    placeholder="Evidence or explanation (optional)..."
                    class="input-field evidence-input"
                />
            </div>

            {#if relationships.length > 0}
                <div class="relationships-list">
                    <h4>Relationships</h4>
                    {#each relationships as rel, i}
                        <div class="relationship-item">
                            <span class="rel-badge">{rel.relationship_type}</span>
                            <span class="rel-target">{rel.target_name}</span>
                            {#if rel.evidence}
                                <span class="rel-evidence">"{rel.evidence}"</span>
                            {/if}
                            <button class="remove-btn" on:click={() => removeRelationship(i)}>×</button>
                        </div>
                    {/each}
                </div>
            {:else}
                <div class="no-relationships">
                    <p>No relationships added yet. You can skip this step if you prefer.</p>
                </div>
            {/if}

            <div class="step-actions">
                <button class="btn btn-secondary" on:click={() => goToStep('define')}>Back</button>
                <button class="btn btn-primary" on:click={() => goToStep('review')}>
                    Next: Review
                </button>
            </div>
        </div>
    {/if}

    <!-- Step 4: Review -->
    {#if currentStep === 'review'}
        <div class="step-content">
            <h3>Review & Create</h3>

            <div class="review-section">
                <div class="review-item">
                    <span class="review-label">Name:</span>
                    <span class="review-value">{conceptName}</span>
                </div>
                <div class="review-item">
                    <span class="review-label">Type:</span>
                    <span class="review-value">
                        {CONCEPT_TYPES.find(t => t.value === conceptType)?.icon}
                        {CONCEPT_TYPES.find(t => t.value === conceptType)?.label}
                    </span>
                </div>
                <div class="review-item">
                    <span class="review-label">Definition:</span>
                    <span class="review-value description-preview">{description}</span>
                </div>
                {#if aliases.length > 0}
                    <div class="review-item">
                        <span class="review-label">Aliases:</span>
                        <span class="review-value">{aliases.join(', ')}</span>
                    </div>
                {/if}
                {#if relationships.length > 0}
                    <div class="review-item">
                        <span class="review-label">Relationships:</span>
                        <span class="review-value">{relationships.length} connection(s)</span>
                    </div>
                {/if}
            </div>

            <div class="source-quotes">
                <h4>Source Quotes</h4>
                <p class="hint">Select quotes from your session to support this concept:</p>
                <div class="quotes-list">
                    {#each sessionData.messages.filter(m => m.role === 'user').slice(0, 5) as msg, i}
                        <label class="quote-item">
                            <input
                                type="checkbox"
                                checked={selectedQuotes.includes(msg.content)}
                                on:change={() => toggleQuote(msg.content)}
                            />
                            <span class="quote-text">"{msg.content.slice(0, 150)}{msg.content.length > 150 ? '...' : ''}"</span>
                        </label>
                    {/each}
                </div>
            </div>

            <div class="step-actions">
                <button class="btn btn-secondary" on:click={() => goToStep('relate')}>Back</button>
                <button
                    class="btn btn-primary btn-create"
                    on:click={handleSubmit}
                    disabled={isSubmitting}
                >
                    {#if isSubmitting}
                        Creating...
                    {:else}
                        Create Concept
                    {/if}
                </button>
            </div>
        </div>
    {/if}
</div>

<style>
    .concept-extractor {
        background: var(--ies-bg-elevated, var(--b3-theme-surface));
        border-radius: var(--ies-radius-lg, 12px);
        padding: var(--ies-space-6, 24px);
        max-width: 600px;
        margin: 0 auto;
        box-shadow: var(--ies-shadow-lg, 0 8px 32px rgba(0,0,0,0.12));
    }

    .extractor-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: var(--ies-space-4, 16px);
        padding-bottom: var(--ies-space-3, 12px);
        border-bottom: 1px solid var(--ies-border, var(--b3-theme-surface-lighter));
    }

    .extractor-header h2 {
        margin: 0;
        font-size: 1.25rem;
        color: var(--ies-text-primary, var(--b3-theme-on-surface));
    }

    .close-btn {
        background: none;
        border: none;
        font-size: 1.5rem;
        cursor: pointer;
        color: var(--ies-text-secondary, var(--b3-theme-on-surface-light));
        line-height: 1;
        padding: 4px;
    }

    .close-btn:hover {
        color: var(--ies-text-primary, var(--b3-theme-on-surface));
    }

    /* Progress steps */
    .progress-steps {
        display: flex;
        justify-content: space-between;
        margin-bottom: var(--ies-space-5, 20px);
        position: relative;
    }

    .progress-steps::before {
        content: '';
        position: absolute;
        top: 14px;
        left: 10%;
        right: 10%;
        height: 2px;
        background: var(--ies-border, var(--b3-theme-surface-lighter));
        z-index: 0;
    }

    .progress-step {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 4px;
        z-index: 1;
    }

    .step-number {
        width: 28px;
        height: 28px;
        border-radius: 50%;
        background: var(--ies-bg-elevated, var(--b3-theme-surface));
        border: 2px solid var(--ies-border, var(--b3-theme-surface-lighter));
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 0.875rem;
        font-weight: 600;
        color: var(--ies-text-secondary, var(--b3-theme-on-surface-light));
    }

    .progress-step.active .step-number {
        background: var(--ies-accent, #c98b2f);
        border-color: var(--ies-accent, #c98b2f);
        color: white;
    }

    .progress-step.completed .step-number {
        background: var(--ies-secondary, #7a9987);
        border-color: var(--ies-secondary, #7a9987);
        color: white;
    }

    .step-label {
        font-size: 0.75rem;
        color: var(--ies-text-secondary, var(--b3-theme-on-surface-light));
    }

    .progress-step.active .step-label {
        color: var(--ies-accent, #c98b2f);
        font-weight: 500;
    }

    /* Error banner */
    .error-banner {
        display: flex;
        align-items: center;
        gap: 8px;
        padding: 12px 16px;
        background: #fef2f2;
        border: 1px solid #fecaca;
        border-radius: 8px;
        margin-bottom: 16px;
        color: #dc2626;
    }

    .dismiss-btn {
        margin-left: auto;
        background: none;
        border: none;
        cursor: pointer;
        font-size: 1.25rem;
        line-height: 1;
        color: #dc2626;
    }

    /* Step content */
    .step-content {
        min-height: 300px;
    }

    .step-content h3 {
        margin: 0 0 8px 0;
        font-size: 1.125rem;
    }

    .step-description {
        color: var(--ies-text-secondary, var(--b3-theme-on-surface-light));
        margin-bottom: 20px;
    }

    /* Entity list */
    .entity-list {
        margin-bottom: 20px;
    }

    .entity-list h4 {
        font-size: 0.875rem;
        margin: 0 0 12px 0;
        color: var(--ies-text-secondary);
    }

    .entity-card {
        display: flex;
        align-items: center;
        gap: 12px;
        width: 100%;
        padding: 12px 16px;
        background: var(--ies-bg-base, var(--b3-theme-background));
        border: 1px solid var(--ies-border, var(--b3-theme-surface-lighter));
        border-radius: 8px;
        cursor: pointer;
        margin-bottom: 8px;
        text-align: left;
    }

    .entity-card:hover {
        border-color: var(--ies-accent, #c98b2f);
        background: var(--ies-bg-elevated, var(--b3-theme-surface));
    }

    .entity-name {
        font-weight: 500;
        flex: 1;
    }

    .entity-type {
        font-size: 0.75rem;
        padding: 2px 8px;
        background: var(--ies-bg-elevated, var(--b3-theme-surface));
        border-radius: 4px;
        color: var(--ies-text-secondary);
    }

    .mention-count {
        font-size: 0.75rem;
        color: var(--ies-text-secondary);
    }

    .no-entities {
        padding: 20px;
        text-align: center;
        color: var(--ies-text-secondary);
        background: var(--ies-bg-base, var(--b3-theme-background));
        border-radius: 8px;
    }

    /* Divider */
    .divider {
        display: flex;
        align-items: center;
        gap: 16px;
        margin: 20px 0;
        color: var(--ies-text-secondary);
    }

    .divider::before,
    .divider::after {
        content: '';
        flex: 1;
        height: 1px;
        background: var(--ies-border, var(--b3-theme-surface-lighter));
    }

    /* Form elements */
    .form-group {
        margin-bottom: 20px;
    }

    .form-group label {
        display: block;
        font-weight: 500;
        margin-bottom: 8px;
        font-size: 0.875rem;
    }

    .input-field, .textarea-field, .select-field {
        width: 100%;
        padding: 10px 12px;
        border: 1px solid var(--ies-border, var(--b3-theme-surface-lighter));
        border-radius: 8px;
        background: var(--ies-bg-base, var(--b3-theme-background));
        color: var(--ies-text-primary, var(--b3-theme-on-surface));
        font-size: 0.9375rem;
    }

    .input-field:focus, .textarea-field:focus, .select-field:focus {
        outline: none;
        border-color: var(--ies-accent, #c98b2f);
        box-shadow: 0 0 0 3px rgba(201, 139, 47, 0.1);
    }

    .char-count {
        font-size: 0.75rem;
        color: var(--ies-text-secondary);
        margin-top: 4px;
    }

    .char-count.warning {
        color: #dc2626;
    }

    /* Type selector */
    .type-selector {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 8px;
    }

    .type-option {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 4px;
        padding: 12px 8px;
        border: 1px solid var(--ies-border, var(--b3-theme-surface-lighter));
        border-radius: 8px;
        background: var(--ies-bg-base, var(--b3-theme-background));
        cursor: pointer;
    }

    .type-option:hover {
        border-color: var(--ies-accent, #c98b2f);
    }

    .type-option.selected {
        border-color: var(--ies-accent, #c98b2f);
        background: rgba(201, 139, 47, 0.1);
    }

    .type-icon {
        font-size: 1.25rem;
    }

    .type-label {
        font-size: 0.75rem;
    }

    /* Alias input */
    .alias-input-row {
        display: flex;
        gap: 8px;
    }

    .alias-input-row .input-field {
        flex: 1;
    }

    .alias-tags {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        margin-top: 12px;
    }

    .alias-tag {
        display: inline-flex;
        align-items: center;
        gap: 4px;
        padding: 4px 10px;
        background: var(--ies-bg-elevated, var(--b3-theme-surface));
        border-radius: 16px;
        font-size: 0.875rem;
    }

    .remove-alias {
        background: none;
        border: none;
        cursor: pointer;
        font-size: 1rem;
        line-height: 1;
        color: var(--ies-text-secondary);
        padding: 0 2px;
    }

    .remove-alias:hover {
        color: #dc2626;
    }

    /* Relationships */
    .relationship-form {
        background: var(--ies-bg-base, var(--b3-theme-background));
        padding: 16px;
        border-radius: 8px;
        margin-bottom: 20px;
    }

    .rel-row {
        display: flex;
        gap: 8px;
        margin-bottom: 8px;
    }

    .rel-row .select-field {
        width: 140px;
    }

    .rel-row .input-field {
        flex: 1;
    }

    .evidence-input {
        margin-top: 8px;
    }

    .relationships-list {
        margin-bottom: 20px;
    }

    .relationships-list h4 {
        font-size: 0.875rem;
        margin: 0 0 12px 0;
    }

    .relationship-item {
        display: flex;
        align-items: center;
        gap: 8px;
        padding: 10px 12px;
        background: var(--ies-bg-base, var(--b3-theme-background));
        border-radius: 8px;
        margin-bottom: 8px;
    }

    .rel-badge {
        font-size: 0.75rem;
        padding: 2px 8px;
        background: var(--ies-accent, #c98b2f);
        color: white;
        border-radius: 4px;
        text-transform: uppercase;
    }

    .rel-target {
        font-weight: 500;
    }

    .rel-evidence {
        font-size: 0.875rem;
        color: var(--ies-text-secondary);
        font-style: italic;
    }

    .remove-btn {
        margin-left: auto;
        background: none;
        border: none;
        cursor: pointer;
        color: var(--ies-text-secondary);
        font-size: 1.25rem;
        line-height: 1;
    }

    .remove-btn:hover {
        color: #dc2626;
    }

    .no-relationships {
        padding: 20px;
        text-align: center;
        color: var(--ies-text-secondary);
        background: var(--ies-bg-base, var(--b3-theme-background));
        border-radius: 8px;
    }

    /* Review section */
    .review-section {
        background: var(--ies-bg-base, var(--b3-theme-background));
        padding: 16px;
        border-radius: 8px;
        margin-bottom: 20px;
    }

    .review-item {
        display: flex;
        gap: 12px;
        padding: 8px 0;
        border-bottom: 1px solid var(--ies-border, var(--b3-theme-surface-lighter));
    }

    .review-item:last-child {
        border-bottom: none;
    }

    .review-label {
        font-weight: 500;
        min-width: 100px;
        color: var(--ies-text-secondary);
    }

    .review-value {
        flex: 1;
    }

    .description-preview {
        white-space: pre-wrap;
    }

    /* Source quotes */
    .source-quotes {
        margin-bottom: 20px;
    }

    .source-quotes h4 {
        margin: 0 0 8px 0;
        font-size: 0.875rem;
    }

    .source-quotes .hint {
        font-size: 0.875rem;
        color: var(--ies-text-secondary);
        margin-bottom: 12px;
    }

    .quotes-list {
        max-height: 200px;
        overflow-y: auto;
    }

    .quote-item {
        display: flex;
        align-items: flex-start;
        gap: 8px;
        padding: 8px;
        background: var(--ies-bg-base, var(--b3-theme-background));
        border-radius: 6px;
        margin-bottom: 8px;
        cursor: pointer;
    }

    .quote-item:hover {
        background: var(--ies-bg-elevated, var(--b3-theme-surface));
    }

    .quote-text {
        font-size: 0.875rem;
        color: var(--ies-text-secondary);
        font-style: italic;
    }

    /* Buttons */
    .btn {
        padding: 10px 20px;
        border-radius: 8px;
        font-weight: 500;
        cursor: pointer;
        border: none;
        transition: all 0.2s;
    }

    .btn:disabled {
        opacity: 0.5;
        cursor: not-allowed;
    }

    .btn-primary {
        background: var(--ies-accent, #c98b2f);
        color: white;
    }

    .btn-primary:hover:not(:disabled) {
        background: #b67d2a;
    }

    .btn-secondary {
        background: var(--ies-bg-elevated, var(--b3-theme-surface));
        color: var(--ies-text-primary, var(--b3-theme-on-surface));
        border: 1px solid var(--ies-border, var(--b3-theme-surface-lighter));
    }

    .btn-secondary:hover:not(:disabled) {
        background: var(--ies-bg-base, var(--b3-theme-background));
    }

    .btn-small {
        padding: 6px 12px;
        font-size: 0.875rem;
    }

    .btn-create {
        min-width: 140px;
    }

    .step-actions {
        display: flex;
        justify-content: space-between;
        gap: 12px;
        margin-top: 24px;
        padding-top: 16px;
        border-top: 1px solid var(--ies-border, var(--b3-theme-surface-lighter));
    }
</style>
