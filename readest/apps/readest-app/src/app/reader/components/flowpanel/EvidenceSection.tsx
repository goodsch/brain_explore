import React from 'react';
import { LuQuote, LuBookOpen, LuSparkles } from 'react-icons/lu';

import { useTranslation } from '@/hooks/useTranslation';
import { EvidencePassage } from '@/store/flowModeStore';

interface EvidenceSectionProps {
  evidence: EvidencePassage[];
  isLoading?: boolean;
  onOpenInReader?: (passage: EvidencePassage) => void;
}

const ConfidenceBadge: React.FC<{ confidence: number; sourceType: string }> = ({
  confidence,
  sourceType,
}) => {
  const isHighConfidence = confidence >= 0.9;
  const isMediumConfidence = confidence >= 0.7;

  return (
    <span
      className={`inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-xs ${
        isHighConfidence
          ? 'bg-success/20 text-success'
          : isMediumConfidence
            ? 'bg-warning/20 text-warning'
            : 'bg-base-content/10 text-base-content/50'
      }`}
    >
      {sourceType === 'chunk' ? (
        <>
          <LuQuote size={10} />
          Direct
        </>
      ) : (
        <>
          <LuBookOpen size={10} />
          Book
        </>
      )}
    </span>
  );
};

const EvidenceSection: React.FC<EvidenceSectionProps> = ({
  evidence,
  isLoading = false,
  onOpenInReader,
}) => {
  const _ = useTranslation();

  const handleOpenPassage = (passage: EvidencePassage) => {
    if (onOpenInReader) {
      onOpenInReader(passage);
    } else {
      // TODO: Navigate to source in reader using CFI
      console.log('Opening passage:', passage);
    }
  };

  if (isLoading) {
    return (
      <section className='space-y-4'>
        <div className='flow-section-header'>
          <LuSparkles size={12} />
          {_('Evidence')}
        </div>
        <div className='flow-card flex items-center justify-center p-6'>
          <span className='loading loading-spinner loading-sm text-primary'></span>
        </div>
      </section>
    );
  }

  if (evidence.length === 0) {
    return null;
  }

  // Separate high-confidence chunks from book mentions
  const directEvidence = evidence.filter((e) => e.sourceType === 'chunk');
  const bookMentions = evidence.filter((e) => e.sourceType === 'book');

  return (
    <section className='space-y-4'>
      <div className='flow-section-header'>
        <LuQuote size={12} />
        {_('Evidence')} ({evidence.length})
      </div>

      <div className='space-y-3'>
        {/* Direct evidence (high confidence chunks) */}
        {directEvidence.map((passage) => (
          <button
            key={passage.id}
            className='flow-card cursor-pointer p-4 transition-all hover:shadow-md w-full text-left'
            onClick={() => handleOpenPassage(passage)}
          >
            <div className='mb-2 flex items-start justify-between gap-2'>
              <span className='text-base-content/60 text-xs font-medium'>
                {passage.sourceTitle}
              </span>
              <ConfidenceBadge confidence={passage.confidence} sourceType={passage.sourceType} />
            </div>

            <blockquote className='text-base-content/80 border-primary/30 border-l-2 pl-3 text-sm italic leading-relaxed'>
              &ldquo;{passage.text.length > 200 ? `${passage.text.slice(0, 200)}...` : passage.text}
              &rdquo;
            </blockquote>

            {(passage.location?.chapter || passage.sourceAuthor) && (
              <div className='text-base-content/40 mt-2 text-xs'>
                {passage.sourceAuthor && <span>{passage.sourceAuthor}</span>}
                {passage.sourceAuthor && passage.location?.chapter && <span> · </span>}
                {passage.location?.chapter && <span>{passage.location.chapter}</span>}
              </div>
            )}
          </button>
        ))}

        {/* Book mentions (lower confidence) */}
        {bookMentions.length > 0 && (
          <div className='flow-card p-4'>
            <div className='text-base-content/60 mb-2 text-xs font-medium'>
              {_('Also mentioned in')}:
            </div>
            <ul className='space-y-1.5'>
              {bookMentions.map((passage) => (
                <li key={passage.id}>
                  <button
                    className='text-base-content/70 hover:text-primary flex w-full items-center gap-2 text-left text-sm transition-colors'
                    onClick={() => handleOpenPassage(passage)}
                  >
                    <LuBookOpen size={12} className='flex-shrink-0' />
                    <span className='truncate'>{passage.sourceTitle}</span>
                    {passage.sourceAuthor && (
                      <span className='text-base-content/40 flex-shrink-0 text-xs'>
                        by {passage.sourceAuthor}
                      </span>
                    )}
                  </button>
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </section>
  );
};

export default EvidenceSection;
