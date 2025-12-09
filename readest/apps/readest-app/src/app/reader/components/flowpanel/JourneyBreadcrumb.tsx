import React from 'react';
import { useFlowModeStore } from '@/store/flowModeStore';

/**
 * Simple journey breadcrumb component showing current exploration path
 * Placeholder for Phase 1 - will be enhanced later with full journey tracking
 */
export default function JourneyBreadcrumb() {
  const { currentJourney } = useFlowModeStore();

  if (!currentJourney || !currentJourney.steps || currentJourney.steps.length === 0) {
    return null;
  }

  return (
    <div className="flex items-center gap-2 text-sm text-base-content/60">
      {currentJourney.steps.slice(-3).map((step, index, arr) => (
        <React.Fragment key={step.entityId}>
          <span className="truncate max-w-[120px]">{step.entityName}</span>
          {index < arr.length - 1 && <span>→</span>}
        </React.Fragment>
      ))}
    </div>
  );
}
