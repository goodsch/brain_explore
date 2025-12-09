import { useState, useRef, useEffect } from 'react';
import clsx from 'clsx';
import type { FlowQuestion } from '../../store/flowStore';
import './question-selector.css';

interface QuestionSelectorProps {
  questions: FlowQuestion[];
  currentQuestionId: string | null;
  onSelect: (questionId: string) => void;
  onCreate: (text: string) => void;
  isLoading: boolean;
}

export function QuestionSelector({
  questions,
  currentQuestionId,
  onSelect,
  onCreate,
  isLoading,
}: QuestionSelectorProps) {
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
    <div ref={dropdownRef} className="question-selector" onKeyDown={handleKeyDown}>
      {/* Collapsed state - shows current question */}
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        disabled={isLoading}
        className={clsx(
          'question-selector__trigger',
          isLoading && 'question-selector__trigger--loading'
        )}
      >
        <span className="question-selector__current">
          <span className="question-selector__icon">🎯</span>
          <span className={clsx(!currentQuestion && 'question-selector__placeholder')}>
            {currentQuestion?.text || 'Select a question...'}
          </span>
        </span>
        <span className={clsx('question-selector__chevron', isExpanded && 'question-selector__chevron--open')}>
          ▾
        </span>
      </button>

      {/* Expanded dropdown */}
      {isExpanded && (
        <div className="question-selector__dropdown">
          {/* Create new question */}
          {isCreating ? (
            <div className="question-selector__create-form">
              <input
                ref={inputRef}
                type="text"
                value={newQuestionText}
                onChange={(e) => setNewQuestionText(e.target.value)}
                placeholder="What do you want to explore?"
                className="question-selector__input"
              />
              <div className="question-selector__create-actions">
                <button
                  onClick={handleCreate}
                  disabled={!newQuestionText.trim()}
                  className="question-selector__btn question-selector__btn--primary"
                >
                  Create
                </button>
                <button
                  onClick={() => setIsCreating(false)}
                  className="question-selector__btn"
                >
                  Cancel
                </button>
              </div>
            </div>
          ) : (
            <button
              onClick={() => setIsCreating(true)}
              className="question-selector__new-btn"
            >
              <span>+</span>
              <span>New question...</span>
            </button>
          )}

          {/* Reader questions */}
          {readerQuestions.length > 0 && (
            <div className="question-selector__section">
              <div className="question-selector__section-header">My Questions</div>
              {readerQuestions.map((q) => (
                <button
                  key={q.id}
                  onClick={() => handleSelect(q.id)}
                  className={clsx(
                    'question-selector__option',
                    q.id === currentQuestionId && 'question-selector__option--selected'
                  )}
                >
                  {q.text}
                </button>
              ))}
            </div>
          )}

          {/* SiYuan questions */}
          {siyuanQuestions.length > 0 && (
            <div className="question-selector__section question-selector__section--bordered">
              <div className="question-selector__section-header">
                🔗 From SiYuan
              </div>
              {siyuanQuestions.map((q) => (
                <button
                  key={q.id}
                  onClick={() => handleSelect(q.id)}
                  className={clsx(
                    'question-selector__option',
                    q.id === currentQuestionId && 'question-selector__option--selected'
                  )}
                >
                  {q.text}
                </button>
              ))}
            </div>
          )}

          {/* Empty state */}
          {questions.length === 0 && !isCreating && (
            <div className="question-selector__empty">
              No questions yet. Create one to start exploring.
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default QuestionSelector;
