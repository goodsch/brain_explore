import { useEffect, useState } from 'react';
import { MdSearch, MdClear } from 'react-icons/md';
import { useTranslation } from '@/hooks/useTranslation';

interface CalibreSearchBarProps {
  onSearchChange: (query: string) => void;
  hasEntitiesOnly: boolean;
  onHasEntitiesChange: (value: boolean) => void;
}

const CalibreSearchBar: React.FC<CalibreSearchBarProps> = ({
  onSearchChange,
  hasEntitiesOnly,
  onHasEntitiesChange,
}) => {
  const _ = useTranslation();
  const [inputValue, setInputValue] = useState('');

  // Debounce search
  useEffect(() => {
    const timer = setTimeout(() => {
      onSearchChange(inputValue);
    }, 300);
    return () => clearTimeout(timer);
  }, [inputValue, onSearchChange]);

  const handleClear = () => {
    setInputValue('');
    onSearchChange('');
  };

  return (
    <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
      {/* Search Input */}
      <div className="relative flex-1">
        <MdSearch className="text-neutral-content/50 absolute left-3 top-1/2 -translate-y-1/2" size={20} />
        <input
          type="text"
          placeholder={_('Search books...')}
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          className="input input-bordered w-full pl-10 pr-10"
        />
        {inputValue && (
          <button
            onClick={handleClear}
            className="text-neutral-content/50 hover:text-neutral-content absolute right-3 top-1/2 -translate-y-1/2"
            aria-label={_('Clear search')}
          >
            <MdClear size={20} />
          </button>
        )}
      </div>

      {/* Has Entities Filter */}
      <label className="flex cursor-pointer items-center gap-2">
        <input
          type="checkbox"
          checked={hasEntitiesOnly}
          onChange={(e) => onHasEntitiesChange(e.target.checked)}
          className="checkbox checkbox-sm checkbox-primary"
        />
        <span className="text-sm">{_('Has entities only')}</span>
      </label>
    </div>
  );
};

export default CalibreSearchBar;
