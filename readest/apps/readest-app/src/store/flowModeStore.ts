import { create } from 'zustand';
import {
  getSyncService,
  AppSource,
  SessionStatus,
  type ReadingPosition,
  type ExplorationSession,
} from '@/services/flow/syncService';

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

// Evidence passages from source materials (Sprint 2)
export interface EvidencePassage {
  id: string;
  text: string;
  sourceTitle: string;
  sourceAuthor?: string;
  location?: {
    chapter?: string;
    page?: number;
    cfi?: string;
  };
  confidence: number;
  sourceType: 'chunk' | 'book';
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

// Question types for Flow v2
export interface FlowQuestion {
  id: string;
  text: string;
  source: 'siyuan' | 'reader' | 'ai-suggested';
  siyuanId?: string;
  parentId?: string;
  status: 'active' | 'paused' | 'resolved';
  createdAt: string;
  updatedAt: string;
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
  evidence: EvidencePassage[];
  thinkingPartnerQuestions: ThinkingPartnerQuestion[];

  // Journey tracking
  currentJourney: BreadcrumbJourney | null;
  journeyStartTime: number | null;
  currentStepStartTime: number | null;

  // Session sync (Sprint 3)
  sessionId: string | null;
  currentSession: ExplorationSession | null;
  readingPosition: ReadingPosition | null;
  isSyncing: boolean;

  // Loading states
  isLoadingEntity: boolean;
  isLoadingEvidence: boolean;
  isLoadingQuestions: boolean;

  // Question state
  questions: FlowQuestion[];
  currentQuestionId: string | null;

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
  setEvidence: (evidence: EvidencePassage[]) => void;
  setThinkingPartnerQuestions: (questions: ThinkingPartnerQuestion[]) => void;
  setIsLoadingEntity: (loading: boolean) => void;
  setIsLoadingEvidence: (loading: boolean) => void;
  setIsLoadingQuestions: (loading: boolean) => void;

  // Actions - Journey
  startJourney: (userId: string, entryPoint: BreadcrumbJourney['entryPoint']) => void;
  addJourneyStep: (entityId: string, entityName: string, sourcePassage?: string) => void;
  addJourneyMark: (mark: Omit<JourneyMark, 'timestamp'>) => void;
  addThinkingPartnerExchange: (question: string, response?: string) => void;
  endJourney: () => BreadcrumbJourney | null;
  getCurrentJourney: () => BreadcrumbJourney | null;

  // Actions - Session Sync (Sprint 3)
  setReadingPosition: (position: ReadingPosition | null) => void;
  syncSession: (userId: string, force?: boolean) => Promise<void>;
  pauseCurrentSession: () => Promise<void>;
  loadSession: (sessionId: string) => Promise<void>;
  setSessionId: (sessionId: string | null) => void;

