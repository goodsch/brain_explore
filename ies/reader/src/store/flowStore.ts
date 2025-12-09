import { create } from 'zustand';

interface Journey {
  path: any[];
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
}));
