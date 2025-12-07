import { Clock, Loader2, CheckCircle, XCircle, RotateCcw, Trash2 } from 'lucide-react';
import { Sheet } from '../ui/Sheet';
import { useIngestionQueue } from '../../hooks/useIngestionQueue';
import type { IngestionQueueItem } from '../../services/graphClient';
import './IngestionQueueSheet.css';

interface IngestionQueueSheetProps {
  isOpen: boolean;
  onClose: () => void;
}

type StatusType = 'queued' | 'processing' | 'completed' | 'failed';

const STATUS_CONFIG: Record<StatusType, {
  label: string;
  icon: typeof Clock;
  className: string;
}> = {
  queued: { label: 'Queued', icon: Clock, className: 'status-queued' },
  processing: { label: 'Processing', icon: Loader2, className: 'status-processing' },
  completed: { label: 'Completed', icon: CheckCircle, className: 'status-completed' },
  failed: { label: 'Failed', icon: XCircle, className: 'status-failed' },
};

function QueueItem({
  item,
  onCancel,
  onRetry,
}: {
  item: IngestionQueueItem;
  onCancel: (calibreId: number) => void;
  onRetry: (calibreId: number) => void;
}) {
  const config = STATUS_CONFIG[item.status as StatusType] || STATUS_CONFIG.queued;
  const StatusIcon = config.icon;
  const isProcessing = item.status === 'processing';
  const isFailed = item.status === 'failed';
  const canCancel = item.status === 'queued';

  return (
    <div className={`queue-item ${config.className}`}>
      <div className="queue-item-icon">
        <StatusIcon size={20} className={isProcessing ? 'spinning' : ''} />
      </div>
      <div className="queue-item-content">
        <div className="queue-item-title">{item.title}</div>
        <div className="queue-item-meta">
          <span className="queue-item-author">{item.author || 'Unknown Author'}</span>
          <span className={`queue-item-status ${config.className}`}>{config.label}</span>
        </div>
        {item.error_message && (
          <div className="queue-item-error">{item.error_message}</div>
        )}
      </div>
      <div className="queue-item-actions">
        {canCancel && (
          <button
            className="queue-item-btn cancel"
            onClick={() => onCancel(item.calibre_id)}
            title="Cancel"
          >
            <Trash2 size={16} />
          </button>
        )}
        {isFailed && (
          <button
            className="queue-item-btn retry"
            onClick={() => onRetry(item.calibre_id)}
            title="Retry"
          >
            <RotateCcw size={16} />
          </button>
        )}
      </div>
    </div>
  );
}

export function IngestionQueueSheet({ isOpen, onClose }: IngestionQueueSheetProps) {
  const {
    items,
    isLoading,
    queuedCount,
    processingCount,
    completedCount,
    failedCount,
    cancelBook,
    retryBook,
    refresh,
  } = useIngestionQueue({ autoStart: true });

  const handleCancel = async (calibreId: number) => {
    await cancelBook(calibreId);
  };

  const handleRetry = async (calibreId: number) => {
    await retryBook(calibreId);
  };

  // Group items by status
  const processingItems = items.filter(i => i.status === 'processing');
  const queuedItems = items.filter(i => i.status === 'queued');
  const failedItems = items.filter(i => i.status === 'failed');
  const completedItems = items.filter(i => i.status === 'completed').slice(0, 5); // Show only recent 5

  const hasItems = items.length > 0;

  return (
    <Sheet
      isOpen={isOpen}
      onClose={onClose}
      snapPoints={['50%', '80%']}
      title="Ingestion Queue"
      key={isOpen ? 'open' : 'closed'}
    >
      <div className="queue-sheet">
        {/* Stats summary */}
        <div className="queue-stats">
          <div className="queue-stat">
            <span className="queue-stat-value">{processingCount}</span>
            <span className="queue-stat-label">Processing</span>
          </div>
          <div className="queue-stat">
            <span className="queue-stat-value">{queuedCount}</span>
            <span className="queue-stat-label">Queued</span>
          </div>
          <div className="queue-stat">
            <span className="queue-stat-value">{completedCount}</span>
            <span className="queue-stat-label">Completed</span>
          </div>
          {failedCount > 0 && (
            <div className="queue-stat failed">
              <span className="queue-stat-value">{failedCount}</span>
              <span className="queue-stat-label">Failed</span>
            </div>
          )}
        </div>

        {/* Empty state */}
        {!hasItems && !isLoading && (
          <div className="queue-empty">
            <Clock size={32} />
            <p>No books in queue</p>
            <span>Queue books for entity extraction from the library</span>
          </div>
        )}

        {/* Loading state */}
        {isLoading && !hasItems && (
          <div className="queue-loading">
            <Loader2 size={24} className="spinning" />
            <span>Loading queue...</span>
          </div>
        )}

        {/* Queue sections */}
        {hasItems && (
          <div className="queue-sections">
            {/* Processing */}
            {processingItems.length > 0 && (
              <div className="queue-section">
                <h4 className="queue-section-title">Currently Processing</h4>
                {processingItems.map(item => (
                  <QueueItem
                    key={item.calibre_id}
                    item={item}
                    onCancel={handleCancel}
                    onRetry={handleRetry}
                  />
                ))}
              </div>
            )}

            {/* Queued */}
            {queuedItems.length > 0 && (
              <div className="queue-section">
                <h4 className="queue-section-title">Waiting</h4>
                {queuedItems.map(item => (
                  <QueueItem
                    key={item.calibre_id}
                    item={item}
                    onCancel={handleCancel}
                    onRetry={handleRetry}
                  />
                ))}
              </div>
            )}

            {/* Failed */}
            {failedItems.length > 0 && (
              <div className="queue-section">
                <h4 className="queue-section-title failed">Failed</h4>
                {failedItems.map(item => (
                  <QueueItem
                    key={item.calibre_id}
                    item={item}
                    onCancel={handleCancel}
                    onRetry={handleRetry}
                  />
                ))}
              </div>
            )}

            {/* Completed (recent) */}
            {completedItems.length > 0 && (
              <div className="queue-section">
                <h4 className="queue-section-title completed">Recently Completed</h4>
                {completedItems.map(item => (
                  <QueueItem
                    key={item.calibre_id}
                    item={item}
                    onCancel={handleCancel}
                    onRetry={handleRetry}
                  />
                ))}
              </div>
            )}
          </div>
        )}

        {/* Refresh button */}
        <div className="queue-footer">
          <button className="queue-refresh-btn" onClick={refresh} disabled={isLoading}>
            <RotateCcw size={16} className={isLoading ? 'spinning' : ''} />
            Refresh
          </button>
        </div>
      </div>
    </Sheet>
  );
}
