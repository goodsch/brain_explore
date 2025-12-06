import { useCallback } from 'react';
import { useFlowStore } from '../store/flowStore';
import { graphClient } from '../services/graphClient';

export function useEntityLookup() {
  const {
    setCurrentEntity,
    setRelationships,
    setBookSources,
    setThinkingPartnerQuestions,
    setIsLoadingEntity,
    setIsLoadingQuestions,
    setFlowPanelOpen,
    addJourneyStep,
    clearEntity,
  } = useFlowStore();

  const lookupEntity = useCallback(
    async (selectedText: string) => {
      if (!selectedText.trim()) return;

      // Clear previous and show panel
      clearEntity();
      setFlowPanelOpen(true);
      setIsLoadingEntity(true);

      try {
        // Search for entities matching the selected text
        const searchResult = await graphClient.searchEntities(selectedText);

        if (searchResult.entities.length === 0) {
          setIsLoadingEntity(false);
          return;
        }

        // Use the first (best) match
        const entity = searchResult.entities[0];
        setCurrentEntity(entity);

        // Get full details (relationships, sources)
        const details = await graphClient.exploreEntity(entity.id);
        setRelationships(details.relationships);
        setBookSources(details.sources);
        setIsLoadingEntity(false);

        // Add to journey
        addJourneyStep(entity.id, entity.name, selectedText);

        // Fetch thinking partner questions (async, non-blocking)
        setIsLoadingQuestions(true);
        try {
          const questions = await graphClient.getThinkingPartnerQuestions(
            entity.id,
            selectedText
          );
          setThinkingPartnerQuestions(questions);
        } catch (err) {
          console.warn('Failed to fetch questions:', err);
        } finally {
          setIsLoadingQuestions(false);
        }
      } catch (error) {
        console.error('Entity lookup failed:', error);
        setIsLoadingEntity(false);
      }
    },
    [
      setCurrentEntity,
      setRelationships,
      setBookSources,
      setThinkingPartnerQuestions,
      setIsLoadingEntity,
      setIsLoadingQuestions,
      setFlowPanelOpen,
      addJourneyStep,
      clearEntity,
    ]
  );

  const navigateToEntity = useCallback(
    async (entityId: string) => {
      setIsLoadingEntity(true);

      try {
        const entity = await graphClient.getEntity(entityId);
        setCurrentEntity(entity);

        const details = await graphClient.exploreEntity(entityId);
        setRelationships(details.relationships);
        setBookSources(details.sources);
        setIsLoadingEntity(false);

        addJourneyStep(entity.id, entity.name);

        // Fetch questions
        setIsLoadingQuestions(true);
        try {
          const questions = await graphClient.getThinkingPartnerQuestions(entityId);
          setThinkingPartnerQuestions(questions);
        } catch {
          // Ignore question fetch errors
        } finally {
          setIsLoadingQuestions(false);
        }
      } catch (error) {
        console.error('Navigate to entity failed:', error);
        setIsLoadingEntity(false);
      }
    },
    [
      setCurrentEntity,
      setRelationships,
      setBookSources,
      setThinkingPartnerQuestions,
      setIsLoadingEntity,
      setIsLoadingQuestions,
      addJourneyStep,
    ]
  );

  return { lookupEntity, navigateToEntity };
}
