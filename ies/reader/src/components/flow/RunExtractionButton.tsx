/**
 * Run Extraction Button - triggers context-aware entity extraction.
 *
 * Appears in FlowPanel when a context is active. Calls backend
 * POST /extraction/run with current context and optional question.
 */

import { Sparkles, Loader2, AlertCircle, CheckCircle } from 'lucide-react';
import { useFlowStore } from '../../store/flowStore';
import './run-extraction-button.css';

interface RunExtractionButtonProps {
  contextId: string;
  questionId?: string;
  disabled?: boolean;
}

export function RunExtractionButton({
  contextId,
  questionId,
  disabled = false,
}: RunExtractionButtonProps) {
  const {
    isExtracting,
    extractionResult,
    extractionError,
    runExtraction,
    clearExtraction,
  } = useFlowStore();

  const handleClick = async () => {
    if (isExtracting || disabled) return;
    await runExtraction(contextId, questionId);
  };

  const handleDismissResult = () => {
    clearExtraction();
  };

  // Show result summary if extraction completed
  if (extractionResult && !isExtracting) {
    const { concepts_found, relations_found, subquestions_generated } = extractionResult;
    const totalFound = concepts_found.length + relations_found.length;

    return (
      <div className="extraction-result">
        <div className="extraction-result-header">
          <CheckCircle size={16} className="extraction-success-icon" />
          <span>Extraction Complete</span>
          <button
            className="extraction-dismiss"
            onClick={handleDismissResult}
            aria-label="Dismiss"
          >
            &times;
          </button>
        </div>
        <div className="extraction-result-stats">
          <div className="stat">
            <span className="stat-value">{concepts_found.length}</span>
            <span className="stat-label">concepts</span>
          </div>
          <div className="stat">
            <span className="stat-value">{relations_found.length}</span>
            <span className="stat-label">relations</span>
          </div>
          {subquestions_generated.length > 0 && (
            <div className="stat">
              <span className="stat-value">{subquestions_generated.length}</span>
              <span className="stat-label">questions</span>
            </div>
          )}
        </div>
        {totalFound === 0 && (
          <p className="extraction-empty">No new entities found in sources.</p>
        )}
      </div>
    );
  }

  // Show error if extraction failed
  if (extractionError) {
    return (
      <div className="extraction-error">
        <AlertCircle size={16} />
        <span>{extractionError}</span>
        <button
          className="extraction-retry"
          onClick={handleClick}
        >
          Retry
        </button>
      </div>
    );
  }

  // Default: show run button
  return (
    <button
      className={`run-extraction-btn ${isExtracting ? 'extracting' : ''}`}
      onClick={handleClick}
      disabled={disabled || isExtracting}
      title={questionId ? 'Extract entities related to this question' : 'Extract entities from context sources'}
    >
      {isExtracting ? (
        <>
          <Loader2 size={16} className="spin" />
          <span>Extracting...</span>
        </>
      ) : (
        <>
          <Sparkles size={16} />
          <span>Run Extraction</span>
        </>
      )}
    </button>
  );
}
