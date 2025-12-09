<script lang="ts">
    import { onMount, onDestroy, tick } from 'svelte';
    import { getFrontend } from 'siyuan';
    import SessionControls from './components/SessionControls.svelte';
    import { t } from './utils/i18n';
    import {
        iesSession,
        isSessionActive,
        canSendMessage
    } from './stores/ies-session';
    import {
        startSession,
        chat,
        endSession,
        checkBackendHealth,
        setBackendUrl,
        type Message
    } from './ies-chat';

    export let plugin: any;

    // User ID (would come from settings in real implementation)
    const USER_ID = 'chris';

    // Backend URL - use same hostname as SiYuan is accessed from
    const BACKEND_URL = typeof window !== 'undefined' && window.location.hostname !== 'localhost'
        ? `http://${window.location.hostname}:8081`
        : 'http://192.168.86.60:8081';

    // UI State
    let inputText = '';
    let isStreaming = false;
    let abortController: AbortController | null = null;
    let messagesContainer: HTMLDivElement;
    let inputElement: HTMLTextAreaElement;
    let isMobile = false;

    // Detect mobile
    onMount(() => {
        setBackendUrl(BACKEND_URL);
        const frontend = getFrontend();
        isMobile = frontend === 'mobile' || frontend === 'browser-mobile';
    });

    // Auto-scroll to bottom when messages change
    $: if ($iesSession.messages.length > 0 && messagesContainer) {
        tick().then(() => {
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
        });
    }

    // Handle session start - skip starting state, go direct
    function handleStartSession() {
        const url = `http://${window.location.hostname}:8081`;

        // Go directly to active with hardcoded data first
        iesSession.startSession(
            'test-123',
            { summary: 'Test', capacity: 7, recentContext: null },
            'Test greeting - if you see this, UI works!'
        );
    }

    // Handle session end
    async function handleEndSession() {
        if (!$iesSession.id) return;

        iesSession.setEnding();

        try {
            const result = await endSession(
                $iesSession.id,
                USER_ID,
                $iesSession.messages
            );

            iesSession.endSession({
                docId: result.doc_id,
                entitiesExtracted: result.entities_extracted,
                summary: result.summary
            });
        } catch (error) {
            console.error('Failed to end session:', error);
            iesSession.setError((error as Error).message);
        }
    }

    // Handle sending a message
    async function handleSend() {
        if (!inputText.trim() || !$canSendMessage || isStreaming) return;

        const message = inputText.trim();
        inputText = '';

        // Add user message
        iesSession.addUserMessage(message);

        // Start streaming assistant response
        isStreaming = true;
        iesSession.addAssistantMessage('');

        abortController = new AbortController();

        try {
            // Get messages for context (excluding the empty assistant message we just added)
            const contextMessages = $iesSession.messages.slice(0, -1);

            await chat({
                sessionId: $iesSession.id!,
                message,
                messages: contextMessages,
                onChunk: (chunk) => {
                    iesSession.appendToLastMessage(chunk);
                },
                onComplete: (fullText) => {
                    isStreaming = false;
                },
                onError: (error) => {
                    console.error('Chat error:', error);
                    isStreaming = false;
                },
                signal: abortController.signal
            });
        } catch (error) {
            if ((error as Error).name !== 'AbortError') {
                console.error('Chat failed:', error);
            }
        } finally {
            isStreaming = false;
            abortController = null;
        }
    }

    // Handle stopping the stream
    function handleStop() {
        if (abortController) {
            abortController.abort();
            abortController = null;
            isStreaming = false;
        }
    }

    // Handle keyboard shortcuts
    function handleKeydown(event: KeyboardEvent) {
        if (event.key === 'Enter' && !event.shiftKey) {
            event.preventDefault();
            handleSend();
        }
    }

    // Auto-resize textarea
    function autoResize(event: Event) {
        const target = event.target as HTMLTextAreaElement;
        target.style.height = 'auto';
        target.style.height = Math.min(target.scrollHeight, 150) + 'px';
    }

    onDestroy(() => {
        if (abortController) {
            abortController.abort();
        }
    });
