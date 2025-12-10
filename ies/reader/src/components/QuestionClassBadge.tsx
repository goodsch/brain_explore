import React, { HTMLAttributes } from 'react';
import { clsx } from 'clsx';
import {
  Building2,
  Square,
  Ruler,
  Zap,
  Sparkles,
  Anchor,
  Eye,
  Brain,
  Link,
  LucideIcon,
} from 'lucide-react';
import './QuestionClassBadge.css';

/**
 * Nine question classes from the IES Question Engine
 * Each class has a distinct cognitive function and maps to specific thinking modes
 */
export type QuestionClass =
  | 'schema-probe'      // Surfaces hidden structure
  | 'boundary'          // Clarifies edges/limits
  | 'dimensional'       // Introduces spectra/coordinates
  | 'causal'            // Pushes for mechanisms
  | 'counterfactual'    // "What if" deviations
  | 'anchor'            // Grounds in concrete instances
  | 'perspective-shift' // Forces viewpoint changes
  | 'meta-cognitive'    // Checks thinking patterns
  | 'reflective-synthesis'; // Integration statements

export type QuestionClassBadgeSize = 'sm' | 'md' | 'lg';

export interface QuestionClassBadgeProps
  extends HTMLAttributes<HTMLSpanElement> {
  /** The question class to display */
  questionClass: QuestionClass;
  /** Size variant */
  size?: QuestionClassBadgeSize;
  /** Show only icon (no label) */
  iconOnly?: boolean;
  /** Additional CSS class */
  className?: string;
}

/**
 * Human-readable labels for each question class
 */
const CLASS_LABELS: Record<QuestionClass, string> = {
  'schema-probe': 'Structure',
  'boundary': 'Boundary',
  'dimensional': 'Dimensional',
  'causal': 'Causal',
  'counterfactual': 'What-If',
  'anchor': 'Anchor',
  'perspective-shift': 'Perspective',
  'meta-cognitive': 'Meta',
  'reflective-synthesis': 'Synthesis',
};

/**
 * Icon mapping for each question class using Lucide icons
 */
const CLASS_ICONS: Record<QuestionClass, LucideIcon> = {
  'schema-probe': Building2,      // Structure questions
  'boundary': Square,             // Edge/limit questions
  'dimensional': Ruler,           // Spectrum questions
  'causal': Zap,                  // Mechanism questions
  'counterfactual': Sparkles,     // What-if questions
  'anchor': Anchor,               // Concrete example questions
  'perspective-shift': Eye,       // Viewpoint change questions
  'meta-cognitive': Brain,        // Thinking pattern questions
  'reflective-synthesis': Link,   // Integration questions
};

/**
 * Icon sizes for each badge size (in pixels)
 */
const ICON_SIZES: Record<QuestionClassBadgeSize, number> = {
  sm: 12,
  md: 14,
  lg: 16,
};

/**
 * QuestionClassBadge - IES Design System v2
 *
 * Display question class with visual identifier (color + icon).
 * Used in thinking sessions, question displays, and ForgeMode UI.
 *
 * Question Classes:
 * - Schema-Probe: Surfaces hidden structure (lists, buckets, taxonomies)
 * - Boundary: Clarifies edges/limits to avoid scope creep
 * - Dimensional: Introduces spectra/coordinates for precise positioning
 * - Causal: Pushes for mechanisms, prerequisites, sequences
 * - Counterfactual: "What if" deviations to expose assumptions
 * - Anchor: Grounds abstractions in concrete instances
 * - Perspective-Shift: Forces viewpoint changes (roles, time, system level)
 * - Meta-Cognitive: Checks thinking patterns directly
 * - Reflective-Synthesis: Integration statements tying threads together
 */
export const QuestionClassBadge = ({
  questionClass,
  size = 'md',
  iconOnly = false,
  className,
  ...props
}: QuestionClassBadgeProps) => {
  const Icon = CLASS_ICONS[questionClass];
  const iconSize = ICON_SIZES[size];
  const label = CLASS_LABELS[questionClass];

  return (
    <span
      className={clsx(
        'ies-question-class-badge',
        `ies-question-class-badge--${questionClass}`,
        `ies-question-class-badge--${size}`,
        { 'ies-question-class-badge--icon-only': iconOnly },
        className
      )}
      role="status"
      aria-label={`${label} question`}
      title={label}
      {...props}
    >
      <Icon
        size={iconSize}
        className="ies-question-class-badge__icon"
        aria-hidden="true"
      />
      {!iconOnly && (
        <span className="ies-question-class-badge__label">{label}</span>
      )}
    </span>
  );
};
