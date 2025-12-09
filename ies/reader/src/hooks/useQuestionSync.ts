/**
 * Hook for syncing questions between flowStore and backend API.
 *
 * Handles:
 * - Loading questions from backend on mount
 * - Creating questions via API
 * - Ensuring a default context exists for questions
 */

import { useEffect, useCallback, useRef, useState } from 'react';
import { useFlowStore, type FlowQuestion } from '../store/flowStore';
import { questionApi, type Question, type QuestionCreate } from '../services/questionApi';
import { contextApi, type Context } from '../services/contextApi';

/**
 * Convert backend Question to FlowQuestion format.
 */
function toFlowQuestion(q: Question): FlowQuestion {
  return {
    id: q.id,
    text: q.text,
    source: q.source === 'dialogue' ? 'reader' : q.source as FlowQuestion['source'],
    status: q.status === 'open' ? 'active' : q.status === 'answered' ? 'resolved' : 'paused',
    siyuanId: q.siyuan_block_id,
    parentId: q.parent_question_id,
    createdAt: q.created_at,
    updatedAt: q.updated_at,
  };
}

export interface UseQuestionSyncResult {
  /** Current context for questions */
  context: Context | null;
  /** Whether initial load is in progress */
  isLoading: boolean;
  /** Error message if sync failed */
  error: string | null;
  /** Create a question and sync to backend */
  createQuestion: (text: string) => Promise<FlowQuestion | null>;
  /** Reload questions from backend */
  reload: () => Promise<void>;
}

export function useQuestionSync(): UseQuestionSyncResult {
  const {
    setQuestions,
    setIsLoadingQuestions,
    addQuestion,
    setCurrentQuestionId,
  } = useFlowStore();

  const [context, setContext] = useState<Context | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const initRef = useRef(false);

  /**
   * Load context and questions from backend.
   */
  const loadQuestions = useCallback(async () => {
    try {
      setIsLoadingQuestions(true);
      setError(null);

      // Get or create default context
      const ctx = await contextApi.getOrCreateDefault('Reading Session');
      setContext(ctx);

      // Load questions for this context
      const questions = await questionApi.list({ context_id: ctx.id });
      const flowQuestions = questions.map(toFlowQuestion);
      setQuestions(flowQuestions);

    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to load questions';
      setError(message);
      console.error('[useQuestionSync] Load error:', err);
    } finally {
      setIsLoadingQuestions(false);
      setIsLoading(false);
    }
  }, [setQuestions, setIsLoadingQuestions]);

  /**
   * Create a new question via API and add to store.
   */
  const createQuestion = useCallback(async (text: string): Promise<FlowQuestion | null> => {
    if (!context) {
      setError('No context available');
      return null;
    }

    try {
      const data: QuestionCreate = {
        context_id: context.id,
        text,
        source: 'reader',
      };

      const created = await questionApi.create(data);
      const flowQuestion = toFlowQuestion(created);

      addQuestion(flowQuestion);
      setCurrentQuestionId(flowQuestion.id);

      return flowQuestion;
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to create question';
      setError(message);
      console.error('[useQuestionSync] Create error:', err);
      return null;
    }
  }, [context, addQuestion, setCurrentQuestionId]);

  // Initialize on mount
  useEffect(() => {
    if (!initRef.current) {
      initRef.current = true;
      loadQuestions();
    }
  }, [loadQuestions]);

  return {
    context,
    isLoading,
    error,
    createQuestion,
    reload: loadQuestions,
  };
}
