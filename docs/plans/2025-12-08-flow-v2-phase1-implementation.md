# Flow Interface v2 — Phase 1 Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build the core infrastructure for Flow v2's dual-mode (desktop panel + mobile standalone) interface

**Architecture:** Extend existing FlowPanel with QuestionSelector and add standalone FlowPage wrapper. Use responsive hook to detect mode and adapt layout. Question state added to Zustand store.

**Tech Stack:** React, TypeScript, Zustand, Tailwind CSS

**Worktree:** `.worktrees/ies-reader/ies/reader/`

---

## Task 1: Create useFlowLayout Hook

**Files:**
- Create: `src/hooks/useFlowLayout.ts`
- Test: `src/__tests__/hooks/useFlowLayout.test.ts`

**Step 1: Write the failing test**

```typescript
// src/__tests__/hooks/useFlowLayout.test.ts
import { renderHook, act } from '@testing-library/react';
import { useFlowLayout } from '../../hooks/useFlowLayout';

describe('useFlowLayout', () => {
  const originalInnerWidth = window.innerWidth;

  afterEach(() => {
    Object.defineProperty(window, 'innerWidth', {
      writable: true,
      configurable: true,
      value: originalInnerWidth,
    });
  });

  it('returns standalone mode for mobile width (<640px)', () => {
    Object.defineProperty(window, 'innerWidth', { value: 500, writable: true });
    const { result } = renderHook(() => useFlowLayout());
    expect(result.current.mode).toBe('standalone');
    expect(result.current.isMobile).toBe(true);
  });

  it('returns panel mode for desktop width (>1024px)', () => {
    Object.defineProperty(window, 'innerWidth', { value: 1200, writable: true });
    const { result } = renderHook(() => useFlowLayout());
    expect(result.current.mode).toBe('panel');
    expect(result.current.isMobile).toBe(false);
  });

  it('returns tablet mode for medium width (640-1024px)', () => {
    Object.defineProperty(window, 'innerWidth', { value: 800, writable: true });
    const { result } = renderHook(() => useFlowLayout());
    expect(result.current.isTablet).toBe(true);
  });
});
```

**Step 2: Run test to verify it fails**

```bash
cd .worktrees/ies-reader/ies/reader
pnpm test src/__tests__/hooks/useFlowLayout.test.ts
```

Expected: FAIL with "Cannot find module '../../hooks/useFlowLayout'"

**Step 3: Write minimal implementation**

```typescript
// src/hooks/useFlowLayout.ts
import { useState, useEffect, useCallback } from 'react';

export type FlowLayoutMode = 'panel' | 'standalone';

interface FlowLayoutState {
  mode: FlowLayoutMode;
  isMobile: boolean;
  isTablet: boolean;
  isDesktop: boolean;
  setMode: (mode: FlowLayoutMode) => void;
}

const MOBILE_BREAKPOINT = 640;
const DESKTOP_BREAKPOINT = 1024;
const STORAGE_KEY = 'ies-flow-layout-mode';

export function useFlowLayout(): FlowLayoutState {
  const [mode, setModeState] = useState<FlowLayoutMode>('panel');
  const [dimensions, setDimensions] = useState({
    isMobile: false,
    isTablet: false,
    isDesktop: true,
  });

  const calculateLayout = useCallback(() => {
    const width = typeof window !== 'undefined' ? window.innerWidth : 1200;
    const isMobile = width < MOBILE_BREAKPOINT;
    const isDesktop = width >= DESKTOP_BREAKPOINT;
    const isTablet = !isMobile && !isDesktop;

    setDimensions({ isMobile, isTablet, isDesktop });

    // Auto-set mode based on screen size
    if (isMobile) {
      setModeState('standalone');
    } else if (isDesktop) {
      setModeState('panel');
    } else {
      // Tablet: respect user preference
      const stored = localStorage.getItem(STORAGE_KEY) as FlowLayoutMode | null;
      setModeState(stored || 'standalone');
    }
  }, []);

  useEffect(() => {
    calculateLayout();
    window.addEventListener('resize', calculateLayout);
    return () => window.removeEventListener('resize', calculateLayout);
  }, [calculateLayout]);

  const setMode = useCallback((newMode: FlowLayoutMode) => {
    setModeState(newMode);
    localStorage.setItem(STORAGE_KEY, newMode);
  }, []);

  return {
    mode,
    ...dimensions,
    setMode,
  };
}
```

