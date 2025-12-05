import React, { useState } from 'react';
import { LuMessageCircleQuestion, LuRefreshCw, LuChevronDown, LuChevronUp } from 'react-icons/lu';

import { useTranslation } from '@/hooks/useTranslation';
import { ThinkingPartnerQuestion, useFlowModeStore } from '@/store/flowModeStore';

interface QuestionsSectionProps {
  questions: ThinkingPartnerQuestion[];
}

const QuestionsSection: React.FC<QuestionsSectionProps> = ({ questions }) => {
  const _ = useTranslation();
  const { isLoadingQuestions, addThinkingPartnerExchange, addJourneyMark } = useFlowModeStore();
  const [expandedIndex, setExpandedIndex] = useState<number | null>(null);

  const getQuestionTypeColor = (type: ThinkingPartnerQuestion['type']): string => {
    const colors: Record<string, string> = {
      clarifying: 'border-l-info',
      connecting: 'border-l-primary',
      challenging: 'border-l-warning',
    };
    return colors[type] || 'border-l-base-content';
  };

  const getQuestionTypeLabel = (type: ThinkingPartnerQuestion['type']): string => {
    const labels: Record<string, string> = {
      clarifying: _('Clarifying'),
      connecting: _('Connecting'),
      challenging: _('Challenging'),
    };
    return labels[type] || type;
  };

  const handleQuestionClick = (question: ThinkingPartnerQuestion, index: number) => {
    // Toggle expanded state
    setExpandedIndex(expandedIndex === index ? null : index);

    // Track the question engagement
    addThinkingPartnerExchange(question.text);
  };

  const handleSaveQuestion = (question: ThinkingPartnerQuestion) => {
    // Save as a journey mark for later reflection
    addJourneyMark({
      type: 'question',
      entityId: '', // Would be current entity ID
      content: question.text,
    });
  };

  const handleRefreshQuestions = () => {
    // TODO: Fetch new questions from the backend
    console.log('Refreshing thinking partner questions');
  };

  if (questions.length === 0 && !isLoadingQuestions) {
    return null;
  }

  return (
    <section className='space-y-3'>
      <div className='flex items-center justify-between'>
        <div className='text-base-content/60 flex items-center gap-1 text-xs font-medium uppercase'>
          <LuMessageCircleQuestion size={12} />
          {_('Thinking Partner')}
        </div>
        <button
          className='btn btn-ghost btn-xs'
          onClick={handleRefreshQuestions}
          disabled={isLoadingQuestions}
          title={_('Get new questions')}
        >
          <LuRefreshCw size={12} className={isLoadingQuestions ? 'animate-spin' : ''} />
        </button>
      </div>

      {isLoadingQuestions ? (
        <div className='bg-base-100 flex items-center justify-center rounded-lg p-4'>
          <span className='loading loading-dots loading-sm'></span>
        </div>
      ) : (
        <div className='space-y-2'>
          {questions.map((question, index) => (
            <div
              key={index}
              className={`bg-base-100 rounded-lg border-l-4 ${getQuestionTypeColor(question.type)}`}
            >
              <button
                className='flex w-full items-start justify-between gap-2 p-3 text-left'
                onClick={() => handleQuestionClick(question, index)}
              >
                <div className='flex-grow'>
                  <div className='text-base-content/50 mb-1 text-xs'>
                    {getQuestionTypeLabel(question.type)}
                  </div>
                  <p className='text-sm leading-relaxed'>{question.text}</p>
                </div>
                {expandedIndex === index ? (
                  <LuChevronUp size={16} className='text-base-content/50 flex-shrink-0' />
                ) : (
                  <LuChevronDown size={16} className='text-base-content/50 flex-shrink-0' />
                )}
              </button>

              {expandedIndex === index && (
                <div className='border-base-200 border-t px-3 pb-3 pt-2'>
                  {question.relatedEntities && question.relatedEntities.length > 0 && (
                    <div className='mb-2'>
                      <span className='text-base-content/50 text-xs'>{_('Related')}:</span>
                      <div className='mt-1 flex flex-wrap gap-1'>
                        {question.relatedEntities.map((entity, i) => (
                          <span key={i} className='badge badge-outline badge-xs'>
                            {entity}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                  <button
                    className='btn btn-ghost btn-xs text-primary'
                    onClick={() => handleSaveQuestion(question)}
                  >
                    {_('Save for later')}
                  </button>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </section>
  );
};

export default QuestionsSection;
