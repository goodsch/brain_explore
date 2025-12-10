import React, { HTMLAttributes, KeyboardEvent } from 'react';
import { clsx } from 'clsx';
import {
  Lightbulb,
  User,
  FlaskConical,
  LayoutGrid,
  ClipboardCheck,
  Sparkles,
  Brain,
  GitBranch,
  Heart,
  RefreshCw,
  Repeat,
  Activity,
  BookOpen,
  Zap,
  LucideIcon,
} from 'lucide-react';
import './EntityBadge.css';

/**
 * All 14 entity types from the IES knowledge graph
 */
export type EntityType =
  | 'Concept'
  | 'Person'
  | 'Theory'
  | 'Framework'
  | 'Assessment'
  | 'Spark'
  | 'Insight'
  | 'Thread'
  | 'FavoriteProblem'
  | 'Reframe'
  | 'Pattern'
  | 'DynamicPattern'
  | 'StoryInsight'
  | 'SchemaBreak';

export type EntityBadgeSize = 'sm' | 'md' | 'lg';

export interface EntityBadgeProps
  extends Omit<HTMLAttributes<HTMLSpanElement>, 'onClick'> {
  /** The entity type to display */
  entityType: EntityType;
  /** Size variant */
  size?: EntityBadgeSize;
  /** Whether the badge is interactive (clickable) */
  interactive?: boolean;
  /** Muted/inactive state */
  muted?: boolean;
  /** Click handler (only used when interactive=true) */
  onClick?: () => void;
  /** Additional CSS class */
  className?: string;
}

/**
 * Icon mapping for each entity type using Lucide icons
 */
const ENTITY_ICONS: Record<EntityType, LucideIcon> = {
  Concept: Lightbulb,
  Person: User,
  Theory: FlaskConical,
  Framework: LayoutGrid,
  Assessment: ClipboardCheck,
  Spark: Sparkles,
  Insight: Brain,
  Thread: GitBranch,
  FavoriteProblem: Heart,
  Reframe: RefreshCw,
  Pattern: Repeat,
  DynamicPattern: Activity,
  StoryInsight: BookOpen,
  SchemaBreak: Zap,
};

/**
 * Icon sizes for each badge size (in pixels)
 */
const ICON_SIZES: Record<EntityBadgeSize, number> = {
  sm: 14,
  md: 16,
  lg: 20,
};

/**
 * EntityBadge - IES Design System v2
 *
 * Display entity type with visual identifier (color + icon).
 * Used in entity labels, search results, entity cards, breadcrumbs.
 *
 * Accessibility:
 * - role="status" for non-interactive badges
 * - role="button" with tabindex="0" for interactive badges
 * - Keyboard support: Enter/Space activates onClick
 * - Proper aria-label including entity type
 */
export const EntityBadge = ({
  entityType,
  size = 'md',
  interactive = false,
  muted = false,
  onClick,
  className,
  ...props
}: EntityBadgeProps) => {
  const Icon = ENTITY_ICONS[entityType];
  const iconSize = ICON_SIZES[size];

  // Normalize entity type to lowercase for CSS class
  const typeClass = entityType.toLowerCase().replace(/([a-z])([A-Z])/g, '$1-$2').toLowerCase();

  const handleClick = () => {
    if (interactive && onClick) {
      onClick();
    }
  };

  const handleKeyDown = (event: KeyboardEvent<HTMLSpanElement>) => {
    if (interactive && onClick && (event.key === 'Enter' || event.key === ' ')) {
      event.preventDefault();
      onClick();
    }
  };

  // Build aria-label
  const ariaLabel = muted
    ? `${entityType} entity (muted)`
    : `${entityType} entity`;

  return (
    <span
      className={clsx(
        'ies-entity-badge',
        `ies-entity-badge--${typeClass}`,
        `ies-entity-badge--${size}`,
        {
          'ies-entity-badge--interactive': interactive,
          'ies-entity-badge--muted': muted,
        },
        className
      )}
      role={interactive ? 'button' : 'status'}
      tabIndex={interactive ? 0 : undefined}
      aria-label={ariaLabel}
      onClick={handleClick}
      onKeyDown={handleKeyDown}
      {...props}
    >
      <Icon
        size={iconSize}
        className="ies-entity-badge__icon"
        aria-hidden="true"
      />
      <span className="ies-entity-badge__label">{entityType}</span>
    </span>
  );
};
