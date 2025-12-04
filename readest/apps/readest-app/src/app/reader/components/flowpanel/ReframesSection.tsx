import React, { useCallback, useEffect, useMemo, useState } from 'react';
import { LuCircleAlert, LuRefreshCw, LuSparkles, LuThumbsDown, LuThumbsUp } from 'react-icons/lu';

import { useTranslation } from '@/hooks/useTranslation';

const DEFAULT_API_BASE =
  typeof window !== 'undefined' && window.location.hostname !== 'localhost'
    ? `http://${window.location.hostname}:8081`
    : 'http://localhost:8081';

interface Reframe {
  id: string;
  type: string;
  text?: string;
  content?: string;
  explanation?: string;
  createdAt?: string;
}

type FeedbackState = 'idle' | 'pending' | 'up' | 'down' | 'error';

interface ReframesSectionProps {
  conceptId: string;
}

const typeBadgeMap: Record<string, string> = {
  metaphor: 'badge-primary',
  analogy: 'badge-secondary',
  story: 'badge-accent',
  experiment: 'badge-info',
  question: 'badge-warning',
};

const parseReframesResponse = (payload: unknown): Reframe[] => {
  if (!payload) return [];
  if (Array.isArray(payload)) return payload as Reframe[];
  if (typeof payload === 'object' && payload !== null) {
    const maybe = (payload as { reframes?: Reframe[] }).reframes;
    return Array.isArray(maybe) ? maybe : [];
  }
  return [];
};

