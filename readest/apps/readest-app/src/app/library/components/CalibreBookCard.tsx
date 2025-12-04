import clsx from 'clsx';
import { useState } from 'react';
import { useTranslation } from '@/hooks/useTranslation';

export interface CalibreBook {
  calibre_id: number;
  title: string;
  author: string;
  path: string;
}

interface CalibreBookCardProps {
  book: CalibreBook;
  entityCount: number | null; // null = loading, -1 = not indexed, >= 0 = count
  apiBaseUrl: string;
  onClick: (book: CalibreBook) => void;
}

const CalibreBookCard: React.FC<CalibreBookCardProps> = ({
  book,
  entityCount,
  apiBaseUrl,
  onClick,
}) => {
  const _ = useTranslation();
  const [imageError, setImageError] = useState(false);
  const [imageLoaded, setImageLoaded] = useState(false);

  const coverUrl = `${apiBaseUrl}/books/${book.calibre_id}/cover`;

  return (
    <button
      className="group flex flex-col rounded-lg p-2 transition-colors hover:bg-base-300 focus:outline-none focus:ring-2 focus:ring-primary"
      onClick={() => onClick(book)}
      aria-label={_('Open {{title}}', { title: book.title })}
    >
      {/* Cover */}
      <div className="relative aspect-[28/41] w-full overflow-hidden rounded shadow-md bg-base-200">
        {!imageError ? (
          <>
            {!imageLoaded && (
              <div className="absolute inset-0 flex items-center justify-center">
                <div className="loading loading-spinner loading-sm" />
              </div>
            )}
            <img
              src={coverUrl}
              alt={book.title}
              className={clsx(
                'h-full w-full object-cover transition-opacity',
                imageLoaded ? 'opacity-100' : 'opacity-0'
              )}
              onLoad={() => setImageLoaded(true)}
              onError={() => setImageError(true)}
            />
          </>
        ) : (
          <div className="flex h-full w-full flex-col items-center justify-center p-2 text-center">
            <span className="text-neutral-content line-clamp-3 text-sm font-medium">
              {book.title}
            </span>
            <span className="text-neutral-content/50 mt-2 line-clamp-1 text-xs">
              {book.author}
            </span>
          </div>
        )}
      </div>

      {/* Title */}
      <h4 className="mt-2 line-clamp-1 w-full text-left text-xs font-semibold">
        {book.title}
      </h4>

      {/* Author */}
      <p className="text-neutral-content line-clamp-1 w-full text-left text-xs">
        {book.author}
      </p>

      {/* Entity Badge */}
      <div className="mt-1 flex items-center gap-1">
        {entityCount === null ? (
          <div className="loading loading-spinner loading-xs" />
        ) : entityCount < 0 ? (
          <span className="text-neutral-content/50 text-xs">{_('Not indexed')}</span>
        ) : (
          <>
            <span className="inline-block h-2 w-2 rounded-full bg-success" />
            <span className="text-xs text-success">
              {entityCount} {entityCount === 1 ? _('entity') : _('entities')}
            </span>
          </>
        )}
      </div>
    </button>
  );
};

export default CalibreBookCard;
