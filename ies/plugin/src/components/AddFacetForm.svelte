<script lang="ts">
    import { createEventDispatcher } from 'svelte';
    import { fetchSyncPost } from 'siyuan';

    export let parentEntity: string;
    export let facetName: string;
    export let backendUrl: string;

    const dispatch = createEventDispatcher<{
        created: { name: string; entity_type: string; created: boolean };
        cancel: void;
    }>();

    const ENTITY_TYPES = [
        'Concept',
        'Theory',
        'Person',
        'Method',
        'Framework',
        'Assessment',
        'Mechanism',
        'Pattern',
        'Phenomenon',
        'Distinction',
    ];

    let entityName = '';
    let entityType = 'Concept';
    let description = '';
    let isSubmitting = false;
    let error: string | null = null;

    async function forwardProxy<T>(method: 'GET' | 'POST', endpoint: string, body?: any): Promise<T> {
        if (!backendUrl) {
            throw new Error('Backend URL is not configured');
        }
        const url = `${backendUrl}${endpoint}`;
        const payload: any = {
            url,
            method,
            timeout: 60000,
            contentType: 'application/json',
            headers: [],
        };
        if (method === 'POST') {
            payload.payload = body ?? {};
        }
        const response = await fetchSyncPost('/api/network/forwardProxy', payload);
        if (response.code !== 0) {
            throw new Error(`Proxy error: ${response.msg}`);
        }
        const proxyData = response.data;
        if (!proxyData || proxyData.status < 200 || proxyData.status >= 300) {
            const errBody = typeof proxyData?.body === 'string' ? proxyData.body : JSON.stringify(proxyData?.body);
            throw new Error(`Backend error ${proxyData?.status || 'unknown'}: ${errBody}`);
        }
        return typeof proxyData.body === 'string' ? JSON.parse(proxyData.body) : proxyData.body;
    }

    async function handleSubmit() {
        if (!entityName.trim()) {
            error = 'Entity name is required';
            return;
        }

        isSubmitting = true;
        error = null;

        try {
            const result = await forwardProxy<{
                name: string;
                entity_type: string;
                created: boolean;
                parent_entity?: string;
                facet_name?: string;
            }>('POST', '/graph/entity', {
                name: entityName.trim(),
                entity_type: entityType,
                parent_entity: parentEntity,
                facet_name: facetName,
                description: description.trim() || null,
            });

            dispatch('created', {
                name: result.name,
                entity_type: result.entity_type,
                created: result.created,
            });

            // Reset form
            entityName = '';
            description = '';
        } catch (err: any) {
            error = err?.message || String(err);
        } finally {
            isSubmitting = false;
        }
    }

    function handleCancel() {
        dispatch('cancel');
    }

    function handleKeydown(event: KeyboardEvent) {
        if (event.key === 'Escape') {
            handleCancel();
        }
    }
</script>