const ReframesSection: React.FC<ReframesSectionProps> = ({ conceptId }) => {
  const _ = useTranslation();
  const [reframes, setReframes] = useState<Reframe[]>([]);
  const [loading, setLoading] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [feedbackStatus, setFeedbackStatus] = useState<Record<string, FeedbackState>>({});

  const getTypeLabel = useCallback(
    (type: string) => {
      const normalized = type?.toLowerCase();
      const labels: Record<string, string> = {
        metaphor: _('Metaphor'),
        analogy: _('Analogy'),
        story: _('Story'),
        experiment: _('Experiment'),
        question: _('Question'),
      };
      return labels[normalized] || type?.replace(/_/g, ' ');
    },
    [_]
  );

  const getTypeBadge = useCallback(
    (type: string) => typeBadgeMap[type?.toLowerCase()] || 'badge-outline',
    []
  );

  const fetchReframes = useCallback(async () => {
    if (!conceptId) return;
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(
        `${DEFAULT_API_BASE}/reframes/concepts/${encodeURIComponent(conceptId)}/reframes`
      );
      if (!response.ok) {
        throw new Error(_('Unable to load reframes right now.'));
      }
      const data = await response.json();
      setReframes(parseReframesResponse(data));
    } catch (err) {
      setError(err instanceof Error ? err.message : _('Something went wrong fetching reframes.'));
      setReframes([]);
    } finally {
      setLoading(false);
    }
  }, [conceptId, _]);

  const handleGenerateReframes = async () => {
    if (!conceptId) return;
    setIsGenerating(true);
    setError(null);
    try {
      const response = await fetch(
        `${DEFAULT_API_BASE}/reframes/concepts/${encodeURIComponent(conceptId)}/reframes/generate`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
        }
      );
      if (!response.ok) {
        throw new Error(_('Unable to generate reframes right now.'));
      }
      await fetchReframes();
    } catch (err) {
      setError(err instanceof Error ? err.message : _('Something went wrong generating reframes.'));
    } finally {
      setIsGenerating(false);
    }
  };

  const handleFeedback = async (reframeId: string, direction: 'up' | 'down') => {
    setFeedbackStatus((prev) => ({ ...prev, [reframeId]: 'pending' }));
    try {
      const response = await fetch(`${DEFAULT_API_BASE}/reframes/reframes/${reframeId}/feedback`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ vote: direction === 'up' ? 'helpful' : 'confusing' }),
      });
      if (!response.ok) {
        throw new Error(_('Unable to send feedback.'));
      }
      setFeedbackStatus((prev) => ({ ...prev, [reframeId]: direction }));
    } catch (err) {
      console.error(err);
      setFeedbackStatus((prev) => ({ ...prev, [reframeId]: 'error' }));
    }
  };

  useEffect(() => {
    fetchReframes();
  }, [fetchReframes]);

  const groupedReframes = useMemo(() => {
    return reframes.reduce<Record<string, Reframe[]>>((acc, reframe) => {
      const type = reframe.type || 'other';
      if (!acc[type]) acc[type] = [];
      acc[type]!.push(reframe);
      return acc;
    }, {});
  }, [reframes]);

  const renderFeedbackButtons = (reframe: Reframe) => {
    const status = feedbackStatus[reframe.id] || 'idle';
    const isPending = status === 'pending';

    return (
      <div className='flex items-center gap-1'>
        <button
          className={`btn btn-ghost btn-xs px-2 ${status === 'up' ? 'text-success' : ''}`}
          onClick={() => handleFeedback(reframe.id, 'up')}
          disabled={isPending}
        >
          {isPending && status !== 'down' && status !== 'up' ? (
            <span className='loading loading-spinner loading-xs'></span>
          ) : (
            <LuThumbsUp size={14} />
          )}
        </button>
        <button
          className={`btn btn-ghost btn-xs px-2 ${status === 'down' ? 'text-error' : ''}`}
          onClick={() => handleFeedback(reframe.id, 'down')}
          disabled={isPending}
        >
          {isPending && status !== 'down' && status !== 'up' ? (
            <span className='loading loading-spinner loading-xs'></span>
          ) : (
            <LuThumbsDown size={14} />
          )}
        </button>
      </div>
    );
  };

  const renderContent = () => {
    if (loading && reframes.length === 0) {
      return (
        <div className='flex h-28 items-center justify-center rounded-lg bg-base-100'>
          <span className='loading loading-spinner loading-sm'></span>
        </div>
      );
    }

    if (!loading && reframes.length === 0) {
      return (
        <div className='rounded-lg border border-dashed border-base-300 p-4 text-center text-sm text-base-content/70'>
          {_('No reframes yet. Click Generate to create metaphors and analogies.')}
        </div>
      );
    }

    return (
      <div className='space-y-3'>
        {Object.entries(groupedReframes).map(([type, items]) => (
          <div key={type} className='rounded-lg bg-base-100 p-3'>
            <div className='mb-2 flex items-center gap-2'>
              <span className={`badge badge-xs ${getTypeBadge(type)}`}>{getTypeLabel(type)}</span>
              <span className='text-xs text-base-content/50'>
                {items.length} {_('entries')}
              </span>
            </div>

            <ul className='space-y-3'>
              {items.map((reframe) => (
                <li key={reframe.id} className='rounded-lg border border-base-200 p-3'>
                  <p className='text-sm leading-relaxed'>{reframe.text || reframe.content}</p>
                  {reframe.explanation && (
                    <p className='text-base-content/60 mt-2 text-xs'>{reframe.explanation}</p>
                  )}
                  <div className='mt-3 flex items-center justify-between text-xs text-base-content/60'>
                    <span>
                      {reframe.createdAt
                        ? new Date(reframe.createdAt).toLocaleString()
                        : _('Freshly generated insight')}
                    </span>
                    {renderFeedbackButtons(reframe)}
                  </div>
                  {feedbackStatus[reframe.id] === 'error' && (
                    <p className='text-error mt-1 text-xs'>{_('We could not record your feedback')}</p>
                  )}
                </li>
              ))}
            </ul>
          </div>
        ))}
      </div>
    );
  };

  return (
    <section className='space-y-3'>
      <div className='flex items-center justify-between'>
        <div className='text-base-content/60 flex items-center gap-1 text-xs font-medium uppercase'>
          <LuSparkles size={12} />
          {_('Reframes')}
        </div>
        <button
          className='btn btn-primary btn-xs gap-1'
          onClick={handleGenerateReframes}
          disabled={isGenerating || loading}
        >
          {isGenerating ? (
            <span className='loading loading-spinner loading-xs'></span>
          ) : (
            <LuRefreshCw size={12} />
          )}
          {_('Generate')}
        </button>
      </div>

      {error && (
        <div className='text-error bg-error/10 flex items-center gap-2 rounded-lg px-3 py-2 text-xs'>
          <LuCircleAlert size={14} />
          <span>{error}</span>
        </div>
      )}

      {renderContent()}
    </section>
  );
};

export default ReframesSection;
