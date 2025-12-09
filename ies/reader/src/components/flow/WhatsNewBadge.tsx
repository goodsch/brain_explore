/**
 * WhatsNewBadge - Small badge showing count of new items
 *
 * Displays new questions, highlights, entities, or relationships.
 * Renders nothing if count === 0.
 */

import type { NewItemsSummary } from '../../types/api';
import './whats-new-badge.css';

interface WhatsNewBadgeProps {
  summary: NewItemsSummary | null;
  isLoading?: boolean;
}

export function WhatsNewBadge({ summary, isLoading }: WhatsNewBadgeProps) {
  if (isLoading) {
    return (
      <span className="whats-new-badge whats-new-badge--loading">
        <span className="whats-new-badge__spinner" />
      </span>
    );
  }

  if (!summary) return null;

  const totalNew =
    summary.new_questions +
    summary.new_highlights +
    summary.new_entities +
    summary.new_relationships;

  if (totalNew === 0) return null;

  return (
    <span className="whats-new-badge" title={`${totalNew} new items since last visit`}>
      {totalNew}
    </span>
  );
}
