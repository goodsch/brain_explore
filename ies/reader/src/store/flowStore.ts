import { create } from 'zustand';
import {
  syncApi,
  type ExplorationSession,
  type JourneyStep,
  type ReadingPosition,
} from '../services';
import { visitApi } from '../services/visitApi';
import { timelineApi } from '../services/timelineApi';
import { questionApi } from '../services/questionApi';
import { contextApi, type Context } from '../services/contextApi';
import type {
  NewItemsSummary,
  NewItemsDetailResponse,
  JourneyTimelineResponse,
  PassageRankingResponse,
  VisitScope,
} from '../types/api';

interface Journey {
  path: JourneyStep[];
}

// Question types for Flow v2
export interface FlowQuestion {
  id: string;
  text: string;
  source: 'siyuan' | 'reader' | 'ai-suggested';
  siyuanId?: string;
  parentId?: string;
  contextId?: string;
  status: 'active' | 'paused' | 'resolved';
  createdAt: string;
  updatedAt: string;
}

interface FlowStore {
  isFlowPanelOpen: boolean;
  setFlowPanelOpen: (open: boolean) => void;
  flowPanelWidth: string;
  userId: string | null;
  setUserId: (id: string) => void;

  // Active context for extraction
  currentContextId: string | null;
  currentContext: Context | null;
  setCurrentContextId: (id: string | null) => void;
  fetchCurrentContext: () => Promise<void>;

  // Selected area of exploration
  selectedArea: string | null;
  setSelectedArea: (area: string | null) => void;

  startJourney: (title: string, id?: number) => void;
  endJourney: () => Journey;
  setSyncStatus: (status: string, error?: string) => void;
  currentEntity: { id: string; name: string } | null;
  setCurrentEntity: (entity: { id: string; name: string } | null) => void;
  addJourneyMark: (mark: JourneyStep) => void;

  // Question state
  questions: FlowQuestion[];
  currentQuestionId: string | null;
  isLoadingQuestions: boolean;

  // Question actions
  addQuestion: (question: FlowQuestion) => void;
  removeQuestion: (questionId: string) => void;
  updateQuestion: (questionId: string, updates: Partial<FlowQuestion>) => void;
  setCurrentQuestionId: (questionId: string | null) => void;
  setQuestions: (questions: FlowQuestion[]) => void;
  setIsLoadingQuestions: (loading: boolean) => void;

  // Session sync state
  currentSessionId: string | null;
  syncStatus: 'idle' | 'syncing' | 'synced' | 'error';
  syncError: string | null;
  journeyPath: JourneyStep[];
  readingPosition: ReadingPosition | null;

  // Session sync actions
  createSession: () => Promise<ExplorationSession | null>;
  updateSession: () => Promise<void>;
  pauseSession: () => Promise<void>;
  resumeSession: (sessionId: string) => Promise<ExplorationSession | null>;
  setReadingPosition: (position: ReadingPosition) => void;
  getActiveSessions: () => Promise<ExplorationSession[]>;

  // P1: Visit tracking (What's New)
  newItemsSummary: NewItemsSummary | null;
  newItemsDetail: NewItemsDetailResponse | null;
  isLoadingNewItems: boolean;
  recordVisit: (scope: VisitScope, scopeId: string) => Promise<void>;
  fetchNewItemsSummary: (scope: VisitScope, scopeId: string) => Promise<void>;
  fetchNewItemsDetail: (scope: VisitScope, scopeId: string, limit?: number) => Promise<void>;
  clearNewItems: () => void;

  // P1: Relevant passages
  relevantPassages: PassageRankingResponse | null;
  isLoadingPassages: boolean;
  fetchRelevantPassages: (questionId: string, maxPassages?: number) => Promise<void>;
  clearRelevantPassages: () => void;

  // P2: Journey timeline
  journeyTimeline: JourneyTimelineResponse | null;
  isLoadingTimeline: boolean;
  activePanelTab: 'explore' | 'timeline';
  setActivePanelTab: (tab: 'explore' | 'timeline') => void;
  fetchTimeline: (contextId?: string, grouping?: string) => Promise<void>;
  clearTimeline: () => void;

