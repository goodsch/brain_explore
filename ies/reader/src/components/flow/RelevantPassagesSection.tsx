/**
 * RelevantPassagesSection - Shows ranked passages for a question
 *
 * Displays passages from books that are relevant to the currently selected question.
 * Includes relevance scoring, source attribution, and keyword matching.
 */

import { useState } from 'react';
import type { PassageRankingResponse, RankedPassage } from '../../types/api';
import './relevant-passages-section.css';

interface RelevantPassagesSectionProps {
  passages: PassageRankingResponse | null;
  isLoading?: boolean;
  onNavigate?: (passage: RankedPassage) => void;
}

export function RelevantPassagesSection({
  passages,
  isLoading,
  onNavigate,
}: RelevantPassagesSectionProps) {
  const [expandedPassages, setExpandedPassages] = useState<Set<string>>(new Set());

  const togglePassage = (chunkId: string) => {
    setExpandedPassages((prev) => {
      const next = new Set(prev);
      if (next.has(chunkId)) {
        next.delete(chunkId);
      } else {
        next.add(chunkId);
      }
      return next;
    });
  };

  if (isLoading) {
    return (
      <div className="relevant-passages-section">
        <div className="relevant-passages-section__loading">
          <div className="relevant-passages-section__spinner" />
          <span>Finding relevant passages...</span>
        </div>
      </div>
    );
  }

  if (!passages || passages.passages.length === 0) {
    return (
      <div className="relevant-passages-section">
        <div className="relevant-passages-section__empty">
          <p>No relevant passages found for this question</p>
          <p className="relevant-passages-section__hint">
            Try asking a more specific question or ensure books are indexed
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="relevant-passages-section">
      <div className="relevant-passages-section__header">
        <h3 className="relevant-passages-section__title">
          Relevant Passages
          <span className="relevant-passages-section__count">{passages.passages.length}</span>
        </h3>
        {passages.keywords_used.length > 0 && (
          <div className="relevant-passages-section__keywords">
            Keywords:{' '}
            {passages.keywords_used.slice(0, 3).map((kw, idx) => (
              <span key={idx} className="relevant-passages-section__keyword">
                {kw}
              </span>
            ))}
            {passages.keywords_used.length > 3 && (
              <span className="relevant-passages-section__keyword-more">
                +{passages.keywords_used.length - 3}
              </span>
            )}
          </div>
        )}
      </div>

      <div className="relevant-passages-section__list">
        {passages.passages.map((passage) => (
          <PassageCard
            key={passage.chunk_id}
            passage={passage}
            isExpanded={expandedPassages.has(passage.chunk_id)}
            onToggle={() => togglePassage(passage.chunk_id)}
            onNavigate={onNavigate}
          />
        ))}
      </div>
    </div>
  );
}

interface PassageCardProps {
  passage: RankedPassage;
  isExpanded: boolean;
  onToggle: () => void;
  onNavigate?: (passage: RankedPassage) => void;
}

function PassageCard({ passage, isExpanded, onToggle, onNavigate }: PassageCardProps) {
  const relevancePercent = Math.round(passage.relevance_score * 100);
  const preview = passage.text.slice(0, 150);
  const needsExpand = passage.text.length > 150;

  return (
    <div className="passage-card">
      <div className="passage-card__header">
        <div className="passage-card__source">
          <span className="passage-card__title">
            {passage.source_title || 'Unknown Source'}
          </span>
          {passage.source_author && (
            <span className="passage-card__author">by {passage.source_author}</span>
          )}
          {passage.chapter && (
            <span className="passage-card__location">{passage.chapter}</span>
          )}
        </div>
        <div
          className="passage-card__relevance"
          title={`Relevance: ${relevancePercent}%`}
          style={{
            opacity: 0.5 + passage.relevance_score * 0.5,
          }}
        >
          {relevancePercent}%
        </div>
      </div>

      <div className="passage-card__text">
        {isExpanded || !needsExpand ? passage.text : `${preview}...`}
      </div>

      {(passage.keywords_matched.length > 0 || passage.concepts_mentioned.length > 0) && (
        <div className="passage-card__meta">
          {passage.keywords_matched.length > 0 && (
            <div className="passage-card__matches">
              <span className="passage-card__label">Keywords:</span>
              {passage.keywords_matched.map((kw, idx) => (
                <span key={idx} className="passage-card__tag passage-card__tag--keyword">
                  {kw}
                </span>
              ))}
            </div>
          )}
          {passage.concepts_mentioned.length > 0 && (
            <div className="passage-card__matches">
              <span className="passage-card__label">Concepts:</span>
              {passage.concepts_mentioned.map((concept, idx) => (
                <span key={idx} className="passage-card__tag passage-card__tag--concept">
                  {concept}
                </span>
              ))}
            </div>
          )}
        </div>
      )}

      <div className="passage-card__actions">
        {needsExpand && (
          <button className="passage-card__btn" onClick={onToggle}>
            {isExpanded ? 'Show less' : 'Show more'}
          </button>
        )}
        {onNavigate && (
          <button className="passage-card__btn passage-card__btn--primary" onClick={() => onNavigate(passage)}>
            Go to passage
          </button>
        )}
      </div>
    </div>
  );
}