</script>

<div class="ies-sidebar" class:ies-sidebar--mobile={isMobile}>
    <!-- Session Controls -->
    <SessionControls
        on:start={handleStartSession}
        on:end={handleEndSession}
    />

    <!-- Messages Area -->
    <div class="ies-sidebar__messages" bind:this={messagesContainer}>
        {#if $iesSession.messages.length === 0 && $iesSession.status === 'idle'}
            <div class="ies-sidebar__welcome">
                <div class="ies-sidebar__welcome-icon">
                    <svg viewBox="0 0 24 24" fill="currentColor">
                        <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
                    </svg>
                </div>
                <h3>IES Develop Mode</h3>
                <p>Start a session to begin Socratic exploration. The AI will guide you through questions adapted to your cognitive profile.</p>
            </div>
        {:else}
            {#each $iesSession.messages as message, index}
                <div
                    class="ies-sidebar__message"
                    class:ies-sidebar__message--user={message.role === 'user'}
                    class:ies-sidebar__message--assistant={message.role === 'assistant'}
                >
                    <div class="ies-sidebar__message-avatar">
                        {#if message.role === 'user'}
                            <svg viewBox="0 0 24 24" fill="currentColor">
                                <path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/>
                            </svg>
                        {:else}
                            <svg viewBox="0 0 24 24" fill="currentColor">
                                <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
                            </svg>
                        {/if}
                    </div>
                    <div class="ies-sidebar__message-content">
                        {message.content}
                        {#if message.role === 'assistant' && isStreaming && index === $iesSession.messages.length - 1}
                            <span class="ies-sidebar__cursor">▊</span>
                        {/if}
                    </div>
                </div>
            {/each}
        {/if}
    </div>

    <!-- Input Area -->
    <div class="ies-sidebar__input-area">
        <div class="ies-sidebar__input-wrapper">
            <textarea
                bind:this={inputElement}
                bind:value={inputText}
                on:keydown={handleKeydown}
                on:input={autoResize}
                placeholder={$canSendMessage ? "Type your response..." : "Start a session first"}
                disabled={!$canSendMessage}
                rows="1"
                class="ies-sidebar__input"
            ></textarea>

            {#if isStreaming}
                <button
                    class="ies-sidebar__button ies-sidebar__button--stop"
                    on:click={handleStop}
                    title="Stop"
                >
                    <svg viewBox="0 0 24 24" fill="currentColor">
                        <path d="M6 6h12v12H6z"/>
                    </svg>
                </button>
            {:else}
                <button
                    class="ies-sidebar__button ies-sidebar__button--send"
                    on:click={handleSend}
                    disabled={!$canSendMessage || !inputText.trim()}
                    title="Send"
                >
                    <svg viewBox="0 0 24 24" fill="currentColor">
                        <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/>
                    </svg>
                </button>
            {/if}
        </div>
    </div>
</div>

<style lang="scss">
    .ies-sidebar {
        display: flex;
        flex-direction: column;
        height: 100%;
        background: var(--b3-theme-background);
    }

    .ies-sidebar__messages {
        flex: 1;
        overflow-y: auto;
        padding: 12px;
        display: flex;
        flex-direction: column;
        gap: 12px;
    }

    .ies-sidebar__welcome {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        height: 100%;
        text-align: center;
        padding: 24px;
        color: var(--b3-theme-on-surface-light);
    }

    .ies-sidebar__welcome-icon {
        width: 48px;
        height: 48px;
        margin-bottom: 16px;
        color: var(--b3-theme-primary);

        svg {
            width: 100%;
            height: 100%;
        }
    }

    .ies-sidebar__welcome h3 {
        margin: 0 0 8px;
        font-size: 16px;
        color: var(--b3-theme-on-background);
    }

    .ies-sidebar__welcome p {
        margin: 0;
        font-size: 13px;
        line-height: 1.5;
    }

    .ies-sidebar__message {
        display: flex;
        gap: 10px;
        max-width: 100%;
    }

    .ies-sidebar__message--user {
        flex-direction: row-reverse;

        .ies-sidebar__message-content {
            background: var(--b3-theme-primary);
            color: var(--b3-theme-on-primary);
            border-radius: 16px 4px 16px 16px;
        }

        .ies-sidebar__message-avatar {
            background: var(--b3-theme-primary-lighter);
            color: var(--b3-theme-primary);
        }
    }

    .ies-sidebar__message--assistant {
        .ies-sidebar__message-content {
            background: var(--b3-theme-surface);
            color: var(--b3-theme-on-surface);
            border-radius: 4px 16px 16px 16px;
        }

        .ies-sidebar__message-avatar {
            background: var(--b3-theme-success-lighter);
            color: var(--b3-theme-success);
        }
    }

    .ies-sidebar__message-avatar {
        flex-shrink: 0;
        width: 32px;
        height: 32px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;

        svg {
            width: 18px;
            height: 18px;
        }
    }

    .ies-sidebar__message-content {
        padding: 10px 14px;
        font-size: 14px;
        line-height: 1.5;
        white-space: pre-wrap;
        word-break: break-word;
        max-width: calc(100% - 50px);
    }

    .ies-sidebar__cursor {
        animation: blink 1s step-end infinite;
    }

    @keyframes blink {
        50% { opacity: 0; }
    }

    .ies-sidebar__input-area {
        padding: 12px;
        border-top: 1px solid var(--b3-border-color);
        background: var(--b3-theme-surface);
    }

    .ies-sidebar__input-wrapper {
        display: flex;
        align-items: flex-end;
        gap: 8px;
        background: var(--b3-theme-background);
        border: 1px solid var(--b3-border-color);
        border-radius: 12px;
        padding: 8px 12px;
        transition: border-color 0.2s;

        &:focus-within {
            border-color: var(--b3-theme-primary);
        }
    }

    .ies-sidebar__input {
        flex: 1;
        border: none;
        background: transparent;
        font-size: 14px;
        line-height: 1.5;
        resize: none;
        outline: none;
        min-height: 24px;
        max-height: 150px;
        color: var(--b3-theme-on-background);

        &::placeholder {
            color: var(--b3-theme-on-surface-light);
        }

        &:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }
    }

    .ies-sidebar__button {
        flex-shrink: 0;
        width: 32px;
        height: 32px;
        border: none;
        border-radius: 8px;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        transition: all 0.2s;

        svg {
            width: 18px;
            height: 18px;
        }
    }

    .ies-sidebar__button--send {
        background: var(--b3-theme-primary);
        color: var(--b3-theme-on-primary);

        &:hover:not(:disabled) {
            opacity: 0.9;
        }

        &:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }
    }

    .ies-sidebar__button--stop {
        background: var(--b3-theme-error);
        color: white;

        &:hover {
            opacity: 0.9;
        }
    }

    /* Mobile styles */
    .ies-sidebar--mobile {
        .ies-sidebar__messages {
            padding: 8px;
        }

        .ies-sidebar__message-content {
            font-size: 15px;
            padding: 12px 16px;
        }

        .ies-sidebar__input {
            font-size: 16px; /* Prevent zoom on iOS */
        }

        .ies-sidebar__button {
            width: 44px;
            height: 44px;

            svg {
                width: 22px;
                height: 22px;
            }
        }
    }

    /* Touch-friendly mobile styles */
    @media (pointer: coarse) {
        .ies-sidebar__button {
            min-width: 44px;
            min-height: 44px;
        }
    }

    /* Small screen adjustments */
    @media (max-width: 400px) {
        .ies-sidebar__message-avatar {
            width: 28px;
            height: 28px;

            svg {
                width: 16px;
                height: 16px;
            }
        }

        .ies-sidebar__message-content {
            max-width: calc(100% - 40px);
        }
    }
</style>
