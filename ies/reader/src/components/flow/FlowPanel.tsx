import { X, Cloud, CloudOff, AlertCircle, Loader2, BookOpen, Link2, HelpCircle } from 'lucide-react';
import { useFlowStore } from '../../store/flowStore';
import { useEntityLookup } from '../../hooks/useEntityLookup';
import { graphClient } from '../../services/graphClient';
import './FlowPanel.css';

export function FlowPanel() {
  const {
    isFlowPanelOpen,
    flowPanelWidth,
    currentEntity,
    relationships,
    bookSources,
    thinkingPartnerQuestions,
    isLoadingEntity,
    isLoadingQuestions,
    setFlowPanelOpen,
    clearEntity,
    syncStatus,
    lastSyncError,
    queuedOperationsCount,
    setSyncStatus,
    setQueuedOperationsCount,
  } = useFlowStore();

  // Handle retry sync for offline queue
  const handleRetrySync = async () => {
    if (queuedOperationsCount === 0) return;

    setSyncStatus('pending');
    try {
      const result = await graphClient.processOfflineQueue();
      const status = graphClient.getOfflineQueueStatus();
      setQueuedOperationsCount(status.queuedCount);

      if (status.queuedCount === 0) {
        setSyncStatus('synced');
      } else if (status.failedCount > 0) {
        setSyncStatus('error', `${result.failed} operations failed`);
      } else {
        setSyncStatus('offline');
      }
    } catch (error) {
      setSyncStatus('error', error instanceof Error ? error.message : 'Sync failed');
    }
  };

  const { navigateToEntity } = useEntityLookup();

  if (!isFlowPanelOpen) return null;

  // Get entity type color
  const getEntityTypeClass = (type: string) => {
    const typeMap: Record<string, string> = {
      concept: 'entity-type-concept',
      person: 'entity-type-person',
      theory: 'entity-type-theory',
      framework: 'entity-type-framework',
      assessment: 'entity-type-assessment',
    };
    return typeMap[type.toLowerCase()] || 'entity-type-default';
  };

  return (
    <div className="flow-panel" style={{ '--panel-width': `${flowPanelWidth}px` } as React.CSSProperties}>
      {/* Header */}
      <header className="flow-panel-header">
        <div className="flow-panel-title">
          <h3>Flow Mode</h3>
          {/* Sync Status Indicator */}
          {(syncStatus !== 'idle' || queuedOperationsCount > 0) && (
            <button
              className={`flow-sync-badge flow-sync-${queuedOperationsCount > 0 ? 'offline' : syncStatus}`}
              title={
                queuedOperationsCount > 0
                  ? `${queuedOperationsCount} pending - click to retry`
                  : lastSyncError || undefined
              }
              onClick={queuedOperationsCount > 0 ? handleRetrySync : undefined}
              disabled={syncStatus === 'pending'}
            >
              {syncStatus === 'pending' && <Loader2 size={12} className="flow-sync-spinner" />}
              {syncStatus === 'synced' && queuedOperationsCount === 0 && <Cloud size={12} />}
              {syncStatus === 'error' && queuedOperationsCount === 0 && <AlertCircle size={12} />}
              {queuedOperationsCount > 0 && (
                <>
                  <CloudOff size={12} />
                  <span className="flow-sync-count">{queuedOperationsCount}</span>
                </>
              )}
            </button>
          )}
        </div>
        <button
          className="flow-panel-close ies-btn ies-btn-ghost"
          onClick={() => {
            clearEntity();
            setFlowPanelOpen(false);
          }}
          aria-label="Close panel"
        >
          <X size={20} />
        </button>
      </header>

      {/* Content */}
      <div className="flow-panel-content">
        {isLoadingEntity ? (
          <div className="flow-loading">
            <Loader2 size={24} className="flow-loading-spinner" />
            <span>Searching knowledge graph...</span>
          </div>
        ) : currentEntity ? (
          <>
            {/* Entity Section */}
            <section className="flow-section flow-entity">
              <span className={`flow-entity-type ${getEntityTypeClass(currentEntity.type)}`}>
                {currentEntity.type}
              </span>
              <h2 className="flow-entity-name">{currentEntity.name}</h2>
              <p className="flow-entity-summary">{currentEntity.summary}</p>
            </section>

            {/* Relationships Section */}
            {relationships.length > 0 && (
              <section className="flow-section">
                <h4 className="flow-section-title">
                  <Link2 size={14} />
                  Related Concepts
                </h4>
                <ul className="flow-relationships">
                  {relationships.map((rel, idx) => (
                    <li key={idx}>
                      <button
                        className="flow-relationship-link"
                        onClick={() => navigateToEntity(rel.target.id)}
                      >
                        <span className="flow-relationship-type">{rel.type}</span>
                        <span className="flow-relationship-target">{rel.target.name}</span>
                      </button>
                    </li>
                  ))}
                </ul>
              </section>
            )}

            {/* Sources Section */}
            {bookSources.length > 0 && (
              <section className="flow-section">
                <h4 className="flow-section-title">
                  <BookOpen size={14} />
                  Found In
                </h4>
                <ul className="flow-sources">
                  {bookSources.map((source, idx) => (
                    <li key={idx} className="flow-source-item">
                      <span className="flow-source-title">{source.bookTitle}</span>
                      {source.chapter && (
                        <span className="flow-source-chapter">{source.chapter}</span>
                      )}
                    </li>
                  ))}
                </ul>
              </section>
            )}

            {/* Thinking Partner Questions */}
            <section className="flow-section">
              <h4 className="flow-section-title">
                <HelpCircle size={14} />
                Thinking Partner
              </h4>
              {isLoadingQuestions ? (
                <div className="flow-loading flow-loading-inline">
                  <Loader2 size={16} className="flow-loading-spinner" />
                  <span>Generating questions...</span>
                </div>
              ) : thinkingPartnerQuestions.length > 0 ? (
                <ul className="flow-questions">
                  {thinkingPartnerQuestions.map((q, idx) => (
                    <li key={idx} className="flow-question-item">
                      <span className={`flow-question-type flow-question-${q.type}`}>
                        {q.type}
                      </span>
                      <p className="flow-question-text">{q.text}</p>
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="flow-empty-hint">
                  Select text to explore related concepts
                </p>
              )}
            </section>
          </>
        ) : (
          <div className="flow-empty">
            <div className="flow-empty-icon">
              <HelpCircle size={48} strokeWidth={1} />
            </div>
            <h4>Explore Concepts</h4>
            <p>Select text in the book to explore related concepts in the knowledge graph.</p>
          </div>
        )}
      </div>
    </div>
  );
}
