'use client';

import { useCallback, useEffect, useMemo, useState } from 'react';
import { MdClose } from 'react-icons/md';
import { useRouter } from 'next/navigation';
import { useTranslation } from '@/hooks/useTranslation';
import { useEnv } from '@/context/EnvContext';
import { useLibraryStore } from '@/store/libraryStore';
import { navigateToReader } from '@/utils/nav';
import CalibreBookCard, { CalibreBook } from './CalibreBookCard';
import CalibreSearchBar from './CalibreSearchBar';

interface CalibreDialogProps {
  isOpen: boolean;
  onClose: () => void;
}

// Determine API base URL dynamically (same logic as flowModeStore)
const getApiBaseUrl = (): string => {
  if (typeof window === 'undefined') return 'http://localhost:8081';
  const hostname = window.location.hostname;
  if (hostname === 'localhost' || hostname === '127.0.0.1') {
    return 'http://localhost:8081';
  }
  return `http://${hostname}:8081`;
};

const CalibreDialog: React.FC<CalibreDialogProps> = ({ isOpen, onClose }) => {
  const _ = useTranslation();
  const router = useRouter();
  const { appService } = useEnv();
  const { library, setLibrary } = useLibraryStore();

  const [books, setBooks] = useState<CalibreBook[]>([]);
  const [entityCounts, setEntityCounts] = useState<Map<number, number>>(new Map());
  const [searchQuery, setSearchQuery] = useState('');
  const [hasEntitiesOnly, setHasEntitiesOnly] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const apiBaseUrl = getApiBaseUrl();

  // Fetch books from Calibre API
  useEffect(() => {
    if (!isOpen) return;

    const fetchBooks = async () => {
      setIsLoading(true);
      setError(null);
      try {
        const response = await fetch(`${apiBaseUrl}/books?limit=500`);
        if (!response.ok) throw new Error('Failed to fetch books');
        const data = await response.json();
        setBooks(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load Calibre library');
      } finally {
        setIsLoading(false);
      }
    };

    fetchBooks();
  }, [isOpen, apiBaseUrl]);

  // Fetch entity counts for visible books
  useEffect(() => {
    if (books.length === 0) return;

    const fetchEntityCounts = async () => {
      const newCounts = new Map<number, number>();

      // Fetch in batches to avoid overwhelming the API
      const batchSize = 10;
      for (let i = 0; i < books.length; i += batchSize) {
        const batch = books.slice(i, i + batchSize);
        await Promise.all(
          batch.map(async (book) => {
            try {
              const response = await fetch(
                `${apiBaseUrl}/graph/entities/by-calibre-id/${book.calibre_id}?limit=1`
              );
              if (response.ok) {
                const data = await response.json();
                newCounts.set(book.calibre_id, data.total ?? 0);
              } else if (response.status === 404) {
                newCounts.set(book.calibre_id, -1); // Not indexed
              }
            } catch {
              newCounts.set(book.calibre_id, -1);
            }
          })
        );
        setEntityCounts(new Map(newCounts));
      }
    };

    fetchEntityCounts();
  }, [books, apiBaseUrl]);

  // Filter books based on search and hasEntitiesOnly
  const filteredBooks = useMemo(() => {
    let result = books;

    // Search filter
    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      result = result.filter(
        (book) =>
          book.title.toLowerCase().includes(query) ||
          book.author.toLowerCase().includes(query)
      );
    }

    // Has entities filter
    if (hasEntitiesOnly) {
      result = result.filter((book) => {
        const count = entityCounts.get(book.calibre_id);
        return count !== undefined && count > 0;
      });
    }

    return result;
  }, [books, searchQuery, hasEntitiesOnly, entityCounts]);

  // Handle book selection - import and open
  const handleBookClick = useCallback(
    async (calibreBook: CalibreBook) => {
      if (!appService) return;

      try {
        // Import the book from Calibre file path
        const newLibrary = [...library];
        const book = await appService.importBook(calibreBook.path, newLibrary, true, true, false, false);

        if (book) {
          // Add calibreId to the book
          book.calibreId = calibreBook.calibre_id;

          // Update library
          setLibrary(newLibrary);
          await appService.saveLibraryBooks(newLibrary);

          // Close dialog and navigate to reader
          onClose();
          navigateToReader(router, [book.hash]);
        }
      } catch (err) {
        console.error('Failed to open Calibre book:', err);
        setError(_('Failed to open book. The file may not be accessible.'));
      }
    },
    [appService, library, setLibrary, onClose, router, _]
  );

  const handleSearchChange = useCallback((query: string) => {
    setSearchQuery(query);
  }, []);

  const handleHasEntitiesChange = useCallback((value: boolean) => {
    setHasEntitiesOnly(value);
  }, []);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
      <div className="bg-base-100 flex h-[90vh] w-[90vw] max-w-4xl flex-col rounded-xl shadow-2xl">
        {/* Header */}
        <div className="flex items-center justify-between border-b border-base-300 px-6 py-4">
          <h2 className="text-xl font-semibold">{_('Calibre Library')}</h2>
          <button
            onClick={onClose}
            className="btn btn-ghost btn-sm btn-circle"
            aria-label={_('Close')}
          >
            <MdClose size={24} />
          </button>
        </div>

        {/* Search Bar */}
        <div className="border-b border-base-300 px-6 py-4">
          <CalibreSearchBar
            onSearchChange={handleSearchChange}
            hasEntitiesOnly={hasEntitiesOnly}
            onHasEntitiesChange={handleHasEntitiesChange}
          />
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto px-6 py-4">
          {isLoading ? (
            <div className="flex h-full items-center justify-center">
              <div className="loading loading-spinner loading-lg" />
            </div>
          ) : error ? (
            <div className="flex h-full flex-col items-center justify-center gap-4">
              <p className="text-error">{error}</p>
              <button
                onClick={() => window.location.reload()}
                className="btn btn-primary btn-sm"
              >
                {_('Retry')}
              </button>
            </div>
          ) : filteredBooks.length === 0 ? (
            <div className="flex h-full items-center justify-center">
              <p className="text-neutral-content">
                {searchQuery || hasEntitiesOnly
                  ? _('No books match your filters')
                  : _('No books in Calibre library')}
              </p>
            </div>
          ) : (
            <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 md:grid-cols-4">
              {filteredBooks.map((book) => (
                <CalibreBookCard
                  key={book.calibre_id}
                  book={book}
                  entityCount={entityCounts.get(book.calibre_id) ?? null}
                  apiBaseUrl={apiBaseUrl}
                  onClick={handleBookClick}
                />
              ))}
            </div>
          )}
        </div>

        {/* Footer with count */}
        <div className="border-t border-base-300 px-6 py-3 text-sm text-neutral-content">
          {_('{{count}} books', { count: filteredBooks.length })}
          {hasEntitiesOnly && ` (${_('filtered')})`}
        </div>
      </div>
    </div>
  );
};

export default CalibreDialog;
