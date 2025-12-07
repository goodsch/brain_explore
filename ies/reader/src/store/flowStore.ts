import { create } from 'zustand';

// Types for entity data from the knowledge graph
export interface GraphEntity {
  id: string;
  name: string;
  type: string;
  summary: string;
}

export interface EntityRelationship {
  type: string;
  target: GraphEntity;
  confidence?: number;
}

export interface BookSource {
  bookId: string;
  bookTitle: string;
  chapter?: string;
  pageRange?: string;
}

export interface ThinkingPartnerQuestion {
  text: string;
  type: 'clarifying' | 'connecting' | 'challenging';
  relatedEntities?: string[];
}

// Journey tracking
export interface JourneyStep {
  entityId: string;
  entityName: string;
  timestamp: string;
  sourcePassage?: string;
  dwellTimeSeconds: number;
}

export interface BreadcrumbJourney {
  id: string;
  startedAt: string;
  endedAt?: string;
  entryPoint: {
    type: 'book' | 'search' | 'dashboard';
    reference: string;
    calibreId?: number;
  };
  path: JourneyStep[];
}

// Sync status for backend operations
export type SyncStatus = 'idle' | 'pending' | 'synced' | 'error' | 'offline';

// Entity types that can be overlaid
export type EntityType = 'Concept' | 'Person' | 'Theory' | 'Framework' | 'Assessment';

// Entity from the overlay (simplified for display)
export interface OverlayEntity {
  name: string;
  type: EntityType;
  mention_count: number;
}

interface FlowModeState {
  // User identity
  userId: string | null;

  // Panel visibility
  isFlowPanelOpen: boolean;
  flowPanelWidth: number;

  // Current entity
  currentEntity: GraphEntity | null;
  relationships: EntityRelationship[];
  bookSources: BookSource[];
  thinkingPartnerQuestions: ThinkingPartnerQuestion[];

  // Loading states
  isLoadingEntity: boolean;
  isLoadingQuestions: boolean;

  // Journey
  currentJourney: BreadcrumbJourney | null;
  currentStepStartTime: number | null;

  // Sync state
  syncStatus: SyncStatus;
  lastSyncError: string | null;
  queuedOperationsCount: number;

  // Entity overlay
  isOverlayEnabled: boolean;
  overlayEntities: OverlayEntity[];
  overlayEntityTypes: Record<EntityType, boolean>;
  isLoadingOverlay: boolean;
  currentBookCalibreId: number | null;

  // Actions
  setUserId: (userId: string) => void;
  setFlowPanelOpen: (open: boolean) => void;
  setFlowPanelWidth: (width: number) => void;
  setCurrentEntity: (entity: GraphEntity | null) => void;
  setRelationships: (relationships: EntityRelationship[]) => void;
  setBookSources: (sources: BookSource[]) => void;
  setThinkingPartnerQuestions: (questions: ThinkingPartnerQuestion[]) => void;
  setIsLoadingEntity: (loading: boolean) => void;
  setIsLoadingQuestions: (loading: boolean) => void;
  setSyncStatus: (status: SyncStatus, error?: string) => void;
  setQueuedOperationsCount: (count: number) => void;

  // Journey actions
  startJourney: (bookTitle: string, calibreId?: number) => void;
  addJourneyStep: (entityId: string, entityName: string, sourcePassage?: string) => void;
  endJourney: () => BreadcrumbJourney | null;

  // Entity overlay actions
  setOverlayEnabled: (enabled: boolean) => void;
  setOverlayEntities: (entities: OverlayEntity[]) => void;
  toggleEntityType: (type: EntityType) => void;
  setIsLoadingOverlay: (loading: boolean) => void;
  setCurrentBookCalibreId: (calibreId: number | null) => void;

  // Clear state
  clearEntity: () => void;
}

