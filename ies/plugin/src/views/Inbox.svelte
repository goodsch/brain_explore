<script lang="ts">
    /**
     * Inbox - External-First Capture with Collaborative Processing
     *
     * Staging area for thoughts captured externally (iOS shortcuts, browser, voice).
     * Supports inline dialogue with AI for collaborative understanding.
     *
     * Design: docs/plans/2025-12-06-inbox-redesign.md
     */
    import { createEventDispatcher, onMount } from 'svelte';
    import { showMessage, fetchSyncPost } from 'siyuan';

    export let backendUrl: string;

    const dispatch = createEventDispatcher();

    // Types
    interface DialogueSuggestion {
        label: string;
        action: string;
        targetId: string | null;
        targetName: string | null;
        confidence: number;
    }

    interface DialogueMessage {
        role: 'assistant' | 'user';
        content: string;
        timestamp: string;
        suggestions?: DialogueSuggestion[];
    }

    interface InboxItem {
        id: string;
        rawText: string;
        source: string;
        capturedAt: string;
        status: 'queued' | 'in_thinking' | 'integrated';
        contextSnippet: string | null;
        autoExtracted: {
            entities: string[];
            topics: string[];
        } | null;
        dialogue: DialogueMessage[];
    }

    // State
    let inboxItems: InboxItem[] = [];
    let selectedItem: InboxItem | null = null;
    let isLoading = false;
    let isSendingMessage = false;
    let messageInput = '';
    let error: string | null = null;

    // Direct capture state (for manual entry)
    let showManualEntry = false;
    let manualText = '';
    let isCreating = false;

    onMount(async () => {
        await loadInboxItems();
    });

    // API helpers
    async function apiGet(endpoint: string): Promise<any> {
        const url = `${backendUrl}${endpoint}`;
        const response = await fetchSyncPost('/api/network/forwardProxy', {
            url: url,
            method: 'GET',
            timeout: 30000,
            contentType: 'application/json',
            headers: [],
            payload: {}
        });

        if (response.code !== 0) {
            throw new Error(`Proxy error: ${response.msg}`);
        }

        const proxyData = response.data;
        if (!proxyData || proxyData.status !== 200) {
            const errorBody = typeof proxyData?.body === 'string'
                ? JSON.parse(proxyData.body)
                : proxyData?.body;
            throw new Error(errorBody?.detail || `Backend error: ${proxyData?.status || 'unknown'}`);
        }

        return typeof proxyData.body === 'string' ? JSON.parse(proxyData.body) : proxyData.body;
    }

    async function apiPost(endpoint: string, body: any): Promise<any> {
        const url = `${backendUrl}${endpoint}`;
        const response = await fetchSyncPost('/api/network/forwardProxy', {
            url: url,
            method: 'POST',
            timeout: 60000,
            contentType: 'application/json',
            headers: [],
            payload: body
        });

        if (response.code !== 0) {
            throw new Error(`Proxy error: ${response.msg}`);
        }

        const proxyData = response.data;
        if (!proxyData || proxyData.status !== 200) {
            const errorBody = typeof proxyData?.body === 'string'
                ? JSON.parse(proxyData.body)
                : proxyData?.body;
            throw new Error(errorBody?.detail || `Backend error: ${proxyData?.status || 'unknown'}`);
        }

        return typeof proxyData.body === 'string' ? JSON.parse(proxyData.body) : proxyData.body;
    }

    async function apiPatch(endpoint: string, body: any): Promise<any> {
        const url = `${backendUrl}${endpoint}`;
        const response = await fetchSyncPost('/api/network/forwardProxy', {
            url: url,
            method: 'PATCH',
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
            const errorBody = typeof proxyData?.body === 'string'
                ? JSON.parse(proxyData.body)
                : proxyData?.body;
            throw new Error(errorBody?.detail || `Backend error: ${proxyData?.status || 'unknown'}`);
        }

        return typeof proxyData.body === 'string' ? JSON.parse(proxyData.body) : proxyData.body;
    }

    async function loadInboxItems() {
        isLoading = true;
        error = null;

        try {
            const result = await apiGet('/inbox?status=queued');
            inboxItems = result.items || [];
        } catch (err) {
            error = err.message || String(err);
            console.error('[Inbox] Load error:', err);
        } finally {
            isLoading = false;
        }
    }

    async function selectItem(item: InboxItem) {
        selectedItem = item;

        // If no dialogue exists, start with initial AI analysis
        if (!item.dialogue || item.dialogue.length === 0) {
            await sendMessage("What is this about?");
        }
    }

    async function sendMessage(content?: string) {
        if (isSendingMessage || !selectedItem) return;

        const messageText = content || messageInput.trim();
        if (!messageText) return;

        isSendingMessage = true;
        error = null;

        try {
            const result = await apiPost(`/inbox/${selectedItem.id}/message`, {
                content: messageText
            });

            // Update the selected item with new dialogue
            selectedItem = result.inboxItem;

            // Update in the list as well
            const idx = inboxItems.findIndex(i => i.id === selectedItem.id);
            if (idx !== -1) {
                inboxItems[idx] = selectedItem;
                inboxItems = [...inboxItems];
            }

            messageInput = '';
        } catch (err) {
            error = err.message || String(err);
            console.error('[Inbox] Message error:', err);
        } finally {
            isSendingMessage = false;
        }
    }

    async function handleSuggestionClick(suggestion: DialogueSuggestion) {
        if (!selectedItem) return;

        try {
            // Call the resolve endpoint
            const result = await apiPost(`/inbox/${selectedItem.id}/resolve`, {
                action: suggestion.action,
                targetId: suggestion.targetId,
                targetName: suggestion.targetName
            });

            if (result.success) {
                // Handle action-specific UI updates
                if (suggestion.action === 'create_note') {
                    // For create_note, we could open SiYuan's note creation
                    // For now, show success and let user create manually
                    showMessage(`Ready to create: ${result.targetName}`, 3000);
                } else if (suggestion.action === 'explore_in_flow') {
                    // Could dispatch event to open FlowMode with session
                    showMessage('Opening in FlowMode...', 2000);
                    dispatch('openFlow', { sessionId: result.targetId });
                } else {
                    showMessage(result.message, 3000);
                }

                // Remove from list and clear selection
                inboxItems = inboxItems.filter(i => i.id !== selectedItem.id);
                selectedItem = null;
            } else {
                showMessage(`Failed: ${result.message}`, 4000);
            }
        } catch (err) {
            error = err.message || String(err);
            console.error('[Inbox] Resolve error:', err);
        }
    }

    async function createManualCapture() {
        if (!manualText.trim() || isCreating) return;

        isCreating = true;
        error = null;

        try {
            const result = await apiPost('/inbox', {
                rawText: manualText.trim(),
                source: 'siyuan'
            });

            inboxItems = [result, ...inboxItems];
            manualText = '';
            showManualEntry = false;
        } catch (err) {
            error = err.message || String(err);
            console.error('[Inbox] Create error:', err);
        } finally {
            isCreating = false;
        }
    }

    function handleBack() {
        if (selectedItem) {
            selectedItem = null;
        } else {
            dispatch('back');
        }
    }

    function getSourceIcon(source: string): string {
        switch (source) {
            case 'ios_shortcut': return '📱';
            case 'browser': return '🌐';
            case 'voice': return '🎤';
            case 'siyuan': return '📝';
            case 'ies_reader': return '📖';
            case 'email': return '✉️';
            case 'assistant_interruption': return '💡';
            default: return '📥';
        }
    }

    function formatTime(isoString: string): string {
        const date = new Date(isoString);
        const now = new Date();
        const diff = now.getTime() - date.getTime();

        if (diff < 60000) return 'just now';
        if (diff < 3600000) return `${Math.floor(diff / 60000)}m ago`;
        if (diff < 86400000) return `${Math.floor(diff / 3600000)}h ago`;
        return date.toLocaleDateString();
    }

    function getConfidenceColor(confidence: number): string {
        if (confidence >= 0.7) return 'var(--b3-theme-success)';
        if (confidence >= 0.4) return 'var(--b3-theme-warning)';
        return 'var(--b3-theme-on-surface-light)';
    }
</script>

<div class="inbox-mode">
    <div class="inbox-header">
        <button class="back-btn" on:click={handleBack} title={selectedItem ? "Back to queue" : "Back to Dashboard"}>
            <svg viewBox="0 0 24 24" width="16" height="16">
                <path fill="currentColor" d="M20 11H7.83l5.59-5.59L12 4l-8 8 8 8 1.41-1.41L7.83 13H20v-2z"/>
            </svg>
        </button>
        <span class="inbox-title">{selectedItem ? 'Processing' : 'Inbox'}</span>
        {#if !selectedItem}
            <button
                class="add-btn"
                on:click={() => showManualEntry = !showManualEntry}
                title="Add item manually"
            >
                <svg viewBox="0 0 24 24" width="16" height="16">
                    <path fill="currentColor" d="M19 13h-6v6h-2v-6H5v-2h6V5h2v6h6v2z"/>
                </svg>
            </button>
        {/if}
    </div>

    {#if error}
        <div class="inbox-error">
            {error}
        </div>
    {/if}

    {#if !selectedItem}
        <!-- Queue View -->
        {#if showManualEntry}
            <div class="manual-entry">
                <textarea
                    bind:value={manualText}
                    placeholder="Type a thought to capture..."
                    rows="3"
                    disabled={isCreating}
                ></textarea>
                <div class="manual-actions">
                    <button class="b3-button" on:click={() => showManualEntry = false}>
                        Cancel
                    </button>
                    <button
                        class="b3-button b3-button--primary"
                        on:click={createManualCapture}
                        disabled={isCreating || !manualText.trim()}
                    >
                        {isCreating ? 'Adding...' : 'Add'}
                    </button>
                </div>
            </div>
        {/if}

        {#if isLoading}
            <div class="inbox-loading">Loading inbox items...</div>
        {:else if inboxItems.length === 0}
            <div class="inbox-empty">
                <span class="empty-icon">📥</span>
                <p>No items in queue</p>
                <p class="empty-hint">Captures from iOS shortcuts, browser, or voice will appear here</p>
            </div>
        {:else}
            <div class="inbox-queue">
                {#each inboxItems as item}
                    <button class="queue-item" on:click={() => selectItem(item)}>
                        <span class="item-source">{getSourceIcon(item.source)}</span>
                        <div class="item-content">
                            <span class="item-text">{item.rawText.slice(0, 80)}{item.rawText.length > 80 ? '...' : ''}</span>
                            <div class="item-meta">
                                <span class="item-time">{formatTime(item.capturedAt)}</span>
                                {#if item.autoExtracted?.entities?.length}
                                    <span class="item-entities">
                                        {item.autoExtracted.entities.slice(0, 2).join(', ')}
                                    </span>
                                {/if}
                            </div>
                        </div>
                        <svg class="item-arrow" viewBox="0 0 24 24" width="16" height="16">
                            <path fill="currentColor" d="M8.59 16.59L13.17 12 8.59 7.41 10 6l6 6-6 6-1.41-1.41z"/>
                        </svg>
                    </button>
                {/each}
            </div>
        {/if}
    {:else}
        <!-- Dialogue View -->
        <div class="dialogue-view">
            <!-- Original capture -->
            <div class="capture-preview">
                <span class="capture-source">{getSourceIcon(selectedItem.source)}</span>
                <div class="capture-text">{selectedItem.rawText}</div>
                {#if selectedItem.contextSnippet}
                    <div class="capture-context">Context: {selectedItem.contextSnippet}</div>
                {/if}
            </div>

            <!-- Dialogue messages -->
            <div class="dialogue-messages">
                {#each selectedItem.dialogue as message}
                    <div class="message" class:message--user={message.role === 'user'} class:message--assistant={message.role === 'assistant'}>
                        <div class="message-content">{message.content}</div>

                        {#if message.suggestions?.length}
                            <div class="message-suggestions">
                                {#each message.suggestions as suggestion}
                                    <button
                                        class="suggestion-btn"
                                        on:click={() => handleSuggestionClick(suggestion)}
                                        title="{suggestion.action}: {suggestion.targetName || 'new'}"
                                    >
                                        <span class="suggestion-label">{suggestion.label}</span>
                                        <span
                                            class="suggestion-confidence"
                                            style="color: {getConfidenceColor(suggestion.confidence)}"
                                        >
                                            {Math.round(suggestion.confidence * 100)}%
                                        </span>
                                    </button>
                                {/each}
                            </div>
                        {/if}
                    </div>
                {/each}

                {#if isSendingMessage}
                    <div class="message message--loading">
                        <div class="loading-dots">
                            <span></span><span></span><span></span>
                        </div>
                    </div>
                {/if}
            </div>

            <!-- Message input -->
            <div class="dialogue-input">
                <input
                    type="text"
                    bind:value={messageInput}
                    placeholder="Ask about this capture..."
                    disabled={isSendingMessage}
                    on:keydown={(e) => e.key === 'Enter' && sendMessage()}
                />
                <button
                    class="send-btn"
                    on:click={() => sendMessage()}
                    disabled={isSendingMessage || !messageInput.trim()}
                >
                    <svg viewBox="0 0 24 24" width="18" height="18">
                        <path fill="currentColor" d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/>
                    </svg>
                </button>
            </div>
        </div>
    {/if}
</div>

<style>
    .inbox-mode {
        display: flex;
        flex-direction: column;
        height: 100%;
        padding: 12px;
        gap: 12px;
    }

    .inbox-header {
        display: flex;
        align-items: center;
        gap: 8px;
    }

    .back-btn, .add-btn {
        background: none;
        border: none;
        cursor: pointer;
        padding: 4px;
        border-radius: 4px;
        color: var(--b3-theme-on-surface);
        display: flex;
        align-items: center;
    }

    .back-btn:hover, .add-btn:hover {
        background: var(--b3-theme-surface);
    }

    .inbox-title {
        font-weight: 600;
        flex: 1;
    }

    .inbox-error {
        padding: 8px 12px;
        background: var(--b3-theme-error-lighter);
        color: var(--b3-theme-error);
        border-radius: 6px;
        font-size: 13px;
    }

    .manual-entry {
        display: flex;
        flex-direction: column;
        gap: 8px;
        padding: 12px;
        background: var(--b3-theme-surface);
        border-radius: 8px;
    }

    .manual-entry textarea {
        width: 100%;
        resize: none;
        border: 1px solid var(--b3-border-color);
        border-radius: 6px;
        padding: 10px;
        font-size: 14px;
        background: var(--b3-theme-background);
        color: var(--b3-theme-on-background);
    }

    .manual-actions {
        display: flex;
        justify-content: flex-end;
        gap: 8px;
    }

    .inbox-loading, .inbox-empty {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        flex: 1;
        color: var(--b3-theme-on-surface-light);
        text-align: center;
        padding: 24px;
    }

    .empty-icon {
        font-size: 48px;
        margin-bottom: 12px;
    }

    .empty-hint {
        font-size: 12px;
        max-width: 200px;
    }

    .inbox-queue {
        display: flex;
        flex-direction: column;
        gap: 8px;
        overflow-y: auto;
        flex: 1;
    }

    .queue-item {
        display: flex;
        align-items: flex-start;
        gap: 12px;
        padding: 12px;
        background: var(--b3-theme-surface);
        border: 1px solid var(--b3-border-color);
        border-radius: 8px;
        cursor: pointer;
        text-align: left;
        transition: all 0.15s;
    }

    .queue-item:hover {
        border-color: var(--b3-theme-primary);
        background: var(--b3-theme-primary-lightest);
    }

    .item-source {
        font-size: 20px;
        flex-shrink: 0;
    }

    .item-content {
        flex: 1;
        min-width: 0;
    }

    .item-text {
        display: block;
        font-size: 14px;
        line-height: 1.4;
        margin-bottom: 4px;
    }

    .item-meta {
        display: flex;
        gap: 8px;
        font-size: 11px;
        color: var(--b3-theme-on-surface-light);
    }

    .item-entities {
        color: var(--b3-theme-primary);
    }

    .item-arrow {
        flex-shrink: 0;
        color: var(--b3-theme-on-surface-light);
    }

    /* Dialogue View */
    .dialogue-view {
        display: flex;
        flex-direction: column;
        flex: 1;
        gap: 12px;
        overflow: hidden;
    }

    .capture-preview {
        display: flex;
        gap: 10px;
        padding: 12px;
        background: var(--b3-theme-surface);
        border-radius: 8px;
        border-left: 3px solid var(--b3-theme-primary);
    }

    .capture-source {
        font-size: 18px;
        flex-shrink: 0;
    }

    .capture-text {
        flex: 1;
        font-size: 14px;
        line-height: 1.5;
    }

    .capture-context {
        font-size: 12px;
        color: var(--b3-theme-on-surface-light);
        font-style: italic;
        margin-top: 4px;
    }

    .dialogue-messages {
        flex: 1;
        overflow-y: auto;
        display: flex;
        flex-direction: column;
        gap: 12px;
        padding: 8px 0;
    }

    .message {
        max-width: 85%;
        padding: 10px 14px;
        border-radius: 12px;
        font-size: 14px;
        line-height: 1.5;
    }

    .message--user {
        align-self: flex-end;
        background: var(--b3-theme-primary);
        color: var(--b3-theme-on-primary);
        border-bottom-right-radius: 4px;
    }

    .message--assistant {
        align-self: flex-start;
        background: var(--b3-theme-surface);
        border: 1px solid var(--b3-border-color);
        border-bottom-left-radius: 4px;
    }

    .message--loading {
        align-self: flex-start;
        background: var(--b3-theme-surface);
        border: 1px solid var(--b3-border-color);
        padding: 14px 20px;
    }

    .loading-dots {
        display: flex;
        gap: 4px;
    }

    .loading-dots span {
        width: 6px;
        height: 6px;
        background: var(--b3-theme-on-surface-light);
        border-radius: 50%;
        animation: bounce 1.4s infinite ease-in-out;
    }

    .loading-dots span:nth-child(1) { animation-delay: 0s; }
    .loading-dots span:nth-child(2) { animation-delay: 0.2s; }
    .loading-dots span:nth-child(3) { animation-delay: 0.4s; }

    @keyframes bounce {
        0%, 80%, 100% { transform: scale(0.6); opacity: 0.5; }
        40% { transform: scale(1); opacity: 1; }
    }

    .message-content {
        white-space: pre-wrap;
    }

    .message-suggestions {
        display: flex;
        flex-wrap: wrap;
        gap: 6px;
        margin-top: 10px;
        padding-top: 10px;
        border-top: 1px solid var(--b3-border-color);
    }

    .suggestion-btn {
        display: flex;
        align-items: center;
        gap: 6px;
        padding: 6px 12px;
        background: var(--b3-theme-background);
        border: 1px solid var(--b3-border-color);
        border-radius: 16px;
        cursor: pointer;
        font-size: 12px;
        transition: all 0.15s;
    }

    .suggestion-btn:hover {
        border-color: var(--b3-theme-primary);
        background: var(--b3-theme-primary-lightest);
    }

    .suggestion-label {
        color: var(--b3-theme-on-background);
    }

    .suggestion-confidence {
        font-weight: 600;
        font-size: 11px;
    }

    .dialogue-input {
        display: flex;
        gap: 8px;
        padding: 8px;
        background: var(--b3-theme-surface);
        border-radius: 8px;
        border: 1px solid var(--b3-border-color);
    }

    .dialogue-input input {
        flex: 1;
        border: none;
        background: transparent;
        padding: 8px;
        font-size: 14px;
        color: var(--b3-theme-on-surface);
    }

    .dialogue-input input:focus {
        outline: none;
    }

    .send-btn {
        padding: 8px;
        background: var(--b3-theme-primary);
        color: var(--b3-theme-on-primary);
        border: none;
        border-radius: 6px;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        transition: opacity 0.15s;
    }

    .send-btn:hover {
        opacity: 0.9;
    }

    .send-btn:disabled {
        opacity: 0.5;
        cursor: not-allowed;
    }
</style>
