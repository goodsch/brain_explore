import { useState, useCallback, useRef, useEffect } from 'react';
import { Reader } from './components/Reader';
import { graphClient } from './services/graphClient';
import { useFlowStore } from './store/flowStore';
import './App.css';

// Sample books for testing (public domain EPUBs via proxy)
const SAMPLE_BOOKS = [
  {
    title: 'Alice in Wonderland',
    url: '/gutenberg/cache/epub/11/pg11-images.epub',
  },
  {
    title: 'Pride and Prejudice',
    url: '/gutenberg/cache/epub/1342/pg1342-images.epub',
  },
  {
    title: 'Frankenstein',
    url: '/gutenberg/cache/epub/84/pg84-images.epub',
  },
];

interface BookInfo {
  title: string;
  url: string;
}

function App() {
  const [currentBook, setCurrentBook] = useState<BookInfo | null>(null);
  const [isLoggingIn, setIsLoggingIn] = useState(true);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const { setUserId } = useFlowStore();

  // Login on app mount
  useEffect(() => {
    async function login() {
      try {
        const profile = await graphClient.login();
        setUserId(profile.user_id);
      } catch (error) {
        console.error('Login failed:', error);
        // Continue without login - user_id will be null
      } finally {
        setIsLoggingIn(false);
      }
    }
    login();
  }, [setUserId]);

  // Handle local file selection
  const handleFileSelect = useCallback(
    (event: React.ChangeEvent<HTMLInputElement>) => {
      const file = event.target.files?.[0];
      if (file && file.name.endsWith('.epub')) {
        const url = URL.createObjectURL(file);
        setCurrentBook({
          title: file.name.replace('.epub', ''),
          url,
        });
      }
    },
    []
  );

  // Open file picker
  const openFilePicker = useCallback(() => {
    fileInputRef.current?.click();
  }, []);

  // Return to book selector
  const closeBook = useCallback(() => {
    if (currentBook?.url.startsWith('blob:')) {
      URL.revokeObjectURL(currentBook.url);
    }
    setCurrentBook(null);
  }, [currentBook]);

  // Show loading while logging in
  if (isLoggingIn) {
    return (
      <div className="app">
        <div className="loading-screen">
          <p>Connecting...</p>
        </div>
      </div>
    );
  }

  // Show reader if a book is selected
  if (currentBook) {
    return (
      <div className="app">
        <Reader url={currentBook.url} title={currentBook.title} onClose={closeBook} />
      </div>
    );
  }

  // Book selector screen
  return (
    <div className="app">
      <div className="book-selector">
        <header className="selector-header">
          <h1>IES Reader</h1>
          <p className="selector-subtitle">
            Explore books with knowledge graph integration
          </p>
        </header>

        <section className="selector-section">
          <h2>Open a Book</h2>
          <input
            ref={fileInputRef}
            type="file"
            accept=".epub"
            onChange={handleFileSelect}
            style={{ display: 'none' }}
          />
          <button className="open-file-btn" onClick={openFilePicker}>
            <svg viewBox="0 0 24 24" width="24" height="24" fill="currentColor">
              <path d="M9 16h6v-6h4l-7-7-7 7h4zm-4 2h14v2H5z" />
            </svg>
            <span>Open EPUB File</span>
          </button>
        </section>

        <section className="selector-section">
          <h2>Sample Books</h2>
          <p className="section-hint">Public domain books for testing</p>
          <div className="book-grid">
            {SAMPLE_BOOKS.map((book) => (
              <button
                key={book.title}
                className="book-card"
                onClick={() => setCurrentBook(book)}
              >
                <div className="book-cover">
                  <svg
                    viewBox="0 0 24 24"
                    width="48"
                    height="48"
                    fill="currentColor"
                  >
                    <path d="M18 2H6c-1.1 0-2 .9-2 2v16c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zM6 4h5v8l-2.5-1.5L6 12V4z" />
                  </svg>
                </div>
                <span className="book-title">{book.title}</span>
              </button>
            ))}
          </div>
        </section>

        <footer className="selector-footer">
          <p>
            Select text while reading to explore related concepts in the
            knowledge graph.
          </p>
        </footer>
      </div>
    </div>
  );
}

export default App;
