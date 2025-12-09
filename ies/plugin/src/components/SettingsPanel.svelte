<script lang="ts">
    import { onMount, createEventDispatcher } from 'svelte';
    import {
        settingsStore,
        updateSettings,
        OPENAI_CHAT_MODELS,
        ANTHROPIC_CHAT_MODELS,
        OPENAI_EMBEDDING_MODELS,
        type IESSettings,
        type ChatProvider,
        type EmbeddingProvider,
    } from '../stores/settings';
    import {
        checkOllamaHealth,
        fetchOllamaModels,
        filterChatModels,
        filterEmbeddingModels,
        formatModelName,
        type OllamaModel,
        type OllamaHealthStatus,
    } from '../utils/ollama';
    import { fetchSyncPost } from 'siyuan';

    interface BackendHealth {
        ok: boolean;
        backendUrl: string;
        checkedAt: number;
        message?: string;
    }

    export let onClose: () => void;
    export let onSave: (settings: IESSettings) => void;

    const dispatch = createEventDispatcher();

    // Local copy of settings for editing (initialized once, not reactive)
    let settings: IESSettings = { ...$settingsStore };
    let initialized = false;

    // Only sync from store on first mount, not on every store update
    $: if (!initialized && $settingsStore) {
        settings = { ...$settingsStore };
        initialized = true;
    }

    // Connection status
    let backendStatus: BackendHealth | null = null;
    let ollamaStatus: OllamaHealthStatus | null = null;
    let checkingBackend = false;
    let checkingOllama = false;

    // Ollama models
    let ollamaChatModels: OllamaModel[] = [];
    let ollamaEmbeddingModels: OllamaModel[] = [];

    // Section collapse state
    let sectionsExpanded = {
        connections: true,
        aiProviders: true,
        apiKeys: false,
        notebooks: false,
        display: false,
    };

    // Debounce timer for URL changes
    let urlDebounceTimer: ReturnType<typeof setTimeout> | null = null;

    onMount(async () => {
        await checkConnections();
    });

    async function checkConnections() {
        await Promise.all([
            checkBackendConnection(),
            checkOllamaConnection(),
        ]);
    }

    async function checkBackendConnection() {
        checkingBackend = true;
        const url = settings.backendUrl;
        try {
            // Use SiYuan's forwardProxy to check backend health
            const response = await fetchSyncPost('/api/network/forwardProxy', {
                url: `${url}/health`,
                method: 'GET',
                timeout: 5000,
                contentType: 'application/json',
                headers: []
            });

            if (response.code === 0 && response.data?.status === 200) {
                backendStatus = {
                    ok: true,
                    backendUrl: url,
                    checkedAt: Date.now(),
                    message: 'Connected',
                };
            } else {
                backendStatus = {
                    ok: false,
                    backendUrl: url,
                    checkedAt: Date.now(),
                    message: response.msg || 'Backend unreachable',
                };
            }
        } catch (e) {
            backendStatus = {
                ok: false,
                backendUrl: url,
                checkedAt: Date.now(),
                message: e instanceof Error ? e.message : 'Connection failed',
            };
        }
        checkingBackend = false;
    }

    async function checkOllamaConnection() {
        checkingOllama = true;
        try {
            ollamaStatus = await checkOllamaHealth(settings.ollamaUrl);
            if (ollamaStatus.ok) {
                const models = await fetchOllamaModels(settings.ollamaUrl);
                ollamaChatModels = filterChatModels(models);
                ollamaEmbeddingModels = filterEmbeddingModels(models);
            } else {
                ollamaChatModels = [];
                ollamaEmbeddingModels = [];
            }
        } catch (e) {
            ollamaStatus = {
                ok: false,
                modelCount: 0,
                error: e instanceof Error ? e.message : 'Connection failed',
            };
            ollamaChatModels = [];
            ollamaEmbeddingModels = [];
        }
        checkingOllama = false;
    }

    function handleUrlChange(type: 'backend' | 'ollama') {
        if (urlDebounceTimer) {
            clearTimeout(urlDebounceTimer);
        }
        urlDebounceTimer = setTimeout(() => {
            if (type === 'backend') {
                checkBackendConnection();
            } else {
                checkOllamaConnection();
            }
        }, 500);
    }

    function handleSettingChange() {
        updateSettings(settings);
        onSave(settings);
    }

    function toggleSection(section: keyof typeof sectionsExpanded) {
        sectionsExpanded[section] = !sectionsExpanded[section];
    }

    function getChatModelsForProvider(provider: ChatProvider) {
        switch (provider) {
            case 'ollama':
                return ollamaChatModels.map(m => ({ id: m.name, name: formatModelName(m.name) }));
            case 'openai':
                return OPENAI_CHAT_MODELS;
            case 'anthropic':
                return ANTHROPIC_CHAT_MODELS;
            default:
                return [];
        }
    }

    function getEmbeddingModelsForProvider(provider: EmbeddingProvider) {
        switch (provider) {
            case 'ollama':
                return ollamaEmbeddingModels.map(m => ({ id: m.name, name: formatModelName(m.name) }));
            case 'openai':
                return OPENAI_EMBEDDING_MODELS;
            default:
                return [];
        }
    }

    // When provider changes, reset model to first available
    function handleChatProviderChange() {
        const models = getChatModelsForProvider(settings.chatProvider);
        if (models.length > 0 && !models.find(m => m.id === settings.chatModel)) {
            settings.chatModel = models[0].id;
        }
        handleSettingChange();
    }

    function handleEmbeddingProviderChange() {
        const models = getEmbeddingModelsForProvider(settings.embeddingProvider);
        if (models.length > 0 && !models.find(m => m.id === settings.embeddingModel)) {
            settings.embeddingModel = models[0].id;
        }
        handleSettingChange();
    }

    function handleBackdropClick(e: MouseEvent) {
        if (e.target === e.currentTarget) {
            onClose();
        }
    }
