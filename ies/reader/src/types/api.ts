/**
 * API type definitions matching backend schemas.
 *
 * These types align with:
 * - ies/backend/src/ies_backend/schemas/visit_tracking.py
 * - ies/backend/src/ies_backend/schemas/passage.py
 * - ies/backend/src/ies_backend/schemas/journey_timeline.py
 */

// ============================================================================
// Visit Tracking Types (P1)
// ============================================================================

export type VisitScope = 'context' | 'book' | 'entity' | 'global';

export interface VisitRecord {
  user_id: string;
  scope: VisitScope;
  scope_id: string;
  last_visited_at: string;
}

export interface RecordVisitResponse {
  visit_record: VisitRecord;
  previous_visit: string | null;
}

export interface NewItemsSummary {
  scope: VisitScope;
  scope_id: string;
  last_visited_at: string | null;
  new_entities: number;
  new_highlights: number;
  new_questions: number;
  new_relationships: number;
  new_journey_entries: number;
}

export interface NewEntity {
  name: string;
  type: string;
  created_at: string;
  source?: string;
}

export interface NewHighlight {
  id: string;
  book_id: string;
  text: string;
  created_at: string;
  context_id?: string;
}

export interface NewQuestion {
  id: string;
  text: string;
  context_id: string;
  created_at: string;
  status: string;
}

export interface NewRelationship {
  source: string;
  relationship_type: string;
  target: string;
  created_at: string;
}

export interface NewItemsDetailResponse {
  scope: VisitScope;
  scope_id: string;
  last_visited_at: string | null;
  entities: NewEntity[];
  highlights: NewHighlight[];
  questions: NewQuestion[];
  relationships: NewRelationship[];
  total_new_items: number;
}

// ============================================================================
// Passage Ranking Types (P1)
// ============================================================================

export interface RankedPassage {
  chunk_id: string;
  text: string;
  relevance_score: number;
  source_id?: string;
  source_title?: string;
  source_author?: string;
  chapter?: string;
  page?: number;
  keywords_matched: string[];
  concepts_mentioned: string[];
}

export interface PassageRankingRequest {
  max_passages?: number;
  min_score?: number;
  source_ids?: string[];
}

export interface PassageRankingResponse {
  question_id: string;
  question_text: string;
  passages: RankedPassage[];
  total_candidates: number;
  keywords_used: string[];
}

// ============================================================================
// Journey Timeline Types (P2)
// ============================================================================

export type TimelineEntryType =
  | 'entity_visit'
  | 'question_asked'
  | 'question_answered'
  | 'highlight_created'
  | 'note_taken'
  | 'concept_formalized'
  | 'extraction_run'
  | 'search_performed'
  | 'facet_explored'
  | 'context_created'
  | 'session_started'
  | 'session_ended';

export type TimelineGrouping = 'by_day' | 'by_session' | 'by_week' | 'by_context' | 'flat';

export interface JourneyTimelineEntry {
  id: string;
  timestamp: string;
  entry_type: TimelineEntryType;
  title: string;
  description?: string;
  context_id?: string;
  context_title?: string;
  focus_id?: string;
  focus_title?: string;
  target_type?: string;
  target_id?: string;
  target_name?: string;
  target_preview?: string;
  source_type?: string;
  source_id?: string;
  source_title?: string;
  source_location?: string;
  dwell_time_seconds?: number;
  previous_entry_id?: string;
  related_entry_ids: string[];
  entity_links: string[];
  tags: string[];
}

export interface TimelineGroup {
  group_key: string;
  group_label: string;
  start_time: string;
  end_time?: string;
  entry_count: number;
  entries: JourneyTimelineEntry[];
  entity_count: number;
  question_count: number;
  highlight_count: number;
  total_dwell_time: number;
}

export interface JourneyTimelineRequest {
  context_id?: string;
  focus_id?: string;
  user_id?: string;
  start_date?: string;
  end_date?: string;
  grouping?: TimelineGrouping;
  entry_types?: TimelineEntryType[];
  limit?: number;
  offset?: number;
}

export interface JourneyTimelineResponse {
  groups: TimelineGroup[];
  total_entries: number;
  total_groups: number;
  date_range: Record<string, string>;
  entry_type_counts: Record<string, number>;
  contexts_involved: string[];
  total_dwell_time: number;
}
