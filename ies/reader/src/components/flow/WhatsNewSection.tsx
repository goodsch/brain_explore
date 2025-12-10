/**
 * WhatsNewSection - Collapsible section showing new items since last visit
 *
 * Displays expandable lists of new questions, highlights, entities, and relationships.
 */

import { useState } from 'react';
import type { NewItemsDetailResponse } from '../../types/api';
import './whats-new-section.css';

interface WhatsNewSectionProps {
  detail: NewItemsDetailResponse | null;
  isLoading?: boolean;
  onRefresh?: () => void;
}

export function WhatsNewSection({ detail, isLoading, onRefresh }: WhatsNewSectionProps) {
  const [expandedSections, setExpandedSections] = useState<Set<string>>(new Set());

  const toggleSection = (section: string) => {
    setExpandedSections((prev) => {
      const next = new Set(prev);
      if (next.has(section)) {
        next.delete(section);
      } else {
        next.add(section);
      }
      return next;
    });
  };

  if (isLoading) {
    return (
      <div className="whats-new-section">
        <div className="whats-new-section__loading">
          <div className="whats-new-section__spinner" />
          <span>Loading new items...</span>
        </div>
      </div>
    );
  }

  if (!detail || detail.total_new_items === 0) {
    return (
      <div className="whats-new-section">
        <div className="whats-new-section__empty">
          <p>No new items since your last visit</p>
          {onRefresh && (
            <button className="whats-new-section__refresh-btn" onClick={onRefresh} aria-label="Refresh new items">
              Refresh
            </button>
          )}
        </div>
      </div>
    );
  }

  const { questions, highlights, entities, relationships } = detail;
  const hasQuestions = questions.length > 0;
  const hasHighlights = highlights.length > 0;
  const hasEntities = entities.length > 0;
  const hasRelationships = relationships.length > 0;

  return (
    <div className="whats-new-section">
      <div className="whats-new-section__header">
        <h3 className="whats-new-section__title">
          What's New
          <span className="whats-new-section__count">{detail.total_new_items}</span>
        </h3>
        {onRefresh && (
          <button className="whats-new-section__refresh-btn" onClick={onRefresh} aria-label="Refresh new items">
            Refresh
          </button>
        )}
      </div>

      {hasQuestions && (
        <div className="whats-new-section__group">
          <button
            className="whats-new-section__group-header"
            onClick={() => toggleSection('questions')}
            aria-label="Toggle questions section"
          >
            <span className="whats-new-section__group-title">
              Questions ({questions.length})
            </span>
            <span
              className={`whats-new-section__chevron ${
                expandedSections.has('questions') ? 'expanded' : ''
              }`}
            >
              ›
            </span>
          </button>
          {expandedSections.has('questions') && (
            <ul className="whats-new-section__list">
              {questions.map((q) => (
                <li key={q.id} className="whats-new-section__item">
                  <span className="whats-new-section__item-text">{q.text}</span>
                  <span className="whats-new-section__item-meta">{q.status}</span>
                </li>
              ))}
            </ul>
          )}
        </div>
      )}

      {hasHighlights && (
        <div className="whats-new-section__group">
          <button
            className="whats-new-section__group-header"
            onClick={() => toggleSection('highlights')}
            aria-label="Toggle highlights section"
          >
            <span className="whats-new-section__group-title">
              Highlights ({highlights.length})
            </span>
            <span
              className={`whats-new-section__chevron ${
                expandedSections.has('highlights') ? 'expanded' : ''
              }`}
            >
              ›
            </span>
          </button>
          {expandedSections.has('highlights') && (
            <ul className="whats-new-section__list">
              {highlights.map((h) => (
                <li key={h.id} className="whats-new-section__item">
                  <span className="whats-new-section__item-text">
                    {h.text.slice(0, 80)}
                    {h.text.length > 80 && '...'}
                  </span>
                  <span className="whats-new-section__item-meta">{h.book_id}</span>
                </li>
              ))}
            </ul>
          )}
        </div>
      )}

      {hasEntities && (
        <div className="whats-new-section__group">
          <button
            className="whats-new-section__group-header"
            onClick={() => toggleSection('entities')}
            aria-label="Toggle entities section"
          >
            <span className="whats-new-section__group-title">
              Entities ({entities.length})
            </span>
            <span
              className={`whats-new-section__chevron ${
                expandedSections.has('entities') ? 'expanded' : ''
              }`}
            >
              ›
            </span>
          </button>
          {expandedSections.has('entities') && (
            <ul className="whats-new-section__list">
              {entities.map((e, idx) => (
                <li key={idx} className="whats-new-section__item">
                  <span className="whats-new-section__item-text">{e.name}</span>
                  <span className="whats-new-section__item-meta">{e.type}</span>
                </li>
              ))}
            </ul>
          )}
        </div>
      )}

      {hasRelationships && (
        <div className="whats-new-section__group">
          <button
            className="whats-new-section__group-header"
            onClick={() => toggleSection('relationships')}
            aria-label="Toggle relationships section"
          >
            <span className="whats-new-section__group-title">
              Relationships ({relationships.length})
            </span>
            <span
              className={`whats-new-section__chevron ${
                expandedSections.has('relationships') ? 'expanded' : ''
              }`}
            >
              ›
            </span>
          </button>
          {expandedSections.has('relationships') && (
            <ul className="whats-new-section__list">
              {relationships.map((r, idx) => (
                <li key={idx} className="whats-new-section__item">
                  <span className="whats-new-section__item-text">
                    {r.source} → {r.target}
                  </span>
                  <span className="whats-new-section__item-meta">{r.relationship_type}</span>
                </li>
              ))}
            </ul>
          )}
        </div>
      )}
    </div>
  );
}
