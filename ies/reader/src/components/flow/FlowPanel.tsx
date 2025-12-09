import { useEffect } from 'react';
import { useFlowStore } from '../../store/flowStore';
import { QuestionSelector } from './QuestionSelector';
import { WhatsNewSection } from './WhatsNewSection';
import { RelevantPassagesSection } from './RelevantPassagesSection';
import { FlowPanelTabs } from './FlowPanelTabs';
import { JourneyTimeline } from './JourneyTimeline';
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
    // P1 features
    newItemsDetail,
    isLoadingNewItems,
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