<div class="add-facet-form" on:keydown={handleKeydown}>
    <div class="form-header">
        <span class="form-icon">+</span>
        <span class="form-title">Add to "{facetName}"</span>
    </div>

    <div class="form-context">
        <span class="context-label">Parent:</span>
        <span class="context-value">{parentEntity}</span>
    </div>

    <form on:submit|preventDefault={handleSubmit}>
        <div class="form-field">
            <label for="entity-name">Entity Name</label>
            <input
                id="entity-name"
                type="text"
                bind:value={entityName}
                placeholder="Enter entity name..."
                disabled={isSubmitting}
                autofocus
            />
        </div>

        <div class="form-field">
            <label for="entity-type">Type</label>
            <select
                id="entity-type"
                bind:value={entityType}
                disabled={isSubmitting}
            >
                {#each ENTITY_TYPES as type}
                    <option value={type}>{type}</option>
                {/each}
            </select>
        </div>

        <div class="form-field">
            <label for="description">Description (optional)</label>
            <textarea
                id="description"
                bind:value={description}
                placeholder="Brief description..."
                rows="3"
                disabled={isSubmitting}
            />
        </div>

        {#if error}
            <div class="form-error">{error}</div>
        {/if}

        <div class="form-actions">
            <button
                type="button"
                class="btn-cancel"
                on:click={handleCancel}
                disabled={isSubmitting}
            >
                Cancel
            </button>
            <button
                type="submit"
                class="btn-submit"
                disabled={isSubmitting || !entityName.trim()}
            >
                {#if isSubmitting}
                    <span class="spinner"></span>
                    Creating...
                {:else}
                    Add Entity
                {/if}
            </button>
        </div>
    </form>
</div>

<style>
    .add-facet-form {
        background: var(--b3-theme-surface);
        border-radius: 8px;
        padding: 16px;
        border: 1px solid var(--b3-theme-primary-lighter);
    }

    .form-header {
        display: flex;
        align-items: center;
        gap: 8px;
        margin-bottom: 12px;
        font-weight: 600;
        color: var(--b3-theme-on-surface);
    }

    .form-icon {
        width: 20px;
        height: 20px;
        display: flex;
        align-items: center;
        justify-content: center;
        background: var(--b3-theme-primary);
        color: white;
        border-radius: 50%;
        font-size: 14px;
        font-weight: bold;
    }

    .form-title {
        font-size: 14px;
    }

    .form-context {
        display: flex;
        gap: 6px;
        margin-bottom: 16px;
        font-size: 12px;
        color: var(--b3-theme-on-surface-light);
    }

    .context-label {
        opacity: 0.7;
    }

    .context-value {
        color: var(--b3-theme-primary);
    }

    form {
        display: flex;
        flex-direction: column;
        gap: 12px;
    }

    .form-field {
        display: flex;
        flex-direction: column;
        gap: 4px;
    }

    .form-field label {
        font-size: 12px;
        font-weight: 500;
        color: var(--b3-theme-on-surface-light);
    }

    .form-field input,
    .form-field select,
    .form-field textarea {
        background: var(--b3-theme-background);
        border: 1px solid var(--b3-border-color);
        border-radius: 4px;
        padding: 8px 10px;
        font-size: 13px;
        color: var(--b3-theme-on-surface);
        transition: border-color 0.15s;
    }

    .form-field input:focus,
    .form-field select:focus,
    .form-field textarea:focus {
        outline: none;
        border-color: var(--b3-theme-primary);
    }

    .form-field input:disabled,
    .form-field select:disabled,
    .form-field textarea:disabled {
        opacity: 0.6;
        cursor: not-allowed;
    }

    .form-field textarea {
        resize: vertical;
        min-height: 60px;
    }

    .form-error {
        font-size: 12px;
        color: var(--b3-theme-error);
        padding: 8px;
        background: rgba(255, 0, 0, 0.05);
        border-radius: 4px;
    }

    .form-actions {
        display: flex;
        justify-content: flex-end;
        gap: 8px;
        margin-top: 4px;
    }

    .btn-cancel,
    .btn-submit {
        padding: 8px 16px;
        border-radius: 4px;
        font-size: 13px;
        font-weight: 500;
        cursor: pointer;
        transition: all 0.15s;
        display: flex;
        align-items: center;
        gap: 6px;
    }

    .btn-cancel {
        background: transparent;
        border: 1px solid var(--b3-border-color);
        color: var(--b3-theme-on-surface-light);
    }

    .btn-cancel:hover:not(:disabled) {
        background: var(--b3-theme-background);
        border-color: var(--b3-theme-on-surface-light);
    }

    .btn-submit {
        background: var(--b3-theme-primary);
        border: 1px solid var(--b3-theme-primary);
        color: white;
    }

    .btn-submit:hover:not(:disabled) {
        background: var(--b3-theme-primary-light);
    }

    .btn-cancel:disabled,
    .btn-submit:disabled {
        opacity: 0.5;
        cursor: not-allowed;
    }

    .spinner {
        width: 14px;
        height: 14px;
        border: 2px solid rgba(255, 255, 255, 0.3);
        border-top-color: white;
        border-radius: 50%;
        animation: spin 0.8s linear infinite;
    }

    @keyframes spin {
        to {
            transform: rotate(360deg);
        }
    }
</style>
