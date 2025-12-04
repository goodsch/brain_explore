/**
 * Entity Type Filter Controls
 *
 * UI component for toggling which entity types are visible in the overlay.
 * Provides master toggle for overlay enable/disable and individual type toggles.
 */

import React from 'react';
import { useFlowModeStore } from '@/store/flowModeStore';

interface EntityTypeConfig {
  type: string;
  label: string;
  colorClass: string;
  bgColor: string;
}

const ENTITY_TYPES: EntityTypeConfig[] = [
  { type: 'Concept', label: 'Concepts', colorClass: 'text-blue-700', bgColor: 'bg-blue-100' },
  { type: 'Person', label: 'People', colorClass: 'text-green-700', bgColor: 'bg-green-100' },
  { type: 'Theory', label: 'Theories', colorClass: 'text-purple-700', bgColor: 'bg-purple-100' },
  { type: 'Framework', label: 'Frameworks', colorClass: 'text-orange-700', bgColor: 'bg-orange-100' },
  { type: 'Assessment', label: 'Assessments', colorClass: 'text-red-700', bgColor: 'bg-red-100' },
];

export const EntityTypeFilter: React.FC = () => {
  const { entityOverlay, toggleEntityType, setEntityOverlayEnabled } = useFlowModeStore();

  const handleMasterToggle = () => {
    setEntityOverlayEnabled(!entityOverlay.enabled);
  };

  const handleTypeToggle = (type: string) => {
    // Only allow toggling if overlay is enabled
    if (!entityOverlay.enabled) return;
    toggleEntityType(type);
  };

  const isTypeVisible = (type: string): boolean => {
    return entityOverlay.visibleTypes.includes(type);
  };

  return (
    <div className="entity-type-filter p-4 bg-base-100 rounded-lg shadow-sm">
      {/* Header with master toggle */}
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-sm font-semibold text-base-content">Entity Overlay</h3>
        <div className="form-control">
          <label className="label cursor-pointer gap-2">
            <span className="label-text text-xs">
              {entityOverlay.enabled ? 'Enabled' : 'Disabled'}
            </span>
            <input
              type="checkbox"
              className="toggle toggle-primary toggle-sm"
              checked={entityOverlay.enabled}
              onChange={handleMasterToggle}
            />
          </label>
        </div>
      </div>

      {/* Type filters */}
      <div className="space-y-2">
        <div className="text-xs font-medium text-base-content/60 mb-2">Visible Types:</div>
        {ENTITY_TYPES.map((config) => {
          const isVisible = isTypeVisible(config.type);
          const isDisabled = !entityOverlay.enabled;

          return (
            <div
              key={config.type}
              className={`flex items-center justify-between p-2 rounded-md transition-colors ${
                isDisabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer hover:bg-base-200'
              } ${isVisible && !isDisabled ? config.bgColor : ''}`}
              onClick={() => handleTypeToggle(config.type)}
            >
              <div className="flex items-center gap-2">
                {/* Color indicator */}
                <div
                  className={`w-3 h-3 rounded-full ${
                    isVisible && !isDisabled
                      ? config.colorClass.replace('text-', 'bg-')
                      : 'bg-base-300'
                  }`}
                />
                {/* Type label */}
                <span
                  className={`text-sm ${
                    isVisible && !isDisabled ? config.colorClass : 'text-base-content/60'
                  }`}
                >
                  {config.label}
                </span>
              </div>

              {/* Checkbox */}
              <input
                type="checkbox"
                className="checkbox checkbox-sm"
                checked={isVisible}
                disabled={isDisabled}
                onChange={(e) => {
                  e.stopPropagation();
                  handleTypeToggle(config.type);
                }}
                onClick={(e) => e.stopPropagation()}
              />
            </div>
          );
        })}
      </div>

      {/* Loading/Error states */}
      {entityOverlay.loading && (
        <div className="mt-4 flex items-center justify-center gap-2 text-xs text-base-content/60">
          <span className="loading loading-spinner loading-xs"></span>
          <span>Loading entities...</span>
        </div>
      )}

      {entityOverlay.error && (
        <div className="mt-4 alert alert-error alert-sm">
          <span className="text-xs">{entityOverlay.error}</span>
        </div>
      )}

      {/* Entity count or "not found" message */}
      {entityOverlay.enabled && !entityOverlay.loading && !entityOverlay.error && (
        <div className="mt-4 text-xs text-center">
          {entityOverlay.entities.length > 0 ? (
            <span className="text-base-content/60">
              {entityOverlay.entities.length} entities loaded
            </span>
          ) : (
            <span className="text-warning">
              Book not in knowledge graph
            </span>
          )}
        </div>
      )}
    </div>
  );
};
