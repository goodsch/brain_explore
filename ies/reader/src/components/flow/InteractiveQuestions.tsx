/**
 * InteractiveQuestions Component
 *
 * Displays thinking partner questions with expandable response input.
 * Enables active cognitive guidance rather than passive question display.
 *
 * Key UX features:
 * - Click question to expand and reveal response input
 * - Cmd/Ctrl+Enter to submit response
 * - Bookmark questions for later reflection
 * - Related entities displayed as chips
 */

import { useState, useRef, useEffect } from 'react';
import { HelpCircle, RefreshCw, ChevronDown, ChevronUp, Send, Bookmark } from 'lucide-react';
import { useFlowStore, type ThinkingPartnerQuestion } from '../../store/flowStore';

export function InteractiveQuestions() {
  const {
    thinkingPartnerQuestions,
    isLoadingQuestions,
    currentEntity,
    addJourneyStep,
  } = useFlowStore();

  const [expandedIndex, setExpandedIndex] = useState<number | null>(null);
  const [responses, setResponses] = useState<Record<number, string>>({});
  const [submittedResponses, setSubmittedResponses] = useState<Record<number, string>>({});
  const textareaRefs = useRef<Record<number, HTMLTextAreaElement | null>>({});

  // Focus textarea when expanding a question
  useEffect(() => {
    if (expandedIndex !== null && textareaRefs.current[expandedIndex]) {
      setTimeout(() => {
        textareaRefs.current[expandedIndex]?.focus();
      }, 100);
    }
  }, [expandedIndex]);

  const getQuestionCardClass = (type: ThinkingPartnerQuestion['type']): string => {
    return `flow-question-card type-${type}`;
  };

  const getQuestionTypeLabel = (type: ThinkingPartnerQuestion['type']): string => {
    const labels: Record<string, string> = {
      clarifying: 'Clarifying',
      connecting: 'Connecting',
      challenging: 'Challenging',
    };
    return labels[type] || type;
  };

  const handleQuestionClick = (index: number) => {
    const isExpanding = expandedIndex !== index;
    setExpandedIndex(isExpanding ? index : null);
  };

  const handleResponseChange = (index: number, value: string) => {
    setResponses((prev) => ({ ...prev, [index]: value }));
  };

  const handleSubmitResponse = (question: ThinkingPartnerQuestion, index: number) => {
    const response = responses[index]?.trim();
    if (!response) return;

    // Track the question-response exchange in the journey
    if (currentEntity) {
      addJourneyStep(
        currentEntity.id,
        currentEntity.name,
        `Q: ${question.text}\nA: ${response}`
      );
    }

    // Mark as submitted and clear input
    setSubmittedResponses((prev) => ({ ...prev, [index]: response }));
    setResponses((prev) => ({ ...prev, [index]: '' }));
  };

  const handleBookmarkQuestion = (question: ThinkingPartnerQuestion) => {
    // Track as a journey step (bookmarked for later)
    if (currentEntity) {
      addJourneyStep(
        currentEntity.id,
        currentEntity.name,
        `[Bookmarked] ${question.text}`
      );
    }
    console.log('Question bookmarked:', question.text);
  };

  const handleKeyDown = (
    e: React.KeyboardEvent,
    question: ThinkingPartnerQuestion,
    index: number
  ) => {
    // Submit on Cmd/Ctrl+Enter
    if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) {
      e.preventDefault();
      handleSubmitResponse(question, index);
    }
  };

  const handleRefreshQuestions = () => {
    // TODO: Fetch new questions from the backend
    console.log('Refreshing thinking partner questions');
  };

  if (thinkingPartnerQuestions.length === 0 && !isLoadingQuestions) {
    return (
      <section className="flow-section">
        <h4 className="flow-section-title">
          <HelpCircle size={14} />
          Thinking Partner
        </h4>
        <p className="flow-empty-hint">Select text to explore related concepts</p>
      </section>
    );
  }

  return (
    <section className="flow-section">
      <div className="flow-questions-header">
        <h4 className="flow-section-title" style={{ margin: 0 }}>
          <HelpCircle size={14} />
          Thinking Partner
        </h4>
        <button
          className="flow-questions-refresh"
          onClick={handleRefreshQuestions}
          disabled={isLoadingQuestions}
          title="Get new questions"
        >
          <RefreshCw size={14} className={isLoadingQuestions ? 'flow-loading-spinner' : ''} />
        </button>
      </div>

      {isLoadingQuestions ? (
        <div className="flow-loading flow-loading-inline">
          <span className="flow-loading-spinner" />
          <span>Generating questions...</span>
        </div>
      ) : (
        <div className="flow-questions">
          {thinkingPartnerQuestions.map((question, index) => (
            <div key={index} className={getQuestionCardClass(question.type)}>
              <button
                className="flow-question-header"
                onClick={() => handleQuestionClick(index)}
              >
                <div className="flow-question-content">
                  <span className={`flow-question-type flow-question-${question.type}`}>
                    {getQuestionTypeLabel(question.type)}
                  </span>
                  <p className="flow-question-text">{question.text}</p>
                </div>
                <span className="flow-question-chevron">
                  {expandedIndex === index ? (
                    <ChevronUp size={16} />
                  ) : (
                    <ChevronDown size={16} />
                  )}
                </span>
              </button>

              {expandedIndex === index && (
                <div className="flow-question-expanded">
                  {/* Related entities */}
                  {question.relatedEntities && question.relatedEntities.length > 0 && (
                    <div className="flow-question-related">
                      <span className="flow-question-related-label">Related:</span>
                      <div className="flow-question-related-chips">
                        {question.relatedEntities.map((entity, i) => (
                          <span key={i} className="flow-question-related-chip">
                            {entity}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Response input or submitted response */}
                  {submittedResponses[index] ? (
                    <div className="flow-question-submitted">
                      <span className="flow-question-submitted-label">Your response:</span>
                      <p className="flow-question-submitted-text">
                        {submittedResponses[index]}
                      </p>
                    </div>
                  ) : (
                    <div className="flow-question-response-input">
                      <textarea
                        ref={(el) => {
                          textareaRefs.current[index] = el;
                        }}
                        className="flow-question-textarea"
                        placeholder="Type your thoughts here... (Cmd+Enter to save)"
                        rows={3}
                        value={responses[index] || ''}
                        onChange={(e) => handleResponseChange(index, e.target.value)}
                        onKeyDown={(e) => handleKeyDown(e, question, index)}
                      />
                      <div className="flow-question-input-footer">
                        <span className="flow-question-hint">
                          Press Cmd+Enter to save your response
                        </span>
                        <button
                          className="flow-question-submit"
                          onClick={() => handleSubmitResponse(question, index)}
                          disabled={!responses[index]?.trim()}
                        >
                          <Send size={14} />
                          Save
                        </button>
                      </div>
                    </div>
                  )}

                  {/* Bookmark button */}
                  <button
                    className="flow-question-bookmark"
                    onClick={() => handleBookmarkQuestion(question)}
                  >
                    <Bookmark size={14} />
                    Bookmark for later
                  </button>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </section>
  );
}
