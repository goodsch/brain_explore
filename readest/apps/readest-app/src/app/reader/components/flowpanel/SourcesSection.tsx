import React from 'react';
import { LuBookMarked, LuExternalLink } from 'react-icons/lu';

import { useTranslation } from '@/hooks/useTranslation';
import { BookSource } from '@/store/flowModeStore';

interface SourcesSectionProps {
  sources: BookSource[];
}

const SourcesSection: React.FC<SourcesSectionProps> = ({ sources }) => {
  const _ = useTranslation();

  const handleOpenSource = (source: BookSource) => {
    // TODO: Navigate to the book/chapter
    console.log('Opening source:', source);
  };

  if (sources.length === 0) {
    return null;
  }

  return (
    <section className='space-y-3'>
      <div className='text-base-content/60 flex items-center gap-1 text-xs font-medium uppercase'>
        <LuBookMarked size={12} />
        {_('Other Sources')} ({sources.length})
      </div>

      <div className='bg-base-100 rounded-lg p-3'>
        <ul className='space-y-2'>
          {sources.map((source, index) => (
            <li key={`${source.bookId}-${index}`}>
              <button
                className='group flex w-full items-start justify-between gap-2 rounded px-2 py-2 text-left transition-colors hover:bg-base-200'
                onClick={() => handleOpenSource(source)}
              >
                <div className='flex-grow'>
                  <div className='group-hover:text-primary text-sm font-medium'>
                    {source.bookTitle}
                  </div>
                  {source.chapter && (
                    <div className='text-base-content/50 text-xs'>{source.chapter}</div>
                  )}
                  {source.pageRange && (
                    <div className='text-base-content/40 text-xs'>
                      {_('Pages')} {source.pageRange}
                    </div>
                  )}
                </div>
                <LuExternalLink
                  size={14}
                  className='text-base-content/30 group-hover:text-primary mt-0.5 flex-shrink-0'
                />
              </button>
            </li>
          ))}
        </ul>
      </div>
    </section>
  );
};

export default SourcesSection;
