import { useState, useCallback, useEffect } from 'react';
import { Reader } from './components/Reader';
import { LibraryBrowser } from './components/library/LibraryBrowser';
import { graphClient, type CalibreBook } from './services/graphClient';
import { useFlowStore } from './store/flowStore';
import './App.css';

interface BookInfo {
  title: string;
  url: string;
  calibreId?: number;
}

function App() {
  const [currentBook, setCurrentBook] = useState<BookInfo | null>(null);
  const [isLoggingIn, setIsLoggingIn] = useState(true);
  const { setUserId } = useFlowStore();
  const [theme, setTheme] = useState<'light' | 'dark'>('dark');

  useEffect(() => {
    async function login() {
      try {
        // Mock login for now to prevent blocking
        setUserId('user-123');
      } finally {
        setIsLoggingIn(false);
      }
    }
    login();
  }, [setUserId]);

  const handleBookSelect = useCallback((book: CalibreBook) => {
    setCurrentBook({
      title: book.title,
      url: `/books/${book.calibre_id}/file`, // Mock URL
      calibreId: book.calibre_id,
    });
  }, []);

  const handleLocalFileSelect = useCallback((file: File) => {
    const url = URL.createObjectURL(file);
    setCurrentBook({
      title: file.name.replace('.epub', ''),
      url,
    });
  }, []);

  const closeBook = useCallback(() => {
    if (currentBook?.url.startsWith('blob:')) {
      URL.revokeObjectURL(currentBook.url);
    }
    setCurrentBook(null);
  }, [currentBook]);

  if (isLoggingIn) {
    return <div className="loading-screen">Loading...</div>;
  }

  if (currentBook) {
    return (
      <Reader
        url={currentBook.url}
        title={currentBook.title}
        calibreId={currentBook.calibreId}
        onClose={closeBook}
      />
    );
  }

  return (
    <LibraryBrowser
      onBookSelect={handleBookSelect}
      onLocalFileSelect={handleLocalFileSelect}
    />
  );
}

export default App;
