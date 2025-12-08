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

  it('updates a question', () => {
    const question = {
      id: 'q1',
      text: 'Original question',
      source: 'reader' as const,
      status: 'active' as const,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    };

    act(() => {
      useFlowModeStore.getState().addQuestion(question);
      useFlowModeStore.getState().updateQuestion('q1', {
        text: 'Updated question',
        status: 'resolved' as const,
      });
    });

    const updated = useFlowModeStore.getState().questions[0];
    expect(updated.text).toBe('Updated question');
    expect(updated.status).toBe('resolved');
    expect(updated.id).toBe('q1');
    expect(updated.source).toBe('reader');
  });

  it('sets questions array', () => {
    const questions = [
      {
        id: 'q1',
        text: 'Question 1',
        source: 'reader' as const,
        status: 'active' as const,
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
      },
      {
        id: 'q2',
        text: 'Question 2',
        source: 'siyuan' as const,
        status: 'active' as const,
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
      },
    ];

    act(() => {
      useFlowModeStore.getState().setQuestions(questions);
    });

    expect(useFlowModeStore.getState().questions).toHaveLength(2);
    expect(useFlowModeStore.getState().questions[0].text).toBe('Question 1');
    expect(useFlowModeStore.getState().questions[1].text).toBe('Question 2');
  });

  it('sets loading state', () => {
    act(() => {
      useFlowModeStore.getState().setIsLoadingQuestions(true);
    });

    expect(useFlowModeStore.getState().isLoadingQuestions).toBe(true);

    act(() => {
      useFlowModeStore.getState().setIsLoadingQuestions(false);
    });

    expect(useFlowModeStore.getState().isLoadingQuestions).toBe(false);
  });

  it('clears currentQuestionId when removed question was current', () => {
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
      useFlowModeStore.getState().setCurrentQuestionId('q1');
      useFlowModeStore.getState().removeQuestion('q1');
    });

    expect(useFlowModeStore.getState().currentQuestionId).toBeNull();
  });
});
