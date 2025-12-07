import { useState, useEffect, useCallback } from 'react';
import { Library, Upload, Wifi, WifiOff, Download, Clock, Loader2, AlertCircle } from 'lucide-react';
import { graphClient, type CalibreBook } from '../../services/graphClient';
import { useIngestionQueue } from '../../hooks/useIngestionQueue';
import { BookCard } from './BookCard';
import { SearchBar } from './SearchBar';
import { IngestionQueueSheet } from './IngestionQueueSheet';
import './LibraryBrowser.css';

interface LibraryBrowserProps {
  onBookSelect: (book: CalibreBook) => void;
  onLocalFileSelect: (file: File) => void;
}

type ViewFilter = 'all' | 'indexed' | 'queued';

export function LibraryBrowser({ onBookSelect, onLocalFileSelect }: LibraryBrowserProps) {
  const [books, setBooks] = useState<CalibreBook[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [filter, setFilter] = useState<ViewFilter>('all');
  const [isOnline, setIsOnline] = useState(true);
  const [showInstallPrompt, setShowInstallPrompt] = useState(false);
  const [deferredPrompt, setDeferredPrompt] = useState<BeforeInstallPromptEvent | null>(null);
  const [showQueueSheet, setShowQueueSheet] = useState(false);

  // Use the ingestion queue hook for automatic polling
  const {
    items: queueItems,
    queuedCount,
    processingCount,
    failedCount,
    hasActiveItems,
    refresh: refreshQueueStatus,
  } = useIngestionQueue({ pollIntervalMs: 10000, pollOnlyWhenActive: true });

  // Derive queuedBookIds set for backward compatibility with BookCard
  const queuedBookIds = new Set(
    queueItems
      .filter(item => item.status === 'queued' || item.status === 'processing')
      .map(item => item.calibre_id)
  );

  // Check backend availability
  useEffect(() => {
    graphClient.isBackendAvailable().then(setIsOnline);
  }, []);

  // Fetch books
  useEffect(() => {
    async function fetchBooks() {
      setLoading(true);
      setError(null);
      try {
        const response = await graphClient.getBooks(searchQuery || undefined);
        setBooks(response.books || []);
      } catch (err) {
        console.error('Failed to fetch books:', err);
        setError('Could not load library. Is the backend running?');
        setBooks([]);
      } finally {
        setLoading(false);
      }
    }

    fetchBooks();
  }, [searchQuery]);

  // Filter books
  const filteredBooks = filter === 'indexed'
    ? books.filter((b) => b.entity_count && b.entity_count > 0)
    : filter === 'queued'
    ? books.filter((b) => queuedBookIds.has(b.calibre_id))
    : books;

  // Handle file input
  const handleFileChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const file = e.target.files?.[0];
      if (file && file.name.endsWith('.epub')) {
        onLocalFileSelect(file);
      }
    },
    [onLocalFileSelect]
  );

  // PWA install prompt
  useEffect(() => {
    const handler = (e: BeforeInstallPromptEvent) => {
      e.preventDefault();
      setDeferredPrompt(e);
      setShowInstallPrompt(true);
    };

    window.addEventListener('beforeinstallprompt', handler as EventListener);
    return () => window.removeEventListener('beforeinstallprompt', handler as EventListener);
  }, []);

  const handleInstall = async () => {
    if (!deferredPrompt) return;

    deferredPrompt.prompt();
    const { outcome } = await deferredPrompt.userChoice;

    if (outcome === 'accepted') {
      setShowInstallPrompt(false);
    }
    setDeferredPrompt(null);
  };

  return (
    <div className="library-browser">
      {/* Header */}
      <header className="library-header">
        <div className="library-header-content">
          <div className="library-brand">
            <Library size={28} strokeWidth={1.5} />
            <h1 className="ies-heading ies-heading-3">IES Reader</h1>
          </div>

          <div className="library-header-actions">
            {/* Online status */}
            <div
              className={`library-status ${isOnline ? 'online' : 'offline'}`}
              title={isOnline ? 'Connected to backend' : 'Backend offline'}
            >
              {isOnline ? <Wifi size={18} /> : <WifiOff size={18} />}
            </div>

            {/* Queue indicator - shows when there are items in queue */}
            {(hasActiveItems || failedCount > 0) && (
              <button
                className={`library-queue-indicator ${failedCount > 0 ? 'has-failed' : processingCount > 0 ? 'processing' : ''}`}
                title={`${queuedCount} queued, ${processingCount} processing${failedCount > 0 ? `, ${failedCount} failed` : ''}`}
                onClick={() => setShowQueueSheet(true)}
              >
                {processingCount > 0 ? (
                  <Loader2 size={16} className="spinning" />
                ) : failedCount > 0 ? (
                  <AlertCircle size={16} />
                ) : (
                  <Clock size={16} />
                )}
                <span>
                  {processingCount > 0
                    ? `${processingCount}/${queuedCount + processingCount}`
                    : failedCount > 0
                    ? `${failedCount} failed`
                    : queuedCount}
                </span>
              </button>
            )}

            {/* Install button */}
            {showInstallPrompt && (
              <button className="ies-btn ies-btn-secondary" onClick={handleInstall}>
                <Download size={18} />
                <span className="ies-hide-mobile">Install App</span>
              </button>
            )}

            {/* Upload button */}
            <label className="ies-btn ies-btn-ghost library-upload-btn">
              <Upload size={18} />
              <span className="ies-hide-mobile">Open File</span>
              <input
                type="file"
                accept=".epub"
                onChange={handleFileChange}
                style={{ display: 'none' }}
              />
            </label>
          </div>
        </div>

        <p className="library-subtitle">
          Explore your books with knowledge graph integration
        </p>
      </header>

      {/* Search and filters */}
      <div className="library-controls">
        <SearchBar onSearch={setSearchQuery} placeholder="Search by title or author..." />

        <div className="library-filters">
          <button
            className={`library-filter-btn ${filter === 'all' ? 'active' : ''}`}
            onClick={() => setFilter('all')}
          >
            All Books
            {!loading && <span className="filter-count">{books.length}</span>}
          </button>
          <button
            className={`library-filter-btn ${filter === 'indexed' ? 'active' : ''}`}
            onClick={() => setFilter('indexed')}
          >
            Indexed
            {!loading && (
              <span className="filter-count">
                {books.filter((b) => b.entity_count && b.entity_count > 0).length}
              </span>
            )}
          </button>
          {queuedBookIds.size > 0 && (
            <button
              className={`library-filter-btn library-filter-btn-queued ${filter === 'queued' ? 'active' : ''}`}
              onClick={() => setFilter('queued')}
            >
              <Clock size={14} />
              Queued
              <span className="filter-count">{queuedBookIds.size}</span>
            </button>
          )}
        </div>
      </div>

      {/* Book grid */}
      <main className="library-content">
        {loading ? (
          <div className="library-grid ies-stagger-children">
            {[...Array(12)].map((_, i) => (
              <div key={i} className="book-card-skeleton-wrapper">
                <div className="book-card-cover">
                  <div className="ies-skeleton" style={{ height: '100%' }} />
                </div>
                <div className="book-card-info">
                  <div className="ies-skeleton" style={{ height: '1rem', width: '80%', marginBottom: '0.5rem' }} />
                  <div className="ies-skeleton" style={{ height: '0.875rem', width: '60%' }} />
                </div>
              </div>
            ))}
          </div>
        ) : error ? (
          <div className="library-error">
            <WifiOff size={48} strokeWidth={1} />
            <h3>Connection Error</h3>
            <p>{error}</p>
            <button className="ies-btn ies-btn-primary" onClick={() => window.location.reload()}>
              Retry
            </button>
          </div>
        ) : filteredBooks.length === 0 ? (
          <div className="library-empty">
            <Library size={48} strokeWidth={1} />
            <h3>No Books Found</h3>
            <p>
              {searchQuery
                ? `No books match "${searchQuery}"`
                : filter === 'indexed'
                ? 'No indexed books yet. Run the ingestion pipeline to index your library.'
                : filter === 'queued'
                ? 'No books are currently queued for indexing.'
                : 'Your library is empty. Add some books to Calibre to get started.'}
            </p>
          </div>
        ) : (
          <div className="library-grid ies-stagger-children">
            {filteredBooks.map((book) => (
              <BookCard
                key={book.calibre_id}
                book={book}
                onSelect={onBookSelect}
                isQueued={queuedBookIds.has(book.calibre_id)}
                onQueueStatusChange={refreshQueueStatus}
              />
            ))}
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="library-footer">
        <p>
          Select text while reading to explore related concepts in the knowledge graph.
        </p>
      </footer>

      {/* Ingestion Queue Sheet */}
      <IngestionQueueSheet
        isOpen={showQueueSheet}
        onClose={() => setShowQueueSheet(false)}
      />
    </div>
  );
}

// Type for PWA install prompt
interface BeforeInstallPromptEvent extends Event {
  prompt: () => Promise<void>;
  userChoice: Promise<{ outcome: 'accepted' | 'dismissed' }>;
}
