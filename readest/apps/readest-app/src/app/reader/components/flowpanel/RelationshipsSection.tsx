import React, { useMemo } from 'react';
import { LuLink, LuChevronRight } from 'react-icons/lu';

import { useTranslation } from '@/hooks/useTranslation';
import { EntityRelationship, useFlowModeStore } from '@/store/flowModeStore';

interface RelationshipsSectionProps {
  relationships: EntityRelationship[];
}

const RelationshipsSection: React.FC<RelationshipsSectionProps> = ({ relationships }) => {
  const _ = useTranslation();
  const { setCurrentEntity, addJourneyStep } = useFlowModeStore();

  // Group relationships by type
  const groupedRelationships = useMemo(() => {
    const groups: Record<string, EntityRelationship[]> = {};
    relationships.forEach((rel) => {
      const type = rel.type;
      if (!groups[type]) {
        groups[type] = [];
      }
      groups[type]!.push(rel);
    });
    return groups;
  }, [relationships]);

  const getRelationshipLabel = (type: string): string => {
    const labels: Record<string, string> = {
      supports: _('Supports'),
      contrasts_with: _('Contrasts with'),
      component_of: _('Component of'),
      develops: _('Develops'),
      is_example_of: _('Example of'),
      operationalizes: _('Operationalizes'),
      related_to: _('Related to'),
    };
    return labels[type] || type.replace(/_/g, ' ');
  };

  const getRelationshipColor = (type: string): string => {
    const colors: Record<string, string> = {
      supports: 'text-success',
      contrasts_with: 'text-warning',
      component_of: 'text-info',
      develops: 'text-primary',
      is_example_of: 'text-secondary',
      operationalizes: 'text-accent',
    };
    return colors[type] || 'text-base-content';
  };

  const handleNavigateToEntity = (rel: EntityRelationship) => {
    // Add to journey
    addJourneyStep(rel.target.id, rel.target.name);
    // Navigate to entity (this would trigger a fetch in a real implementation)
    setCurrentEntity(rel.target);
  };

  if (relationships.length === 0) {
    return null;
  }

  return (
    <section className='space-y-3'>
      <div className='text-base-content/60 flex items-center gap-1 text-xs font-medium uppercase'>
        <LuLink size={12} />
        {_('Relationships')} ({relationships.length})
      </div>

      <div className='space-y-3'>
        {Object.entries(groupedRelationships).map(([type, rels]) => (
          <div key={type} className='bg-base-100 rounded-lg p-3'>
            <div className={`mb-2 text-xs font-semibold ${getRelationshipColor(type)}`}>
              {getRelationshipLabel(type)}
            </div>
            <ul className='space-y-1'>
              {rels.map((rel, index) => (
                <li key={`${rel.target.id}-${index}`}>
                  <button
                    className='group flex w-full items-center justify-between rounded px-2 py-1.5 text-left text-sm transition-colors hover:bg-base-200'
                    onClick={() => handleNavigateToEntity(rel)}
                  >
                    <span className='group-hover:text-primary'>{rel.target.name}</span>
                    <LuChevronRight
                      size={14}
                      className='text-base-content/30 group-hover:text-primary'
                    />
                  </button>
                </li>
              ))}
            </ul>
          </div>
        ))}
      </div>
    </section>
  );
};

export default RelationshipsSection;
