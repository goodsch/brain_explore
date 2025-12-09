/**
 * Reading position tracking hook for IES Reader.
 *
 * Tracks reading position in epub.js and syncs to backend
 * for cross-app continuity.
 *
 * Features:
 * - Hooks into epub.js 'relocated' event
 * - Debounces position updates by 2 seconds
 * - Saves immediately on window blur
 * - Extracts CFI, chapter, progress percentage
 */

import { useEffect, useRef, useCallback } from 'react';
import type { Rendition, Location } from 'epubjs';
import { sessionStateApi, type ReadingPosition } from '../services/sessionStateApi';

interface UseReadingPositionOptions {
  rendition: Rendition | null;
  calibreId?: number;
  userId?: string;
  enabled?: boolean;
  debounceMs?: number;  // default 2000
}

export function useReadingPosition(options: UseReadingPositionOptions) {
  const {
    rendition,
    calibreId,
    userId = 'default_user',
    enabled = true,
    debounceMs = 2000,
  } = options;

  const writeTimerRef = useRef<NodeJS.Timeout | null>(null);
  const lastPositionRef = useRef<ReadingPosition | null>(null);

  /**
   * Write reading position to backend.
   */
  const writePosition = useCallback(async (position: ReadingPosition) => {
    if (!enabled || !calibreId) return;

    try {
      await sessionStateApi.updateState(userId, {
        current_book: position,
      });

      lastPositionRef.current = position;
      console.log('[useReadingPosition] Position synced:', position);
    } catch (error) {
      console.error('[useReadingPosition] Failed to write position:', error);
    }
  }, [enabled, calibreId, userId]);

  /**
   * Debounced write: clear existing timer and schedule new write.
   */
  const scheduleWrite = useCallback((position: ReadingPosition) => {
    if (writeTimerRef.current) {
      clearTimeout(writeTimerRef.current);
    }

    writeTimerRef.current = setTimeout(() => {
      writePosition(position);
    }, debounceMs);
  }, [writePosition, debounceMs]);

  /**
   * Extract reading position from epub.js location.
   */
  const extractPosition = useCallback((location: Location): ReadingPosition | null => {
    if (!calibreId) return null;

    const { start, atEnd, atStart } = location;

    // Extract chapter title from location
    let chapterTitle: string | undefined;
    if (start && start.displayed && start.displayed.page) {
      // Try to get chapter from spine item
      const spineItem = rendition?.location?.start?.href;
      if (spineItem && rendition?.book?.navigation) {
        const toc = rendition.book.navigation.toc;
        const chapter = toc.find((item: any) => item.href === spineItem);
        chapterTitle = chapter?.label;
      }
    }

    // Calculate progress percentage
    let progressPercent: number | undefined;
    if (start && start.displayed && start.displayed.total > 0) {
      progressPercent = (start.displayed.page / start.displayed.total) * 100;
    } else if (atStart) {
      progressPercent = 0;
    } else if (atEnd) {
      progressPercent = 100;
    }

    // Get CFI
    const cfi = start?.cfi || '';

    // Get page number if available
    const pageNumber = start?.displayed?.page;

    return {
      calibre_id: calibreId,
      cfi,
      chapter_title: chapterTitle,
      page_number: pageNumber,
      progress_percent: progressPercent,
      last_read_at: new Date().toISOString(),
    };
  }, [calibreId, rendition]);

  /**
   * Handle epub.js relocated event.
   */
  useEffect(() => {
    if (!enabled || !rendition || !calibreId) return;

    const handleRelocated = (location: Location) => {
      const position = extractPosition(location);
      if (position) {
        scheduleWrite(position);
      }
    };

    // Register event listener
    rendition.on('relocated', handleRelocated);

    return () => {
      // Cleanup: write any pending position before unmounting
      if (writeTimerRef.current) {
        clearTimeout(writeTimerRef.current);
        if (lastPositionRef.current) {
          writePosition(lastPositionRef.current);
        }
      }

      // Unregister event listener
      rendition.off('relocated', handleRelocated);
    };
  }, [enabled, rendition, calibreId, extractPosition, scheduleWrite, writePosition]);

  /**
   * Save immediately on window blur (user switching away).
   */
  useEffect(() => {
    if (!enabled || !calibreId) return;

    const handleBlur = () => {
      // Cancel any pending debounced write
      if (writeTimerRef.current) {
        clearTimeout(writeTimerRef.current);
        writeTimerRef.current = null;
      }

      // Write immediately if we have a last position
      if (lastPositionRef.current) {
        console.log('[useReadingPosition] Window blur, saving position immediately');
        writePosition(lastPositionRef.current);
      }
    };

    window.addEventListener('blur', handleBlur);

    return () => {
      window.removeEventListener('blur', handleBlur);
    };
  }, [enabled, calibreId, writePosition]);

  /**
   * Extract current position on demand (useful for manual saves).
   *
   * Note: Returns the last tracked position, as rendition.currentLocation()
   * may not return full Location data. For live tracking, rely on the
   * 'relocated' event which this hook already handles.
   */
  const getCurrentPosition = useCallback((): ReadingPosition | null => {
    return lastPositionRef.current;
  }, []);

  return {
    getCurrentPosition,
    writePosition,
  };
}