**Step 4: Run test to verify it passes**

```bash
cd .worktrees/ies-reader/ies/reader
pnpm test src/__tests__/hooks/useFlowLayout.test.ts
```

Expected: PASS

**Step 5: Commit**

```bash
git add src/hooks/useFlowLayout.ts src/__tests__/hooks/useFlowLayout.test.ts
git commit -m "feat(flow): add useFlowLayout hook for responsive mode detection"
```

---

## Task 2: Add Question Types to Store

**Files:**
- Modify: `src/store/flowModeStore.ts`
- Test: `src/__tests__/store/flowModeStore.test.ts`

**Step 1: Write the failing test**

```typescript
// src/__tests__/store/flowModeStore.test.ts
import { useFlowModeStore } from '../../store/flowModeStore';
import { act } from '@testing-library/react';

describe('flowModeStore - questions', () => {
  beforeEach(() => {
    useFlowModeStore.setState({
      questions: [],
      currentQuestionId: null,
      isLoadingQuestions: false,
    });
  });

  it('adds a question to the store', () => {
    const question = {
      id: 'q1',
      text: 'How does ADHD affect time perception?',
      source: 'reader' as const,
      status: 'active' as const,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    };

    act(() => {
      useFlowModeStore.getState().addQuestion(question);
    });

    expect(useFlowModeStore.getState().questions).toHaveLength(1);
    expect(useFlowModeStore.getState().questions[0].text).toBe('How does ADHD affect time perception?');
  });

  it('sets current question', () => {
    act(() => {
      useFlowModeStore.getState().setCurrentQuestionId('q1');
    });

    expect(useFlowModeStore.getState().currentQuestionId).toBe('q1');
  });

  it('removes a question', () => {
    const question = {
      id: 'q1',
      text: 'Test question',
      source: 'reader' as const,
      status: 'active' as const,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    };

    act(() => {
      useFlowModeStore.getState().addQuestion(question);
      useFlowModeStore.getState().removeQuestion('q1');
    });

    expect(useFlowModeStore.getState().questions).toHaveLength(0);
  });
});
```

**Step 2: Run test to verify it fails**

```bash
cd .worktrees/ies-reader/ies/reader
pnpm test src/__tests__/store/flowModeStore.test.ts
```

Expected: FAIL with "addQuestion is not a function"

**Step 3: Add question types and actions to store**

Add to `src/store/flowModeStore.ts` after existing interfaces (~line 70):

```typescript
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
```

Add to FlowModeState interface (~line 115):

```typescript
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
```

Add initial state (~line 155):

```typescript
  questions: [],
  currentQuestionId: null,
  isLoadingQuestions: false,
```

Add actions (~line 195):

```typescript
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
```

**Step 4: Run test to verify it passes**

```bash
cd .worktrees/ies-reader/ies/reader
pnpm test src/__tests__/store/flowModeStore.test.ts
```

Expected: PASS

**Step 5: Commit**

```bash
git add src/store/flowModeStore.ts src/__tests__/store/flowModeStore.test.ts
git commit -m "feat(flow): add question state management to flowModeStore"
```

---

## Task 3: Create QuestionSelector Component

**Files:**
- Create: `src/app/reader/components/flowpanel/QuestionSelector.tsx`
- Test: `src/__tests__/components/QuestionSelector.test.tsx`

**Step 1: Write the failing test**

