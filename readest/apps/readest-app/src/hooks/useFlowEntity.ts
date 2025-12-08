/**
 * useFlowEntity Hook
 *
 * Provides entity lookup and data fetching for Flow mode.
 * Integrates the Graph API client with the Flow mode store.
 */

import { useCallback } from 'react';
import { useFlowModeStore, EntityRelationship } from '@/store/flowModeStore';
import { getGraphClient } from '@/services/flow/graphClient';

interface UseFlowEntityOptions {
  apiBaseUrl?: string;
}

export function useFlowEntity(options: UseFlowEntityOptions = {}) {
  const {
    setCurrentEntity,
    setRelationships,
    setBookSources,
    setEvidence,
    setThinkingPartnerQuestions,
    setIsLoadingEntity,
    setIsLoadingEvidence,
    setIsLoadingQuestions,
    addJourneyStep,
    currentJourney,
  } = useFlowModeStore();

  const client = getGraphClient({ baseUrl: options.apiBaseUrl });

  /**
   * Fetch entity by ID and update store
   */
  const fetchEntity = useCallback(
    async (entityId: string) => {
      setIsLoadingEntity(true);

      try {
        // Fetch entity details
        const response = await client.getEntity(entityId);

        // Update store with entity data
        setCurrentEntity(response.entity);
        setRelationships(response.relationships);
        setBookSources(response.sources);

        // Add to journey path
        addJourneyStep(response.entity.id, response.entity.name);

        // Fetch thinking partner questions and evidence asynchronously
        fetchQuestions(entityId);
        fetchEvidence(entityId);
      } catch (error) {
        console.error('Failed to fetch entity:', error);
        setCurrentEntity(null);
        setRelationships([]);
        setBookSources([]);
        setEvidence([]);
      } finally {
        setIsLoadingEntity(false);
      }
    },
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [
      client,
      setCurrentEntity,
      setRelationships,
      setBookSources,
      setEvidence,
      setIsLoadingEntity,
      addJourneyStep,
      // Note: fetchQuestions and fetchEvidence intentionally omitted to avoid circular dependency
      // They are stable references created with useCallback
    ]
  );

  /**
   * Search for entities and return matches
   */
  const searchEntities = useCallback(
    async (query: string, limit = 10) => {
      try {
        return await client.searchEntities(query, limit);
      } catch (error) {
        console.error('Failed to search entities:', error);
        return [];
      }
    },
    [client]
  );

  /**
   * Fetch thinking partner questions for current entity
   */
  const fetchQuestions = useCallback(
    async (entityId: string) => {
      setIsLoadingQuestions(true);

      try {
        // Build context from current journey
        const recentPath = currentJourney?.path.slice(-5).map((step) => step.entityId) || [];

        const questions = await client.getThinkingPartnerQuestions(entityId, {
          recentPath,
          userProfileId: currentJourney?.userId,
        });

        setThinkingPartnerQuestions(questions);
      } catch (error) {
        console.error('Failed to fetch thinking partner questions:', error);
        setThinkingPartnerQuestions([]);
      } finally {
        setIsLoadingQuestions(false);
      }
    },
    [client, currentJourney, setThinkingPartnerQuestions, setIsLoadingQuestions]
  );

  /**
   * Fetch evidence passages for current entity (Sprint 2)
   */
  const fetchEvidence = useCallback(
    async (entityId: string, limit = 10) => {
      setIsLoadingEvidence(true);

      try {
        const evidence = await client.getEntityEvidence(entityId, limit);
        setEvidence(evidence);
      } catch (error) {
        console.error('Failed to fetch evidence:', error);
        setEvidence([]);
      } finally {
        setIsLoadingEvidence(false);
      }
    },
    [client, setEvidence, setIsLoadingEvidence]
  );

  /**
   * Explore neighborhood of current entity
   */
  const exploreNeighborhood = useCallback(
    async (entityId: string, depth = 1, limit = 20) => {
      try {
        const response = await client.exploreNeighborhood(entityId, depth, limit);

        // Convert neighbors to relationships format
        const relationships: EntityRelationship[] = response.neighbors.map((neighbor) => ({
          type: neighbor.relationship,
          target: neighbor.entity,
        }));

        setRelationships(relationships);
        return response;
      } catch (error) {
        console.error('Failed to explore neighborhood:', error);
        return null;
      }
    },
    [client, setRelationships]
  );

  /**
   * Lookup entity from text selection
   * Searches for matching entities and fetches the best match
   */
  const lookupFromSelection = useCallback(
    async (selectedText: string) => {
      if (!selectedText.trim()) return null;

      try {
        // Search for matching entities
        const matches = await searchEntities(selectedText.trim(), 5);

        if (matches.length > 0) {
          // Fetch the best match
          await fetchEntity(matches[0]!.id);
          return matches[0];
        }

        return null;
      } catch (error) {
        console.error('Failed to lookup entity from selection:', error);
        return null;
      }
    },
    [searchEntities, fetchEntity]
  );

  return {
    fetchEntity,
    searchEntities,
    fetchQuestions,
    fetchEvidence,
    exploreNeighborhood,
    lookupFromSelection,
  };
}

export default useFlowEntity;
