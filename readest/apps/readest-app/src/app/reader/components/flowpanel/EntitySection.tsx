import React from 'react';
import { LuBookOpen } from 'react-icons/lu';

import { useTranslation } from '@/hooks/useTranslation';
import { GraphEntity } from '@/store/flowModeStore';

interface EntitySectionProps {
  entity: GraphEntity;
}

const EntitySection: React.FC<EntitySectionProps> = ({ entity }) => {
  const _ = useTranslation();

  const getTypeColor = (type: string) => {
    const colors: Record<string, string> = {
      concept: 'badge-primary',
      theory: 'badge-secondary',
      framework: 'badge-accent',
      phenomenon: 'badge-info',
      person: 'badge-success',
      assessment: 'badge-warning',
    };
    return colors[type.toLowerCase()] || 'badge-neutral';
  };

  return (
    <section className='space-y-3'>
      <div className='flex items-start justify-between gap-2'>
        <h3 className='text-lg font-bold leading-tight'>{entity.name}</h3>
        <span className={`badge ${getTypeColor(entity.type)} badge-sm flex-shrink-0`}>
          {entity.type}
        </span>
      </div>

      <div className='bg-base-100 rounded-lg p-3'>
        <div className='text-base-content/60 mb-1 flex items-center gap-1 text-xs font-medium uppercase'>
          <LuBookOpen size={12} />
          {_('Definition')}
        </div>
        <p className='text-base-content text-sm leading-relaxed'>{entity.summary}</p>
      </div>
    </section>
  );
};

export default EntitySection;