```typescript
// src/__tests__/components/QuestionSelector.test.tsx
import { render, screen, fireEvent } from '@testing-library/react';
import QuestionSelector from '../../app/reader/components/flowpanel/QuestionSelector';

const mockQuestions = [
  {
    id: 'q1',
    text: 'How does ADHD affect time perception?',
    source: 'reader' as const,
    status: 'active' as const,
    createdAt: '2025-01-01T00:00:00Z',
    updatedAt: '2025-01-01T00:00:00Z',
  },
  {
    id: 'q2',
    text: 'Why do I procrastinate?',
    source: 'siyuan' as const,
    status: 'active' as const,
    createdAt: '2025-01-01T00:00:00Z',
    updatedAt: '2025-01-01T00:00:00Z',
  },
];

describe('QuestionSelector', () => {
  it('displays current question text when collapsed', () => {
    render(
      <QuestionSelector
        questions={mockQuestions}
        currentQuestionId="q1"
        onSelect={jest.fn()}
        onCreate={jest.fn()}
        isLoading={false}
      />
    );

    expect(screen.getByText(/How does ADHD affect time perception/)).toBeInTheDocument();
  });

  it('shows placeholder when no question selected', () => {
    render(
      <QuestionSelector
        questions={mockQuestions}
        currentQuestionId={null}
        onSelect={jest.fn()}
        onCreate={jest.fn()}
        isLoading={false}
      />
    );

    expect(screen.getByText(/Select a question/)).toBeInTheDocument();
  });

  it('expands dropdown on click', () => {
    render(
      <QuestionSelector
        questions={mockQuestions}
        currentQuestionId={null}
        onSelect={jest.fn()}
        onCreate={jest.fn()}
        isLoading={false}
      />
    );

    fireEvent.click(screen.getByRole('button'));
    expect(screen.getByText('Why do I procrastinate?')).toBeInTheDocument();
  });

  it('calls onSelect when question clicked', () => {
    const onSelect = jest.fn();
    render(
      <QuestionSelector
        questions={mockQuestions}
        currentQuestionId={null}
        onSelect={onSelect}
        onCreate={jest.fn()}
        isLoading={false}
      />
    );

    fireEvent.click(screen.getByRole('button'));
    fireEvent.click(screen.getByText('Why do I procrastinate?'));
    expect(onSelect).toHaveBeenCalledWith('q2');
  });
});
```

**Step 2: Run test to verify it fails**

```bash
cd .worktrees/ies-reader/ies/reader
pnpm test src/__tests__/components/QuestionSelector.test.tsx
```

Expected: FAIL with "Cannot find module"

**Step 3: Write minimal implementation**

