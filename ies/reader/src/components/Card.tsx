import { HTMLAttributes, ReactNode } from 'react';
import { clsx } from 'clsx';
import './Card.css';

export interface CardProps extends HTMLAttributes<HTMLDivElement> {
  variant?: 'default' | 'elevated' | 'outlined' | 'glass';
  padding?: 'none' | 'sm' | 'md' | 'lg';
  header?: ReactNode;
  title?: string;
  actions?: ReactNode;
  footer?: ReactNode;
  clickable?: boolean;
  children: ReactNode;
}

/**
 * Card - IES Design System v2
 *
 * Container component for organizing related content.
 * Follows the glassmorphic design language with multiple variants.
 */
export const Card = ({
  variant = 'default',
  padding = 'md',
  header,
  title,
  actions,
  footer,
  clickable = false,
  className,
  children,
  onClick,
  ...props
}: CardProps) => {
  const hasHeader = header || title || actions;

  return (
    <div
      className={clsx(
        'ies-card',
        `ies-card--${variant}`,
        `ies-card--padding-${padding}`,
        {
          'ies-card--clickable': clickable,
        },
        className
      )}
      onClick={onClick}
      role={clickable ? 'button' : undefined}
      tabIndex={clickable ? 0 : undefined}
      onKeyDown={
        clickable
          ? (e) => {
              if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                onClick?.(e as any);
              }
            }
          : undefined
      }
      {...props}
    >
      {hasHeader && (
        <div className="ies-card__header">
          {header ? (
            header
          ) : (
            <>
              {title && <h3 className="ies-card__title">{title}</h3>}
              {actions && <div className="ies-card__actions">{actions}</div>}
            </>
          )}
        </div>
      )}

      <div className="ies-card__content">{children}</div>

      {footer && <div className="ies-card__footer">{footer}</div>}
    </div>
  );
};
