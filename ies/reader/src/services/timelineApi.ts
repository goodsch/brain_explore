/**
 * Journey Timeline API client for IES Reader.
 *
 * Aggregates exploration history across contexts, showing entity visits,
 * questions asked, highlights created, and other journey events.
 */

import type { JourneyTimelineRequest, JourneyTimelineResponse } from '../types/api';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8081';

class TimelineApiClient {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE) {
    this.baseUrl = baseUrl;
  }

  /**
   * Get timeline with flexible filtering and grouping.
   */
  async getTimeline(request: JourneyTimelineRequest): Promise<JourneyTimelineResponse> {
    const res = await fetch(`${this.baseUrl}/journey-timeline`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(request),
    });

    if (!res.ok) {
      throw new Error(`Failed to fetch timeline: ${res.statusText}`);
    }

    return res.json();
  }

  /**
   * Get timeline for a specific context.
   */
  async getContextTimeline(
    contextId: string,
    grouping: JourneyTimelineRequest['grouping'] = 'by_day'
  ): Promise<JourneyTimelineResponse> {
    const res = await fetch(
      `${this.baseUrl}/journey-timeline/context/${contextId}?grouping=${grouping}`
    );

    if (!res.ok) {
      throw new Error(`Failed to fetch context timeline: ${res.statusText}`);
    }

    return res.json();
  }

  /**
   * Get timeline for a specific user.
   */
  async getUserTimeline(
    userId: string,
    grouping: JourneyTimelineRequest['grouping'] = 'by_day'
  ): Promise<JourneyTimelineResponse> {
    const res = await fetch(
      `${this.baseUrl}/journey-timeline/user/${userId}?grouping=${grouping}`
    );

    if (!res.ok) {
      throw new Error(`Failed to fetch user timeline: ${res.statusText}`);
    }

    return res.json();
  }

  /**
   * Get timeline statistics.
   */
  async getStats(): Promise<{
    total_entries: number;
    unique_entities: number;
    time_span_days: number;
    most_active_day: string | null;
  }> {
    const res = await fetch(`${this.baseUrl}/journey-timeline/stats`);

    if (!res.ok) {
      throw new Error(`Failed to fetch timeline stats: ${res.statusText}`);
    }

    return res.json();
  }
}

// Singleton instance
export const timelineApi = new TimelineApiClient();

// Export class for testing/custom instances
export { TimelineApiClient };