```typescript
// src/app/reader/components/flowpanel/QuestionSelector.tsx
import React, { useState, useRef, useEffect } from 'react';
import clsx from 'clsx';
import { LuChevronDown, LuPlus, LuLink } from 'react-icons/lu';
import type { FlowQuestion } from '@/store/flowModeStore';

interface QuestionSelectorProps {
  questions: FlowQuestion[];
  currentQuestionId: string | null;
  onSelect: (questionId: string) => void;
  onCreate: (text: string) => void;
  isLoading: boolean;
}

const QuestionSelector: React.FC<QuestionSelectorProps> = ({
  questions,
  currentQuestionId,
  onSelect,
  onCreate,
  isLoading,
}) => {
  const [isExpanded, setIsExpanded] = useState(false);
  const [isCreating, setIsCreating] = useState(false);
  const [newQuestionText, setNewQuestionText] = useState('');
  const dropdownRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const currentQuestion = questions.find((q) => q.id === currentQuestionId);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsExpanded(false);
        setIsCreating(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Focus input when creating
  useEffect(() => {
    if (isCreating && inputRef.current) {
      inputRef.current.focus();
    }
  }, [isCreating]);

  const handleSelect = (questionId: string) => {
    onSelect(questionId);
    setIsExpanded(false);
  };

  const handleCreate = () => {
    if (newQuestionText.trim()) {
      onCreate(newQuestionText.trim());
      setNewQuestionText('');
      setIsCreating(false);
      setIsExpanded(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Escape') {
      setIsExpanded(false);
      setIsCreating(false);
    } else if (e.key === 'Enter' && isCreating) {
      handleCreate();
    }
  };

  const readerQuestions = questions.filter((q) => q.source === 'reader');
  const siyuanQuestions = questions.filter((q) => q.source === 'siyuan');

  return (
    <div ref={dropdownRef} className="relative" onKeyDown={handleKeyDown}>
      {/* Collapsed state - shows current question */}
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        disabled={isLoading}
        className={clsx(
          'w-full flex items-center justify-between gap-2 px-3 py-2',
          'bg-base-200/50 hover:bg-base-200 rounded-lg',
          'border border-base-300 transition-colors',
          isLoading && 'opacity-50 cursor-not-allowed'
        )}
      >
        <span className="flex items-center gap-2 text-left truncate">
          <span className="text-primary">🎯</span>
          <span className={clsx(!currentQuestion && 'text-base-content/50')}>
            {currentQuestion?.text || 'Select a question...'}
          </span>
        </span>
        <LuChevronDown
          className={clsx('w-4 h-4 transition-transform', isExpanded && 'rotate-180')}
        />
      </button>

      {/* Expanded dropdown */}
      {isExpanded && (
        <div className="absolute top-full left-0 right-0 mt-1 z-50 bg-base-100 border border-base-300 rounded-lg shadow-lg max-h-80 overflow-y-auto">
          {/* Create new question */}
          {isCreating ? (
            <div className="p-2 border-b border-base-300">
              <input
                ref={inputRef}
                type="text"
                value={newQuestionText}
                onChange={(e) => setNewQuestionText(e.target.value)}
                placeholder="What do you want to explore?"
                className="w-full px-3 py-2 bg-base-200 rounded-lg text-sm"
              />
              <div className="flex gap-2 mt-2">
                <button
                  onClick={handleCreate}
                  disabled={!newQuestionText.trim()}
                  className="flex-1 px-3 py-1 bg-primary text-primary-content rounded text-sm disabled:opacity-50"
                >
                  Create
                </button>
                <button
                  onClick={() => setIsCreating(false)}
                  className="px-3 py-1 bg-base-200 rounded text-sm"
                >
                  Cancel
                </button>
              </div>
            </div>
          ) : (
            <button
              onClick={() => setIsCreating(true)}
              className="w-full flex items-center gap-2 px-3 py-2 hover:bg-base-200 text-left text-sm border-b border-base-300"
            >
              <LuPlus className="w-4 h-4" />
              <span>New question...</span>
            </button>
          )}

          {/* Reader questions */}
          {readerQuestions.length > 0 && (
            <div className="py-1">
              <div className="px-3 py-1 text-xs text-base-content/50 uppercase">My Questions</div>
              {readerQuestions.map((q) => (
                <button
                  key={q.id}
                  onClick={() => handleSelect(q.id)}
                  className={clsx(
                    'w-full flex items-center gap-2 px-3 py-2 hover:bg-base-200 text-left text-sm',
                    q.id === currentQuestionId && 'bg-primary/10'
                  )}
                >
                  <span className="truncate">{q.text}</span>
                </button>
              ))}
            </div>
          )}

          {/* SiYuan questions */}
          {siyuanQuestions.length > 0 && (
            <div className="py-1 border-t border-base-300">
              <div className="px-3 py-1 text-xs text-base-content/50 uppercase flex items-center gap-1">
                <LuLink className="w-3 h-3" />
                From SiYuan
              </div>
              {siyuanQuestions.map((q) => (
                <button
                  key={q.id}
                  onClick={() => handleSelect(q.id)}
                  className={clsx(
                    'w-full flex items-center gap-2 px-3 py-2 hover:bg-base-200 text-left text-sm',
                    q.id === currentQuestionId && 'bg-primary/10'
                  )}
                >
                  <span className="truncate">{q.text}</span>
                </button>
              ))}
            </div>
          )}

          {/* Empty state */}
          {questions.length === 0 && !isCreating && (
            <div className="px-3 py-4 text-center text-sm text-base-content/50">
              No questions yet. Create one to start exploring.
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default QuestionSelector;
```

**Step 4: Run test to verify it passes**

```bash
cd .worktrees/ies-reader/ies/reader
pnpm test src/__tests__/components/QuestionSelector.test.tsx
```

Expected: PASS

**Step 5: Commit**

```bash
git add src/app/reader/components/flowpanel/QuestionSelector.tsx src/__tests__/components/QuestionSelector.test.tsx
git commit -m "feat(flow): add QuestionSelector component for question-driven exploration"
```

---

## Task 4: Create FlowPage Standalone Wrapper

**Files:**
- Create: `src/app/flow/page.tsx`
- Create: `src/app/flow/layout.tsx`

**Step 1: Create the layout**

```typescript
// src/app/flow/layout.tsx
import React from 'react';

export default function FlowLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen bg-base-100">
      {children}
    </div>
  );
}
```

**Step 2: Create the page**

