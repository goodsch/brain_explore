import { useState, memo } from 'react';
import { BookOpen, Sparkles } from 'lucide-react';
import type { CalibreBook } from '../../services/graphClient';
import { graphClient } from '../../services/graphClient';

interface BookCardProps {
  book: CalibreBook;
  onSelect: (book: CalibreBook) => void;
}

export const BookCard = memo(function BookCard({ book, onSelect }: BookCardProps) {
  const [imageError, setImageError] = useState(false);
  const [imageLoaded, setImageLoaded] = useState(false);

  const coverUrl = graphClient.getBookCoverUrl(book.calibre_id);
  const hasEntities = book.entity_count && book.entity_count > 0;

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
      </div>

      <div className="book-card-info">
        <h3 className="book-card-title">{book.title}</h3>
        <p className="book-card-author">{book.author}</p>
      </div>
    </button>
  );
});
