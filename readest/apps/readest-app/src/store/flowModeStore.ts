import { create } from 'zustand';
import type { EntityOverlay } from '../services/transformers/types';

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

// Breadcrumb journey tracking
export interface JourneyStep {
  entityId: string;
  entityName: string;
  timestamp: string;
  sourcePassage?: string;
  dwellTimeSeconds: number;
}

export interface JourneyMark {
  type: 'highlight' | 'annotation' | 'question';
  entityId: string;
  content: string;
  timestamp: string;
}

export interface ThinkingPartnerExchange {
  question: string;
  response?: string;
  timestamp: string;
}

export interface BreadcrumbJourney {
  id: string;
  userId: string;
  startedAt: string;
  endedAt?: string;
  entryPoint: {
    type: 'book' | 'search' | 'dashboard';
    reference: string;
  };
  path: JourneyStep[];
  marks: JourneyMark[];
  thinkingPartnerExchanges: ThinkingPartnerExchange[];
}

interface FlowModeState {
  // Panel visibility and layout
  flowPanelWidth: string;
  isFlowModeActive: boolean;
  isFlowPanelPinned: boolean;

  // Current entity being explored
  currentEntity: GraphEntity | null;
  relationships: EntityRelationship[];
  bookSources: BookSource[];
  thinkingPartnerQuestions: ThinkingPartnerQuestion[];

  // Journey tracking
  currentJourney: BreadcrumbJourney | null;
  journeyStartTime: number | null;
  currentStepStartTime: number | null;

  // Entity overlay state
  entityOverlay: {
    enabled: boolean;
    entities: EntityOverlay[];
    visibleTypes: string[];
    loading: boolean;
    error: string | null;
  };

  // Loading states
  isLoadingEntity: boolean;
  isLoadingQuestions: boolean;

  // Actions - Panel
  getFlowPanelWidth: () => string;
  setFlowPanelWidth: (width: string) => void;
  toggleFlowMode: () => void;
  toggleFlowPanelPin: () => void;
  setFlowModeActive: (active: boolean) => void;
  setFlowPanelPinned: (pinned: boolean) => void;

  // Actions - Entity
  setCurrentEntity: (entity: GraphEntity | null) => void;
  setRelationships: (relationships: EntityRelationship[]) => void;
  setBookSources: (sources: BookSource[]) => void;
  setThinkingPartnerQuestions: (questions: ThinkingPartnerQuestion[]) => void;
  setIsLoadingEntity: (loading: boolean) => void;
  setIsLoadingQuestions: (loading: boolean) => void;

  // Actions - Journey
  startJourney: (userId: string, entryPoint: BreadcrumbJourney['entryPoint']) => void;
  addJourneyStep: (entityId: string, entityName: string, sourcePassage?: string) => void;
  addJourneyMark: (mark: Omit<JourneyMark, 'timestamp'>) => void;
  addThinkingPartnerExchange: (question: string, response?: string) => void;
  endJourney: () => BreadcrumbJourney | null;
  getCurrentJourney: () => BreadcrumbJourney | null;

  // Actions - Entity Overlay
  setEntityOverlayEnabled: (enabled: boolean) => void;
  setEntityOverlayEntities: (entities: EntityOverlay[]) => void;
  setVisibleTypes: (types: string[]) => void;
  toggleEntityType: (type: string) => void;
  fetchEntitiesForBook: (bookHash: string) => Promise<void>;
}

