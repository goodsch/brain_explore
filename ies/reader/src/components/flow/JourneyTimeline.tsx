/**
 * JourneyTimeline - Timeline view of exploration history
 *
 * Displays grouped timeline entries showing entity visits, questions asked,
 * highlights created, and other journey events.
 */

import { useState } from 'react';
import type { JourneyTimelineResponse, TimelineGroup, TimelineGrouping } from '../../types/api';
import './journey-timeline.css';

interface JourneyTimelineProps {
  timeline: JourneyTimelineResponse | null;
  isLoading?: boolean;
  onGroupingChange?: (grouping: TimelineGrouping) => void;
}

const ENTRY_TYPE_ICONS: Record<string, string> = {
  entity_visit: '🔍',
  question_asked: '❓',
  question_answered: '✅',
  highlight_created: '✏️',
  note_taken: '📝',
  concept_formalized: '💡',
  extraction_run: '🔬',
  search_performed: '🔎',
  facet_explored: '🧩',
  context_created: '📂',
  session_started: '▶️',
  session_ended: '⏹️',
};

export function JourneyTimeline({ timeline, isLoading, onGroupingChange }: JourneyTimelineProps) {
  const [selectedGrouping, setSelectedGrouping] = useState<TimelineGrouping>('by_day');

  const handleGroupingChange = (grouping: TimelineGrouping) => {
    setSelectedGrouping(grouping);
    onGroupingChange?.(grouping);
  };

  if (isLoading) {
    return (
      <div className="journey-timeline">
        <div className="journey-timeline__loading">
          <div className="journey-timeline__spinner" />
          <span>Loading timeline...</span>
        </div>
      </div>
    );
  }

  if (!timeline || timeline.total_entries === 0) {
    return (
      <div className="journey-timeline">
        <div className="journey-timeline__empty">
          <p>No journey entries yet</p>
          <p className="journey-timeline__hint">
            Start exploring to build your journey history
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="journey-timeline">
      <div className="journey-timeline__header">
        <h3 className="journey-timeline__title">
          Journey Timeline
          <span className="journey-timeline__count">{timeline.total_entries}</span>
        </h3>
        <select
          className="journey-timeline__grouping"
          value={selectedGrouping}
          onChange={(e) => handleGroupingChange(e.target.value as TimelineGrouping)}
        >
          <option value="by_day">By Day</option>
          <option value="by_week">By Week</option>
          <option value="by_session">By Session</option>
          <option value="by_context">By Context</option>
          <option value="flat">Flat</option>
        </select>
      </div>

      {timeline.total_dwell_time > 0 && (
        <div className="journey-timeline__stats">
          <span className="journey-timeline__stat">
            Total time: {Math.round(timeline.total_dwell_time / 60)} min
          </span>
          <span className="journey-timeline__stat">
            {timeline.total_groups} {selectedGrouping === 'by_day' ? 'days' : 'groups'}
          </span>
        </div>
      )}

      <div className="journey-timeline__groups">
        {timeline.groups.map((group) => (
          <TimelineGroupView key={group.group_key} group={group} />
        ))}
      </div>
    </div>
  );
}

interface TimelineGroupViewProps {
  group: TimelineGroup;
}

function TimelineGroupView({ group }: TimelineGroupViewProps) {
  const [isExpanded, setIsExpanded] = useState(true);

  return (
    <div className="timeline-group">
      <button className="timeline-group__header" onClick={() => setIsExpanded(!isExpanded)}>
        <div className="timeline-group__label">
          <span className="timeline-group__title">{group.group_label}</span>
          <span className="timeline-group__count">{group.entry_count} entries</span>
        </div>
        <div className="timeline-group__stats">
          {group.entity_count > 0 && (
            <span className="timeline-group__stat">🔍 {group.entity_count}</span>
          )}
          {group.question_count > 0 && (
            <span className="timeline-group__stat">❓ {group.question_count}</span>
          )}
          {group.highlight_count > 0 && (
            <span className="timeline-group__stat">✏️ {group.highlight_count}</span>
          )}
        </div>
        <span className={`timeline-group__chevron ${isExpanded ? 'expanded' : ''}`}>›</span>
      </button>

      {isExpanded && (
        <div className="timeline-group__entries">
          {group.entries.map((entry) => (
            <div key={entry.id} className="timeline-entry">
              <div className="timeline-entry__icon">
                {ENTRY_TYPE_ICONS[entry.entry_type] || '•'}
              </div>
              <div className="timeline-entry__content">
                <div className="timeline-entry__header">
                  <span className="timeline-entry__title">{entry.title}</span>
                  <span className="timeline-entry__time">
                    {new Date(entry.timestamp).toLocaleTimeString('en-US', {
                      hour: 'numeric',
                      minute: '2-digit',
                    })}
                  </span>
                </div>
                {entry.description && (
                  <p className="timeline-entry__description">{entry.description}</p>
                )}
                {entry.target_name && (
                  <div className="timeline-entry__target">
                    <span className="timeline-entry__target-label">{entry.target_type}:</span>
                    <span className="timeline-entry__target-name">{entry.target_name}</span>
                  </div>
                )}
                {entry.source_title && (
                  <div className="timeline-entry__source">
                    From: {entry.source_title}
                    {entry.source_location && ` (${entry.source_location})`}
                  </div>
                )}
                {entry.dwell_time_seconds && entry.dwell_time_seconds > 0 && (
                  <div className="timeline-entry__dwell">
                    ⏱️ {Math.round(entry.dwell_time_seconds)}s
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
