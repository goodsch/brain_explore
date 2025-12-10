import React, { HTMLAttributes } from 'react';
import { clsx } from 'clsx';
import './ProgressRing.css';

export type ProgressRingSize = 'sm' | 'md' | 'lg' | 'xl';
export type ProgressRingVariant = 'default' | 'success' | 'warning' | 'error' | 'info';

export interface ProgressRingProps extends HTMLAttributes<HTMLDivElement> {
  /** Progress value (0-100) */
  value: number;
  /** Size variant */
  size?: ProgressRingSize;
  /** Color variant */
  variant?: ProgressRingVariant;
  /** Show percentage label in center */
  showLabel?: boolean;
  /** Custom label (overrides percentage) */
  label?: string;
  /** Stroke width (in pixels) */
  strokeWidth?: number;
  /** Additional CSS class */
  className?: string;
}

/**
 * Size configurations (diameter in pixels)
 */
const SIZE_CONFIG: Record<ProgressRingSize, { diameter: number; strokeWidth: number }> = {
  sm: { diameter: 24, strokeWidth: 3 },
  md: { diameter: 40, strokeWidth: 4 },
  lg: { diameter: 64, strokeWidth: 5 },
  xl: { diameter: 96, strokeWidth: 6 },
};

/**
 * ProgressRing - IES Design System v2
 *
 * SVG circular progress indicator with accessible announcements.
 * Used for loading states, completion tracking, and progress visualization.
 *
 * Accessibility:
 * - role="progressbar" for screen readers
 * - aria-valuenow, aria-valuemin, aria-valuemax for current progress
 * - aria-label describes the progress context
 */
export const ProgressRing = ({
  value,
  size = 'md',
  variant = 'default',
  showLabel = false,
  label,
  strokeWidth: customStrokeWidth,
  className,
  ...props
}: ProgressRingProps) => {
  // Clamp value between 0 and 100
  const clampedValue = Math.max(0, Math.min(100, value));

  // Get size configuration
  const config = SIZE_CONFIG[size];
  const diameter = config.diameter;
  const strokeWidth = customStrokeWidth ?? config.strokeWidth;

  // Calculate SVG dimensions
  const radius = (diameter - strokeWidth) / 2;
  const circumference = radius * 2 * Math.PI;
  const offset = circumference - (clampedValue / 100) * circumference;

  // Center point
  const center = diameter / 2;

  // Display label
  const displayLabel = label ?? `${Math.round(clampedValue)}%`;

  return (
    <div
      className={clsx(
        'ies-progress-ring',
        `ies-progress-ring--${size}`,
        `ies-progress-ring--${variant}`,
        className
      )}
      role="progressbar"
      aria-valuenow={clampedValue}
      aria-valuemin={0}
      aria-valuemax={100}
      aria-label={`Progress: ${Math.round(clampedValue)}%`}
      {...props}
    >
      <svg
        width={diameter}
        height={diameter}
        className="ies-progress-ring__svg"
      >
        {/* Background track */}
        <circle
          className="ies-progress-ring__track"
          cx={center}
          cy={center}
          r={radius}
          strokeWidth={strokeWidth}
          fill="none"
        />
        {/* Progress arc */}
        <circle
          className="ies-progress-ring__progress"
          cx={center}
          cy={center}
          r={radius}
          strokeWidth={strokeWidth}
          fill="none"
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          transform={`rotate(-90 ${center} ${center})`}
        />
      </svg>
      {showLabel && (
        <span className="ies-progress-ring__label" aria-hidden="true">
          {displayLabel}
        </span>
      )}
    </div>
  );
};