  // Extraction
  extractionResult: import('../services/extractionApi').ExtractionResult | null;
  isExtracting: boolean;
  extractionError: string | null;
  runExtraction: (contextId: string, questionId?: string) => Promise<void>;
  clearExtraction: () => void;
}

export const useFlowStore = create<FlowStore>((set, get) => ({
  isFlowPanelOpen: false,
  setFlowPanelOpen: (open) => set({ isFlowPanelOpen: open }),
  flowPanelWidth: '30%',
  userId: null,
  setUserId: (id) => set({ userId: id }),

  // Active context for extraction
  currentContextId: null,
  currentContext: null,
  setCurrentContextId: (id) => {
    set({ currentContextId: id });
    // Auto-fetch context when ID changes
    if (id) {
      get().fetchCurrentContext();
    } else {
      set({ currentContext: null, selectedArea: null });
    }
  },

  fetchCurrentContext: async () => {
    const { currentContextId } = get();
    if (!currentContextId) return;

    try {
      const context = await contextApi.get(currentContextId);
      set({ currentContext: context });
    } catch (error) {
      console.error('Failed to fetch context:', error);
      set({ currentContext: null });
    }
  },

  // Selected area of exploration
  selectedArea: null,
  setSelectedArea: (area) => set({ selectedArea: area }),

  startJourney: () => set({ journeyPath: [] }),
  endJourney: () => {
    const { journeyPath } = get();
    set({ journeyPath: [] });
    return { path: journeyPath };
  },
  setSyncStatus: (status, error) =>
    set({
      syncStatus: status as 'idle' | 'syncing' | 'synced' | 'error',
      syncError: error || null,
    }),
  currentEntity: null,
  setCurrentEntity: (entity) => set({ currentEntity: entity }),
  addJourneyMark: (mark: JourneyStep) =>
    set((state) => ({ journeyPath: [...state.journeyPath, mark] })),

  // Question state
  questions: [],
  currentQuestionId: null,
  isLoadingQuestions: false,

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

  setIsLoadingQuestions: (loading: boolean) => set({ isLoadingQuestions: loading }),

  // Session sync state
  currentSessionId: null,
  syncStatus: 'idle',
  syncError: null,
  journeyPath: [],
  readingPosition: null,

  // Session sync actions
  createSession: async () => {
    const { userId, currentEntity, journeyPath, readingPosition } = get();
    if (!userId) return null;

    set({ syncStatus: 'syncing' });
    try {
      const session = await syncApi.createOrUpdate({
        user_id: userId,
        app_source: 'reader',
        current_entity_id: currentEntity?.id,
        current_entity_name: currentEntity?.name,
        journey_path: journeyPath,
        reading_position: readingPosition || undefined,
      });
      set({ currentSessionId: session.id, syncStatus: 'synced', syncError: null });
      return session;
    } catch (error) {
      set({ syncStatus: 'error', syncError: (error as Error).message });
      return null;
    }
  },

  updateSession: async () => {
    const { currentSessionId, userId, currentEntity, journeyPath, readingPosition } = get();
    if (!currentSessionId || !userId) return;

    set({ syncStatus: 'syncing' });
    try {
      await syncApi.updateSession(currentSessionId, {
        current_entity_id: currentEntity?.id,
        current_entity_name: currentEntity?.name,
        journey_path: journeyPath,
        reading_position: readingPosition || undefined,
      });
      set({ syncStatus: 'synced', syncError: null });
    } catch (error) {
      set({ syncStatus: 'error', syncError: (error as Error).message });
    }
  },

  pauseSession: async () => {
    const { currentSessionId } = get();
    if (!currentSessionId) return;

    try {
      await syncApi.updateStatus(currentSessionId, 'paused');
      set({ currentSessionId: null, syncStatus: 'idle' });
    } catch (error) {
      set({ syncStatus: 'error', syncError: (error as Error).message });
    }
  },

  resumeSession: async (sessionId: string) => {
    set({ syncStatus: 'syncing' });
    try {
      const session = await syncApi.getSession(sessionId);
      if (session) {
        set({
          currentSessionId: session.id,
          journeyPath: session.journey_path || [],
          readingPosition: session.reading_position || null,
          currentEntity: session.current_entity_id
            ? { id: session.current_entity_id, name: session.current_entity_name || '' }
            : null,
          syncStatus: 'synced',
          syncError: null,
        });
        // Mark as active
        await syncApi.updateStatus(sessionId, 'active');
      }
      return session;
    } catch (error) {
      set({ syncStatus: 'error', syncError: (error as Error).message });
      return null;
    }
  },

  setReadingPosition: (position: ReadingPosition) => set({ readingPosition: position }),

  getActiveSessions: async () => {
    const { userId } = get();
    if (!userId) return [];
    try {
      return await syncApi.getActiveSessions(userId);
    } catch {
      return [];
    }
  },

  // P1: Visit tracking (What's New)
  newItemsSummary: null,
  newItemsDetail: null,
  isLoadingNewItems: false,

  recordVisit: async (scope: VisitScope, scopeId: string) => {
    const { userId } = get();
    try {
      await visitApi.recordVisit({
        user_id: userId || 'default_user',
        scope,
        scope_id: scopeId,
      });
    } catch (error) {
      console.error('Failed to record visit:', error);
    }
  },

  fetchNewItemsSummary: async (scope: VisitScope, scopeId: string) => {
    const { userId } = get();
    set({ isLoadingNewItems: true });
    try {
      const summary = await visitApi.getNewItemsSummary(
        scope,
        scopeId,
        userId || 'default_user'
      );
      set({ newItemsSummary: summary, isLoadingNewItems: false });
    } catch (error) {
      console.error('Failed to fetch new items summary:', error);
      set({ isLoadingNewItems: false });
    }
  },

  fetchNewItemsDetail: async (scope: VisitScope, scopeId: string, limit = 50) => {
    const { userId } = get();
    set({ isLoadingNewItems: true });
    try {
      const detail = await visitApi.getNewItemsDetail({
        user_id: userId || 'default_user',
        scope,
        scope_id: scopeId,
        limit,
      });
      set({ newItemsDetail: detail, isLoadingNewItems: false });
    } catch (error) {
      console.error('Failed to fetch new items detail:', error);
      set({ isLoadingNewItems: false });
    }
  },

  clearNewItems: () => set({ newItemsSummary: null, newItemsDetail: null }),

  // P1: Relevant passages
  relevantPassages: null,
  isLoadingPassages: false,

  fetchRelevantPassages: async (questionId: string, maxPassages = 10) => {
    set({ isLoadingPassages: true });
    try {
      const passages = await questionApi.getRelevantPassages(questionId, {
        max_passages: maxPassages,
        min_score: 0.1,
      });
      set({ relevantPassages: passages, isLoadingPassages: false });
    } catch (error) {
      console.error('Failed to fetch relevant passages:', error);
      set({ isLoadingPassages: false });
    }
  },

  clearRelevantPassages: () => set({ relevantPassages: null }),

  // P2: Journey timeline
  journeyTimeline: null,
  isLoadingTimeline: false,
  activePanelTab: 'explore',

  setActivePanelTab: (tab: 'explore' | 'timeline') => set({ activePanelTab: tab }),

  fetchTimeline: async (contextId?: string, grouping = 'by_day') => {
    set({ isLoadingTimeline: true });
    try {
      const timeline = contextId
        ? await timelineApi.getContextTimeline(contextId, grouping as any)
        : await timelineApi.getTimeline({ grouping: grouping as any });
      set({ journeyTimeline: timeline, isLoadingTimeline: false });
    } catch (error) {
      console.error('Failed to fetch timeline:', error);
      set({ isLoadingTimeline: false });
    }
  },

  clearTimeline: () => set({ journeyTimeline: null }),

  // Extraction state
  extractionResult: null,
  isExtracting: false,
  extractionError: null,

  runExtraction: async (contextId: string, questionId?: string) => {
    set({ isExtracting: true, extractionError: null });
    try {
      const { extractionApi } = await import('../services/extractionApi');
      const response = await extractionApi.runExtraction({
        context_id: contextId,
        question_id: questionId,
      });
      set({ extractionResult: response.result, isExtracting: false });
    } catch (error) {
      console.error('Extraction failed:', error);
      set({
        isExtracting: false,
        extractionError: (error as Error).message,
      });
    }
  },

  clearExtraction: () => set({ extractionResult: null, extractionError: null }),
}));
