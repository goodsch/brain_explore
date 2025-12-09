import { useEffect } from 'react';
import { useFlowStore } from '../../store/flowStore';
import { QuestionSelector } from './QuestionSelector';
import { AreasChips } from './AreasChips';
import { WhatsNewSection } from './WhatsNewSection';
import { RelevantPassagesSection } from './RelevantPassagesSection';
import { FlowPanelTabs } from './FlowPanelTabs';
import { JourneyTimeline } from './JourneyTimeline';
import { RunExtractionButton } from './RunExtractionButton';
import { useFlowLayout } from '../../hooks/useFlowLayout';
import { useQuestionSync } from '../../hooks/useQuestionSync';
import './flow-panel.css';

export function FlowPanel() {
  const {
    isFlowPanelOpen,
    questions,
    currentQuestionId,
    isLoadingQuestions,
    setCurrentQuestionId,
    currentEntity,
    // Context for extraction and areas
    currentContextId,
    currentContext,
    selectedArea,
    setSelectedArea,
    // P1 features
    newItemsDetail,
    isLoadingNewItems,
    recordVisit,
    fetchNewItemsSummary,
    fetchNewItemsDetail,
    relevantPassages,
    isLoadingPassages,
    fetchRelevantPassages,
    clearRelevantPassages,
    // P2 features
    activePanelTab,
    setActivePanelTab,
    journeyTimeline,
    isLoadingTimeline,
    fetchTimeline,
  } = useFlowStore();

  const { mode, isMobile } = useFlowLayout();
  const { createQuestion, error } = useQuestionSync();

  // Don't render if closed or if on mobile (use standalone FlowPage instead)
  if (!isFlowPanelOpen || (isMobile && mode === 'standalone')) return null;

  // When panel opens, record visit and fetch "What's New"
  useEffect(() => {
    if (isFlowPanelOpen) {
      // Record the visit
      recordVisit('global', 'global');
      // Fetch summary for badge
      fetchNewItemsSummary('global', 'global');
      // Fetch detailed new items for section
      fetchNewItemsDetail('global', 'global');
    }
  }, [isFlowPanelOpen, recordVisit, fetchNewItemsSummary, fetchNewItemsDetail]);

  // When question changes, fetch relevant passages
  useEffect(() => {
    if (currentQuestionId) {
      fetchRelevantPassages(currentQuestionId);
    } else {
      clearRelevantPassages();
    }
  }, [currentQuestionId, fetchRelevantPassages, clearRelevantPassages]);

  // Fetch timeline when timeline tab is active
  useEffect(() => {
    if (activePanelTab === 'timeline' && !journeyTimeline) {
      fetchTimeline();
    }
  }, [activePanelTab, journeyTimeline, fetchTimeline]);

  const handleCreateQuestion = async (text: string) => {
    await createQuestion(text);
  };

  const handleRefreshNewItems = () => {
    // Refresh for global scope
    fetchNewItemsDetail('global', 'global');
  };

  const handleTimelineGroupingChange = (grouping: string) => {
    fetchTimeline(undefined, grouping);
  };

  const handleSelectArea = (area: string | null) => {
    setSelectedArea(area);
    // TODO: Could trigger filtered entity search or other area-specific behavior
    console.log('Selected area:', area);
  };

  // Get areas from current context
  const areas = currentContext?.areas_of_exploration || [];

  return (
    <div className="flow-panel">
      <div className="flow-panel__header">
        <h2 className="flow-panel__title">Flow</h2>
      </div>

      <FlowPanelTabs activeTab={activePanelTab} onTabChange={setActivePanelTab} />

      {error && (
        <div className="flow-panel__error">
          {error}
        </div>
      )}

      {activePanelTab === 'explore' ? (
        <>
          {/* What's New Section */}
          {newItemsDetail && (
            <WhatsNewSection
              detail={newItemsDetail}
              isLoading={isLoadingNewItems}
              onRefresh={handleRefreshNewItems}
            />
          )}

          {/* Extraction Button - shown when context is active */}
          {currentContextId && (
            <div className="flow-panel__extraction">
              <RunExtractionButton
                contextId={currentContextId}
                questionId={currentQuestionId || undefined}
              />
            </div>
          )}

          {/* Areas of Exploration - shown when context has areas */}
          {areas.length > 0 && (
            <div className="flow-panel__areas">
              <AreasChips
                areas={areas}
                selectedArea={selectedArea}
                onSelectArea={handleSelectArea}
              />
            </div>
          )}

          {/* Question Selector */}
          <div className="flow-panel__question-selector">
            <QuestionSelector
              questions={questions}
              currentQuestionId={currentQuestionId}
              onSelect={setCurrentQuestionId}
              onCreate={handleCreateQuestion}
              isLoading={isLoadingQuestions}
            />
          </div>

          {/* Relevant Passages Section (shown when question selected) */}
          {currentQuestionId && (
            <RelevantPassagesSection
              passages={relevantPassages}
              isLoading={isLoadingPassages}
            />
          )}

          {/* Entity/Content Section */}
          <div className="flow-panel__content">
            {currentEntity ? (
              <div className="flow-panel__entity">
                <h3 className="flow-panel__entity-name">{currentEntity.name}</h3>
                {/* Entity details will be expanded in future phases */}
              </div>
            ) : (
              <div className="flow-panel__empty">
                <p>Select a question to start exploring, or select text in the book to look up entities.</p>
              </div>
            )}
          </div>
        </>
      ) : (
        /* Timeline Tab */
        <JourneyTimeline
          timeline={journeyTimeline}
          isLoading={isLoadingTimeline}
          onGroupingChange={handleTimelineGroupingChange}
        />
      )}
    </div>
  );
}