```typescript
// src/app/flow/page.tsx
'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import clsx from 'clsx';
import { LuArrowLeft, LuMessageCircle, LuCompass, LuHelpCircle } from 'react-icons/lu';

import { useFlowModeStore } from '@/store/flowModeStore';
import QuestionSelector from '@/app/reader/components/flowpanel/QuestionSelector';
import EntitySection from '@/app/reader/components/flowpanel/EntitySection';
import EvidenceSection from '@/app/reader/components/flowpanel/EvidenceSection';
import JourneyBreadcrumb from '@/app/reader/components/flowpanel/JourneyBreadcrumb';

type FlowTab = 'questions' | 'explore' | 'chat';

export default function FlowPage() {
  const router = useRouter();
  const [activeTab, setActiveTab] = useState<FlowTab>('explore');

  const {
    questions,
    currentQuestionId,
    currentEntity,
    evidence,
    isLoadingEntity,
    isLoadingEvidence,
    isLoadingQuestions,
    addQuestion,
    setCurrentQuestionId,
  } = useFlowModeStore();

  const handleBack = () => {
    router.back();
  };

  const handleCreateQuestion = (text: string) => {
    const newQuestion = {
      id: `q-${Date.now()}`,
      text,
      source: 'reader' as const,
      status: 'active' as const,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    };
    addQuestion(newQuestion);
    setCurrentQuestionId(newQuestion.id);
  };

  return (
    <div className="flex flex-col h-screen bg-base-100">
      {/* Header */}
      <header className="flex items-center justify-between px-4 py-3 border-b border-base-300 bg-base-100/80 backdrop-blur-sm">
        <button onClick={handleBack} className="p-2 -ml-2 hover:bg-base-200 rounded-lg">
          <LuArrowLeft className="w-5 h-5" />
        </button>
        <h1 className="font-semibold">Flow</h1>
        <div className="w-9" /> {/* Spacer for centering */}
      </header>

      {/* Question Selector */}
      <div className="px-4 py-3 border-b border-base-300">
        <QuestionSelector
          questions={questions}
          currentQuestionId={currentQuestionId}
          onSelect={setCurrentQuestionId}
          onCreate={handleCreateQuestion}
          isLoading={isLoadingQuestions}
        />
      </div>

      {/* Journey Breadcrumb */}
      <div className="px-4 py-2 border-b border-base-300">
        <JourneyBreadcrumb />
      </div>

      {/* Tab Content */}
      <div className="flex-1 overflow-y-auto px-4 py-4">
        {activeTab === 'questions' && (
          <QuestionsTab />
        )}

        {activeTab === 'explore' && (
          <div className="space-y-4">
            {isLoadingEntity ? (
              <div className="flex items-center justify-center py-12">
                <span className="loading loading-spinner loading-md text-primary" />
              </div>
            ) : currentEntity ? (
              <>
                <EntitySection entity={currentEntity} />
                <EvidenceSection evidence={evidence} isLoading={isLoadingEvidence} />
              </>
            ) : (
              <div className="text-center py-12 text-base-content/50">
                <LuCompass className="w-12 h-12 mx-auto mb-3 opacity-50" />
                <p>Select a question to start exploring</p>
              </div>
            )}
          </div>
        )}

        {activeTab === 'chat' && (
          <ChatTab />
        )}
      </div>

      {/* Bottom Tab Bar */}
      <nav className="flex border-t border-base-300 bg-base-100">
        <TabButton
          icon={<LuHelpCircle className="w-5 h-5" />}
          label="Questions"
          isActive={activeTab === 'questions'}
          onClick={() => setActiveTab('questions')}
        />
        <TabButton
          icon={<LuCompass className="w-5 h-5" />}
          label="Explore"
          isActive={activeTab === 'explore'}
          onClick={() => setActiveTab('explore')}
        />
        <TabButton
          icon={<LuMessageCircle className="w-5 h-5" />}
          label="Chat"
          isActive={activeTab === 'chat'}
          onClick={() => setActiveTab('chat')}
        />
      </nav>
    </div>
  );
}

// Tab Button Component
function TabButton({
  icon,
  label,
  isActive,
  onClick,
}: {
  icon: React.ReactNode;
  label: string;
  isActive: boolean;
  onClick: () => void;
}) {
  return (
    <button
      onClick={onClick}
      className={clsx(
        'flex-1 flex flex-col items-center gap-1 py-3 transition-colors',
        isActive ? 'text-primary' : 'text-base-content/50 hover:text-base-content'
      )}
    >
      {icon}
      <span className="text-xs">{label}</span>
    </button>
  );
}

// Questions Tab (placeholder)
function QuestionsTab() {
  const { questions, currentQuestionId, setCurrentQuestionId } = useFlowModeStore();

  return (
    <div className="space-y-4">
      <h2 className="text-lg font-semibold">My Questions</h2>
      {questions.length === 0 ? (
        <p className="text-base-content/50 text-sm">
          No questions yet. Use the selector above to create one.
        </p>
      ) : (
        <div className="space-y-2">
          {questions.map((q) => (
            <button
              key={q.id}
              onClick={() => setCurrentQuestionId(q.id)}
              className={clsx(
                'w-full text-left p-3 rounded-lg border transition-colors',
                q.id === currentQuestionId
                  ? 'border-primary bg-primary/10'
                  : 'border-base-300 hover:bg-base-200'
              )}
            >
              <p className="font-medium">{q.text}</p>
              <p className="text-xs text-base-content/50 mt-1">
                {q.source === 'siyuan' ? '🔗 From SiYuan' : '📝 Created here'}
              </p>
            </button>
          ))}
        </div>
      )}
    </div>
  );
}

// Chat Tab (placeholder)
function ChatTab() {
  return (
    <div className="flex flex-col h-full">
      <div className="flex-1 flex items-center justify-center text-base-content/50">
        <div className="text-center">
          <LuMessageCircle className="w-12 h-12 mx-auto mb-3 opacity-50" />
          <p>AI thinking partner coming soon</p>
        </div>
      </div>
      <div className="mt-auto">
        <input
          type="text"
          placeholder="Ask the AI..."
          className="w-full px-4 py-3 bg-base-200 rounded-lg"
          disabled
        />
      </div>
    </div>
  );
}
```