</script>

<!-- svelte-ignore a11y-click-events-have-key-events -->
<!-- svelte-ignore a11y-no-static-element-interactions -->
<div class="settings-backdrop" on:click={handleBackdropClick}>
    <div class="settings-panel">
        <header class="settings-header">
            <h2>Settings</h2>
            <button class="close-btn" on:click={onClose} title="Close">
                <svg viewBox="0 0 24 24" width="20" height="20">
                    <path fill="currentColor" d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/>
                </svg>
            </button>
        </header>

        <div class="settings-content">
            <!-- Connections Section -->
            <section class="settings-section">
                <button class="section-header" on:click={() => toggleSection('connections')}>
                    <span class="section-icon">{sectionsExpanded.connections ? '▼' : '▶'}</span>
                    <span class="section-title">Connections</span>
                </button>

                {#if sectionsExpanded.connections}
                    <div class="section-content">
                        <div class="setting-row">
                            <label for="backend-url">IES Backend URL</label>
                            <input
                                id="backend-url"
                                type="text"
                                bind:value={settings.backendUrl}
                                on:input={() => handleUrlChange('backend')}
                                on:blur={handleSettingChange}
                                placeholder="http://192.168.86.60:8081"
                            />
                            <div class="status-indicator">
                                {#if checkingBackend}
                                    <span class="status checking">Checking...</span>
                                {:else if backendStatus?.ok}
                                    <span class="status connected">● Connected</span>
                                {:else}
                                    <span class="status disconnected">● Disconnected</span>
                                {/if}
                            </div>
                        </div>

                        <div class="setting-row">
                            <label for="ollama-url">Ollama URL</label>
                            <input
                                id="ollama-url"
                                type="text"
                                bind:value={settings.ollamaUrl}
                                on:input={() => handleUrlChange('ollama')}
                                on:blur={handleSettingChange}
                                placeholder="http://localhost:11434"
                            />
                            <div class="status-indicator">
                                {#if checkingOllama}
                                    <span class="status checking">Checking...</span>
                                {:else if ollamaStatus?.ok}
                                    <span class="status connected">● Connected ({ollamaStatus.modelCount} models)</span>
                                {:else}
                                    <span class="status disconnected">● Not available</span>
                                {/if}
                            </div>
                        </div>
                    </div>
                {/if}
            </section>

            <!-- AI Providers Section -->
            <section class="settings-section">
                <button class="section-header" on:click={() => toggleSection('aiProviders')}>
                    <span class="section-icon">{sectionsExpanded.aiProviders ? '▼' : '▶'}</span>
                    <span class="section-title">AI Providers</span>
                </button>

                {#if sectionsExpanded.aiProviders}
                    <div class="section-content">
                        <div class="setting-row">
                            <label for="chat-provider">Chat / Generation</label>
                            <select
                                id="chat-provider"
                                bind:value={settings.chatProvider}
                                on:change={handleChatProviderChange}
                            >
                                <option value="ollama" disabled={!ollamaStatus?.ok}>
                                    Ollama {ollamaStatus?.ok ? '' : '(not connected)'}
                                </option>
                                <option value="openai">OpenAI</option>
                                <option value="anthropic">Anthropic</option>
                            </select>
                        </div>

                        <div class="setting-row">
                            <label for="chat-model">Chat Model</label>
                            <select
                                id="chat-model"
                                bind:value={settings.chatModel}
                                on:change={handleSettingChange}
                            >
                                {#each getChatModelsForProvider(settings.chatProvider) as model}
                                    <option value={model.id}>{model.name}</option>
                                {/each}
                                {#if getChatModelsForProvider(settings.chatProvider).length === 0}
                                    <option value="" disabled>No models available</option>
                                {/if}
                            </select>
                        </div>

                        <div class="setting-row">
                            <label for="embedding-provider">Embeddings</label>
                            <select
                                id="embedding-provider"
                                bind:value={settings.embeddingProvider}
                                on:change={handleEmbeddingProviderChange}
                            >
                                <option value="ollama" disabled={!ollamaStatus?.ok || ollamaEmbeddingModels.length === 0}>
                                    Ollama {ollamaStatus?.ok && ollamaEmbeddingModels.length > 0 ? '' : '(no embedding models)'}
                                </option>
                                <option value="openai">OpenAI</option>
                            </select>
                        </div>

                        <div class="setting-row">
                            <label for="embedding-model">Embedding Model</label>
                            <select
                                id="embedding-model"
                                bind:value={settings.embeddingModel}
                                on:change={handleSettingChange}
                            >
                                {#each getEmbeddingModelsForProvider(settings.embeddingProvider) as model}
                                    <option value={model.id}>{model.name}</option>
                                {/each}
                                {#if getEmbeddingModelsForProvider(settings.embeddingProvider).length === 0}
                                    <option value="" disabled>No models available</option>
                                {/if}
                            </select>
                        </div>
                    </div>
                {/if}
            </section>

            <!-- API Keys Section -->
            <section class="settings-section">
                <button class="section-header" on:click={() => toggleSection('apiKeys')}>
                    <span class="section-icon">{sectionsExpanded.apiKeys ? '▼' : '▶'}</span>
                    <span class="section-title">Cloud API Keys</span>
                </button>

                {#if sectionsExpanded.apiKeys}
                    <div class="section-content">
                        <div class="setting-row">
                            <label for="openai-key">OpenAI API Key</label>
                            <input
                                id="openai-key"
                                type="password"
                                bind:value={settings.openaiApiKey}
                                on:blur={handleSettingChange}
                                placeholder="sk-..."
                            />
                        </div>

                        <div class="setting-row">
                            <label for="anthropic-key">Anthropic API Key</label>
                            <input
                                id="anthropic-key"
                                type="password"
                                bind:value={settings.anthropicApiKey}
                                on:blur={handleSettingChange}
                                placeholder="sk-ant-..."
                            />
                        </div>

                        <p class="hint">API keys are stored locally and never sent to the backend.</p>
                    </div>
                {/if}
            </section>

            <!-- Notebook Preferences Section -->
            <section class="settings-section">
                <button class="section-header" on:click={() => toggleSection('notebooks')}>
                    <span class="section-icon">{sectionsExpanded.notebooks ? '▼' : '▶'}</span>
                    <span class="section-title">Notebook Preferences</span>
                </button>

                {#if sectionsExpanded.notebooks}
                    <div class="section-content">
                        <div class="setting-row">
                            <label for="notebooks">Preferred Notebooks</label>
                            <input
                                id="notebooks"
                                type="text"
                                value={settings.preferredNotebooks.join(', ')}
                                on:blur={(e) => {
                                    settings.preferredNotebooks = e.currentTarget.value
                                        .split(',')
                                        .map(s => s.trim())
                                        .filter(s => s.length > 0);
                                    handleSettingChange();
                                }}
                                placeholder="Personal, Knowledge, Notes"
                            />
                            <p class="hint">Comma-separated list of notebook names (in priority order)</p>
                        </div>
                    </div>
                {/if}
            </section>

            <!-- User & Display Section -->
            <section class="settings-section">
                <button class="section-header" on:click={() => toggleSection('display')}>
                    <span class="section-icon">{sectionsExpanded.display ? '▼' : '▶'}</span>
                    <span class="section-title">User & Display</span>
                </button>

                {#if sectionsExpanded.display}
                    <div class="section-content">
                        <div class="setting-row">
                            <label for="user-id">User ID</label>
                            <input
                                id="user-id"
                                type="text"
                                bind:value={settings.userId}
                                on:blur={handleSettingChange}
                                placeholder="chris"
                            />
                        </div>

                        <div class="setting-row checkbox-row">
                            <label>
                                <input
                                    type="checkbox"
                                    bind:checked={settings.showQuestionBadges}
                                    on:change={handleSettingChange}
                                />
                                Show question class badges
                            </label>
                        </div>

                        <div class="setting-row checkbox-row">
                            <label>
                                <input
                                    type="checkbox"
                                    bind:checked={settings.autoSaveSessions}
                                    on:change={handleSettingChange}
                                />
                                Auto-save session documents
                            </label>
                        </div>
                    </div>
                {/if}
            </section>
        </div>
    </div>
</div>

<style>
    .settings-backdrop {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(0, 0, 0, 0.5);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 999;
    }

    .settings-panel {
        background: var(--bg-elevated, #fff);
        border-radius: var(--radius-lg, 16px);
        box-shadow: var(--shadow-lg, 0 8px 32px rgba(0, 0, 0, 0.2));
        width: 90%;
        max-width: 480px;
        max-height: 85vh;
        display: flex;
        flex-direction: column;
        overflow: hidden;
    }

    .settings-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 16px 20px;
        border-bottom: 1px solid var(--border-subtle, #e5e5e5);
    }

    .settings-header h2 {
        margin: 0;
        font-size: 18px;
        font-weight: 600;
        color: var(--text-primary, #1a1a1a);
    }

    .close-btn {
        background: none;
        border: none;
        cursor: pointer;
        padding: 4px;
        border-radius: 4px;
        color: var(--text-secondary, #666);
        display: flex;
        align-items: center;
        justify-content: center;
    }

    .close-btn:hover {
        background: var(--bg-overlay, #f5f5f5);
        color: var(--text-primary, #1a1a1a);
    }

    .settings-content {
        flex: 1;
        overflow-y: auto;
        padding: 8px 0;
    }

    .settings-section {
        border-bottom: 1px solid var(--border-subtle, #e5e5e5);
    }

    .settings-section:last-child {
        border-bottom: none;
    }

    .section-header {
        width: 100%;
        display: flex;
        align-items: center;
        gap: 8px;
        padding: 12px 20px;
        background: none;
        border: none;
        cursor: pointer;
        text-align: left;
        color: var(--text-primary, #1a1a1a);
        font-size: 14px;
        font-weight: 600;
    }

    .section-header:hover {
        background: var(--bg-overlay, #f5f5f5);
    }

    .section-icon {
        font-size: 10px;
        color: var(--text-muted, #999);
        width: 12px;
    }

    .section-content {
        padding: 0 20px 16px 40px;
    }

    .setting-row {
        margin-bottom: 12px;
    }

    .setting-row:last-child {
        margin-bottom: 0;
    }

    .setting-row label {
        display: block;
        font-size: 13px;
        color: var(--text-secondary, #666);
        margin-bottom: 4px;
    }

    .setting-row input[type="text"],
    .setting-row input[type="password"],
    .setting-row select {
        width: 100%;
        padding: 8px 12px;
        border: 1px solid var(--border-light, #ddd);
        border-radius: var(--radius-sm, 6px);
        font-size: 14px;
        background: var(--bg-base, #fff);
        color: var(--text-primary, #1a1a1a);
    }

    .setting-row input:focus,
    .setting-row select:focus {
        outline: none;
        border-color: var(--accent, #c9872e);
        box-shadow: 0 0 0 2px rgba(201, 135, 46, 0.2);
    }

    .checkbox-row label {
        display: flex;
        align-items: center;
        gap: 8px;
        cursor: pointer;
        font-size: 14px;
        color: var(--text-primary, #1a1a1a);
    }

    .checkbox-row input[type="checkbox"] {
        width: 16px;
        height: 16px;
        cursor: pointer;
    }

    .status-indicator {
        margin-top: 4px;
    }

    .status {
        font-size: 12px;
    }

    .status.connected {
        color: var(--success, #059669);
    }

    .status.disconnected {
        color: var(--error, #dc2626);
    }

    .status.checking {
        color: var(--text-muted, #999);
    }

    .hint {
        font-size: 12px;
        color: var(--text-muted, #999);
        margin-top: 8px;
        margin-bottom: 0;
    }
</style>
