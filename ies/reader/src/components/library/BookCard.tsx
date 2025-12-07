import { useState, memo, useCallback } from 'react';
import { BookOpen, Sparkles, Database, Loader2, Check, Clock } from 'lucide-react';
import type { CalibreBook } from '../../services/graphClient';
import { graphClient } from '../../services/graphClient';

interface BookCardProps {
  book: CalibreBook;
  onSelect: (book: CalibreBook) => void;
  isQueued?: boolean;
  onQueueStatusChange?: () => void;
}

export const BookCard = memo(function BookCard({
  book,
  onSelect,
  isQueued = false,
  onQueueStatusChange,
}: BookCardProps) {
  const [imageError, setImageError] = useState(false);
  const [imageLoaded, setImageLoaded] = useState(false);
  const [queueState, setQueueState] = useState<'idle' | 'loading' | 'success' | 'error'>('idle');

  const coverUrl = graphClient.getBookCoverUrl(book.calibre_id);
  const hasEntities = book.entity_count && book.entity_count > 0;

  const handleQueueForIngestion = useCallback(async (e: React.MouseEvent) => {
    e.stopPropagation(); // Prevent opening the book
    e.preventDefault();

    if (queueState === 'loading') return;

    setQueueState('loading');
    try {
      await graphClient.queueBookForIngestion(book.calibre_id);
      setQueueState('success');
      onQueueStatusChange?.();
      // Reset to idle after showing success
      setTimeout(() => setQueueState('idle'), 2000);
    } catch (error) {
      console.error('Failed to queue book:', error);
      setQueueState('error');
      setTimeout(() => setQueueState('idle'), 3000);
    }
  }, [book.calibre_id, queueState, onQueueStatusChange]);

  return (
    <button
      className="book-card"
      onClick={() => onSelect(book)}
      aria-label={`Open ${book.title} by ${book.author}`}
    >
      <div className="book-card-cover">
        {!imageError ? (
          <>
            {!imageLoaded && (
              <div className="book-card-skeleton ies-skeleton" />
            )}
            <img
              src={coverUrl}
              alt={`Cover of ${book.title}`}
              loading="lazy"
              onLoad={() => setImageLoaded(true)}
              onError={() => setImageError(true)}
              style={{ opacity: imageLoaded ? 1 : 0 }}
            />
          </>
        ) : (
          <div className="book-card-placeholder">
            <BookOpen size={48} strokeWidth={1.5} />
          </div>
        )}

        {/* Indexed badge */}
        {hasEntities && (
          <div className="book-card-badge" title={`${book.entity_count} entities indexed`}>
            <Sparkles size={12} />
            <span>{book.entity_count}</span>
          </div>
        )}

        {/* Queued badge */}
        {isQueued && !hasEntities && (
          <div className="book-card-badge book-card-badge-queued" title="Queued for indexing">
            <Clock size={12} />
            <span>Queued</span>
          </div>
        )}
      </div>

      <div className="book-card-info">
        <h3 className="book-card-title">{book.title}</h3>
        <p className="book-card-author">{book.author}</p>

        {/* Queue for indexing button - only show when not indexed and not queued */}
        {!hasEntities && !isQueued && (
          <button
            className={`book-card-queue-btn ${queueState}`}
            onClick={handleQueueForIngestion}
            disabled={queueState === 'loading'}
            title="Queue this book for entity extraction"
          >
            {queueState === 'idle' && (
              <>
                <Database size={12} />
                <span>Index</span>
              </>
            )}
            {queueState === 'loading' && (
              <>
                <Loader2 size={12} className="spin" />
                <span>Queuing...</span>
              </>
            )}
            {queueState === 'success' && (
              <>
                <Check size={12} />
                <span>Queued!</span>
              </>
            )}
            {queueState === 'error' && (
              <>
                <Database size={12} />
                <span>Retry</span>
              </>
            )}
          </button>
        )}
      </div>
    </button>
  );
});
