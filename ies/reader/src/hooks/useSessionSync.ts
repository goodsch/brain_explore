/**
 * Session sync hook for IES Reader.
 *
 * Syncs active session state (context, question, journey trail) with backend
 * to enable cross-app continuity.
 *
 * Features:
 * - Polls backend every 5s when active, 30s when backgrounded
 * - Debounces writes by 3 seconds
 * - Syncs context_id and question_id from flowStore
 * - Syncs journey trail from backend (read-only, SiYuan writes)
 * - Updates when document visibility changes
 */

import { useEffect, useRef, useCallback } from 'react';
import { useFlowStore } from '../store/flowStore';
import { sessionStateApi, type SessionStateUpdate, type JourneyTrailItem } from '../services/sessionStateApi';

interface UseSessionSyncOptions {
  userId?: string;
  enabled?: boolean;
  activePollInterval?: number;  // ms, default 5000
  backgroundPollInterval?: number;  // ms, default 30000
  writeDebounce?: number;  // ms, default 3000
}

export function useSessionSync(options: UseSessionSyncOptions = {}) {
  const {
    userId = 'default_user',
    enabled = true,
    activePollInterval = 5000,
    backgroundPollInterval = 30000,
    writeDebounce = 3000,
  } = options;

  const currentContextId = useFlowStore((state) => state.currentContextId);
  const currentQuestionId = useFlowStore((state) => state.currentQuestionId);

  const writeTimerRef = useRef<NodeJS.Timeout | null>(null);
  const pollTimerRef = useRef<NodeJS.Timeout | null>(null);
  const isBackgroundRef = useRef(false);
  const lastSyncedStateRef = useRef<{
    contextId: string | null;
    questionId: string | null;
  }>({
    contextId: null,
    questionId: null,
  });

  /**
   * Write state changes to backend with debouncing.
   */
  const writeState = useCallback(async () => {
    if (!enabled) return;

    // Check if state has changed since last sync
    const { contextId: lastContextId, questionId: lastQuestionId } = lastSyncedStateRef.current;
    if (lastContextId === currentContextId && lastQuestionId === currentQuestionId) {
      return; // No changes to sync
    }

    try {
      useFlowStore.getState().setSyncStatus('syncing');

      const update: SessionStateUpdate = {
        active_context_id: currentContextId || null,
        active_question_id: currentQuestionId || null,
      };

      await sessionStateApi.updateState(userId, update);

      // Update last synced state
      lastSyncedStateRef.current = {
        contextId: currentContextId,
        questionId: currentQuestionId,
      };

      useFlowStore.getState().setSyncStatus('synced');
      console.log('[useSessionSync] State synced:', update);
    } catch (error) {
      console.error('[useSessionSync] Failed to write state:', error);
      useFlowStore.getState().setSyncStatus('error', String(error));
    }
  }, [enabled, userId, currentContextId, currentQuestionId]);

  /**
   * Debounced write: clear existing timer and schedule new write.
   */
  const scheduleWrite = useCallback(() => {
    if (writeTimerRef.current) {
      clearTimeout(writeTimerRef.current);
    }

    writeTimerRef.current = setTimeout(() => {
      writeState();
    }, writeDebounce);
  }, [writeState, writeDebounce]);

  /**
   * Poll backend for state updates from other frontends.
   */
  const pollState = useCallback(async () => {
    if (!enabled) return;

    try {
      const state = await sessionStateApi.getState(userId);

      // Update local state if backend has different values
      const {
        currentContextId: localContext,
        currentQuestionId: localQuestion,
        journeyTrail: localTrail,
        syncStatus,
      } = useFlowStore.getState();

      if (state.active_context_id !== localContext) {
        console.log('[useSessionSync] Context updated from backend:', state.active_context_id);
        useFlowStore.getState().setCurrentContextId(state.active_context_id || null);
        lastSyncedStateRef.current.contextId = state.active_context_id || null;
      }

      if (state.active_question_id !== localQuestion) {
        console.log('[useSessionSync] Question updated from backend:', state.active_question_id);
        useFlowStore.getState().setCurrentQuestionId(state.active_question_id || null);
        lastSyncedStateRef.current.questionId = state.active_question_id || null;
      }

      // Sync journey trail from backend (trail is managed by backend, Reader reads only)
      const remoteTrail = state.journey_trail || [];
      if (remoteTrail.length !== localTrail.length ||
          (remoteTrail.length > 0 && remoteTrail[0]?.entity_id !== localTrail[0]?.entity_id)) {
        console.log('[useSessionSync] Journey trail updated from backend:', remoteTrail.length, 'items');
        useFlowStore.getState().setJourneyTrail(remoteTrail);
      }

      // Sync last app source
      if (state.last_app_source) {
        useFlowStore.getState().setLastAppSource(state.last_app_source);
      }

      // Update sync status to synced if we successfully polled
      if (syncStatus === 'idle' || syncStatus === 'error') {
        useFlowStore.getState().setSyncStatus('synced');
      }
    } catch (error) {
      console.error('[useSessionSync] Failed to poll state:', error);
      useFlowStore.getState().setSyncStatus('error', String(error));
    }
  }, [enabled, userId]);

  /**
   * Schedule next poll based on document visibility.
   */
  const scheduleNextPoll = useCallback(() => {
    if (pollTimerRef.current) {
      clearTimeout(pollTimerRef.current);
    }

    const interval = isBackgroundRef.current ? backgroundPollInterval : activePollInterval;

    pollTimerRef.current = setTimeout(() => {
      pollState();
      scheduleNextPoll(); // Schedule next poll
    }, interval);
  }, [pollState, activePollInterval, backgroundPollInterval]);

  /**
   * Send heartbeat without full sync.
   */
  const sendHeartbeat = useCallback(async () => {
    if (!enabled) return;

    try {
      await sessionStateApi.heartbeat(userId);
      console.log('[useSessionSync] Heartbeat sent');
    } catch (error) {
      console.error('[useSessionSync] Failed to send heartbeat:', error);
    }
  }, [enabled, userId]);

  /**
   * Add entity visit to journey trail.
   * Call this when user navigates to/focuses on an entity in the Reader.
   */
  const addEntityVisit = useCallback(async (
    entityId: string,
    entityName: string,
    options?: {
      entityType?: string;
      sourceContext?: string;
      dwellSeconds?: number;
    }
  ) => {
    if (!enabled) return;

    const trailItem: JourneyTrailItem = {
      entity_id: entityId,
      entity_name: entityName,
      entity_type: options?.entityType || null,
      source_app: 'reader',
      timestamp: new Date().toISOString(),
      dwell_seconds: options?.dwellSeconds || null,
      source_context: options?.sourceContext || null,
    };

    try {
      const updatedState = await sessionStateApi.addTrailItem(userId, trailItem);

      // Update local state with response
      useFlowStore.getState().setJourneyTrail(updatedState.journey_trail || []);
      useFlowStore.getState().setLastAppSource(updatedState.last_app_source || null);

      console.log('[useSessionSync] Entity visit added:', entityName);
    } catch (error) {
      console.error('[useSessionSync] Failed to add entity visit:', error);
    }
  }, [enabled, userId]);

  /**
   * Handle visibility changes (tab backgrounding).
   */
  useEffect(() => {
    if (!enabled) return;

    const handleVisibilityChange = () => {
      const isHidden = document.hidden;
      isBackgroundRef.current = isHidden;

      if (isHidden) {
        console.log('[useSessionSync] App backgrounded, switching to 30s poll interval');
        // Write any pending changes before backgrounding
        if (writeTimerRef.current) {
          clearTimeout(writeTimerRef.current);
          writeState();
        }
      } else {
        console.log('[useSessionSync] App foregrounded, switching to 5s poll interval');
        // Immediate poll when coming back to foreground
        pollState();
      }

      // Restart polling with new interval
      scheduleNextPoll();
    };

    document.addEventListener('visibilitychange', handleVisibilityChange);

    return () => {
      document.removeEventListener('visibilitychange', handleVisibilityChange);
    };
  }, [enabled, writeState, pollState, scheduleNextPoll]);

  /**
   * Debounce writes when context or question changes.
   */
  useEffect(() => {
    if (!enabled) return;

    scheduleWrite();

    // Cleanup on unmount
    return () => {
      if (writeTimerRef.current) {
        clearTimeout(writeTimerRef.current);
      }
    };
  }, [enabled, currentContextId, currentQuestionId, scheduleWrite]);

  /**
   * Start polling on mount.
   */
  useEffect(() => {
    if (!enabled) return;

    // Initial poll
    pollState();

    // Start poll loop
    scheduleNextPoll();

    // Cleanup on unmount
    return () => {
      if (pollTimerRef.current) {
        clearTimeout(pollTimerRef.current);
      }
    };
  }, [enabled, pollState, scheduleNextPoll]);

  /**
   * Send heartbeat every 60 seconds (independent of polling).
   */
  useEffect(() => {
    if (!enabled) return;

    const heartbeatInterval = setInterval(sendHeartbeat, 60000);

    return () => {
      clearInterval(heartbeatInterval);
    };
  }, [enabled, sendHeartbeat]);

  return {
    writeState,
    sendHeartbeat,
    addEntityVisit,
  };
}
