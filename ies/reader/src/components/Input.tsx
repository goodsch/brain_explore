import { InputHTMLAttributes, ReactNode, forwardRef } from 'react';
import { clsx } from 'clsx';
import './Input.css';

export interface InputProps extends Omit<InputHTMLAttributes<HTMLInputElement>, 'size'> {
  variant?: 'default' | 'error' | 'success';
  size?: 'sm' | 'md' | 'lg';
  label?: string;
  helperText?: string;
  errorMessage?: string;
  leftIcon?: ReactNode;
  rightIcon?: ReactNode;
  fullWidth?: boolean;
}

/**
 * Input - IES Design System v2
 *
 * Text input component following the glassmorphic design language.
 * Supports multiple variants, sizes, and accessibility features.
 */
export const Input = forwardRef<HTMLInputElement, InputProps>(
  (
    {
      variant = 'default',
      size = 'md',
      label,
      helperText,
      errorMessage,
      leftIcon,
      rightIcon,
      fullWidth = false,
      disabled,
      className,
      id,
      ...props
    },
    ref
  ) => {
    const inputId = id || `input-${Math.random().toString(36).substr(2, 9)}`;
    const helperId = helperText ? `${inputId}-helper` : undefined;
    const errorId = errorMessage ? `${inputId}-error` : undefined;

    // Error variant takes precedence over variant prop
    const effectiveVariant = errorMessage ? 'error' : variant;

    return (
      <div
        className={clsx('ies-input-wrapper', {
          'ies-input-wrapper--full-width': fullWidth,
        })}
      >
        {label && (
          <label htmlFor={inputId} className="ies-input-label">
            {label}
          </label>
        )}

        <div
          className={clsx(
            'ies-input-container',
            `ies-input-container--${effectiveVariant}`,
            `ies-input-container--${size}`,
            {
              'ies-input-container--disabled': disabled,
              'ies-input-container--with-left-icon': leftIcon,
              'ies-input-container--with-right-icon': rightIcon,
            }
          )}
        >
          {leftIcon && <div className="ies-input-icon ies-input-icon--left">{leftIcon}</div>}

          <input
            ref={ref}
            id={inputId}
            className={clsx('ies-input', className)}
            disabled={disabled}
            aria-invalid={effectiveVariant === 'error'}
            aria-describedby={clsx(helperId, errorId).trim() || undefined}
            {...props}
          />

          {rightIcon && <div className="ies-input-icon ies-input-icon--right">{rightIcon}</div>}
        </div>

        {helperText && !errorMessage && (
          <p id={helperId} className="ies-input-helper">
            {helperText}
          </p>
        )}

        {errorMessage && (
          <p id={errorId} className="ies-input-error">
            {errorMessage}
          </p>
        )}
      </div>
    );
  }
);

Input.displayName = 'Input';
