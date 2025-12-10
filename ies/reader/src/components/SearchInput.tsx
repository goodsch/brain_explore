import React, {
  InputHTMLAttributes,
  useState,
  useEffect,
  useRef,
  useCallback,
} from 'react';
import { clsx } from 'clsx';
import { Search, X, Loader2 } from 'lucide-react';
import './SearchInput.css';

export type SearchInputSize = 'sm' | 'md' | 'lg';

export interface SearchInputProps
  extends Omit<InputHTMLAttributes<HTMLInputElement>, 'size' | 'onChange'> {
  /** Current search value */
  value: string;
  /** Change handler */
  onChange: (value: string) => void;
  /** Placeholder text */
  placeholder?: string;
  /** Size variant */
  size?: SearchInputSize;
  /** Debounce delay in milliseconds (0 = no debounce) */
  debounce?: number;
  /** Show loading spinner */
  loading?: boolean;
  /** Disable the input */
  disabled?: boolean;
  /** Called when clear button is clicked */
  onClear?: () => void;
  /** Called on Enter key press */
  onSubmit?: (value: string) => void;
  /** Additional CSS class */
  className?: string;
}

/**
 * SearchInput - IES Design System v2
 *
 * Search input with debounce support, clear button, and loading state.
 * Used for entity search, book search, and filtering.
 *
 * Accessibility:
 * - role="searchbox" for screen readers
 * - aria-label describes search purpose
 * - Clear button has aria-label
 * - Escape key clears input
 */
export const SearchInput = ({
  value,
  onChange,
  placeholder = 'Search...',
  size = 'md',
  debounce = 0,
  loading = false,
  disabled = false,
  onClear,
  onSubmit,
  className,
  ...props
}: SearchInputProps) => {
  // Internal state for debounced value
  const [internalValue, setInternalValue] = useState(value);
  const debounceTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // Sync internal value when external value changes
  useEffect(() => {
    setInternalValue(value);
  }, [value]);

  // Debounced onChange
  const debouncedOnChange = useCallback(
    (newValue: string) => {
      if (debounceTimerRef.current) {
        clearTimeout(debounceTimerRef.current);
      }

      if (debounce > 0) {
        debounceTimerRef.current = setTimeout(() => {
          onChange(newValue);
        }, debounce);
      } else {
        onChange(newValue);
      }
    },
    [onChange, debounce]
  );

  // Cleanup debounce timer
  useEffect(() => {
    return () => {
      if (debounceTimerRef.current) {
        clearTimeout(debounceTimerRef.current);
      }
    };
  }, []);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newValue = e.target.value;
    setInternalValue(newValue);
    debouncedOnChange(newValue);
  };

  const handleClear = () => {
    setInternalValue('');
    onChange('');
    onClear?.();
    inputRef.current?.focus();
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Escape') {
      handleClear();
    } else if (e.key === 'Enter' && onSubmit) {
      onSubmit(internalValue);
    }
  };

  const showClearButton = internalValue.length > 0 && !loading && !disabled;

  return (
    <div
      className={clsx(
        'ies-search-input',
        `ies-search-input--${size}`,
        {
          'ies-search-input--disabled': disabled,
          'ies-search-input--loading': loading,
          'ies-search-input--has-value': internalValue.length > 0,
        },
        className
      )}
    >
      <Search
        className="ies-search-input__icon"
        aria-hidden="true"
      />
      <input
        ref={inputRef}
        type="text"
        role="searchbox"
        className="ies-search-input__input"
        value={internalValue}
        onChange={handleChange}
        onKeyDown={handleKeyDown}
        placeholder={placeholder}
        disabled={disabled}
        aria-label={placeholder}
        {...props}
      />
      {loading && (
        <Loader2
          className="ies-search-input__spinner"
          aria-hidden="true"
        />
      )}
      {showClearButton && (
        <button
          type="button"
          className="ies-search-input__clear"
          onClick={handleClear}
          aria-label="Clear search"
          tabIndex={-1}
        >
          <X size={16} aria-hidden="true" />
        </button>
      )}
    </div>
  );
};
