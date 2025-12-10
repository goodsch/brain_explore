import React, { HTMLAttributes, useState, KeyboardEvent } from 'react';
import { clsx } from 'clsx';
import { ChevronDown, ChevronUp, ExternalLink, BookOpen } from 'lucide-react';
import { EntityBadge, EntityType } from './EntityBadge';
import './EntityCard.css';

export interface Entity {
  id: string;
  name: string;
  type: EntityType;
  description?: string;
  connectionCount?: number;
  sourceCount?: number;
  lastVisited?: Date;
}

export interface EntityCardProps
  extends Omit<HTMLAttributes<HTMLDivElement>, 'onClick'> {
  /** Entity data to display */
  entity: Entity;
  /** Whether the card is expanded to show full description */
  expanded?: boolean;
  /** Whether the card is currently selected */
  selected?: boolean;
  /** Compact mode (smaller padding, single line description) */
  compact?: boolean;
  /** Click handler for the entire card */
  onClick?: (entity: Entity) => void;
  /** Handler for "View Details" action */
  onViewDetails?: (entity: Entity) => void;
  /** Handler for "View Sources" action */
  onViewSources?: (entity: Entity) => void;
  /** Additional CSS class */
  className?: string;
}

/**
 * Format relative time (e.g., "2 hours ago", "3 days ago")
 */
const formatRelativeTime = (date: Date): string => {
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMins / 60);
  const diffDays = Math.floor(diffHours / 24);

  if (diffMins < 1) return 'Just now';
  if (diffMins < 60) return `${diffMins}m ago`;
  if (diffHours < 24) return `${diffHours}h ago`;
  if (diffDays < 7) return `${diffDays}d ago`;
  return date.toLocaleDateString();
};

/**
 * EntityCard - IES Design System v2
 *
 * Display entity information in a card format with expandable details.
 * Used in search results, related entities, entity lists.
 *
 * Features:
 * - Header with EntityBadge + Name
 * - Body with description preview (2-3 lines)
 * - Footer with connection count + timestamp
 * - Expandable to show full description
 * - Selected state with highlighted border
 *
 * Accessibility:
 * - Keyboard navigable (Tab, Enter/Space to click)
 * - role="article" for semantic structure
 * - aria-expanded for expand state
 * - Focus visible indicator
 */
export const EntityCard = ({
  entity,
  expanded: controlledExpanded,
  selected = false,
  compact = false,
  onClick,
  onViewDetails,
  onViewSources,
  className,
  ...props
}: EntityCardProps) => {
  // Internal expand state (can be overridden by controlled prop)
  const [internalExpanded, setInternalExpanded] = useState(false);
  const expanded = controlledExpanded ?? internalExpanded;

  const handleClick = () => {
    onClick?.(entity);
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLDivElement>) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      handleClick();
    }
  };

  const toggleExpand = (e: React.MouseEvent) => {
    e.stopPropagation();
    setInternalExpanded(!internalExpanded);
  };

  const handleViewDetails = (e: React.MouseEvent) => {
    e.stopPropagation();
    onViewDetails?.(entity);
  };

  const handleViewSources = (e: React.MouseEvent) => {
    e.stopPropagation();
    onViewSources?.(entity);
  };

  const hasDescription = entity.description && entity.description.length > 0;
  const isLongDescription = hasDescription && entity.description!.length > 150;
  const showExpandButton = isLongDescription && !compact;

  // Truncate description for preview
  const displayDescription =
    hasDescription && !expanded && !compact
      ? entity.description!.slice(0, 150) + (isLongDescription ? '...' : '')
      : entity.description;

  return (
    <div
      className={clsx(
        'ies-entity-card',
        {
          'ies-entity-card--expanded': expanded,
          'ies-entity-card--selected': selected,
          'ies-entity-card--compact': compact,
          'ies-entity-card--clickable': !!onClick,
        },
        className
      )}
      role="article"
      aria-expanded={showExpandButton ? expanded : undefined}
      tabIndex={onClick ? 0 : undefined}
      onClick={onClick ? handleClick : undefined}
      onKeyDown={onClick ? handleKeyDown : undefined}
      {...props}
    >
      {/* Header */}
      <div className="ies-entity-card__header">
        <EntityBadge entityType={entity.type} size={compact ? 'sm' : 'md'} />
        <h3 className="ies-entity-card__name">{entity.name}</h3>
        {showExpandButton && (
          <button
            type="button"
            className="ies-entity-card__expand-btn"
            onClick={toggleExpand}
            aria-label={expanded ? 'Collapse description' : 'Expand description'}
          >
            {expanded ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
          </button>
        )}
      </div>

      {/* Description */}
      {hasDescription && !compact && (
        <p className="ies-entity-card__description">{displayDescription}</p>
      )}

      {/* Compact description (single line) */}
      {hasDescription && compact && (
        <p className="ies-entity-card__description ies-entity-card__description--compact">
          {entity.description}
        </p>
      )}

      {/* Footer */}
      <div className="ies-entity-card__footer">
        <div className="ies-entity-card__meta">
          {entity.connectionCount !== undefined && entity.connectionCount > 0 && (
            <span className="ies-entity-card__stat">
              {entity.connectionCount} connection{entity.connectionCount !== 1 ? 's' : ''}
            </span>
          )}
          {entity.sourceCount !== undefined && entity.sourceCount > 0 && (
            <span className="ies-entity-card__stat">
              {entity.sourceCount} source{entity.sourceCount !== 1 ? 's' : ''}
            </span>
          )}
          {entity.lastVisited && (
            <span className="ies-entity-card__timestamp">
              {formatRelativeTime(entity.lastVisited)}
            </span>
          )}
        </div>

        {/* Action buttons */}
        {(onViewDetails || onViewSources) && !compact && (
          <div className="ies-entity-card__actions">
            {onViewDetails && (
              <button
                type="button"
                className="ies-entity-card__action"
                onClick={handleViewDetails}
                aria-label={`View details for ${entity.name}`}
              >
                <ExternalLink size={14} />
                <span>Details</span>
              </button>
            )}
            {onViewSources && entity.sourceCount !== undefined && entity.sourceCount > 0 && (
              <button
                type="button"
                className="ies-entity-card__action"
                onClick={handleViewSources}
                aria-label={`View sources for ${entity.name}`}
              >
                <BookOpen size={14} />
                <span>Sources</span>
              </button>
            )}
          </div>
        )}
      </div>
    </div>
  );
};
