import { create } from 'zustand';

interface Journey {
  path: any[];
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
  addJourneyMark: (mark: any) => void;

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
}

export const useFlowStore = create<FlowStore>((set) => ({
  isFlowPanelOpen: false,
  setFlowPanelOpen: (open) => set({ isFlowPanelOpen: open }),
  flowPanelWidth: '30%',
  userId: null,
  setUserId: (id) => set({ userId: id }),
  startJourney: () => {},
  endJourney: () => ({ path: [] }),
  setSyncStatus: () => {},
  currentEntity: null,
  addJourneyMark: () => {},

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
}));
