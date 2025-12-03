/**
 * Journey Local Storage Service
 *
 * Persists breadcrumb journeys to local storage as a fallback
 * when the backend is unavailable or for offline use.
 */

import { BreadcrumbJourney } from '@/store/flowModeStore';

const STORAGE_KEY = 'readest_flow_journeys';
const MAX_STORED_JOURNEYS = 50;

interface StoredJourneys {
  journeys: BreadcrumbJourney[];
  lastUpdated: string;
}

/**
 * Get all stored journeys from local storage
 */
export function getStoredJourneys(): BreadcrumbJourney[] {
  try {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (!stored) return [];

    const data: StoredJourneys = JSON.parse(stored);
    return data.journeys || [];
  } catch (error) {
    console.error('Failed to read journeys from local storage:', error);
    return [];
  }
}

/**
 * Save a journey to local storage
 */
export function saveJourneyToStorage(journey: BreadcrumbJourney): boolean {
  try {
    const journeys = getStoredJourneys();

    // Check if journey already exists (update) or is new (add)
    const existingIndex = journeys.findIndex((j) => j.id === journey.id);

    if (existingIndex >= 0) {
      journeys[existingIndex] = journey;
    } else {
      journeys.unshift(journey);
    }

    // Trim to max stored journeys
    const trimmedJourneys = journeys.slice(0, MAX_STORED_JOURNEYS);

    const data: StoredJourneys = {
      journeys: trimmedJourneys,
      lastUpdated: new Date().toISOString(),
    };

    localStorage.setItem(STORAGE_KEY, JSON.stringify(data));
    return true;
  } catch (error) {
    console.error('Failed to save journey to local storage:', error);
    return false;
  }
}

/**
 * Get a specific journey by ID
 */
export function getJourneyFromStorage(journeyId: string): BreadcrumbJourney | null {
  const journeys = getStoredJourneys();
  return journeys.find((j) => j.id === journeyId) || null;
}

/**
 * Get journeys for a specific user
 */
export function getUserJourneysFromStorage(userId: string, limit = 20): BreadcrumbJourney[] {
  const journeys = getStoredJourneys();
  return journeys.filter((j) => j.userId === userId).slice(0, limit);
}

/**
 * Delete a journey from local storage
 */
export function deleteJourneyFromStorage(journeyId: string): boolean {
  try {
    const journeys = getStoredJourneys();
    const filteredJourneys = journeys.filter((j) => j.id !== journeyId);

    if (filteredJourneys.length === journeys.length) {
      return false; // Journey not found
    }

    const data: StoredJourneys = {
      journeys: filteredJourneys,
      lastUpdated: new Date().toISOString(),
    };

    localStorage.setItem(STORAGE_KEY, JSON.stringify(data));
    return true;
  } catch (error) {
    console.error('Failed to delete journey from local storage:', error);
    return false;
  }
}

/**
 * Clear all stored journeys
 */
export function clearStoredJourneys(): void {
  try {
    localStorage.removeItem(STORAGE_KEY);
  } catch (error) {
    console.error('Failed to clear journeys from local storage:', error);
  }
}

/**
 * Get journeys that haven't been synced to the backend
 */
export function getUnsyncedJourneys(): BreadcrumbJourney[] {
  const journeys = getStoredJourneys();
  // For now, consider all completed journeys as potentially unsynced
  // In a real implementation, you'd track sync status per journey
  return journeys.filter((j) => j.endedAt);
}

/**
 * Mark a journey as synced (by removing from local storage after backend save)
 */
export function markJourneyAsSynced(journeyId: string): void {
  // In a simple implementation, we keep journeys locally but could add a sync flag
  // For now, this is a no-op as we want to keep local copies
  console.log(`Journey ${journeyId} synced to backend`);
}

/**
 * Export journeys as JSON (for backup/export functionality)
 */
export function exportJourneysAsJson(): string {
  const journeys = getStoredJourneys();
  return JSON.stringify(
    {
      exportedAt: new Date().toISOString(),
      journeyCount: journeys.length,
      journeys,
    },
    null,
    2
  );
}

/**
 * Import journeys from JSON (for restore/import functionality)
 */
export function importJourneysFromJson(json: string): number {
  try {
    const data = JSON.parse(json);
    const importedJourneys: BreadcrumbJourney[] = data.journeys || [];

    if (!Array.isArray(importedJourneys)) {
      throw new Error('Invalid journeys format');
    }

    let importedCount = 0;
    importedJourneys.forEach((journey) => {
      if (journey.id && journey.startedAt) {
        saveJourneyToStorage(journey);
        importedCount++;
      }
    });

    return importedCount;
  } catch (error) {
    console.error('Failed to import journeys:', error);
    return 0;
  }
}
