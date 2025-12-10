import React, { ButtonHTMLAttributes } from 'react';
import { clsx } from 'clsx';
import './Button.css';

export interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'ghost' | 'danger';
  size?: 'sm' | 'md' | 'lg';
  isLoading?: boolean;
  children: React.ReactNode;
}

/**
 * Button - IES Design System v2
 *
 * Primary interactive component following the glassmorphic design language.
 */
export const Button = ({
  variant = 'primary',
  size = 'md',
  isLoading = false,
  disabled,
  className,
  children,
  ...props
}: ButtonProps) => {
  return (
    <button
      className={clsx(
        'ies-button',
        `ies-button--${variant}`,
        `ies-button--${size}`,
        {
          'ies-button--loading': isLoading,
          'ies-button--disabled': disabled || isLoading,
        },
        className
      )}
      disabled={disabled || isLoading}
      {...props}
    >
      {isLoading ? (
        <span className="ies-button__spinner" />
      ) : null}
      <span className={clsx('ies-button__content', { 'ies-button__content--loading': isLoading })}>
        {children}
      </span>
    </button>
  );
};