export const useFlowStore = create<FlowModeState>((set, get) => ({
  // Initial state
  userId: null,
  isFlowPanelOpen: false,
  flowPanelWidth: 400,
  currentEntity: null,
  relationships: [],
  bookSources: [],
  thinkingPartnerQuestions: [],
  isLoadingEntity: false,
  isLoadingQuestions: false,
  currentJourney: null,
  currentStepStartTime: null,
  syncStatus: 'idle',
  lastSyncError: null,
  queuedOperationsCount: 0,

  // Entity overlay initial state
  isOverlayEnabled: false,
  overlayEntities: [],
  overlayEntityTypes: {
    Concept: true,
    Person: true,
    Theory: true,
    Framework: true,
    Assessment: true,
  },
  isLoadingOverlay: false,
  currentBookCalibreId: null,

  // User actions
  setUserId: (userId) => set({ userId }),

  // Panel actions
  setFlowPanelOpen: (open) => set({ isFlowPanelOpen: open }),
  setFlowPanelWidth: (width) => set({ flowPanelWidth: width }),

  // Entity actions
  setCurrentEntity: (entity) => set({ currentEntity: entity }),
  setRelationships: (relationships) => set({ relationships }),
  setBookSources: (sources) => set({ bookSources: sources }),
  setThinkingPartnerQuestions: (questions) => set({ thinkingPartnerQuestions: questions }),
  setIsLoadingEntity: (loading) => set({ isLoadingEntity: loading }),
  setIsLoadingQuestions: (loading) => set({ isLoadingQuestions: loading }),
  setSyncStatus: (status, error) =>
    set({ syncStatus: status, lastSyncError: error || null }),
  setQueuedOperationsCount: (count) => set({ queuedOperationsCount: count }),

  // Journey actions
  startJourney: (bookTitle, calibreId) => {
    const now = Date.now();
    const journey: BreadcrumbJourney = {
      id: `journey-${now}-${Math.random().toString(36).substr(2, 9)}`,
      startedAt: new Date(now).toISOString(),
      entryPoint: { type: 'book', reference: bookTitle, calibreId },
      path: [],
    };
    set({ currentJourney: journey, currentStepStartTime: now });
  },

  addJourneyStep: (entityId, entityName, sourcePassage) => {
    const state = get();
    if (!state.currentJourney) return;

    const now = Date.now();
    const dwellTime = state.currentStepStartTime
      ? Math.round((now - state.currentStepStartTime) / 1000)
      : 0;

    // Update previous step's dwell time
    const updatedPath = [...state.currentJourney.path];
    if (updatedPath.length > 0) {
      updatedPath[updatedPath.length - 1] = {
        ...updatedPath[updatedPath.length - 1],
        dwellTimeSeconds: dwellTime,
      };
    }

    // Add new step
    updatedPath.push({
      entityId,
      entityName,
      timestamp: new Date(now).toISOString(),
      sourcePassage,
      dwellTimeSeconds: 0,
    });

    set({
      currentJourney: { ...state.currentJourney, path: updatedPath },
      currentStepStartTime: now,
    });
  },

  endJourney: () => {
    const state = get();
    if (!state.currentJourney) return null;

    const completedJourney: BreadcrumbJourney = {
      ...state.currentJourney,
      endedAt: new Date().toISOString(),
    };

    set({ currentJourney: null, currentStepStartTime: null });
    return completedJourney;
  },

  // Entity overlay actions
  setOverlayEnabled: (enabled) => set({ isOverlayEnabled: enabled }),
  setOverlayEntities: (entities) => set({ overlayEntities: entities }),
  toggleEntityType: (type) =>
    set((state) => ({
      overlayEntityTypes: {
        ...state.overlayEntityTypes,
        [type]: !state.overlayEntityTypes[type],
      },
    })),
  setIsLoadingOverlay: (loading) => set({ isLoadingOverlay: loading }),
  setCurrentBookCalibreId: (calibreId) => set({ currentBookCalibreId: calibreId }),

  clearEntity: () =>
    set({
      currentEntity: null,
      relationships: [],
      bookSources: [],
      thinkingPartnerQuestions: [],
    }),
}));
