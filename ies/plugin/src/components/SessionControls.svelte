<script lang="ts">
    import { createEventDispatcher, onDestroy } from 'svelte';
    import {
        iesSession,
        isSessionActive,
        isSessionStarting,
        isSessionEnding,
        sessionDuration
    } from '../stores/ies-session';
    import { t } from '../utils/i18n';

    const dispatch = createEventDispatcher();

    // Format duration as MM:SS
    function formatDuration(seconds: number): string {
        const mins = Math.floor(seconds / 60);
        const secs = seconds % 60;
        return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    }

    // Update duration every second when active
    let durationInterval: ReturnType<typeof setInterval> | null = null;
    let displayDuration = 0;

    $: if ($isSessionActive && !durationInterval) {
        durationInterval = setInterval(() => {
            displayDuration = $sessionDuration;
        }, 1000);
    } else if (!$isSessionActive && durationInterval) {
        clearInterval(durationInterval);
        durationInterval = null;
    }

    onDestroy(() => {
        if (durationInterval) {
            clearInterval(durationInterval);
        }
    });

    function handleStart() {
        dispatch('start');
    }

    function handleEnd() {
        dispatch('end');
    }
</script>

<div class="session-controls" class:session-controls--mobile={false}>
    <div class="session-controls__header">
        <span class="session-controls__mode">
            <svg class="session-controls__icon" viewBox="0 0 24 24" fill="currentColor">
                <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
            </svg>
            IES Develop
        </span>
    </div>

    <div class="session-controls__body">
        {#if $iesSession.status === 'idle'}
            <button
                class="session-controls__button session-controls__button--start b3-button b3-button--primary"
                on:click={handleStart}
            >
                <svg class="session-controls__button-icon" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M8 5v14l11-7z"/>
                </svg>
                {t('ies.session.start') || 'Start Session'}
            </button>
        {:else if $isSessionStarting}
            <div class="session-controls__status session-controls__status--starting">
                <div class="session-controls__spinner"></div>
                <span>{t('ies.session.starting') || 'Starting...'}</span>
            </div>
        {:else if $isSessionActive}
            <div class="session-controls__active">
                <div class="session-controls__status session-controls__status--active">
                    <span class="session-controls__indicator"></span>
                    <span class="session-controls__timer">{formatDuration(displayDuration)}</span>
                    {#if $iesSession.profile}
                        <span class="session-controls__capacity">
                            Capacity: {$iesSession.profile.capacity}/10
                        </span>
                    {/if}
                </div>
                <button
                    class="session-controls__button session-controls__button--end b3-button"
                    on:click={handleEnd}
                >
                    <svg class="session-controls__button-icon" viewBox="0 0 24 24" fill="currentColor">
                        <path d="M6 6h12v12H6z"/>
                    </svg>
                    {t('ies.session.end') || 'End Session'}
                </button>
            </div>
        {:else if $isSessionEnding}
            <div class="session-controls__status session-controls__status--ending">
                <div class="session-controls__spinner"></div>
                <span>{t('ies.session.ending') || 'Processing...'}</span>
            </div>
        {:else if $iesSession.status === 'ended'}
            <div class="session-controls__ended">
                {#if $iesSession.extractionResult}
                    <div class="session-controls__result">
                        <span class="session-controls__result-icon">✓</span>
                        <span>{$iesSession.extractionResult.entitiesExtracted} entities extracted</span>
                    </div>
                {/if}
                <button
                    class="session-controls__button session-controls__button--new b3-button b3-button--primary"
                    on:click={handleStart}
                >
                    {t('ies.session.new') || 'New Session'}
                </button>
            </div>
        {:else if $iesSession.status === 'error'}
            <div class="session-controls__error">
                <span class="session-controls__error-icon">!</span>
                <span class="session-controls__error-text">{$iesSession.error}</span>
                <button
                    class="session-controls__button b3-button"
                    on:click={handleStart}
                >
                    {t('ies.session.retry') || 'Retry'}
                </button>
            </div>
        {/if}
    </div>
</div>

<style lang="scss">
    .session-controls {
        padding: 12px;
        border-bottom: 1px solid var(--b3-border-color);
        background: var(--b3-theme-surface);
    }

    .session-controls__header {
        margin-bottom: 8px;
    }

    .session-controls__mode {
        display: flex;
        align-items: center;
        gap: 6px;
        font-size: 14px;
        font-weight: 600;
        color: var(--b3-theme-primary);
    }

    .session-controls__icon {
        width: 18px;
        height: 18px;
    }

    .session-controls__body {
        display: flex;
        flex-direction: column;
        gap: 8px;
    }

    .session-controls__button {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 6px;
        padding: 8px 16px;
        font-size: 13px;
        border-radius: 6px;
        cursor: pointer;
        transition: all 0.2s;
        width: 100%;
    }

    .session-controls__button--start {
        background: var(--b3-theme-primary);
        color: var(--b3-theme-on-primary);

        &:hover {
            opacity: 0.9;
        }
    }

    .session-controls__button--end {
        background: var(--b3-theme-error-lighter);
        color: var(--b3-theme-error);
        border: 1px solid var(--b3-theme-error);

        &:hover {
            background: var(--b3-theme-error);
            color: white;
        }
    }

    .session-controls__button-icon {
        width: 16px;
        height: 16px;
    }

    .session-controls__active {
        display: flex;
        flex-direction: column;
        gap: 8px;
    }

    .session-controls__status {
        display: flex;
        align-items: center;
        gap: 8px;
        font-size: 13px;
        color: var(--b3-theme-on-surface);
    }

    .session-controls__status--active {
        padding: 6px 10px;
        background: var(--b3-theme-success-lighter);
        border-radius: 6px;
    }

    .session-controls__status--starting,
    .session-controls__status--ending {
        padding: 8px;
        justify-content: center;
    }

    .session-controls__indicator {
        width: 8px;
        height: 8px;
        background: var(--b3-theme-success);
        border-radius: 50%;
        animation: pulse 2s infinite;
    }

    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }

    .session-controls__timer {
        font-family: monospace;
        font-weight: 600;
    }

    .session-controls__capacity {
        margin-left: auto;
        font-size: 12px;
        color: var(--b3-theme-on-surface-light);
    }

    .session-controls__spinner {
        width: 16px;
        height: 16px;
        border: 2px solid var(--b3-theme-primary-lighter);
        border-top-color: var(--b3-theme-primary);
        border-radius: 50%;
        animation: spin 1s linear infinite;
    }

    @keyframes spin {
        to { transform: rotate(360deg); }
    }

    .session-controls__ended {
        display: flex;
        flex-direction: column;
        gap: 8px;
    }

    .session-controls__result {
        display: flex;
        align-items: center;
        gap: 6px;
        padding: 8px;
        background: var(--b3-theme-success-lighter);
        border-radius: 6px;
        font-size: 13px;
        color: var(--b3-theme-success);
    }

    .session-controls__result-icon {
        font-weight: bold;
    }

    .session-controls__error {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 8px;
        padding: 8px;
        background: var(--b3-theme-error-lighter);
        border-radius: 6px;
    }

    .session-controls__error-icon {
        width: 24px;
        height: 24px;
        display: flex;
        align-items: center;
        justify-content: center;
        background: var(--b3-theme-error);
        color: white;
        border-radius: 50%;
        font-weight: bold;
    }

    .session-controls__error-text {
        font-size: 12px;
        color: var(--b3-theme-error);
        text-align: center;
    }

    /* Mobile responsive styles */
    @media (max-width: 768px) {
        .session-controls {
            padding: 10px;
        }

        .session-controls__button {
            padding: 12px 16px;
            font-size: 14px;
        }

        .session-controls__status--active {
            flex-wrap: wrap;
        }

        .session-controls__capacity {
            width: 100%;
            margin-left: 0;
            margin-top: 4px;
        }
    }

    /* Touch-friendly mobile styles */
    @media (pointer: coarse) {
        .session-controls__button {
            min-height: 44px;
        }
    }
</style>