export const useFlowModeStore = create<FlowModeState>((set, get) => ({
  // Initial state
  flowPanelWidth: '35%',
  isFlowModeActive: false,
  isFlowPanelPinned: false,
  currentEntity: null,
  relationships: [],
  bookSources: [],
  thinkingPartnerQuestions: [],
  currentJourney: null,
  journeyStartTime: null,
  currentStepStartTime: null,
  isLoadingEntity: false,
  isLoadingQuestions: false,

  // Entity overlay initial state
  entityOverlay: {
    enabled: false,
    entities: [],
    visibleTypes: ['Concept', 'Person', 'Theory', 'Framework', 'Assessment'],
    loading: false,
    error: null,
  },

  // Panel actions
  getFlowPanelWidth: () => get().flowPanelWidth,
  setFlowPanelWidth: (width: string) => set({ flowPanelWidth: width }),
  toggleFlowMode: () => set((state) => ({ isFlowModeActive: !state.isFlowModeActive })),
  toggleFlowPanelPin: () => set((state) => ({ isFlowPanelPinned: !state.isFlowPanelPinned })),
  setFlowModeActive: (active: boolean) => set({ isFlowModeActive: active }),
  setFlowPanelPinned: (pinned: boolean) => set({ isFlowPanelPinned: pinned }),

  // Entity actions
  setCurrentEntity: (entity: GraphEntity | null) => set({ currentEntity: entity }),
  setRelationships: (relationships: EntityRelationship[]) => set({ relationships }),
  setBookSources: (sources: BookSource[]) => set({ bookSources: sources }),
  setThinkingPartnerQuestions: (questions: ThinkingPartnerQuestion[]) =>
    set({ thinkingPartnerQuestions: questions }),
  setIsLoadingEntity: (loading: boolean) => set({ isLoadingEntity: loading }),
  setIsLoadingQuestions: (loading: boolean) => set({ isLoadingQuestions: loading }),

  // Journey actions
  startJourney: (userId: string, entryPoint: BreadcrumbJourney['entryPoint']) => {
    const now = Date.now();
    const journey: BreadcrumbJourney = {
      id: `journey-${now}-${Math.random().toString(36).substr(2, 9)}`,
      userId,
      startedAt: new Date(now).toISOString(),
      entryPoint,
      path: [],
      marks: [],
      thinkingPartnerExchanges: [],
    };
    set({
      currentJourney: journey,
      journeyStartTime: now,
      currentStepStartTime: now,
    });
  },

  addJourneyStep: (entityId: string, entityName: string, sourcePassage?: string) => {
    const state = get();
    if (!state.currentJourney) return;

    const now = Date.now();
    const dwellTime = state.currentStepStartTime
      ? Math.round((now - state.currentStepStartTime) / 1000)
      : 0;

    // Update previous step's dwell time if exists
    const updatedPath = [...state.currentJourney.path];
    if (updatedPath.length > 0) {
      updatedPath[updatedPath.length - 1] = {
        ...updatedPath[updatedPath.length - 1]!,
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
      currentJourney: {
        ...state.currentJourney,
        path: updatedPath,
      },
      currentStepStartTime: now,
    });
  },

  addJourneyMark: (mark: Omit<JourneyMark, 'timestamp'>) => {
    const state = get();
    if (!state.currentJourney) return;

    const newMark: JourneyMark = {
      ...mark,
      timestamp: new Date().toISOString(),
    };

    set({
      currentJourney: {
        ...state.currentJourney,
        marks: [...state.currentJourney.marks, newMark],
      },
    });
  },

  addThinkingPartnerExchange: (question: string, response?: string) => {
    const state = get();
    if (!state.currentJourney) return;

    const exchange: ThinkingPartnerExchange = {
      question,
      response,
      timestamp: new Date().toISOString(),
    };

    set({
      currentJourney: {
        ...state.currentJourney,
        thinkingPartnerExchanges: [...state.currentJourney.thinkingPartnerExchanges, exchange],
      },
    });
  },

  endJourney: () => {
    const state = get();
    if (!state.currentJourney) return null;

    const now = Date.now();

    // Update last step's dwell time
    const updatedPath = [...state.currentJourney.path];
    if (updatedPath.length > 0 && state.currentStepStartTime) {
      const dwellTime = Math.round((now - state.currentStepStartTime) / 1000);
      updatedPath[updatedPath.length - 1] = {
        ...updatedPath[updatedPath.length - 1]!,
        dwellTimeSeconds: dwellTime,
      };
    }

    const completedJourney: BreadcrumbJourney = {
      ...state.currentJourney,
      path: updatedPath,
      endedAt: new Date(now).toISOString(),
    };

    set({
      currentJourney: null,
      journeyStartTime: null,
      currentStepStartTime: null,
    });

    return completedJourney;
  },

  getCurrentJourney: () => get().currentJourney,

  // Entity Overlay actions
  setEntityOverlayEnabled: (enabled: boolean) => {
    set((state) => ({
      entityOverlay: {
        ...state.entityOverlay,
        enabled,
      },
    }));
  },

  setEntityOverlayEntities: (entities: EntityOverlay[]) => {
    set((state) => ({
      entityOverlay: {
        ...state.entityOverlay,
        entities,
      },
    }));
  },

  setVisibleTypes: (types: string[]) => {
    set((state) => ({
      entityOverlay: {
        ...state.entityOverlay,
        visibleTypes: types,
      },
    }));
  },

  toggleEntityType: (type: string) => {
    set((state) => {
      const currentTypes = state.entityOverlay.visibleTypes;
      const isVisible = currentTypes.includes(type);

      return {
        entityOverlay: {
          ...state.entityOverlay,
          visibleTypes: isVisible
            ? currentTypes.filter((t) => t !== type)
            : [...currentTypes, type],
        },
      };
    });
  },

  fetchEntitiesForBook: async (bookHash: string) => {
    set((state) => ({
      entityOverlay: {
        ...state.entityOverlay,
        loading: true,
        error: null,
      },
    }));

    try {
      const response = await fetch(
        `http://localhost:8081/api/v1/graph/entities/by-book/${bookHash}`
      );

      if (!response.ok) {
        throw new Error(`Failed to fetch entities: ${response.statusText}`);
      }

      const data = await response.json();
      const entities: EntityOverlay[] = data.entities || [];

      set((state) => ({
        entityOverlay: {
          ...state.entityOverlay,
          entities,
          loading: false,
        },
      }));
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      set((state) => ({
        entityOverlay: {
          ...state.entityOverlay,
          loading: false,
          error: errorMessage,
        },
      }));
    }
  },
}));
