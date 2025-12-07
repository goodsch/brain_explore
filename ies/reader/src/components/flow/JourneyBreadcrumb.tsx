/**
 * JourneyBreadcrumb Component
 *
 * Displays the user's exploration path through the knowledge graph.
 * Makes the invisible journey visible and navigable.
 *
 * This addresses the UX gap where journeys were tracked but never shown.
 */

import { Route, ChevronRight, Clock } from 'lucide-react';
import { useFlowStore, type JourneyStep } from '../../store/flowStore';

export function JourneyBreadcrumb() {
  const { currentJourney, setCurrentEntity } = useFlowStore();

  if (!currentJourney || currentJourney.path.length === 0) {
    return null;
  }

  const handleStepClick = (step: JourneyStep) => {
    // Navigate back to this entity
    setCurrentEntity({
      id: step.entityId,
      name: step.entityName,
      type: 'Concept', // Default type
      summary: step.sourcePassage || 'Revisiting previous exploration point',
    });
  };

  const formatDwellTime = (seconds: number): string => {
    if (seconds < 60) return `${seconds}s`;
    const minutes = Math.floor(seconds / 60);
    const remaining = seconds % 60;
    return remaining > 0 ? `${minutes}m ${remaining}s` : `${minutes}m`;
  };

  // Show only the last 5 steps to avoid clutter
  const recentPath = currentJourney.path.slice(-5);
  const hasMoreSteps = currentJourney.path.length > 5;

  return (
    <section className="flow-section flow-journey">
      <h4 className="flow-section-title">
        <Route size={14} />
        Your exploration path
      </h4>

      <div className="journey-breadcrumb-container">
        <div className="journey-breadcrumb-path">
          {hasMoreSteps && (
            <>
              <span className="journey-overflow">
                +{currentJourney.path.length - 5} more
              </span>
              <ChevronRight size={12} className="journey-chevron" />
            </>
          )}

          {recentPath.map((step, index) => (
            <span key={`${step.entityId}-${index}`} className="journey-step-wrapper">
              {index > 0 && (
                <ChevronRight size={12} className="journey-chevron" />
              )}
              <button
                className="journey-step"
                onClick={() => handleStepClick(step)}
                title={step.sourcePassage || step.entityName}
              >
                <span className="journey-step-name">{step.entityName}</span>
                {step.dwellTimeSeconds > 0 && (
                  <span className="journey-step-time">
                    <Clock size={10} />
                    {formatDwellTime(step.dwellTimeSeconds)}
                  </span>
                )}
              </button>
            </span>
          ))}
        </div>
      </div>
    </section>
  );
}
