import { useState } from 'react';
import clsx from 'clsx';
import './areas-chips.css';

interface AreasChipsProps {
  areas: string[];
  selectedArea: string | null;
  onSelectArea: (area: string | null) => void;
}

export function AreasChips({
  areas,
  selectedArea,
  onSelectArea,
}: AreasChipsProps) {
  const [isExpanded, setIsExpanded] = useState(false);

  if (areas.length === 0) {
    return null;
  }

  const handleChipClick = (area: string) => {
    // Toggle selection - clicking selected area deselects it
    if (selectedArea === area) {
      onSelectArea(null);
    } else {
      onSelectArea(area);
    }
  };

  // Show first 3 areas when collapsed, all when expanded
  const displayedAreas = isExpanded ? areas : areas.slice(0, 3);
  const hasMore = areas.length > 3;

  return (
    <div className="areas-chips">
      <div className="areas-chips__header">
        <span className="areas-chips__icon">🗺️</span>
        <span className="areas-chips__label">Areas of Exploration</span>
        {hasMore && (
          <button
            onClick={() => setIsExpanded(!isExpanded)}
            className="areas-chips__toggle"
          >
            {isExpanded ? 'Show less' : `+${areas.length - 3} more`}
          </button>
        )}
      </div>

      <div className="areas-chips__container">
        {displayedAreas.map((area) => (
          <button
            key={area}
            onClick={() => handleChipClick(area)}
            className={clsx(
              'areas-chips__chip',
              selectedArea === area && 'areas-chips__chip--selected'
            )}
          >
            {area}
          </button>
        ))}
      </div>
    </div>
  );
}

export default AreasChips;
