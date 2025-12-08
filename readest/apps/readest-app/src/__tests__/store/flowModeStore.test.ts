// src/__tests__/store/flowModeStore.test.ts
import { describe, it, expect, beforeEach } from 'vitest';
import { act } from '@testing-library/react';
import { useFlowModeStore } from '../../store/flowModeStore';

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
