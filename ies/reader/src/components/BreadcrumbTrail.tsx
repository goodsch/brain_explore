import React, { HTMLAttributes, useRef, useState, useEffect } from 'react';
import { clsx } from 'clsx';
import { ChevronRight, MoreHorizontal } from 'lucide-react';
import { EntityBadge, EntityType } from './EntityBadge';
import './BreadcrumbTrail.css';

export interface BreadcrumbItem {
  id: string;
  name: string;
  type: EntityType;
  /** Source app that recorded this visit */
  sourceApp?: 'reader' | 'siyuan';
  /** Timestamp of visit */
  timestamp?: Date;
}

export interface BreadcrumbTrailProps
  extends Omit<HTMLAttributes<HTMLElement>, 'onClick'> {
  /** Array of breadcrumb items (most recent first) */
  trail: BreadcrumbItem[];
  /** Maximum visible items before overflow */
  maxVisible?: number;
  /** Click handler for an item */
  onItemClick?: (item: BreadcrumbItem, index: number) => void;
  /** Show entity type badges */
  showBadges?: boolean;
  /** Compact mode (smaller text, tighter spacing) */
  compact?: boolean;
  /** Additional CSS class */
  className?: string;
}

/**
 * BreadcrumbTrail - IES Design System v2
 *
 * Navigation component showing exploration path through the knowledge graph.
 * Displays journey trail with overflow handling.
 *
 * Features:
 * - Horizontal scroll on overflow
 * - Collapsible overflow with dropdown
 * - Clickable items for navigation
 * - Entity type badges (optional)
 * - Current item highlighted (first in list)
 *
 * Accessibility:
 * - nav element with aria-label
 * - ol/li for semantic list structure
 * - aria-current on current item
 * - Keyboard navigable
 */
export const BreadcrumbTrail = ({
  trail,
  maxVisible = 5,
  onItemClick,
  showBadges = true,
  compact = false,
  className,
  ...props
}: BreadcrumbTrailProps) => {
  const containerRef = useRef<HTMLElement>(null);
  const [showOverflowMenu, setShowOverflowMenu] = useState(false);

  // Close overflow menu when clicking outside
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(e.target as Node)) {
        setShowOverflowMenu(false);
      }
    };

    if (showOverflowMenu) {
      document.addEventListener('click', handleClickOutside);
      return () => document.removeEventListener('click', handleClickOutside);
    }
  }, [showOverflowMenu]);

  if (trail.length === 0) {
    return null;
  }

  // Reverse trail for display (most recent last in breadcrumb)
  const displayTrail = [...trail].reverse();

  // Determine visible and overflow items
  const hasOverflow = displayTrail.length > maxVisible;
  const overflowItems = hasOverflow ? displayTrail.slice(0, displayTrail.length - maxVisible + 1) : [];
  const visibleItems = hasOverflow ? displayTrail.slice(displayTrail.length - maxVisible + 1) : displayTrail;

  const handleItemClick = (item: BreadcrumbItem, index: number) => {
    onItemClick?.(item, trail.length - 1 - index); // Convert back to original index
  };

  const handleOverflowToggle = (e: React.MouseEvent) => {
    e.stopPropagation();
    setShowOverflowMenu(!showOverflowMenu);
  };

  const handleOverflowItemClick = (item: BreadcrumbItem, originalIndex: number) => {
    setShowOverflowMenu(false);
    onItemClick?.(item, originalIndex);
  };

  return (
    <nav
      ref={containerRef}
      className={clsx(
        'ies-breadcrumb-trail',
        { 'ies-breadcrumb-trail--compact': compact },
        className
      )}
      aria-label="Journey trail"
      {...props}
    >
      <ol className="ies-breadcrumb-trail__list">
        {/* Overflow indicator */}
        {hasOverflow && (
          <>
            <li className="ies-breadcrumb-trail__item ies-breadcrumb-trail__overflow">
              <button
                type="button"
                className="ies-breadcrumb-trail__overflow-btn"
                onClick={handleOverflowToggle}
                aria-expanded={showOverflowMenu}
                aria-label={`${overflowItems.length} more items`}
              >
                <MoreHorizontal size={16} />
              </button>
              {showOverflowMenu && (
                <div className="ies-breadcrumb-trail__overflow-menu" role="menu">
                  {overflowItems.map((item, idx) => {
                    const originalIndex = displayTrail.indexOf(item);
                    return (
                      <button
                        key={item.id}
                        type="button"
                        className="ies-breadcrumb-trail__overflow-item"
                        onClick={() => handleOverflowItemClick(item, trail.length - 1 - originalIndex)}
                        role="menuitem"
                      >
                        {showBadges && (
                          <EntityBadge entityType={item.type} size="sm" />
                        )}
                        <span className="ies-breadcrumb-trail__item-name">{item.name}</span>
                      </button>
                    );
                  })}
                </div>
              )}
            </li>
            <li className="ies-breadcrumb-trail__separator" aria-hidden="true">
              <ChevronRight size={14} />
            </li>
          </>
        )}

        {/* Visible items */}
        {visibleItems.map((item, idx) => {
          const isLast = idx === visibleItems.length - 1;
          const displayIndex = hasOverflow ? overflowItems.length + idx : idx;

          return (
            <React.Fragment key={item.id}>
              <li
                className={clsx('ies-breadcrumb-trail__item', {
                  'ies-breadcrumb-trail__item--current': isLast,
                })}
              >
                {onItemClick && !isLast ? (
                  <button
                    type="button"
                    className="ies-breadcrumb-trail__link"
                    onClick={() => handleItemClick(item, displayIndex)}
                    aria-current={isLast ? 'page' : undefined}
                  >
                    {showBadges && (
                      <EntityBadge entityType={item.type} size="sm" />
                    )}
                    <span className="ies-breadcrumb-trail__item-name">{item.name}</span>
                  </button>
                ) : (
                  <span
                    className="ies-breadcrumb-trail__current"
                    aria-current={isLast ? 'page' : undefined}
                  >
                    {showBadges && (
                      <EntityBadge entityType={item.type} size="sm" />
                    )}
                    <span className="ies-breadcrumb-trail__item-name">{item.name}</span>
                  </span>
                )}
              </li>
              {!isLast && (
                <li className="ies-breadcrumb-trail__separator" aria-hidden="true">
                  <ChevronRight size={14} />
                </li>
              )}
            </React.Fragment>
          );
        })}
      </ol>
    </nav>
  );
};
