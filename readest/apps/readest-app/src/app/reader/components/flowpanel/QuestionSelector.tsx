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
