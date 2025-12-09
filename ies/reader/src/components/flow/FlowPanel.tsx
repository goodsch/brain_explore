import { useFlowStore } from '../../store/flowStore';
import { QuestionSelector } from './QuestionSelector';
import { useFlowLayout } from '../../hooks/useFlowLayout';
import { useQuestionSync } from '../../hooks/useQuestionSync';
import './flow-panel.css';

export function FlowPanel() {
  const {
    isFlowPanelOpen,
    questions,
    currentQuestionId,
    isLoadingQuestions,
    setCurrentQuestionId,
    currentEntity
  } = useFlowStore();

  const { mode, isMobile } = useFlowLayout();
  const { createQuestion, error } = useQuestionSync();

  // Don't render if closed or if on mobile (use standalone FlowPage instead)
  if (!isFlowPanelOpen || (isMobile && mode === 'standalone')) return null;

  const handleCreateQuestion = async (text: string) => {
    await createQuestion(text);
  };

  return (
    <div className="flow-panel">
      <div className="flow-panel__header">
        <h2 className="flow-panel__title">Flow</h2>
      </div>

      {error && (
        <div className="flow-panel__error">
          {error}
        </div>
      )}

      <div className="flow-panel__question-selector">
        <QuestionSelector
          questions={questions}
          currentQuestionId={currentQuestionId}
          onSelect={setCurrentQuestionId}
          onCreate={handleCreateQuestion}
          isLoading={isLoadingQuestions}
        />
      </div>

      <div className="flow-panel__content">
        {currentEntity ? (
          <div className="flow-panel__entity">
            <h3 className="flow-panel__entity-name">{currentEntity.name}</h3>
            {/* Entity details will be expanded in future phases */}
          </div>
        ) : (
          <div className="flow-panel__empty">
            <p>Select a question to start exploring, or select text in the book to look up entities.</p>
          </div>
        )}
      </div>
    </div>
  );
}