  // Question actions
  addQuestion: (question: FlowQuestion) => void;
  removeQuestion: (questionId: string) => void;
  updateQuestion: (questionId: string, updates: Partial<FlowQuestion>) => void;
  setCurrentQuestionId: (questionId: string | null) => void;
  setQuestions: (questions: FlowQuestion[]) => void;
}

// Debounce helper
let syncDebounceTimer: NodeJS.Timeout | null = null;
const SYNC_DEBOUNCE_MS = 2000; // 2 seconds for entity navigation
const POSITION_SYNC_DEBOUNCE_MS = 5000; // 5 seconds for reading position

export const useFlowModeStore = create<FlowModeState>((set, get) => ({
  // Initial state
  flowPanelWidth: '35%',
  isFlowModeActive: false,
  isFlowPanelPinned: false,
  currentEntity: null,
  relationships: [],
  bookSources: [],
  evidence: [],
  thinkingPartnerQuestions: [],
  currentJourney: null,
  journeyStartTime: null,
  currentStepStartTime: null,
  sessionId: null,
  currentSession: null,
  readingPosition: null,
  isSyncing: false,
  isLoadingEntity: false,
  isLoadingEvidence: false,
  isLoadingQuestions: false,
  questions: [],
  currentQuestionId: null,

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
  setFlowModeActive: (active: boolean) => {
    set({ isFlowModeActive: active });
    // Auto-pause session when flow panel closes
    if (!active) {
      const state = get();
      if (state.sessionId) {
        get().pauseCurrentSession().catch(console.error);
      }
    }
  },
  setFlowPanelPinned: (pinned: boolean) => set({ isFlowPanelPinned: pinned }),

  // Entity actions
  setCurrentEntity: (entity: GraphEntity | null) => {
    set({ currentEntity: entity });
    // Auto-sync on entity navigation (debounced)
    if (entity) {
      const state = get();
      if (state.currentJourney) {
        get().addJourneyStep(entity.id, entity.name);
      }
      // Trigger sync after debounce
      if (syncDebounceTimer) clearTimeout(syncDebounceTimer);
      syncDebounceTimer = setTimeout(() => {
        const userId = state.currentJourney?.userId || 'default-user';
        get().syncSession(userId, false).catch(console.error);
      }, SYNC_DEBOUNCE_MS);
    }
  },
  setRelationships: (relationships: EntityRelationship[]) => set({ relationships }),
  setBookSources: (sources: BookSource[]) => set({ bookSources: sources }),
  setEvidence: (evidence: EvidencePassage[]) => set({ evidence }),
  setThinkingPartnerQuestions: (questions: ThinkingPartnerQuestion[]) =>
    set({ thinkingPartnerQuestions: questions }),
  setIsLoadingEntity: (loading: boolean) => set({ isLoadingEntity: loading }),
  setIsLoadingEvidence: (loading: boolean) => set({ isLoadingEvidence: loading }),
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
    // Start sync session
    get().syncSession(userId, true).catch(console.error);
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

  // Session Sync actions (Sprint 3)
  setReadingPosition: (position: ReadingPosition | null) => {
    set({ readingPosition: position });
    // Auto-sync reading position (debounced longer - 5s)
    if (position) {
      if (syncDebounceTimer) clearTimeout(syncDebounceTimer);
      syncDebounceTimer = setTimeout(() => {
        const state = get();
        const userId = state.currentJourney?.userId || 'default-user';
        get().syncSession(userId, false).catch(console.error);
      }, POSITION_SYNC_DEBOUNCE_MS);
    }
  },

  setSessionId: (sessionId: string | null) => {
    set({ sessionId });
  },

  syncSession: async (userId: string, force = false) => {
    const state = get();
    if (state.isSyncing && !force) return;

    set({ isSyncing: true });
    try {
      const syncService = getSyncService();

      // Convert journey path to sync format
      const journeyPath = state.currentJourney?.path.map((step) => ({
        entity_id: step.entityId,
        entity_name: step.entityName,
        timestamp: step.timestamp,
        source_passage: step.sourcePassage,
        dwell_time: step.dwellTimeSeconds,
      })) || [];

      const session = await syncService.createOrUpdateSession(
        {
          user_id: userId,
          app_source: AppSource.READER,
          status: SessionStatus.ACTIVE,
          current_entity_id: state.currentEntity?.id,
          current_entity_name: state.currentEntity?.name,
          reading_position: state.readingPosition || undefined,
          journey_path: journeyPath,
        },
        state.sessionId || undefined,
      );

      set({
        sessionId: session.id,
        currentSession: session,
      });
    } catch (error) {
      console.error('Failed to sync session:', error);
    } finally {
      set({ isSyncing: false });
    }
  },

  pauseCurrentSession: async () => {
    const state = get();
    if (!state.sessionId) return;

    try {
      const syncService = getSyncService();
      const session = await syncService.pauseSession(state.sessionId);
      set({ currentSession: session });
    } catch (error) {
      console.error('Failed to pause session:', error);
    }
  },

  loadSession: async (sessionId: string) => {
    try {
      const syncService = getSyncService();
      const session = await syncService.getSession(sessionId);

      // Restore state from session
      set({
        sessionId: session.id,
        currentSession: session,
        readingPosition: session.reading_position || null,
      });

      // Restore current entity if available
      if (session.current_entity_id && session.current_entity_name) {
        set({
          currentEntity: {
            id: session.current_entity_id,
            name: session.current_entity_name,
            type: 'Concept',
            summary: '',
          },
        });
      }

      // Restore journey if available
      if (session.journey_path.length > 0) {
        const journey: BreadcrumbJourney = {
          id: `restored-${session.id}`,
          userId: session.user_id,
          startedAt: session.created_at,
          entryPoint: {
            type: 'book',
            reference: session.reading_position?.book_hash || 'unknown',
          },
          path: session.journey_path.map((step) => ({
            entityId: step.entity_id,
            entityName: step.entity_name,
            timestamp: step.timestamp,
            sourcePassage: step.source_passage,
            dwellTimeSeconds: step.dwell_time,
          })),
          marks: [],
          thinkingPartnerExchanges: [],
        };
        set({ currentJourney: journey });
      }
    } catch (error) {
      console.error('Failed to load session:', error);
    }
  },

  // Question actions
  addQuestion: (question: FlowQuestion) =>
    set((state) => ({ questions: [...state.questions, question] })),

  removeQuestion: (questionId: string) =>
    set((state) => ({
      questions: state.questions.filter((q) => q.id !== questionId),
      currentQuestionId: state.currentQuestionId === questionId ? null : state.currentQuestionId,
    })),

  updateQuestion: (questionId: string, updates: Partial<FlowQuestion>) =>
    set((state) => ({
      questions: state.questions.map((q) =>
        q.id === questionId ? { ...q, ...updates, updatedAt: new Date().toISOString() } : q
      ),
    })),

  setCurrentQuestionId: (questionId: string | null) => set({ currentQuestionId: questionId }),

  setQuestions: (questions: FlowQuestion[]) => set({ questions }),
}));
