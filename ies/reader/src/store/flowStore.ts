import { create } from 'zustand';
import {
  syncApi,
  type ExplorationSession,
  type JourneyStep,
  type ReadingPosition,
} from '../services';

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
}

export const useFlowStore = create<FlowStore>((set, get) => ({
  isFlowPanelOpen: false,
  setFlowPanelOpen: (open) => set({ isFlowPanelOpen: open }),
  flowPanelWidth: '30%',
  userId: null,
  setUserId: (id) => set({ userId: id }),
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
}));
