import React, { HTMLAttributes } from 'react';
import { clsx } from 'clsx';
import './Badge.css';

export type BadgeVariant =
  | 'default'
  | 'success'
  | 'warning'
  | 'error'
  | 'info'
  | 'concept'
  | 'person'
  | 'theory'
  | 'framework'
  | 'assessment'
  | 'spark'
  | 'insight'
  | 'thread';

export type BadgeSize = 'sm' | 'md';

export interface BadgeProps extends HTMLAttributes<HTMLSpanElement> {
  variant?: BadgeVariant;
  size?: BadgeSize;
  children: React.ReactNode;
}

/**
 * Badge - IES Design System v2
 *
 * Static pill-shaped indicator for entity types, semantic states, and labels.
 * Non-interactive display component.
 */
export const Badge = ({
  variant = 'default',
  size = 'md',
  className,
  children,
  ...props
}: BadgeProps) => {
  return (
    <span
      className={clsx(
        'ies-badge',
        `ies-badge--${variant}`,
        `ies-badge--${size}`,
        className
      )}
      {...props}
    >
      {children}
    </span>
  );
};
