import { useEffect, useCallback } from 'react';
import { useFlowStore, type OverlayEntity } from '../store/flowStore';
import { graphClient } from '../services/graphClient';

/**
 * Hook to manage entity overlay state when a book is opened.
 * Fetches entities from the backend and updates the flow store.
 */
export function useEntityOverlay(calibreId: number | undefined) {
  const {
    setCurrentBookCalibreId,
    setOverlayEntities,
    setIsLoadingOverlay,
    setOverlayEnabled,
  } = useFlowStore();

  // Fetch entities when calibreId changes
  useEffect(() => {
    if (calibreId === undefined) {
      // No book open, clear overlay state
      setCurrentBookCalibreId(null);
      setOverlayEntities([]);
      setOverlayEnabled(false);
      return;
    }

    // Set the current book and start loading
    setCurrentBookCalibreId(calibreId);
    setIsLoadingOverlay(true);

    // Fetch entities for this book
    const fetchEntities = async () => {
      try {
        const result = await graphClient.getEntitiesByBook(calibreId);

        // Transform entities to overlay format
        const overlayEntities: OverlayEntity[] = result.entities.map((entity) => ({
          name: entity.name,
          type: entity.type as OverlayEntity['type'],
          mention_count: 1, // Default, could be enhanced with actual count from backend
        }));

        setOverlayEntities(overlayEntities);

        // Auto-enable overlay if book has entities
        if (overlayEntities.length > 0) {
          setOverlayEnabled(true);
        }
      } catch (error) {
        console.error('Failed to fetch entities for overlay:', error);
        setOverlayEntities([]);
      } finally {
        setIsLoadingOverlay(false);
      }
    };

    fetchEntities();

    // Cleanup when book changes or unmounts
    return () => {
      // Don't clear immediately - let the store persist for panel display
    };
  }, [calibreId, setCurrentBookCalibreId, setOverlayEntities, setIsLoadingOverlay, setOverlayEnabled]);

  // Refresh entities manually
  const refreshEntities = useCallback(async () => {
    if (calibreId === undefined) return;

    setIsLoadingOverlay(true);
    try {
      const result = await graphClient.getEntitiesByBook(calibreId);
      const overlayEntities: OverlayEntity[] = result.entities.map((entity) => ({
        name: entity.name,
        type: entity.type as OverlayEntity['type'],
        mention_count: 1,
      }));
      setOverlayEntities(overlayEntities);
    } catch (error) {
      console.error('Failed to refresh entities:', error);
    } finally {
      setIsLoadingOverlay(false);
    }
  }, [calibreId, setOverlayEntities, setIsLoadingOverlay]);

  return { refreshEntities };
}
