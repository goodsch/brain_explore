import { create } from 'zustand';
import { graphClient, type IngestionQueueItem } from '../services/graphClient';

interface IngestionQueueState {
  items: IngestionQueueItem[];
  isLoading: boolean;
  lastFetch: number | null;
  error: string | null;

  // Derived stats (computed from items)
  queuedCount: number;
  processingCount: number;
  failedCount: number;
  completedCount: number;

  // Actions
  fetchQueue: () => Promise<void>;
  queueBook: (calibreId: number) => Promise<void>;
  cancelBook: (calibreId: number) => Promise<void>;
  retryBook: (calibreId: number) => Promise<void>;
  clearError: () => void;
}

// Helper to compute stats from items
function computeStats(items: IngestionQueueItem[]) {
  return {
    queuedCount: items.filter((i) => i.status === 'queued').length,
    processingCount: items.filter((i) => i.status === 'processing').length,
    failedCount: items.filter((i) => i.status === 'failed').length,
    completedCount: items.filter((i) => i.status === 'completed').length,
  };
}

export const useIngestionQueueStore = create<IngestionQueueState>((set, get) => ({
  // Initial state
  items: [],
  isLoading: false,
  lastFetch: null,
  error: null,
  queuedCount: 0,
  processingCount: 0,
  failedCount: 0,
  completedCount: 0,

  // Fetch current queue from backend
  fetchQueue: async () => {
    set({ isLoading: true, error: null });

    try {
      const response = await graphClient.getIngestionQueue();
      const stats = computeStats(response.items);

      set({
        items: response.items,
        isLoading: false,
        lastFetch: Date.now(),
        ...stats,
      });
    } catch (error) {
      set({
        isLoading: false,
        error: error instanceof Error ? error.message : 'Failed to fetch queue',
      });
    }
  },

  // Queue a book for entity extraction
  queueBook: async (calibreId: number) => {
    const currentItems = get().items;

    // Optimistic update: add item as queued
    const optimisticItem: IngestionQueueItem = {
      calibre_id: calibreId,
      title: 'Loading...',
      author: '',
      queued_at: new Date().toISOString(),
      status: 'queued',
    };

    const optimisticItems = [...currentItems, optimisticItem];
    set({
      items: optimisticItems,
      ...computeStats(optimisticItems),
    });

    try {
      await graphClient.queueBookForIngestion(calibreId);
      // Refresh to get actual data from backend
      await get().fetchQueue();
    } catch (error) {
      // Rollback optimistic update
      set({
        items: currentItems,
        ...computeStats(currentItems),
        error: error instanceof Error ? error.message : 'Failed to queue book',
      });
    }
  },

  // Cancel a queued book
  cancelBook: async (calibreId: number) => {
    const currentItems = get().items;

    // Optimistic update: remove item
    const optimisticItems = currentItems.filter((i) => i.calibre_id !== calibreId);
    set({
      items: optimisticItems,
      ...computeStats(optimisticItems),
    });

    try {
      await graphClient.removeFromIngestionQueue(calibreId);
    } catch (error) {
      // Rollback optimistic update
      set({
        items: currentItems,
        ...computeStats(currentItems),
        error: error instanceof Error ? error.message : 'Failed to cancel book',
      });
    }
  },

  // Retry a failed book (re-queue it)
  retryBook: async (calibreId: number) => {
    const currentItems = get().items;

    // Optimistic update: set status back to queued
    const optimisticItems = currentItems.map((i) =>
      i.calibre_id === calibreId ? { ...i, status: 'queued' as const } : i
    );
    set({
      items: optimisticItems,
      ...computeStats(optimisticItems),
    });

    try {
      await graphClient.queueBookForIngestion(calibreId);
      // Refresh to get actual data from backend
      await get().fetchQueue();
    } catch (error) {
      // Rollback optimistic update
      set({
        items: currentItems,
        ...computeStats(currentItems),
        error: error instanceof Error ? error.message : 'Failed to retry book',
      });
    }
  },

  // Clear error state
  clearError: () => set({ error: null }),
}));
