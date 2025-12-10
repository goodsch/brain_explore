/**
 * IES Design System v2 — Component Library
 * @module @ies/components
 * @version 2.0.0
 *
 * Phase 1 Components (Dec 2025):
 * - EntityBadge: Entity type indicator with icon
 * - QuestionClassBadge: Question class indicator for thinking sessions
 * - ProgressRing: Circular progress indicator
 * - SearchInput: Debounced search input with clear button
 * - EntityCard: Entity display card with expandable details
 * - BreadcrumbTrail: Journey navigation trail
 *
 * Foundation Components (existing):
 * - Button: Primary button component
 * - Input: Form input component
 * - Badge: Simple label badge
 * - Card: Container card component
 * - Chip: Interactive chip component
 * - ErrorBoundary: Error boundary wrapper
 */

// Phase 1 Components
export { EntityBadge } from './EntityBadge';
export type { EntityBadgeProps, EntityType, EntityBadgeSize } from './EntityBadge';

export { QuestionClassBadge } from './QuestionClassBadge';
export type { QuestionClassBadgeProps, QuestionClass, QuestionClassBadgeSize } from './QuestionClassBadge';

export { ProgressRing } from './ProgressRing';
export type { ProgressRingProps, ProgressRingSize, ProgressRingVariant } from './ProgressRing';

export { SearchInput } from './SearchInput';
export type { SearchInputProps, SearchInputSize } from './SearchInput';

export { EntityCard } from './EntityCard';
export type { EntityCardProps, Entity } from './EntityCard';

export { BreadcrumbTrail } from './BreadcrumbTrail';
export type { BreadcrumbTrailProps, BreadcrumbItem } from './BreadcrumbTrail';

// Foundation Components
export { Button } from './Button';
export type { ButtonProps } from './Button';

export { Badge } from './Badge';
export type { BadgeProps, BadgeVariant, BadgeSize } from './Badge';

export { Card } from './Card';
export type { CardProps } from './Card';

export { Chip } from './Chip';
export type { ChipProps, ChipVariant, ChipSize } from './Chip';

export { Input } from './Input';
export type { InputProps } from './Input';

export { ErrorBoundary } from './ErrorBoundary';
