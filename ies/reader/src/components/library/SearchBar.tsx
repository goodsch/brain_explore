import { useState, useCallback, useEffect, useRef } from 'react';
import { Search, X } from 'lucide-react';

interface SearchBarProps {
  onSearch: (query: string) => void;
  placeholder?: string;
  debounceMs?: number;
}

export function SearchBar({
  onSearch,
  placeholder = 'Search books...',
  debounceMs = 300,
}: SearchBarProps) {
  const [value, setValue] = useState('');
  const timeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // Debounced search
  useEffect(() => {
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
    }

    timeoutRef.current = setTimeout(() => {
      onSearch(value);
    }, debounceMs);

    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
    };
  }, [value, onSearch, debounceMs]);

  const handleClear = useCallback(() => {
    setValue('');
    onSearch('');
    inputRef.current?.focus();
  }, [onSearch]);

  // Keyboard shortcut: / to focus
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === '/' && document.activeElement !== inputRef.current) {
        e.preventDefault();
        inputRef.current?.focus();
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, []);

  return (
    <div className="search-bar">
      <Search className="search-bar-icon" size={20} />
      <input
        ref={inputRef}
        type="text"
        className="search-bar-input ies-input"
        value={value}
        onChange={(e) => setValue(e.target.value)}
        placeholder={placeholder}
        aria-label="Search books"
      />
      {value && (
        <button
          className="search-bar-clear"
          onClick={handleClear}
          aria-label="Clear search"
        >
          <X size={18} />
        </button>
      )}
      <kbd className="search-bar-hint">/</kbd>
    </div>
  );
}
