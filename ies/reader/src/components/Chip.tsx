import React, { ButtonHTMLAttributes } from 'react';
import { clsx } from 'clsx';
import './Chip.css';

export type ChipVariant = 'default' | 'selected';
export type ChipSize = 'sm' | 'md';

export interface ChipProps extends Omit<ButtonHTMLAttributes<HTMLButtonElement>, 'type'> {
  variant?: ChipVariant;
  size?: ChipSize;
  selected?: boolean;
  onRemove?: (event: React.MouseEvent<HTMLButtonElement>) => void;
  leadingIcon?: React.ReactNode;
  children: React.ReactNode;
}

/**
 * Chip - IES Design System v2
 *
 * Interactive pill-shaped component for selections, filters, and tags.
 * Supports selection states, removal, and optional icons.
 */
export const Chip = ({
  variant = 'default',
  size = 'md',
  selected = false,
  onRemove,
  leadingIcon,
  className,
  children,
  disabled,
  onClick,
  ...props
}: ChipProps) => {
  const handleRemove = (event: React.MouseEvent<HTMLButtonElement>) => {
    event.stopPropagation();
    onRemove?.(event);
  };

  return (
    <button
      type="button"
      className={clsx(
        'ies-chip',
        `ies-chip--${variant}`,
        `ies-chip--${size}`,
        {
          'ies-chip--selected': selected,
          'ies-chip--disabled': disabled,
          'ies-chip--clickable': onClick && !disabled,
        },
        className
      )}
      disabled={disabled}
      onClick={onClick}
      aria-pressed={selected}
      {...props}
    >
      {leadingIcon && (
        <span className="ies-chip__icon ies-chip__icon--leading">
          {leadingIcon}
        </span>
      )}
      <span className="ies-chip__label">{children}</span>
      {onRemove && !disabled && (
        <button
          type="button"
          className="ies-chip__remove"
          onClick={handleRemove}
          aria-label="Remove"
          tabIndex={-1}
        >
          <svg
            width="12"
            height="12"
            viewBox="0 0 12 12"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
            aria-hidden="true"
          >
            <path
              d="M9 3L3 9M3 3L9 9"
              stroke="currentColor"
              strokeWidth="1.5"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>
        </button>
      )}
    </button>
  );
};
