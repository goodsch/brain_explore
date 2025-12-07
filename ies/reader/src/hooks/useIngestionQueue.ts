import { useEffect, useCallback } from 'react';
import { useIngestionQueueStore } from '../store/ingestionQueueStore';

interface UseIngestionQueueOptions {
  /** Polling interval in milliseconds (default: 10000 = 10 seconds) */
  pollIntervalMs?: number;
  /** Whether to start polling automatically (default: true) */
  autoStart?: boolean;
  /** Only poll when there are active items (queued or processing) */
  pollOnlyWhenActive?: boolean;
}

/**
 * Hook for managing ingestion queue with automatic polling.
 *
 * Usage:
 * ```tsx
 * const { items, isLoading, queueBook, cancelBook, retryBook, refresh } = useIngestionQueue();
 * ```
 */
export function useIngestionQueue(options: UseIngestionQueueOptions = {}) {
  const { pollIntervalMs = 10000, autoStart = true, pollOnlyWhenActive = true } = options;

  const {
    items,
    isLoading,
    lastFetch,
    error,
    queuedCount,
    processingCount,
    failedCount,
    completedCount,
    fetchQueue,
    queueBook,
    cancelBook,
    retryBook,
    clearError,
  } = useIngestionQueueStore();

  // Memoized refresh function
  const refresh = useCallback(() => {
    return fetchQueue();
  }, [fetchQueue]);

  // Setup polling
  useEffect(() => {
    if (!autoStart) return;

    // Initial fetch
    fetchQueue();

    // Setup polling interval
    const interval = setInterval(() => {
      // Skip polling if configured to only poll when active and no active items
      if (pollOnlyWhenActive && queuedCount === 0 && processingCount === 0) {
        return;
      }

      fetchQueue();
    }, pollIntervalMs);

    // Cleanup on unmount
    return () => clearInterval(interval);
  }, [autoStart, pollIntervalMs, pollOnlyWhenActive, queuedCount, processingCount, fetchQueue]);

  // Check if a specific book is in the queue
  const isBookQueued = useCallback(
    (calibreId: number): boolean => {
      return items.some((i) => i.calibre_id === calibreId);
    },
    [items]
  );

  // Get status for a specific book
  const getBookQueueStatus = useCallback(
    (calibreId: number) => {
      const item = items.find((i) => i.calibre_id === calibreId);
      return item?.status ?? null;
    },
    [items]
  );

  // Computed: has any items
  const hasItems = items.length > 0;

  // Computed: has active items (queued or processing)
  const hasActiveItems = queuedCount > 0 || processingCount > 0;

  return {
    // State
    items,
    isLoading,
    lastFetch,
    error,

    // Stats
    queuedCount,
    processingCount,
    failedCount,
    completedCount,
    hasItems,
    hasActiveItems,

    // Actions
    queueBook,
    cancelBook,
    retryBook,
    refresh,
    clearError,

    // Helpers
    isBookQueued,
    getBookQueueStatus,
  };
}