**Step 3: Verify it builds**

```bash
cd .worktrees/ies-reader/ies/reader
pnpm build
```

Expected: Build succeeds

**Step 4: Commit**

```bash
git add src/app/flow/
git commit -m "feat(flow): add standalone FlowPage with tab navigation for mobile"
```

---

## Task 5: Integrate QuestionSelector into FlowPanel

**Files:**
- Modify: `src/app/reader/components/flowpanel/FlowPanel.tsx`
- Modify: `src/app/reader/components/flowpanel/index.ts`

**Step 1: Update FlowPanel imports and add QuestionSelector**

In `src/app/reader/components/flowpanel/FlowPanel.tsx`, add import:

```typescript
import QuestionSelector from './QuestionSelector';
```

**Step 2: Add question state to FlowPanel**

Add to the destructured store values (~line 35):

```typescript
const {
  // ... existing values
  questions,
  currentQuestionId,
  isLoadingQuestions,
  addQuestion,
  setCurrentQuestionId,
} = useFlowModeStore();
```

**Step 3: Add QuestionSelector to the panel layout**

After the FlowPanelHeader and before EntityTypeFilter (~line 160):

```typescript
{/* Question Selector - new in Flow v2 */}
<div className='px-4 py-3 border-b border-base-300/50'>
  <QuestionSelector
    questions={questions}
    currentQuestionId={currentQuestionId}
    onSelect={setCurrentQuestionId}
    onCreate={(text) => {
      const newQuestion = {
        id: `q-${Date.now()}`,
        text,
        source: 'reader' as const,
        status: 'active' as const,
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
      };
      addQuestion(newQuestion);
      setCurrentQuestionId(newQuestion.id);
    }}
    isLoading={isLoadingQuestions}
  />
</div>
```

**Step 4: Update index.ts exports**

```typescript
// src/app/reader/components/flowpanel/index.ts
export { default as FlowPanel } from './FlowPanel';
export { default as QuestionSelector } from './QuestionSelector';
// ... other exports
```

**Step 5: Verify it builds and renders**

```bash
cd .worktrees/ies-reader/ies/reader
pnpm build && pnpm dev
```

Open in browser, verify QuestionSelector appears in FlowPanel.

**Step 6: Commit**

```bash
git add src/app/reader/components/flowpanel/FlowPanel.tsx src/app/reader/components/flowpanel/index.ts
git commit -m "feat(flow): integrate QuestionSelector into FlowPanel"
```

---

## Summary

**Phase 1 delivers:**
1. ✅ `useFlowLayout` hook — Responsive mode detection
2. ✅ Question state in store — CRUD for FlowQuestion
3. ✅ `QuestionSelector` component — Dropdown with create/select
4. ✅ `FlowPage` standalone — Mobile full-screen with tabs
5. ✅ FlowPanel integration — QuestionSelector in desktop panel

**Total: 5 tasks, ~15 commits**

**Next Phase:** Question API endpoints and SiYuan sync
