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

  return (
    <div className="flow-panel" style={{ width: flowPanelWidth }}>
      <div className="flow-panel-header">
        <div className="flow-panel-title">
          <h3>Flow Mode</h3>
          {(syncStatus !== 'idle' || queuedOperationsCount > 0) && (
            <span
              className={`sync-indicator sync-${queuedOperationsCount > 0 ? 'offline' : syncStatus}`}
              title={
                queuedOperationsCount > 0
                  ? `${queuedOperationsCount} pending - click to retry`
                  : lastSyncError || undefined
              }
              onClick={queuedOperationsCount > 0 ? handleRetrySync : undefined}
            >
              {syncStatus === 'pending' && '⏳'}
              {syncStatus === 'synced' && queuedOperationsCount === 0 && '✓'}
              {syncStatus === 'error' && queuedOperationsCount === 0 && '⚠'}
              {queuedOperationsCount > 0 && (
                <>
                  📴
                  <span className="queue-count">{queuedOperationsCount}</span>
                </>
              )}
            </span>
          )}
        </div>
        <button
          className="flow-panel-close"
          onClick={() => {
            clearEntity();
            setFlowPanelOpen(false);
          }}
        >
          ×
        </button>
      </div>

      <div className="flow-panel-content">
        {isLoadingEntity ? (
          <div className="flow-loading">Searching knowledge graph...</div>
        ) : currentEntity ? (
          <>
            {/* Entity Section */}
            <section className="flow-section">
              <span className="entity-type">{currentEntity.type}</span>
              <h2 className="entity-name">{currentEntity.name}</h2>
              <p className="entity-summary">{currentEntity.summary}</p>
            </section>

            {/* Relationships Section */}
            {relationships.length > 0 && (
              <section className="flow-section">
                <h4>Related Concepts</h4>
                <ul className="relationships-list">
                  {relationships.map((rel, idx) => (
                    <li key={idx} className="relationship-item">
                      <button
                        className="relationship-link"
                        onClick={() => navigateToEntity(rel.target.id)}
                      >
                        <span className="relationship-type">{rel.type}</span>
                        <span className="relationship-target">
                          {rel.target.name}
                        </span>
                      </button>
                    </li>
                  ))}
                </ul>
              </section>
            )}

            {/* Sources Section */}
            {bookSources.length > 0 && (
              <section className="flow-section">
                <h4>Found In</h4>
                <ul className="sources-list">
                  {bookSources.map((source, idx) => (
                    <li key={idx} className="source-item">
                      <span className="source-title">{source.bookTitle}</span>
                      {source.chapter && (
                        <span className="source-chapter">{source.chapter}</span>
                      )}
                    </li>
                  ))}
                </ul>
              </section>
            )}

            {/* Thinking Partner Questions */}
            <section className="flow-section">
              <h4>Thinking Partner</h4>
              {isLoadingQuestions ? (
                <div className="flow-loading">Generating questions...</div>
              ) : thinkingPartnerQuestions.length > 0 ? (
                <ul className="questions-list">
                  {thinkingPartnerQuestions.map((q, idx) => (
                    <li key={idx} className="question-item">
                      <span className={`question-type question-type-${q.type}`}>
                        {q.type}
                      </span>
                      <p className="question-text">{q.text}</p>
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="no-questions">
                  Select text to explore related concepts
                </p>
              )}
            </section>
          </>
        ) : (
          <div className="flow-empty">
            <p>Select text in the book to explore related concepts.</p>
            <p className="flow-hint">
              The knowledge graph contains entities extracted from your library.
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
